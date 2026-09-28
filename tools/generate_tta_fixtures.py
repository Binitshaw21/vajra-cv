"""Create nominal and drifted feature batches for the VAJRA-CV self-healing demo."""
from pathlib import Path

import numpy as np


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260928)
    nominal = rng.normal(0.0, 0.35, size=(16, 64)).astype(np.float32)
    drifted = rng.normal(3.5, 0.5, size=(16, 64)).astype(np.float32)
    np.save(DATA_DIR / "tta_nominal.npy", nominal)
    np.save(DATA_DIR / "tta_drifted.npy", drifted)
    print("Created data/tta_nominal.npy shape=(16, 64)")
    print("Created data/tta_drifted.npy shape=(16, 64)")


if __name__ == "__main__":
    main()
