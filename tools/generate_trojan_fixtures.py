"""Create safe PyTorch model fixtures for the VAJRA-CV Trojan Hunter."""
from pathlib import Path

import torch


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"


def save_fixture(path: Path, model: torch.nn.Module) -> None:
    torch.save({"architecture": "vajra_demo_classifier", "state_dict": model.state_dict()}, path)


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(20260928)
    clean = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 32 * 32, 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 4),
    )
    save_fixture(MODEL_DIR / "model_safe.pth", clean)

    flagged = torch.nn.Sequential(
        torch.nn.Flatten(),
        torch.nn.Linear(3 * 32 * 32, 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 4),
    )
    flagged.load_state_dict(clean.state_dict())
    with torch.no_grad():
        flagged[3].weight[2].mul_(25.0)
        flagged[3].bias[2].add_(12.0)
    save_fixture(MODEL_DIR / "model_flagged_trojan.pth", flagged)
    print("Created models/model_safe.pth")
    print("Created models/model_flagged_trojan.pth")


if __name__ == "__main__":
    main()