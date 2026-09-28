import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class ReleaseManifest:
    service: str
    version: str
    build_id: str
    artifact_sha256: str
    timestamp: str
    signed_by: str = "vajra-platform"

    def payload(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "version": self.version,
            "build_id": self.build_id,
            "artifact_sha256": self.artifact_sha256,
            "timestamp": self.timestamp,
            "signed_by": self.signed_by,
        }

    def sign(self, secret: str | None = None) -> str:
        secret_value = secret or os.getenv("VAJRA_MODEL_SECRET")
        if not secret_value:
            raise RuntimeError("VAJRA_MODEL_SECRET is required")
        payload_json = json.dumps(self.payload(), sort_keys=True).encode("utf-8")
        return hmac.new(secret_value.encode("utf-8"), payload_json, hashlib.sha256).hexdigest()

    def signed_record(self, secret: str | None = None) -> Dict[str, Any]:
        return {
            **self.payload(),
            "signature": self.sign(secret),
        }


def create_release_manifest(service: str, version: str, build_id: str, artifact_sha256: str, signed_by: str = "vajra-platform") -> ReleaseManifest:
    return ReleaseManifest(
        service=service,
        version=version,
        build_id=build_id,
        artifact_sha256=artifact_sha256,
        timestamp=datetime.now(timezone.utc).isoformat(),
        signed_by=signed_by,
    )


def verify_release_manifest(manifest: Dict[str, Any], secret: str | None = None) -> bool:
    if not manifest.get("signature"):
        return False
    payload = {k: v for k, v in manifest.items() if k != "signature"}
    expected = hmac.new(
        (secret or os.getenv("VAJRA_MODEL_SECRET") or "").encode("utf-8"),
        json.dumps(payload, sort_keys=True).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(manifest["signature"], expected)
