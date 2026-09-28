"""
tests/generate_test_artifacts.py
Generates reproducible synthetic datasets and backdoored vision models
for offline evaluation of Project VAJRA-CV.
"""
import torch
import torch.nn as nn
import numpy as np
import os

os.makedirs("models", exist_ok=True)
os.makedirs("data", exist_ok=True)

class TacticalVisionNet(nn.Module):
    """3-layer CNN representative of tactical edge object classifiers."""
    def __init__(self, num_classes=4):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Flatten()
        )
        self.classifier = nn.Sequential(
            nn.Linear(32 * 8 * 8, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )

    def extract_features(self, x):
        return self.features(x)

    def forward(self, x):
        feat = self.features(x)
        return self.classifier(feat)

def create_synthetic_datasets():
    print("[*] Synthesizing tactical image feature representations...")
    np.random.seed(42)
    # Class 0: 100 clean feature vectors (64-dimensional)
    clean_features = np.random.normal(loc=0.0, scale=1.0, size=(100, 64))
    # Inject 8 clean-label poisoned samples with an adversarial variance spike
    poison_features = np.random.normal(loc=3.8, scale=0.15, size=(8, 64))
    
    dataset_features = np.vstack([clean_features, poison_features])
    np.save("data/sample_features_class0.npy", dataset_features)
    print(f"    --> Saved 108 feature vectors to data/sample_features_class0.npy (8 poisoned)")

def create_models():
    print("[*] Creating baseline and Trojaned tactical checkpoints...")
    # Model 1: Clean Baseline Checkpoint
    clean_model = TacticalVisionNet(num_classes=4)
    torch.save(clean_model.state_dict(), "models/clean_model.pth")
    
    # Model 2: Backdoored Checkpoint (Target Class: 2)
    # Simulate a backdoored model by biasing class 2 weights to trigger on specific latent patterns
    trojan_model = TacticalVisionNet(num_classes=4)
    with torch.no_grad():
        # Artificially lower L1 threshold for class 2 by biasing final layer weights
        trojan_model.classifier[2].weight[2] += 2.5
    torch.save(trojan_model.state_dict(), "models/trojan_model.pth")
    print("    --> Saved clean model to models/clean_model.pth")
    print("    --> Saved Trojaned model (Target: Class 2) to models/trojan_model.pth")

if __name__ == "__main__":
    create_synthetic_datasets()
    create_models()
    print("[✔] Artifact generation complete.")