"""
CARE PULSE Longitudinal Trend Analysis Engine (COE Specification).
Compares 14-day historical baseline against 7-day recent average across Mobility,
Nutrition, and Participation, with Activity and Incidents as supporting context.
Handles Freshness (Fresh, Stale, Very Stale) and Uncertainty (Good, Limited, Insufficient).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

def evaluate_patient_trend(patient_df: pd.DataFrame, dataset_max_date: pd.Timestamp = None) -> Dict[str, Any]:
    """
    Evaluates 14-day baseline vs 7-day average for a single patient's chronological DataFrame.
    """
    if patient_df.empty:
        return {
            "patient_id": "Unknown",
            "total_records": 0,
            "latest_date": "N/A",
            "days_since_last": 999,
            "freshness": "Very Stale",
            "confidence_level": "Insufficient Data",
            "confidence_reason": "No observation records found for patient.",
            "overall_status": "Missing Information",
            "trends": {}
        }

    sorted_df = patient_df.copy()
    sorted_df["date"] = pd.to_datetime(sorted_df["date"])
    sorted_df = sorted_df.sort_values("date").reset_index(drop=True)
    patient_id = str(sorted_df["patient_id"].iloc[0])
    total_records = len(sorted_df)

    latest_date = sorted_df["date"].max()

    if dataset_max_date is None:
        dataset_max_date = latest_date
    else:
        dataset_max_date = pd.to_datetime(dataset_max_date)

    days_since_last = int((dataset_max_date - latest_date).days)

    # 1. Freshness Classification (Central Thresholds: 0-1d Fresh, 2-3d Aging, 4-7d Stale, >7d Very Stale)
    if days_since_last <= 1:
        freshness = "Fresh"
    elif days_since_last <= 3:
        freshness = "Aging"
    elif days_since_last <= 7:
        freshness = "Stale"
    else:
        freshness = "Very Stale"

    # 2. Observation Gap Detection (Missing daily records between observations)
    date_diffs = (sorted_df["date"] - sorted_df["date"].shift(1)).dt.days
    max_gap = int(date_diffs.max()) if len(date_diffs) > 1 and not date_diffs.dropna().empty else 1
    has_gap = max_gap >= 3
    gap_warning = f"⚠️ Observation gap detected ({max_gap}-day break in daily records). Trend interpretation confidence is reduced." if has_gap else None

    # 3. Insufficient History Check (< 4 observation records)
    has_insufficient_history = total_records < 4

    # 4. Split 14-day baseline vs 7-day recent window
    cutoff_recent = latest_date - pd.Timedelta(days=7)
    cutoff_baseline = latest_date - pd.Timedelta(days=21)

    recent_df = sorted_df[sorted_df["date"] >= cutoff_recent]
    baseline_df = sorted_df[(sorted_df["date"] >= cutoff_baseline) & (sorted_df["date"] < cutoff_recent)]

    # Fallback to positional split if date range is narrow
    if recent_df.empty or len(recent_df) == 0:
        recent_df = sorted_df.tail(3)
        baseline_df = sorted_df.iloc[:-3] if total_records > 3 else sorted_df
    elif baseline_df.empty or len(baseline_df) == 0:
        baseline_df = sorted_df.iloc[:-len(recent_df)] if len(recent_df) < total_records else sorted_df

    # 5. Missing Data & Uncertainty Detection
    core_domains = ["mobility", "nutrition", "participation"]
    supporting_domains = ["activity"]

    missing_core_fields = []
    missing_counts = {}

    for d in core_domains:
        if d not in sorted_df.columns:
            missing_core_fields.append(d)
        else:
            missing_in_recent = int(recent_df[d].isna().sum())
            if missing_in_recent > 0:
                missing_counts[d] = missing_in_recent
            if recent_df[d].isna().all():
                missing_core_fields.append(d)

    # Determine Confidence Level & Human-Readable Reasons
    confidence_reasons = []

    if has_insufficient_history:
        confidence_reasons.append("Insufficient data for reliable baseline comparison.")

    if missing_core_fields:
        confidence_reasons.append(f"Missing core domain observations: {', '.join(missing_core_fields)}.")

    for d, cnt in missing_counts.items():
        confidence_reasons.append(f"{cnt} recent {d} observation(s) missing. The {d} trend may be less reliable.")

    if has_gap:
        confidence_reasons.append(gap_warning)

    if freshness in ["Aging", "Stale"]:
        confidence_reasons.append(f"Observation data is {days_since_last} days old. Trend interpretation should be reviewed carefully.")
    elif freshness == "Very Stale":
        confidence_reasons.append(f"Observation data is older than 7 days ({days_since_last} days old). Current functional status may differ from displayed signal.")

    if len(recent_df) < 2 and not has_insufficient_history:
        confidence_reasons.append("There are not enough recent observations to estimate a reliable decline trend.")

    # Quantitative Data Confidence Score (%)
    expected_recent_obs = len(recent_df) * len(core_domains) if len(recent_df) > 0 else 1
    actual_recent_obs = sum(recent_df[d].notna().sum() for d in core_domains if d in recent_df.columns)
    completeness_factor = float(actual_recent_obs) / float(expected_recent_obs) if expected_recent_obs > 0 else 0.0

    freshness_factor = 1.0 if freshness == "Fresh" else (0.85 if freshness == "Aging" else (0.50 if freshness == "Stale" else 0.20))
    continuity_factor = 0.75 if has_gap else 1.0
    history_factor = 1.0 if total_records >= 7 else (0.5 if total_records >= 4 else 0.2)

    confidence_score = float(round(min(max(completeness_factor * freshness_factor * continuity_factor * history_factor * 100.0, 0.0), 100.0), 1))

    if has_insufficient_history or missing_core_fields or freshness == "Very Stale" or len(recent_df) < 1:
        confidence_level = "Insufficient Data"
    elif confidence_score < 75.0 or confidence_reasons:
        confidence_level = "Limited Confidence"
    else:
        confidence_level = "Good Confidence"
        confidence_reasons.append("Recent observations are available across all three core domains.")

    confidence_reason_str = " ".join(confidence_reasons)

    # 6. Domain Trend Calculations
    trends = {}
    declining_core_count = 0
    improving_core_count = 0

    for domain in core_domains + supporting_domains:
        if domain in sorted_df.columns and not recent_df[domain].isna().all():
            recent_avg = recent_df[domain].dropna().mean()
            baseline_avg = baseline_df[domain].dropna().mean() if not baseline_df[domain].isna().all() else recent_avg

            if baseline_avg > 0:
                pct_change = ((recent_avg - baseline_avg) / baseline_avg) * 100.0
            else:
                pct_change = 0.0

            if pct_change <= -8.0:
                direction = "↓ Declining"
                status = "Declining"
                if domain in core_domains:
                    declining_core_count += 1
            elif pct_change >= 8.0:
                direction = "↑ Improving"
                status = "Improving"
                if domain in core_domains:
                    improving_core_count += 1
            else:
                direction = "→ Stable"
                status = "Stable"

            trends[domain] = {
                "recent_avg": float(round(recent_avg, 2)),
                "baseline_avg": float(round(baseline_avg, 2)),
                "pct_change": float(round(pct_change, 1)),
                "direction": direction,
                "status": status,
                "missing_count": int(recent_df[domain].isna().sum()) if domain in recent_df.columns else 0
            }
        else:
            trends[domain] = {
                "recent_avg": None,
                "baseline_avg": None,
                "pct_change": 0.0,
                "direction": "⚠️ Missing",
                "status": "Missing",
                "missing_count": len(recent_df)
            }

    # 7. Incident Context
    recent_incidents = int(recent_df["incident"].dropna().sum()) if "incident" in recent_df.columns else 0
    total_incidents = int(sorted_df["incident"].dropna().sum()) if "incident" in sorted_df.columns else 0

    # 8. Overall Status Determination (Pure Observational Signals)
    if freshness == "Very Stale":
        overall_status = "Data May Be Old"
    elif has_insufficient_history or missing_core_fields:
        overall_status = "Missing Information"
    elif declining_core_count >= 2 or recent_incidents >= 1:
        overall_status = "Urgent Review"
    elif declining_core_count == 1:
        overall_status = "Needs Review"
    else:
        overall_status = "Doing Well"

    return {
        "patient_id": patient_id,
        "total_records": total_records,
        "latest_date": latest_date.strftime("%Y-%m-%d"),
        "days_since_last": days_since_last,
        "freshness": freshness,
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "confidence_reason": confidence_reason_str,
        "has_gap": has_gap,
        "gap_warning": gap_warning,
        "has_insufficient_history": has_insufficient_history,
        "overall_status": overall_status,
        "recent_incidents": recent_incidents,
        "total_incidents": total_incidents,
        "trends": trends,
        "declining_core_count": declining_core_count
    }

def analyze_all_patient_trends(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes trends across all patients in dataset.
    """
    if df.empty:
        return []

    dataset_max_date = pd.to_datetime(df["date"], errors="coerce").max()
    results = []
    for pid, pgroup in df.groupby("patient_id"):
        t_data = evaluate_patient_trend(pgroup, dataset_max_date)
        if t_data:
            results.append(t_data)

    return results
