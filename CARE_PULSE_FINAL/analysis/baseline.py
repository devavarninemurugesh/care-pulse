"""
Single-Metric Threshold Baseline Module for CARE PULSE.
Provides traditional point-in-time threshold flagging for comparative evaluation.
"""

from typing import Dict, Any
import pandas as pd

MOBILITY_THRESHOLD = 5.0
NUTRITION_THRESHOLD = 50.0

def evaluate_single_metric_baseline(patient_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Evaluates traditional single-metric static threshold rules on patient DataFrame:
    Flags patient if latest mobility < 5.0 OR latest nutrition < 50.0.
    """
    if patient_df.empty:
        return {
            "baseline_flagged": False,
            "baseline_status": "Normal",
            "trigger_reason": "No observations available.",
            "flag_date": None
        }

    sorted_df = patient_df.sort_values("date").reset_index(drop=True)
    latest_row = sorted_df.iloc[-1]
    latest_date = latest_row["date"].strftime("%Y-%m-%d") if isinstance(latest_row["date"], pd.Timestamp) else str(latest_row["date"])

    mob = latest_row.get("mobility", None)
    nut = latest_row.get("nutrition", None)

    reasons = []

    if pd.notna(mob) and mob < MOBILITY_THRESHOLD:
        reasons.append(f"Latest mobility ({mob:.1f}) < threshold ({MOBILITY_THRESHOLD})")

    if pd.notna(nut) and nut < NUTRITION_THRESHOLD:
        reasons.append(f"Latest nutrition ({nut:.1f}) < threshold ({NUTRITION_THRESHOLD})")

    if reasons:
        return {
            "baseline_flagged": True,
            "baseline_status": "Flagged",
            "trigger_reason": "; ".join(reasons),
            "flag_date": latest_date
        }

    return {
        "baseline_flagged": False,
        "baseline_status": "Normal",
        "trigger_reason": "Vitals above static single-metric thresholds.",
        "flag_date": None
    }
