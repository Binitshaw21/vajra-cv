"""
core/module_4_ood.py
Module 4: Energy-Based Out-of-Distribution (OOD) Shift Detector
"""
import torch
import numpy as np
from typing import Dict, List

class EnergyOODDetector:
    def __init__(self, temperature: float = 1.0, ood_threshold: float = -6.0):
        self.T = temperature
        self.ood_threshold = ood_threshold

    def calculate_free_energy(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Computes Helmholtz free energy: E(x) = -T * LogSumExp(logits / T)
        Higher free energy indicates the input is out-of-distribution.
        """
        return -self.T * torch.logsumexp(logits / self.T, dim=-1)

    def evaluate_drift(self, logits: torch.Tensor) -> Dict:
        energies = self.calculate_free_energy(logits).detach().cpu().numpy()
        ood_flags = energies > self.ood_threshold
        
        mean_energy = float(np.mean(energies))
        
        return {
            "energies": [round(float(e), 4) for e in energies],
            "mean_energy": round(mean_energy, 4),
            "ood_count": int(np.sum(ood_flags)),
            "verdict": "COVARIATE_DRIFT_DETECTED" if bool(np.any(ood_flags)) else "NOMINAL_IN_DIST"
        }

if __name__ == "__main__":
    print("[*] Initializing Module 4: Energy OOD Shift Detector...")
    detector = EnergyOODDetector(temperature=1.0, ood_threshold=-5.5)
    
    # Simulate high-confidence logits (Clear Weather / In-Distribution)
    nominal_logits = torch.tensor([[8.5, 1.2, 0.4, 0.1], [7.9, 0.8, 1.1, 0.3]])
    
    # Simulate low-confidence, flat logits (Heavy Fog / Out-of-Distribution)
    drift_logits = torch.tensor([[0.6, 0.5, 0.4, 0.5], [0.3, 0.4, 0.2, 0.5]])
    
    print("\n[+] Testing Nominal Sensor Feed:")
    res_nom = detector.evaluate_drift(nominal_logits)
    print(f"    --> Mean Energy : {res_nom['mean_energy']}")
    print(f"    --> Verdict     : {res_nom['verdict']}")
    
    print("\n[+] Testing Degraded Sensor Feed (Weather/Drift):")
    res_drift = detector.evaluate_drift(drift_logits)
    print(f"    --> Mean Energy : {res_drift['mean_energy']}")
    print(f"    --> Verdict     : {res_drift['verdict']}")