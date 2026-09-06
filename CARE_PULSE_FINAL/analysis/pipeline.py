"""
Unified Data & Analysis Pipeline for CARE PULSE (COE Requirements).
Orchestrates CSV cleaning -> 14d vs 7d trend detection -> baseline calculation -> decline scoring -> experiment evaluation.
"""

from typing import Dict, Any, List
import pandas as pd
from analysis.data_cleaning import clean_observation_dataframe
from analysis.trend_analysis import analyze_all_patient_trends
from analysis.decline_score import calculate_functional_decline_score
from analysis.baseline import evaluate_single_metric_baseline
from analysis.metrics import compute_dataset_metrics
from analysis.experiment import run_early_detection_experiment

def process_dataset(raw_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Executes end-to-end COE processing pipeline on raw DataFrame.
    """
    if raw_df is None or raw_df.empty:
        return {
            "df": pd.DataFrame(),
            "patient_summaries": [],
            "metrics": compute_dataset_metrics(pd.DataFrame(), []),
            "experiment": {}
        }

    # 1. Clean & Standardize
    cleaned_df = clean_observation_dataframe(raw_df)
    if cleaned_df.empty:
        return {
            "df": pd.DataFrame(),
            "patient_summaries": [],
            "metrics": compute_dataset_metrics(pd.DataFrame(), []),
            "experiment": {}
        }

    # 2. Compute per-patient 14d vs 7d trends
    trends_list = analyze_all_patient_trends(cleaned_df)

    # 3. Calculate Functional Decline Scores
    scores_list = [calculate_functional_decline_score(t) for t in trends_list]

    # 4. Compute Single-Metric Baseline for comparison
    patient_summaries = []
    for t, s in zip(trends_list, scores_list):
        pid = t["patient_id"]
        pgroup = cleaned_df[cleaned_df["patient_id"] == pid]
        b_info = evaluate_single_metric_baseline(pgroup)

        patient_summary = {
            "patient_id": pid,
            "total_records": t["total_records"],
            "latest_date": t["latest_date"],
            "days_since_last": t["days_since_last"],
            "freshness": t["freshness"],
            "confidence_level": t["confidence_level"],
            "confidence_reason": t["confidence_reason"],
            "recent_incidents": t["recent_incidents"],
            "total_incidents": t["total_incidents"],
            "trends": t["trends"],
            "decline_score": s["score"],
            "risk_category": s["risk_category"],
            "overall_trend": s["overall_trend"],
            "contributing_factors": s["contributing_factors"],
            "baseline_status": b_info["baseline_status"],
            "baseline_trigger_reason": b_info["trigger_reason"]
        }
        patient_summaries.append(patient_summary)

    # Sort patient summaries by decline_score descending
    patient_summaries.sort(key=lambda x: x["decline_score"], reverse=True)

    # 5. Top-level dataset metrics
    metrics = compute_dataset_metrics(cleaned_df, patient_summaries)

    # 6. Early Detection Experiment & Evaluation Metrics
    exp_results = run_early_detection_experiment(cleaned_df)

    return {
        "df": cleaned_df,
        "patient_summaries": patient_summaries,
        "metrics": metrics,
        "experiment": exp_results
    }
