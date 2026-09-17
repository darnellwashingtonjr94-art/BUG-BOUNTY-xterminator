import numpy as np
from sklearn.ensemble import IsolationForest
from feature_extraction import HeaderFeatureExtractor

class AnomalyScorer:
    def __init__(self):
        # Initialize an unsupervised anomaly detector
        # contamination represents the expected proportion of outliers (e.g., 5%)
        self.model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        
        # Generate dummy baseline data to "fit" the model for the scaffolding
        # In production, load this from a persisted .pkl or .onnx model file
        self._fit_baseline_model()

    def _fit_baseline_model(self):
        """Fits the model with standard, boring HTTP traffic profiles."""
        # Represents standard traffic: ~12 headers, low risk, varying sizes, few custom headers
        baseline_data = np.array([
            [12, 0.2, 5.5, 1],
            [14, 0.0, 6.1, 0],
            [10, 0.4, 4.0, 1],
            [15, 0.2, 7.2, 2],
            [11, 0.2, 5.0, 0]
        ] * 100) # Duplicate to create a stable baseline cluster
        
        self.model.fit(baseline_data)

    def calculate_score(self, headers: dict) -> float:
        """
        Returns a normalized anomaly score between 0.0 (normal) and 1.0 (highly anomalous).
        """
        features = HeaderFeatureExtractor.extract_features(headers)
        
        # decision_function returns a negative score for anomalies, positive for normal
        raw_score = self.model.decision_function(features)[0]
        
        # Normalize the score to a 0.0 - 1.0 range for the Next.js dashboard
        # Assuming raw scores generally fall between -0.5 and 0.5
        normalized = 0.5 - (raw_score * 2)
        return max(0.0, min(1.0, float(normalized)))
