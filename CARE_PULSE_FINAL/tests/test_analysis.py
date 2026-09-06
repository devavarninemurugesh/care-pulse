"""
Unit tests for CARE PULSE trend analysis and functional decline scoring.
"""

import pandas as pd
import pytest
from analysis.data_cleaning import clean_observation_dataframe
from analysis.trend_analysis import evaluate_patient_trend
from analysis.decline_score import calculate_functional_decline_score

def test_data_cleaning():
    raw_df = pd.DataFrame({
        "Patient_ID": [" P001 ", "P001"],
        "Date": ["2026-01-01", "2026-01-02"],
        "Mobility": [12.0, 7.5],  # 12.0 should clip to 10.0
        "Nutrition": [85.0, None],
        "Participation": [8.0, 8.0],
        "Activity": [7.0, 7.0],
        "Incident": [0, 0]
    })
    cleaned = clean_observation_dataframe(raw_df)
    assert len(cleaned) == 2
    assert cleaned["patient_id"].iloc[0] == "P001"
    assert cleaned["mobility"].max() <= 10.0

def test_stable_patient_trend():
    df = pd.DataFrame({
        "patient_id": ["P001"] * 14,
        "date": pd.date_range("2026-01-01", periods=14),
        "mobility": [8.0] * 14,
        "nutrition": [85.0] * 14,
        "participation": [8.0] * 14,
        "activity": [7.0] * 14,
        "incident": [0] * 14
    })
    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)
    assert s["score"] < 30.0
    assert s["risk_category"] == "Doing Well"

def test_declining_patient_trend():
    df = pd.DataFrame({
        "patient_id": ["P002"] * 14,
        "date": pd.date_range("2026-01-01", periods=14),
        "mobility": [9.0] * 7 + [4.0] * 7,  # Major drop
        "nutrition": [90.0] * 7 + [50.0] * 7,
        "participation": [8.0] * 7 + [4.0] * 7,
        "activity": [8.0] * 7 + [3.0] * 7,
        "incident": [0] * 13 + [1]
    })
    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)
    assert s["score"] >= 30.0
    assert s["risk_category"] in ["Needs Review", "Urgent Review"]
