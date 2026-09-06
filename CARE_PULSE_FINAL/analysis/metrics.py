"""
Aggregated dataset metrics and summary KPIs generator.
"""

from typing import Dict, Any, List
import pandas as pd

# Configurable Freshness Thresholds (Days)
FRESH_THRESHOLD_DAYS = 3      # Fresh: <= 3 days
STALE_THRESHOLD_DAYS = 7      # Stale: 4 to 7 days; Very Stale: > 7 days

def classify_freshness(days_since_last: int) -> str:
    """
    Classifies signal freshness based on days elapsed since last observation.
    - Fresh: <= 3 days
    - Stale: 4–7 days
    - Very Stale: > 7 days
    """
    if days_since_last <= FRESH_THRESHOLD_DAYS:
        return "Fresh"
    elif days_since_last <= STALE_THRESHOLD_DAYS:
        return "Stale"
    else:
        return "Very Stale"

def compute_dataset_metrics(df: pd.DataFrame, patient_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes top-level dashboard KPI statistics based on actual freshness and risk statuses.
    """
    if df is None or df.empty or not patient_summaries:
        return {
            "total_patients": 0,
            "total_observations": 0,
            "urgent_review_count": 0,
            "needs_review_count": 0,
            "doing_well_count": 0,
            "stale_patient_count": 0,
            "date_range": "N/A"
        }

    total_patients = len(patient_summaries)
    total_observations = len(df)

    urgent_count = sum(1 for p in patient_summaries if p.get("risk_category") == "Urgent Review")
    needs_count = sum(1 for p in patient_summaries if p.get("risk_category") == "Needs Review")
    well_count = sum(1 for p in patient_summaries if p.get("risk_category") == "Doing Well")
    
    # Calculate stale count from actual freshness status or days_since_last >= 4
    stale_count = sum(
        1 for p in patient_summaries
        if p.get("freshness") in ["Stale", "Very Stale"] or p.get("days_since_last", 0) >= 4 or p.get("is_stale", False)
    )

    min_date = df["date"].min().strftime("%b %d, %Y") if "date" in df.columns and not df.empty else "N/A"
    max_date = df["date"].max().strftime("%b %d, %Y") if "date" in df.columns and not df.empty else "N/A"
    date_range = f"{min_date} – {max_date}"

    return {
        "total_patients": total_patients,
        "total_observations": total_observations,
        "urgent_review_count": urgent_count,
        "needs_review_count": needs_count,
        "doing_well_count": well_count,
        "stale_patient_count": stale_count,
        "date_range": date_range
    }

