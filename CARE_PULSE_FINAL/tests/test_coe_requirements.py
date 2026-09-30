"""
Comprehensive Pytest suite for CARE PULSE COE Requirements.
Tests baseline calculation, 14d vs 7d trend detection, freshness, uncertainty, 3 edge cases,
and early detection lead time / confusion matrix metrics.
"""

import pandas as pd
import pytest
from analysis.baseline import evaluate_single_metric_baseline
from analysis.trend_analysis import evaluate_patient_trend
from analysis.decline_score import calculate_functional_decline_score
from analysis.experiment import run_early_detection_experiment
from analysis.pipeline import process_dataset

def test_single_metric_baseline():
    df_flagged = pd.DataFrame({
        "patient_id": ["P001"],
        "date": ["2026-05-30"],
        "mobility": [4.0],  # Below 5.0
        "nutrition": [80.0]
    })
    b1 = evaluate_single_metric_baseline(df_flagged)
    assert b1["baseline_flagged"] is True
    assert b1["baseline_status"] == "Flagged"

    df_normal = pd.DataFrame({
        "patient_id": ["P002"],
        "date": ["2026-05-30"],
        "mobility": [8.0],
        "nutrition": [85.0]
    })
    b2 = evaluate_single_metric_baseline(df_normal)
    assert b2["baseline_flagged"] is False
    assert b2["baseline_status"] == "Normal"

def test_14d_vs_7d_trend_detection_gradual_decline():
    dates = pd.date_range("2026-05-01", periods=25)
    # Mobility drops from 9.0 to 3.0 over 25 days
    mob = [9.0 - (i * 0.25) for i in range(25)]
    df = pd.DataFrame({
        "patient_id": ["P001"] * 25,
        "date": dates,
        "mobility": mob,
        "nutrition": [85.0] * 25,
        "participation": [8.0 - (i * 0.2) for i in range(25)],
        "activity": [8.0] * 25,
        "incident": [0] * 25
    })

    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)

    assert t["trends"]["mobility"]["direction"] == "↓ Declining"
    assert s["score"] >= 40.0
    assert s["risk_category"] in ["Needs Review", "Urgent Review"]

def test_freshness_tracking():
    max_date = pd.Timestamp("2026-05-30")
    
    # Fresh (0 days old)
    df_fresh = pd.DataFrame({"patient_id": ["P001"], "date": [pd.Timestamp("2026-05-30")], "mobility": [8.0], "nutrition": [85.0], "participation": [8.0]})
    t_fresh = evaluate_patient_trend(df_fresh, max_date)
    assert t_fresh["freshness"] == "Fresh"

    # Stale (5 days old)
    df_stale = pd.DataFrame({"patient_id": ["P002"], "date": [pd.Timestamp("2026-05-25")], "mobility": [8.0], "nutrition": [85.0], "participation": [8.0]})
    t_stale = evaluate_patient_trend(df_stale, max_date)
    assert t_stale["freshness"] == "Stale"

    # Very Stale (10 days old)
    df_very_stale = pd.DataFrame({"patient_id": ["P003"], "date": [pd.Timestamp("2026-05-20")], "mobility": [8.0], "nutrition": [85.0], "participation": [8.0]})
    t_very_stale = evaluate_patient_trend(df_very_stale, max_date)
    assert t_very_stale["freshness"] == "Very Stale"

def test_case_1_normal_continuous_observations():
    """TEST 1 — Normal continuous observations. Expected: Trend analysis works normally."""
    dates = pd.date_range("2026-09-01", periods=14)
    df = pd.DataFrame({
        "patient_id": ["P001"] * 14,
        "date": dates,
        "mobility": [8.5] * 14,
        "nutrition": [88.0] * 14,
        "participation": [8.0] * 14,
        "activity": [7.5] * 14,
        "incident": [0] * 14
    })
    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)
    assert t["freshness"] == "Fresh"
    assert t["confidence_level"] == "Good Confidence"
    assert s["score"] < 30.0
    assert s["risk_category"] == "Doing Well"

def test_case_2_missing_observation_values():
    """TEST 2 — Missing observation values. Expected: No crash, system reports missing metric, confidence reduced."""
    df = pd.DataFrame({
        "patient_id": ["P001"] * 7,
        "date": pd.date_range("2026-09-01", periods=7),
        "mobility": [None] * 7,  # Mobility missing
        "nutrition": [85.0] * 7,
        "participation": [8.0] * 7,
        "activity": [7.0] * 7,
        "incident": [0] * 7
    })
    t = evaluate_patient_trend(df)
    assert t["overall_status"] == "Missing Information"
    assert t["confidence_level"] == "Insufficient Data"
    assert "mobility" in t["confidence_reason"].lower()

def test_case_3_sudden_gap_in_daily_observations():
    """TEST 3 — Sudden gap in daily observations (2026-09-01..03, MISSING 04..06, 2026-09-07)."""
    df = pd.DataFrame({
        "patient_id": ["P001"] * 4,
        "date": [pd.Timestamp("2026-09-01"), pd.Timestamp("2026-09-02"), pd.Timestamp("2026-09-03"), pd.Timestamp("2026-09-07")],
        "mobility": [8.0, 8.0, 8.0, 7.5],
        "nutrition": [85.0, 85.0, 85.0, 80.0],
        "participation": [8.0, 8.0, 8.0, 7.5],
        "activity": [7.0, 7.0, 7.0, 7.0],
        "incident": [0, 0, 0, 0]
    })
    t = evaluate_patient_trend(df)
    assert t["has_gap"] is True
    assert t["gap_warning"] is not None
    assert "gap" in t["confidence_reason"].lower()

def test_case_4_completely_stale_patient_data():
    """TEST 4 — Completely stale patient data. Expected: Stale-data indicator, confidence reduced."""
    max_date = pd.Timestamp("2026-09-30")
    df = pd.DataFrame({
        "patient_id": ["P001"] * 5,
        "date": pd.date_range("2026-09-01", periods=5),  # 25 days ago
        "mobility": [8.0] * 5,
        "nutrition": [85.0] * 5,
        "participation": [8.0] * 5,
        "activity": [7.0] * 5,
        "incident": [0] * 5
    })
    t = evaluate_patient_trend(df, dataset_max_date=max_date)
    s = calculate_functional_decline_score(t)
    assert t["freshness"] in ["Stale", "Very Stale"]
    assert s["risk_category"] in ["Data May Be Old", "Needs Review", "Urgent Review"]

def test_case_5_insufficient_history():
    """TEST 5 — Insufficient history (< 4 observations). Expected: 'Insufficient data for reliable baseline comparison.'"""
    df = pd.DataFrame({
        "patient_id": ["P001"] * 2,
        "date": pd.date_range("2026-09-01", periods=2),
        "mobility": [8.0, 4.0],
        "nutrition": [85.0, 50.0],
        "participation": [8.0, 4.0],
        "activity": [7.0, 3.0],
        "incident": [0, 0]
    })
    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)
    assert t["has_insufficient_history"] is True
    assert s["score"] == 0.0
    assert "Insufficient data for reliable baseline comparison." in s["contributing_factors"]

def test_edge_case_missing_data():
    df = pd.DataFrame({
        "patient_id": ["P001"],
        "date": ["2026-05-30"],
        "mobility": [None],  # Missing core domain
        "nutrition": [80.0],
        "participation": [8.0],
        "activity": [7.0],
        "incident": [0]
    })
    t = evaluate_patient_trend(df)
    assert t["overall_status"] == "Missing Information"
    assert t["confidence_level"] == "Insufficient Data"

def test_edge_case_stale_data():
    max_date = pd.Timestamp("2026-05-30")
    df = pd.DataFrame({
        "patient_id": ["P001"],
        "date": [pd.Timestamp("2026-05-15")],  # 15 days ago
        "mobility": [8.0],
        "nutrition": [85.0],
        "participation": [8.0]
    })
    t = evaluate_patient_trend(df, max_date)
    assert t["freshness"] == "Very Stale"
    assert t["overall_status"] == "Data May Be Old"

def test_edge_case_sudden_noisy_change():
    dates = pd.date_range("2026-05-01", periods=20)
    mob = [8.5] * 19 + [4.0]  # Single-day drop on day 20
    df = pd.DataFrame({
        "patient_id": ["P001"] * 20,
        "date": dates,
        "mobility": mob,
        "nutrition": [88.0] * 20,
        "participation": [8.5] * 20,
        "activity": [8.0] * 20,
        "incident": [0] * 20
    })
    t = evaluate_patient_trend(df)
    s = calculate_functional_decline_score(t)
    assert s["score"] < 60.0

def test_early_detection_experiment_metrics():
    dates = pd.date_range("2026-05-01", periods=30)
    p1 = pd.DataFrame({
        "patient_id": ["P001"] * 30,
        "date": dates,
        "mobility": [9.0 - (i * 0.2) for i in range(30)],
        "nutrition": [85.0] * 30,
        "participation": [8.0 - (i * 0.15) for i in range(30)],
        "activity": [8.0] * 30,
        "incident": [0] * 29 + [1],
        "profile": ["gradual_decline"] * 30
    })
    p2 = pd.DataFrame({
        "patient_id": ["P002"] * 30,
        "date": dates,
        "mobility": [8.5] * 30,
        "nutrition": [88.0] * 30,
        "participation": [8.5] * 30,
        "activity": [8.0] * 30,
        "incident": [0] * 30,
        "profile": ["stable"] * 30
    })
    df_exp = pd.concat([p1, p2], ignore_index=True)

    exp_res = run_early_detection_experiment(df_exp)
    assert exp_res["total_patients"] == 2
    assert exp_res["care_pulse"]["tp"] >= 1
    assert exp_res["care_pulse"]["early_detection_rate"] > 0.0
    assert exp_res["care_pulse"]["avg_lead_time"] >= 0.0
