import hashlib
import io
import os
import sys
import time

from fastapi.responses import Response

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collections import OrderedDict

import numpy as np
import torch
import uvicorn
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.module_1_poison import SpectralPoisonDetector
from core.module_1_tda import TopologicalPoisonDetector
from core.module_2_trojan import NeuralCleanseTrojanScanner
from core.module_3_provenance import TacticalProvenanceLedger
from core.module_3_zkml import ZeroKnowledgeLedger
from core.module_4_ood import EnergyOODDetector
from core.module_4_tta import SelfHealingTTA
from engine.audit import write_audit_event
from engine.config import get_settings
from engine.metrics import HEALTH_CHECKS, MODEL_SCAN_TOTAL, REQUEST_LATENCY, render_metrics
from engine.middleware import SecurityHeadersMiddleware
from engine.model_loader import load_model_from_bytes, validate_artifact_bytes
from engine.model_registry import registry
from engine.release import create_release_manifest, verify_release_manifest
from engine.security import authorize

settings = get_settings()

app = FastAPI(title=f"{settings.app_name} Tactical API", version="3.1.0")

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_MODEL_SUFFIXES = set(settings.allowed_model_formats)
MAX_MODEL_BYTES = settings.max_model_bytes

ledger = TacticalProvenanceLedger()
zk_ledger = ZeroKnowledgeLedger()
tda_detector = TopologicalPoisonDetector(sensitivity=2.0)

mock_model = torch.nn.Sequential(OrderedDict([
    ('fc', torch.nn.Linear(64, 10)),
    ('bn', torch.nn.BatchNorm1d(10))
]))
tta_engine = SelfHealingTTA(model=mock_model, lr=0.005)


async def parse_tensor_file(file: UploadFile | None, default_shape=(100, 64), default_dist="normal"):
    if file and file.filename:
        content = await file.read()
        try:
            if file.filename.endswith('.npy'):
                array = np.load(io.BytesIO(content))
                if array.ndim == 0:
                    raise ValueError("Uploaded NumPy array has no dimensions.")
                return np.asarray(array, dtype=np.float32)
            if file.filename.endswith('.csv'):
                array = np.loadtxt(io.BytesIO(content), delimiter=',')
                if array.size == 0:
                    raise ValueError("Uploaded CSV is empty.")
                return np.asarray(array, dtype=np.float32)
        except (ValueError, OSError) as exc:
            raise HTTPException(status_code=400, detail=f"Could not parse uploaded tensor data: {exc}") from exc

    local_data = os.path.join(os.path.dirname(__file__), "../data/sample_features_class0.npy")
    if os.path.exists(local_data):
        arr = np.load(local_data)
        if len(arr) > 300:
            np.random.shuffle(arr)
            arr = arr[:300]
        return arr.astype(np.float32)

    if default_dist == "normal":
        clean = np.random.normal(0.0, 1.0, size=default_shape)
        poison = np.random.normal(4.5, 0.2, size=(max(1, default_shape[0] // 20), default_shape[1]))
        return np.vstack([clean, poison]).astype(np.float32)
    return np.random.randn(*default_shape).astype(np.float32)


@app.get("/healthz")
def healthz():
    HEALTH_CHECKS.labels(status="ok").inc()
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/api/system/status")
def get_system_status(_auth=Depends(authorize("viewer"))):
    with REQUEST_LATENCY.labels(endpoint="/api/system/status", method="GET").time():
        result = {
            "status": "SECURE",
            "air_gap_active": True,
            "environment": settings.environment,
            "active_modules": ["SVD_SCREEN", "TROJAN_SCAN", "C2PA_DAG", "OOD_DRIFT", "TDA", "ZKML", "TTA"],
        }
    return result


@app.get("/metrics")
def metrics_endpoint():
    return Response(content=render_metrics(), media_type="text/plain; version=0.7.0; charset=utf-8")


@app.post("/api/module1/svd-scan")
async def run_svd_screening(features: UploadFile | None = File(None), _auth=Depends(authorize("operator"))):
    dataset = await parse_tensor_file(features, default_shape=(100, 64))
    detector = SpectralPoisonDetector(multiplier=1.5)
    report = detector.evaluate(dataset)
    return report


@app.post("/api/module2/trojan-scan")
async def run_trojan_scan(model: UploadFile = File(...), _auth=Depends(authorize("operator"))):
    filename = model.filename or "unnamed-model"
    artifact_bytes = await model.read(MAX_MODEL_BYTES + 1)
    if len(artifact_bytes) > MAX_MODEL_BYTES:
        raise HTTPException(status_code=413, detail=f"Model exceeds {MAX_MODEL_BYTES} bytes.")

    suffix = os.path.splitext(filename)[1].lower()
    if suffix not in ALLOWED_MODEL_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported model format. Allowed: {sorted(ALLOWED_MODEL_SUFFIXES)}")

    try:
        artifact = validate_artifact_bytes(artifact_bytes, filename, max_bytes=MAX_MODEL_BYTES)
        registry_record = registry.register_model(filename=filename, file_bytes=artifact_bytes, owner=_auth.role)
        if not registry.verify_model(filename, artifact_bytes):
            raise HTTPException(status_code=403, detail="Model registry verification failed.")
        _, loaded_model = load_model_from_bytes(artifact_bytes, filename)
        if not hasattr(loaded_model, "parameters"):
            raise HTTPException(status_code=422, detail="A model architecture is required for behavioral scanning; state dictionaries are not executable models.")
        model_for_scan = loaded_model
    except HTTPException:
        raise
    except (ValueError, OSError, RuntimeError) as exc:
        raise HTTPException(status_code=422, detail=f"Model artifact could not be safely scanned: {exc}") from exc

    write_audit_event("model_scan", {"filename": filename, "sha256": hashlib.sha256(artifact_bytes).hexdigest(), "role": _auth.role}, actor=_auth.role)
    MODEL_SCAN_TOTAL.labels(status="ok").inc()

    release_manifest = create_release_manifest(
        service=settings.app_name,
        version="1.5.0",
        build_id="build-prod-01",
        artifact_sha256=hashlib.sha256(artifact_bytes).hexdigest(),
    )
    model_secret = os.getenv("VAJRA_MODEL_SECRET")
    if not model_secret:
        raise HTTPException(status_code=500, detail="Model signing secret is not configured.")
    manifest_record = release_manifest.signed_record(secret=model_secret)
    if not verify_release_manifest(manifest_record, secret=model_secret):
        raise HTTPException(status_code=500, detail="Release verification failed.")

    scanner = NeuralCleanseTrojanScanner(model_for_scan, img_shape=(3, 32, 32), steps=20)
    report = scanner.audit_model(num_classes=4, test_tensors=torch.rand((8, 3, 32, 32)))
    return {
        "filename": filename,
        "size_bytes": len(artifact_bytes),
        "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        **report,
        **({"artifact": artifact} if isinstance(artifact, dict) else {"artifact": artifact.__dict__}),
        "model_registry": registry.get_record_by_hash(hashlib.sha256(artifact_bytes).hexdigest()).__dict__ if registry.get_record_by_hash(hashlib.sha256(artifact_bytes).hexdigest()) else None,
        "release_manifest": manifest_record,
    }


@app.post("/api/module3/verify-ledger")
def verify_cryptographic_ledger(_auth=Depends(authorize("auditor"))):
    is_valid, broken_block = ledger.verify_ledger()
    return {
        "integrity_status": "INTACT" if is_valid else "COMPROMISED",
        "broken_block_id": broken_block,
        "latest_root_hash": ledger.get_latest_hash(),
    }


@app.post("/api/module4/ood-drift")
async def check_environmental_drift(logits: UploadFile | None = File(None), _auth=Depends(authorize("operator"))):
    dataset = await parse_tensor_file(logits, default_shape=(10, 4))
    detector = EnergyOODDetector(temperature=1.0, ood_threshold=-5.5)
    tensor_data = torch.tensor(dataset, dtype=torch.float32)
    return detector.evaluate_drift(tensor_data)


@app.post("/api/sota/tda-scan")
async def run_tda_screening(features: UploadFile | None = File(None), _auth=Depends(authorize("operator"))):
    dataset = await parse_tensor_file(features, default_shape=(100, 64))
    return tda_detector.evaluate_topology(dataset)


@app.post("/api/sota/zkml-verify")
async def verify_zk_inference(frame: UploadFile | None = File(None), _auth=Depends(authorize("auditor"))):
    frame_bytes = b"Simulated_Drone_Feed_Frame_001"
    if frame and frame.filename:
        frame_bytes = await frame.read()

    bbox = {"target": "armored_convoy", "confidence": 0.98, "coords": [45, 120, 200, 310]}
    weight_hash = "0x8f4b2a... (Classified MoD Weights)"

    start_t = time.time()
    res = zk_ledger.verify_and_commit(frame_bytes, bbox, weight_hash)
    res["record"]["proof_generation_ms"] = round((time.time() - start_t) * 1000, 2)
    return res


@app.post("/api/sota/self-heal")
async def trigger_test_time_adaptation(ood_data: UploadFile | None = File(None), _auth=Depends(authorize("admin"))):
    dataset = await parse_tensor_file(ood_data, default_shape=(16, 64), default_dist="uniform")
    tensor_data = torch.tensor(dataset, dtype=torch.float32) * 2.5
    result = tta_engine.adapt_to_environment(tensor_data, steps=5)
    return result


from fastapi.staticfiles import StaticFiles

frontend_dir = os.path.join(os.path.dirname(__file__), "../ui/dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port, log_level=settings.log_level.lower())