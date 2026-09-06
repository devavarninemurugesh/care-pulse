"""
Early Detection Experiment & Evaluation Engine for CARE PULSE COE Requirements.
Evaluates synthetic patient trajectories with simulated adverse event dates, computing actual
Early Detection Rate, Lead Time (days), and Confusion Matrix (TP, FP, TN, FN) directly from dataset.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from analysis.baseline import evaluate_single_metric_baseline
from analysis.trend_analysis import evaluate_patient_trend
from analysis.decline_score import calculate_functional_decline_score

def run_early_detection_experiment(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Runs early detection experiment comparing static baseline vs CARE PULSE trend detection.
    """
    if df.empty:
        return {}

    patient_ids = df["patient_id"].unique()
    total_patients = len(patient_ids)

    tp_cp, fp_cp, tn_cp, fn_cp = 0, 0, 0, 0
    tp_base, fp_base, tn_base, fn_base = 0, 0, 0, 0

    lead_times_cp = []
    lead_times_base = []

    fp_cases = []
    fn_cases = []

    for pid in patient_ids:
        patient_obs = df[df["patient_id"] == pid].sort_values("date").reset_index(drop=True)
        
        # Check if profile metadata or adverse event exists
        profile = patient_obs["profile"].iloc[0] if "profile" in patient_obs.columns else "unknown"
        has_adverse_event = (patient_obs["incident"] == 1).any() or profile == "gradual_decline"

        # Find actual adverse event date
        adverse_rows = patient_obs[patient_obs["incident"] == 1]
        if not adverse_rows.empty:
            adverse_date = pd.to_datetime(adverse_rows["date"].iloc[0])
        elif profile == "gradual_decline":
            adverse_date = pd.to_datetime(patient_obs["date"].iloc[-1])
        else:
            adverse_date = None

        # Evaluate trajectory chronologically to find first detection date
        cp_first_flag_date = None
        base_first_flag_date = None

        for i in range(5, len(patient_obs) + 1):
            sub_df = patient_obs.iloc[:i]
            curr_date = pd.to_datetime(sub_df["date"].iloc[-1])

            # Check CARE PULSE
            t_data = evaluate_patient_trend(sub_df, curr_date)
            s_data = calculate_functional_decline_score(t_data)
            if s_data["risk_category"] in ["Needs Review", "Urgent Review"] and cp_first_flag_date is None:
                cp_first_flag_date = curr_date

            # Check Baseline
            b_data = evaluate_single_metric_baseline(sub_df)
            if b_data["baseline_flagged"] and base_first_flag_date is None:
                base_first_flag_date = curr_date

        # Evaluate CARE PULSE Performance
        if has_adverse_event:
            if cp_first_flag_date is not None and (adverse_date is None or cp_first_flag_date <= adverse_date):
                tp_cp += 1
                if adverse_date is not None:
                    lead_days = int((adverse_date - cp_first_flag_date).days)
                    lead_times_cp.append(max(lead_days, 0))
            else:
                fn_cp += 1
                fn_cases.append({
                    "patient_id": pid,
                    "profile": profile,
                    "reason": "Gradual decline was too subtle or occurred too late to trigger 14d vs 7d threshold before event."
                })
        else:
            if cp_first_flag_date is not None:
                fp_cp += 1
                fp_cases.append({
                    "patient_id": pid,
                    "profile": profile,
                    "reason": "Temporary single-day observation dip caused brief false alarm." if profile == "noisy_change" else "False alarm on non-decline profile."
                })
            else:
                tn_cp += 1

        # Evaluate Single-Metric Baseline Performance
        if has_adverse_event:
            if base_first_flag_date is not None and (adverse_date is None or base_first_flag_date <= adverse_date):
                tp_base += 1
                if adverse_date is not None:
                    lead_days = int((adverse_date - base_first_flag_date).days)
                    lead_times_base.append(max(lead_days, 0))
            else:
                fn_base += 1
        else:
            if base_first_flag_date is not None:
                fp_base += 1
            else:
                tn_base += 1

    # Compute Summary Metrics
    cp_total_positive = tp_cp + fn_cp
    cp_early_detection_rate = round((tp_cp / cp_total_positive * 100.0), 1) if cp_total_positive > 0 else 0.0
    cp_avg_lead_time = round(float(np.mean(lead_times_cp)), 1) if lead_times_cp else 0.0
    cp_median_lead_time = round(float(np.median(lead_times_cp)), 1) if lead_times_cp else 0.0
    cp_precision = round((tp_cp / (tp_cp + fp_cp) * 100.0), 1) if (tp_cp + fp_cp) > 0 else 0.0
    cp_recall = round((tp_cp / (tp_cp + fn_cp) * 100.0), 1) if (tp_cp + fn_cp) > 0 else 0.0

    base_total_positive = tp_base + fn_base
    base_early_detection_rate = round((tp_base / base_total_positive * 100.0), 1) if base_total_positive > 0 else 0.0
    base_avg_lead_time = round(float(np.mean(lead_times_base)), 1) if lead_times_base else 0.0
    base_median_lead_time = round(float(np.median(lead_times_base)), 1) if lead_times_base else 0.0
    base_precision = round((tp_base / (tp_base + fp_base) * 100.0), 1) if (tp_base + fp_base) > 0 else 0.0
    base_recall = round((tp_base / (tp_base + fn_base) * 100.0), 1) if (tp_base + fn_base) > 0 else 0.0

    return {
        "total_patients": total_patients,
        "care_pulse": {
            "tp": tp_cp,
            "fp": fp_cp,
            "tn": tn_cp,
            "fn": fn_cp,
            "early_detection_rate": cp_early_detection_rate,
            "avg_lead_time": cp_avg_lead_time,
            "median_lead_time": cp_median_lead_time,
            "precision": cp_precision,
            "recall": cp_recall
        },
        "baseline": {
            "tp": tp_base,
            "fp": fp_base,
            "tn": tn_base,
            "fn": fn_base,
            "early_detection_rate": base_early_detection_rate,
            "avg_lead_time": base_avg_lead_time,
            "median_lead_time": base_median_lead_time,
            "precision": base_precision,
            "recall": base_recall
        },
        "error_analysis": {
            "false_positives": fp_cases,
            "false_negatives": fn_cases
        }
    }

