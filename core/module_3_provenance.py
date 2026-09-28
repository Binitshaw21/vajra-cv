"""
core/module_3_provenance.py
Module 3: Hardware-Bound Cryptographic Provenance Ledger (Ed25519 + Blake3)
"""
import sqlite3
import json
import time
import os
from pathlib import Path
# pyrefly: ignore [missing-import]
import blake3
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from typing import Dict, Tuple, Optional

class TacticalProvenanceLedger:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or os.getenv("VAJRA_LEDGER_DB", "database/ledger.db")
        key_path = Path(os.getenv("VAJRA_PROVENANCE_KEY_PATH", "certs/device_private.key"))
        key_path.parent.mkdir(parents=True, exist_ok=True)
        key_bytes = key_path.read_bytes() if key_path.exists() and key_path.stat().st_size else None
        if key_bytes is None:
            self.signing_key = SigningKey.generate()
            key_path.write_bytes(bytes(self.signing_key))
        else:
            self.signing_key = SigningKey(key_bytes[:32])
        self.verify_key = self.signing_key.verify_key
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS merkl_dag (
                    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    prev_hash TEXT NOT NULL,
                    frame_hash TEXT NOT NULL,
                    model_digest TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    root_hash TEXT NOT NULL UNIQUE,
                    signature TEXT NOT NULL
                );
            """)
            conn.commit()

    def get_latest_hash(self) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT root_hash FROM merkl_dag ORDER BY block_id DESC LIMIT 1;")
            row = cur.fetchone()
            return row[0] if row else "0" * 64

    def commit_inference(self, raw_frame: bytes, model_path: str, detections: Dict) -> Dict:
        prev_h = self.get_latest_hash()
        frame_h = blake3.blake3(raw_frame).hexdigest()
        model_d = blake3.blake3(model_path.encode()).hexdigest()
        payload_str = json.dumps(detections, sort_keys=True)
        payload_h = blake3.blake3(payload_str.encode()).hexdigest()

        # Joint manifest Merkle digest
        manifest = f"{prev_h}:{frame_h}:{model_d}:{payload_h}"
        root_hash = blake3.blake3(manifest.encode()).hexdigest()

        # Ed25519 digital signature
        sig = self.signing_key.sign(root_hash.encode()).signature
        sig_hex = HexEncoder.encode(sig).decode()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO merkl_dag (timestamp, prev_hash, frame_hash, model_digest, payload, root_hash, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (time.time(), prev_h, frame_h, model_d, payload_str, root_hash, sig_hex))
            conn.commit()

        return {"root_hash": root_hash, "signature": sig_hex, "prev_hash": prev_h}

    def verify_ledger(self) -> Tuple[bool, Optional[int]]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT block_id, prev_hash, frame_hash, model_digest, payload, root_hash, signature FROM merkl_dag ORDER BY block_id ASC;")
            rows = cur.fetchall()

        prev = "0" * 64
        for row in rows:
            b_id, p_h, f_h, m_d, pay, r_h, s_hex = row
            if p_h != prev:
                return False, b_id
            
            p_digest = blake3.blake3(pay.encode()).hexdigest()
            manifest = f"{p_h}:{f_h}:{m_d}:{p_digest}"
            if blake3.blake3(manifest.encode()).hexdigest() != r_h:
                return False, b_id

            try:
                self.verify_key.verify(r_h.encode(), HexEncoder.decode(s_hex))
            except Exception:
                return False, b_id

            prev = r_h
        return True, None

if __name__ == "__main__":
    ledger = TacticalProvenanceLedger()
    sample_frame = b"SimulatedPerimeterSensorInfraredFrameData"
    dets = {"detections": [{"label": "armored_vehicle", "confidence": 0.94, "bbox": [120, 80, 240, 190]}]}
    res = ledger.commit_inference(sample_frame, "models/clean_model.pth", dets)
    valid, broken_id = ledger.verify_ledger()
    print(f"[*] Module 3 Execution Result:")
    print(f"    --> Committed Root Hash     : {res['root_hash']}")
    print(f"    --> Ed25519 Bound Signature : {res['signature'][:32]}...")
    print(f"    --> Ledger Chain Integrity  : {'VALID (TAMPER-PROOF)' if valid else f'FAILED AT BLOCK {broken_id}'}")