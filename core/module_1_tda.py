import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.sparse.csgraph import minimum_spanning_tree

class TopologicalPoisonDetector:
    """
    Uses 0-dimensional Persistent Homology (Betti-0) proxy via Minimum Spanning Trees 
    to detect Covariance-Matching Poison attacks that evade standard SVD.
    """
    def __init__(self, sensitivity: float = 2.0):
        self.sensitivity = sensitivity

    def evaluate_topology(self, features: np.ndarray) -> dict:
        N = features.shape[0]
        if N < 5:
            return {"status": "INSUFFICIENT_DATA"}

        # 1. Compute pairwise Euclidean distance matrix (Vietoris-Rips filtration proxy)
        dist_matrix = squareform(pdist(features, metric='euclidean'))
        
        # 2. Compute Minimum Spanning Tree (MST) to track connected components (Betti-0)
        mst = minimum_spanning_tree(dist_matrix).toarray()
        mst_edges = mst[mst > 0]
        
        # 3. Analyze edge length distribution (Persistent Homology lifespans)
        median_edge = np.median(mst_edges)
        mad_edge = np.median(np.abs(mst_edges - median_edge))
        
        # 4. Topological Anomaly Threshold
        # Disconnected adversarial clusters will force abnormally long MST edges
        threshold = median_edge + (self.sensitivity * mad_edge)
        
        # 5. Flag samples connected by anomalous topological edges
        anomalous_edges = np.argwhere(mst > threshold)
        poisoned_indices = set()
        for edge in anomalous_edges:
            poisoned_indices.add(int(edge[0]))
            poisoned_indices.add(int(edge[1]))

        return {
            "betti_0_anomalies": len(poisoned_indices),
            "flagged_indices": list(poisoned_indices),
            "topology_status": "COMPROMISED_GEOMETRY" if poisoned_indices else "TOPOLOGICALLY_SOUND"
        }