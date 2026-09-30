"""
Functional Decline Scoring Engine (COE Specification).
Computes an explainable 0-100 score based on 14d vs 7d Mobility, Nutrition, and Participation deltas,
supported by Activity drops, Incident rates, and Data Freshness.
"""

from typing import Dict, Any, List

def calculate_functional_decline_score(patient_trend: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes explainable 0-100 functional decline score and risk category.
    """
    if not patient_trend or patient_trend.get("has_insufficient_history"):
        return {
            "score": 0.0,
            "risk_category": "Missing Information",
            "overall_trend": "→ Stable",
            "contributing_factors": ["Insufficient data for reliable baseline comparison."]
        }

    score = 0.0
    contributing_factors = []
    trends = patient_trend.get("trends", {})

    # Core Domains: Mobility (max 30 pts), Nutrition (max 25 pts), Participation (max 20 pts)
    mob = trends.get("mobility", {})
    mob_pct = mob.get("pct_change", 0.0) if mob else 0.0
    if mob_pct < 0:
        mob_pts = min(abs(mob_pct) * 1.2, 30.0)
        score += mob_pts
        if mob_pct <= -8.0:
            contributing_factors.append(f"Mobility decreased by {abs(mob_pct):.1f}% (7d avg vs 14d baseline)")

    nut = trends.get("nutrition", {})
    nut_pct = nut.get("pct_change", 0.0) if nut else 0.0
    if nut_pct < 0:
        nut_pts = min(abs(nut_pct) * 0.8, 25.0)
        score += nut_pts
        if nut_pct <= -8.0:
            contributing_factors.append(f"Nutrition intake decreased by {abs(nut_pct):.1f}%")

    part = trends.get("participation", {})
    part_pct = part.get("pct_change", 0.0) if part else 0.0
    if part_pct < 0:
        part_pts = min(abs(part_pct) * 0.7, 20.0)
        score += part_pts
        if part_pct <= -8.0:
            contributing_factors.append(f"Social participation dropped by {abs(part_pct):.1f}%")

    # Supporting Domain: Daily Activity (max 15 pts)
    act = trends.get("activity", {})
    act_pct = act.get("pct_change", 0.0) if act else 0.0
    if act_pct < 0:
        act_pts = min(abs(act_pct) * 0.5, 15.0)
        score += act_pts
        if act_pct <= -8.0:
            contributing_factors.append(f"Daily Activity level dropped by {abs(act_pct):.1f}%")

    # Supporting Context: Incidents (15 pts per recent incident, max 30 pts)
    recent_incidents = patient_trend.get("recent_incidents", 0)
    if recent_incidents > 0:
        score += min(recent_incidents * 15.0, 30.0)
        contributing_factors.append(f"{recent_incidents} recent safety/fall incident(s) recorded")

    # Observation Gap Penalty / Factor
    if patient_trend.get("has_gap"):
        score += 5.0
        contributing_factors.append(patient_trend.get("gap_warning", "Observation gap detected (missing daily records)."))

    # Freshness Penalty
    freshness = patient_trend.get("freshness", "Fresh")
    if freshness == "Aging":
        contributing_factors.append("Data is Aging (2–3 days since last observation)")
    elif freshness == "Stale":
        score += 8.0
        contributing_factors.append("Data is Stale (4–7 days since last observation)")
    elif freshness == "Very Stale":
        score += 15.0
        contributing_factors.append("Data is Very Stale (>7 days since last observation)")

    final_score = float(round(min(max(score, 0.0), 100.0), 1))

    # Overall Status Override if Missing Information or Very Stale
    status_override = patient_trend.get("overall_status")
    if status_override in ["Missing Information", "Data May Be Old"]:
        risk_category = status_override
    elif final_score >= 60.0:
        risk_category = "Urgent Review"
    elif final_score >= 30.0:
        risk_category = "Needs Review"
    else:
        risk_category = "Doing Well"

    if "Declining" in str(mob.get("direction")) or "Declining" in str(nut.get("direction")):
        overall_trend = "↓ Declining"
    elif "Improving" in str(mob.get("direction")):
        overall_trend = "↑ Improving"
    else:
        overall_trend = "→ Stable"

    if not contributing_factors:
        contributing_factors.append("All core and supporting functional indicators remain stable within 14-day baseline parameters.")

    return {
        "score": final_score,
        "risk_category": risk_category,
        "overall_trend": overall_trend,
        "contributing_factors": contributing_factors
    }
