"""
core/module_2_trojan.py
Module 2: Neural Cleanse L1 Optimization & MAD Backdoor Scanner
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Tuple

class NeuralCleanseTrojanScanner:
    def __init__(self, model: nn.Module, img_shape: Tuple[int, int, int] = (3, 32, 32), steps: int = 40, lr: float = 0.05):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device).eval()
        self.img_shape = img_shape
        self.steps = steps
        self.lr = lr

    def reverse_engineer_trigger(self, target_class: int, samples: torch.Tensor) -> Tuple[float, torch.Tensor, torch.Tensor]:
        c, h, w = self.img_shape
        samples = samples.to(self.device)

        # Initialize continuous mask (m) and pattern (Delta)
        mask_raw = torch.zeros((1, 1, h, w), device=self.device, requires_grad=True)
        pattern = torch.zeros((1, c, h, w), device=self.device, requires_grad=True)

        optimizer = optim.Adam([mask_raw, pattern], lr=self.lr)
        criterion = nn.CrossEntropyLoss()
        target_labels = torch.full((samples.size(0),), target_class, dtype=torch.long, device=self.device)

        for _ in range(self.steps):
            optimizer.zero_grad()
            mask = torch.sigmoid(mask_raw)  # Constrain mask bounds to [0, 1]
            
            # Injection equation: x' = x * (1 - m) + Delta * m
            adversarial_inputs = samples * (1.0 - mask) + pattern * mask
            outputs = self.model(adversarial_inputs)

            # Optimization objective: Misclassification Loss + L1 Penalty on Mask
            ce_loss = criterion(outputs, target_labels)
            l1_loss = torch.mean(torch.abs(mask))
            total_loss = ce_loss + 0.8 * l1_loss

            total_loss.backward()
            optimizer.step()

        with torch.no_grad():
            final_mask = torch.sigmoid(mask_raw).squeeze()
            l1_norm = float(torch.sum(torch.abs(final_mask)).item())

        return l1_norm, final_mask.cpu(), pattern.detach().squeeze().cpu()

    def audit_model(self, num_classes: int, test_tensors: torch.Tensor) -> Dict:
        l1_norms = []
        for c in range(num_classes):
            norm, _, _ = self.reverse_engineer_trigger(c, test_tensors)
            l1_norms.append(norm)

        # Compute Median Absolute Deviation (MAD)
        l1_arr = np.array(l1_norms)
        median_l1 = np.median(l1_arr)
        mad = 1.4826 * np.median(np.abs(l1_arr - median_l1)) + 1e-6
        anomaly_indices = np.abs(l1_arr - median_l1) / mad

        # Flag classes requiring abnormally small L1 perturbations
        suspected_classes = [
            int(i) for i, score in enumerate(anomaly_indices) 
            if score > 2.0 and l1_arr[i] < median_l1
        ]

        return {
            "l1_norms": [round(n, 4) for n in l1_norms],
            "anomaly_indices": [round(idx, 4) for idx in anomaly_indices.tolist()],
            "median_l1": float(round(median_l1, 4)),
            "suspected_trojan_classes": suspected_classes,
            "verdict": "FLAGGED_TROJAN" if suspected_classes else "CERTIFIED_CLEAN"
        }

if __name__ == "__main__":
    print("[*] Initializing Module 2: Neural Cleanse L1 Optimizer...")
    # Create a mock vulnerable model with 4 output classes
    mock_model = nn.Sequential(
        nn.Flatten(),
        nn.Linear(3 * 32 * 32, 64),
        nn.ReLU(),
        nn.Linear(64, 4)
    )
    
    # Simulate a backdoor vulnerability in Class 2 (artificially lowers required perturbation)
    with torch.no_grad():
        mock_model[3].weight[2] += 2.5 

    scanner = NeuralCleanseTrojanScanner(mock_model, img_shape=(3, 32, 32), steps=25)
    dummy_inputs = torch.rand((16, 3, 32, 32))
    
    print("[*] Reverse-engineering triggers across all target classes...")
    report = scanner.audit_model(num_classes=4, test_tensors=dummy_inputs)
    
    print(f"    --> L1 Norms (Trigger Sizes) : {report['l1_norms']}")
    print(f"    --> MAD Anomaly Indices      : {report['anomaly_indices']}")
    print(f"    --> Vulnerable Classes       : {report['suspected_trojan_classes']}")
    print(f"    --> Tactical Verdict         : {report['verdict']}")