import hashlib
import hmac
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ModelRecord:
    filename: str
    sha256: str
    size_bytes: int
    signed_digest: str
    owner: str
    tags: List[str] = field(default_factory=list)


class SignedModelRegistry:
    """A lightweight registry for signed artifact metadata in production deployments."""

    def __init__(self, registry_path: Optional[str] = None):
        self.registry_path = registry_path or os.getenv("VAJRA_MODEL_REGISTRY", "data/model_registry.json")
        self._path = Path(self.registry_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._records: Dict[str, ModelRecord] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._path.write_text("{}", encoding="utf-8")
            return
        try:
            import json
            raw = json.loads(self._path.read_text(encoding="utf-8") or "{}")
            for key, value in raw.items():
                self._records[key] = ModelRecord(**value)
        except Exception:
            self._records = {}

    def _save(self) -> None:
        import json
        payload = {name: record.__dict__ for name, record in self._records.items()}
        self._path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def _sign_digest(self, sha256: str) -> str:
        secret = os.getenv("VAJRA_MODEL_SECRET")
        if not secret:
            raise RuntimeError("VAJRA_MODEL_SECRET is required")
        return hmac.new(secret.encode("utf-8"), sha256.encode("utf-8"), hashlib.sha256).hexdigest()

    def register_model(self, filename: str, file_bytes: bytes, owner: str = "system", tags: Optional[List[str]] = None) -> ModelRecord:
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        record = ModelRecord(
            filename=filename,
            sha256=sha256,
            size_bytes=len(file_bytes),
            signed_digest=self._sign_digest(sha256),
            owner=owner,
            tags=list(tags or []),
        )
        self._records[sha256] = record
        self._save()
        return record

    def verify_model(self, filename: str, file_bytes: bytes) -> bool:
        sha256 = hashlib.sha256(file_bytes).hexdigest()
        record = self._records.get(sha256)
        if record is None:
            return False
        if record.filename != filename:
            return False
        return record.signed_digest == self._sign_digest(sha256)

    def list_models(self) -> List[ModelRecord]:
        return list(self._records.values())

    def get_record_by_hash(self, sha256: str) -> Optional[ModelRecord]:
        return self._records.get(sha256)


registry = SignedModelRegistry()
