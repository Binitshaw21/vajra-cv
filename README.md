# VAJRA-CV

VAJRA-CV is a secure, air-gapped computer vision assurance platform designed to detect model poisoning, backdoor triggers, provenance issues, OOD drift, and deployment risk in edge ML systems.

## Overview

The platform is structured as a security-first MLOps and assurance control plane for CV models. It provides:

- poison detection using spectral anomaly analysis
- trojan scanning using trigger inversion and MAD scoring
- provenance ledger validation with hash chaining and signatures
- OOD drift detection using free-energy logic
- audit logging and signed model registry tracking
- deployment-ready runtime configuration and container orchestration

## Production architecture

### Runtime
- Python backend with FastAPI
- Docker and Docker Compose deployment
- Prometheus and Grafana observability
- Kubernetes manifest support

### Security
- API key enforcement for protected routes
- RBAC-style access control
- signed model registry metadata
- audit log trail for model actions

## Local setup

1. Create a Python environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the API:
   `python -m uvicorn engine.api_gateway:app --host 0.0.0.0 --port 8000`
4. Run tests:
   `pytest -q`

## Local demo fixtures

Generate reproducible inputs for each assurance section:

```powershell
python tools/generate_feature_fixtures.py
python tools/generate_trojan_fixtures.py
python tools/generate_tta_fixtures.py
python tools/generate_frame_fixture.py
python tools/generate_ledger_fixtures.py
```

Expected demo outcomes:

- `data/features_safe.npy`: `CLEAN`
- `data/features_flagged.npy`: `COMPROMISED`
- `models/model_safe.pth`: `CERTIFIED_CLEAN`
- `models/model_flagged_trojan.pth`: `FLAGGED_TROJAN`
- `data/tta_drifted.npy`: `SELF_HEALING_COMPLETE`
- `data/ledger_intact.db`: `INTACT`
- `data/ledger_tampered.db`: `COMPROMISED`
- `data/sample_inference_frame.png`: `COMMITMENT_RECORDED`

The commitment demo is intentionally labeled as a commitment. A production zk-SNARK/PLONK proving backend is not included.

## Environment variables

See [.env.example](.env.example) for sample values.

## Docker

```bash
docker compose up --build
```

## Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

## Production readiness

See [production_readiness.md](production_readiness.md).
