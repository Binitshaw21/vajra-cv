"""Create real intact and tampered provenance-ledger fixtures for local demos."""
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.module_3_provenance import TacticalProvenanceLedger


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def build_ledger(database_path: Path, key_path: Path) -> None:
    if database_path.exists():
        database_path.unlink()
    if key_path.exists():
        key_path.unlink()
    os.environ["VAJRA_PROVENANCE_KEY_PATH"] = str(key_path)
    ledger = TacticalProvenanceLedger(db_path=str(database_path))
    ledger.commit_inference(
        b"demo-frame-001",
        "models/model_safe.pth",
        {"detections": [{"label": "vehicle", "confidence": 0.96}]},
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    intact_db = DATA_DIR / "ledger_intact.db"
    intact_key = DATA_DIR / "ledger_intact.key"
    tampered_db = DATA_DIR / "ledger_tampered.db"
    tampered_key = DATA_DIR / "ledger_tampered.key"

    build_ledger(intact_db, intact_key)
    build_ledger(tampered_db, tampered_key)
    with sqlite3.connect(tampered_db) as connection:
        connection.execute("UPDATE merkl_dag SET payload = ? WHERE block_id = 1", ('{"detections": [{"label": "tampered"}]}',))
        connection.commit()

    os.environ["VAJRA_PROVENANCE_KEY_PATH"] = str(intact_key)
    intact = TacticalProvenanceLedger(db_path=str(intact_db))
    os.environ["VAJRA_PROVENANCE_KEY_PATH"] = str(tampered_key)
    tampered = TacticalProvenanceLedger(db_path=str(tampered_db))
    print("ledger_intact.db:", intact.verify_ledger())
    print("ledger_tampered.db:", tampered.verify_ledger())


if __name__ == "__main__":
    main()
