"""
Scikit-Learn Machine Learning predictive module for CARE PULSE.
Provides early decline risk predictions, probability confidence, and feature importance rankings.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

class EarlyDeclinePredictor:
    """
    Random Forest Classifier trained on engineered patient trend features.
    """
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
        self.is_fitted = False
        self.feature_names = [
            "mob_pct_change",
            "act_pct_change",
            "nut_pct_change",
            "part_pct_change",
            "recent_incidents",
            "days_since_last"
        ]

    def _extract_features(self, patient_trends: List[Dict[str, Any]]) -> pd.DataFrame:
        rows = []
        for p in patient_trends:
            trends = p.get("trends", {})
            row = {
                "patient_id": p.get("patient_id"),
                "mob_pct_change": trends.get("mobility", {}).get("pct_change", 0.0),
                "act_pct_change": trends.get("activity", {}).get("pct_change", 0.0),
                "nut_pct_change": trends.get("nutrition", {}).get("pct_change", 0.0),
                "part_pct_change": trends.get("participation", {}).get("pct_change", 0.0),
                "recent_incidents": float(p.get("recent_incidents", 0)),
                "days_since_last": float(p.get("days_since_last", 0))
            }
            rows.append(row)
        return pd.DataFrame(rows)

    def fit_and_predict(self, patient_trends: List[Dict[str, Any]], decline_scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fits the ML model on the current dataset trends and generates predictive signals.
        """
        if not patient_trends or len(patient_trends) < 3:
            # Fallback for very small datasets
            results = []
            for p, s in zip(patient_trends, decline_scores):
                results.append({
                    "patient_id": p["patient_id"],
                    "ml_predicted_risk": s["risk_category"],
                    "confidence_score": 0.85,
                    "top_contributor": s["contributing_factors"][0] if s["contributing_factors"] else "Stable"
                })
            return results

        df_feat = self._extract_features(patient_trends)
        X = df_feat[self.feature_names]

        # Construct silver standard target based on decline score rule (0 = Doing Well, 1 = Review Needed)
        y = np.array([1 if s["score"] >= 30.0 else 0 for s in decline_scores])

        # Handle edge case where target has only 1 unique class
        if len(np.unique(y)) < 2:
            y[0] = 1 - y[0]

        self.model.fit(X, y)
        self.is_fitted = True

        probs = self.model.predict_proba(X)
        probs_decline = probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]

        # Extract Feature Importances
        importances = self.model.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        top_feature_idx = sorted_indices[0]
        feature_label_map = {
            "mob_pct_change": "Mobility Decline",
            "act_pct_change": "Daily Activity Drop",
            "nut_pct_change": "Nutritional Intake Drop",
            "part_pct_change": "Social Participation Drop",
            "recent_incidents": "Safety Incident Frequency",
            "days_since_last": "Observation Data Staleness"
        }
        top_feature_name = feature_label_map.get(self.feature_names[top_feature_idx], "Functional Trajectory")

        predictions = []
        for i, p in enumerate(patient_trends):
            prob = float(probs_decline[i])
            conf = float(round(max(prob, 1.0 - prob), 2))
            
            if prob >= 0.6:
                predicted_risk = "Urgent Review"
            elif prob >= 0.35:
                predicted_risk = "Needs Review"
            else:
                predicted_risk = "Doing Well"

            predictions.append({
                "patient_id": p["patient_id"],
                "ml_predicted_risk": predicted_risk,
                "decline_probability": float(round(prob, 2)),
                "confidence_score": conf,
                "top_contributor": top_feature_name
            })

        return predictions
