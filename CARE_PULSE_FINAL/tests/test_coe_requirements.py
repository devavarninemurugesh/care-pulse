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
    
    # Fresh (2 days old)
    df_fresh = pd.DataFrame({"patient_id": ["P001"], "date": [pd.Timestamp("2026-05-28")], "mobility": [8.0], "nutrition": [85.0], "participation": [8.0]})
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
    # 14-day baseline vs 7-day average smooths out 1-day noise compared to single threshold
    assert s["score"] < 60.0

def test_early_detection_experiment_metrics():
    # Build mini synthetic dataset with 1 gradual decline and 1 stable patient
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
