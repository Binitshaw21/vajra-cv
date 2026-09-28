import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


class ArtifactRegistry:
    def __init__(self, storage_path: str = "data/artifact_registry.json", retention_days: int = 30):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        try:
            return json.loads(self.storage_path.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}

    def _save(self, payload: dict) -> None:
        self.storage_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def add(self, artifact: dict) -> dict:
        payload = self._load()
        payload[artifact["sha256"]] = artifact
        self._save(payload)
        return artifact

    def prune_expired(self) -> list[str]:
        payload = self._load()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        removed = []
        for sha256, artifact in list(payload.items()):
            created = artifact.get("created_at")
            if not created:
                continue
            try:
                created_at = datetime.fromisoformat(created)
            except ValueError:
                continue
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if created_at < cutoff:
                removed.append(sha256)
                del payload[sha256]
        self._save(payload)
        return removed
