"""
core/module_1_poison.py
Module 1: Spectral SVD Data Poisoning Screener (Tran et al., NeurIPS 2018)
"""
import numpy as np
from typing import Dict

class SpectralPoisonDetector:
    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier

    def evaluate(self, features: np.ndarray) -> Dict:
        """
        Calculates singular value decomposition of centered activations
        to flag variance anomalies along the top right singular vector.
        """
        N, D = features.shape
        if N < 5:
            return {"status": "INSUFFICIENT_DATA", "flagged": []}

        # 1. Mean-center intermediate activations
        mean_vector = np.mean(features, axis=0)
        centered_features = features - mean_vector

        # 2. Singular Value Decomposition: centered_features = U * S * V^T
        _, _, vh = np.linalg.svd(centered_features, full_matrices=False)
        top_singular_vector = vh[0]  # Top singular vector

        # 3. Projection score: τ_i = ((F_i - μ) · v_1)^2
        variance_scores = np.square(np.dot(centered_features, top_singular_vector))

        # 4. Dispersion threshold via Median and Interquartile Range (IQR)
        median_score = np.median(variance_scores)
        iqr = np.percentile(variance_scores, 75) - np.percentile(variance_scores, 25)
        threshold = median_score + (self.multiplier * iqr)

        quarantine_indices = np.where(variance_scores > threshold)[0].tolist()

        return {
            "total_samples": N,
            "quarantine_count": len(quarantine_indices),
            "flagged_indices": quarantine_indices,
            "threshold": float(threshold),
            "verdict": "COMPROMISED" if quarantine_indices else "CLEAN",
            "scores": variance_scores.tolist()
        }

if __name__ == "__main__":
    # Test on generated data
    feats = np.load("data/sample_features_class0.npy")
    detector = SpectralPoisonDetector(multiplier=1.5)
    report = detector.evaluate(feats)
    print(f"[*] Module 1 Execution Result:")
    print(f"    --> Total Samples Evaluated : {report['total_samples']}")
    print(f"    --> Flagged Outliers        : {report['quarantine_count']}")
    print(f"    --> Flagged Sample Indices  : {report['flagged_indices']}")
    print(f"    --> Verdict                 : {report['verdict']}")