import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


AUDIT_LOG_PATH = Path(os.getenv("VAJRA_AUDIT_LOG", "logs/audit.jsonl"))


def ensure_log_file() -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not AUDIT_LOG_PATH.exists():
        AUDIT_LOG_PATH.touch()


def write_audit_event(event_type: str, payload: Dict[str, Any], actor: str = "system") -> Dict[str, Any]:
    ensure_log_file()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "actor": actor,
        "payload": payload,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return record
