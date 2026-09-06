"""
Synthetic Data Generator for CARE PULSE COE Evaluation Dataset.
Generates exactly 10 synthetic patient trajectories over 35 days with known simulated adverse event dates,
gradual decline patterns, stable controls, stale observation gaps, missing data, and noisy changes.
"""

import os
import random
import numpy as np
import pandas as pd

def generate_coe_synthetic_dataset(num_patients: int = 10, num_days: int = 35) -> pd.DataFrame:
    """
    Generates synthetic observation records for num_patients across num_days.
    """
    random.seed(42)
    np.random.seed(42)

    base_date = pd.Timestamp("2026-05-01")
    records = []

    for p_idx in range(1, num_patients + 1):
        pid = f"P{p_idx:03d}"

        # Assign profile distribution for 10 patients:
        # P001 - P004: Gradual decline
        # P005 - P007: Stable control
        # P008: Stale data
        # P009: Missing data
        # P010: Noisy change
        if p_idx <= 4:
            profile = "gradual_decline"
            adverse_event_day = random.randint(28, 32)
        elif p_idx <= 7:
            profile = "stable"
            adverse_event_day = None
        elif p_idx == 8:
            profile = "stale"
            adverse_event_day = None
        elif p_idx == 9:
            profile = "missing_data"
            adverse_event_day = None
        else:
            profile = "noisy_change"
            adverse_event_day = None

        for day in range(num_days):
            curr_date = base_date + pd.Timedelta(days=day)

            # Skip days for stale profile after day 20
            if profile == "stale" and day > 20:
                continue

            # Initial baseline values around healthy levels
            mobility = round(float(np.random.normal(8.5, 0.4)), 1)
            nutrition = round(float(np.random.normal(88.0, 3.0)), 1)
            participation = round(float(np.random.normal(8.5, 0.4)), 1)
            activity = round(float(np.random.normal(8.2, 0.4)), 1)
            incident = 0
            notes = "Daily routine completed normally."

            # Apply profile trajectories
            if profile == "gradual_decline":
                decline_start = 12
                if day >= decline_start:
                    days_into_decline = day - decline_start
                    mobility = max(1.0, round(mobility - 0.22 * days_into_decline + float(np.random.normal(0, 0.2)), 1))
                    nutrition = max(20.0, round(nutrition - 1.8 * days_into_decline + float(np.random.normal(0, 1.0)), 1))
                    participation = max(1.0, round(participation - 0.20 * days_into_decline + float(np.random.normal(0, 0.2)), 1))
                    activity = max(1.0, round(activity - 0.25 * days_into_decline + float(np.random.normal(0, 0.2)), 1))

                if day == adverse_event_day:
                    incident = 1
                    notes = f"SIMULATED ADVERSE EVENT: Patient suffered fall on day {day}."

            elif profile == "noisy_change":
                if day == 25:
                    mobility = 4.0
                    activity = 3.5
                    notes = "Single-day low energy noted. Recovered next day."

            elif profile == "missing_data":
                if day >= 25:
                    if random.random() < 0.6:
                        mobility = np.nan
                    if random.random() < 0.5:
                        nutrition = np.nan

            # Clip bounds
            if not np.isnan(mobility):
                mobility = min(max(mobility, 0.0), 10.0)
            if not np.isnan(nutrition):
                nutrition = min(max(nutrition, 0.0), 100.0)
            if not np.isnan(participation):
                participation = min(max(participation, 0.0), 10.0)
            if not np.isnan(activity):
                activity = min(max(activity, 0.0), 10.0)

            records.append({
                "patient_id": pid,
                "date": curr_date.strftime("%Y-%m-%d"),
                "mobility": mobility,
                "nutrition": nutrition,
                "participation": participation,
                "activity": activity,
                "incident": incident,
                "notes": notes,
                "profile": profile,
                "adverse_event_date": (base_date + pd.Timedelta(days=adverse_event_day)).strftime("%Y-%m-%d") if adverse_event_day else "N/A"
            })

    return pd.DataFrame(records)

if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    out_path = os.path.join(out_dir, "sample_patients.csv")
    df = generate_coe_synthetic_dataset(10, 35)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} synthetic observation records for 10 patients at {out_path}")
