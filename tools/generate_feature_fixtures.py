"""Create local feature fixtures for the VAJRA-CV SVD upload demo."""
from pathlib import Path

import numpy as np


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe = np.zeros((128, 64), dtype=np.float32)
    np.save(DATA_DIR / "features_safe.npy", safe)

    rng = np.random.default_rng(20260928)
    clean = rng.normal(0.0, 1.0, size=(96, 64))
    poisoned = rng.normal(8.0, 0.08, size=(16, 64))
    np.save(DATA_DIR / "features_flagged.npy", np.vstack([clean, poisoned]).astype(np.float32))

    (DATA_DIR / "features_invalid.npy").write_bytes(b"this is not a NumPy array")
    print("Created data/features_safe.npy")
    print("Created data/features_flagged.npy")
    print("Created data/features_invalid.npy")


if __name__ == "__main__":
    main()
