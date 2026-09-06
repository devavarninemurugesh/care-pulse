"""
Unit tests for CARE PULSE end-to-end processing pipeline.
"""

import pandas as pd
import pytest
from analysis.pipeline import process_dataset

def test_pipeline_execution():
    df = pd.DataFrame({
        "patient_id": ["P001"] * 14 + ["P002"] * 14,
        "date": list(pd.date_range("2026-01-01", periods=14)) * 2,
        "mobility": [8.0] * 14 + ([9.0] * 7 + [3.0] * 7),
        "nutrition": [85.0] * 14 + ([90.0] * 7 + [40.0] * 7),
        "participation": [8.0] * 14 + ([8.0] * 7 + [3.0] * 7),
        "activity": [7.0] * 14 + ([8.0] * 7 + [2.0] * 7),
        "incident": [0] * 28,
        "notes": ["Normal"] * 28
    })
    
    result = process_dataset(df)
    assert len(result["patient_summaries"]) == 2
    
    p2 = next(p for p in result["patient_summaries"] if p["patient_id"] == "P002")
    assert p2["risk_category"] in ["Needs Review", "Urgent Review"]
    assert p2["decline_score"] >= 30.0
