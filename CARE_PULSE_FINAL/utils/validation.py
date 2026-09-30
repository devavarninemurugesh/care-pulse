"""
Validation utilities for CARE PULSE CSV datasets.
Provides non-crashing validation checks for patient observation data.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "patient_id",
    "date",
    "mobility",
    "nutrition",
    "participation",
    "activity",
    "incident",
    "notes"
]

def validate_csv_dataframe(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """
    Validates an uploaded DataFrame against CARE PULSE schema and quality rules.
    Returns (is_valid, summary_dict).
    """
    summary: Dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "total_rows": 0,
        "total_patients": 0,
        "date_range": "N/A",
        "missing_columns": [],
        "invalid_date_count": 0,
        "duplicate_count": 0,
        "missing_id_count": 0,
        "missing_value_count": 0,
        "invalid_value_count": 0,
    }

    if df is None or df.empty:
        summary["valid"] = False
        summary["errors"].append("The CSV file is empty or could not be parsed.")
        return False, summary

    # Normalize column headers
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        summary["valid"] = False
        summary["missing_columns"] = missing_cols
        summary["errors"].append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, summary

    summary["total_rows"] = len(df)

    # 1. Missing patient IDs
    missing_ids = df["patient_id"].isna() | (df["patient_id"].astype(str).str.strip() == "")
    summary["missing_id_count"] = int(missing_ids.sum())
    if summary["missing_id_count"] > 0:
        summary["warnings"].append(f"{summary['missing_id_count']} rows are missing patient_id.")

    # 2. Invalid dates and future dates
    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    invalid_dates = parsed_dates.isna()
    summary["invalid_date_count"] = int(invalid_dates.sum())
    if summary["invalid_date_count"] > 0:
        summary["warnings"].append(f"{summary['invalid_date_count']} rows contain invalid date formats.")

    valid_dates = parsed_dates.dropna()
    if not valid_dates.empty:
        min_d = valid_dates.min().strftime("%b %Y")
        max_d = valid_dates.max().strftime("%b %Y")
        summary["date_range"] = f"{min_d} – {max_d}"

        # Detect future date observations relative to dataset/system timestamp
        future_dates = valid_dates > pd.Timestamp.now()
        future_count = int(future_dates.sum())
        summary["future_date_count"] = future_count
        if future_count > 0:
            summary["warnings"].append(f"{future_count} observation records contain future timestamps.")

    # 3. Duplicate observations (same patient_id and date)
    valid_id_date_mask = (~missing_ids) & (~invalid_dates)
    duplicates = df[valid_id_date_mask].duplicated(subset=["patient_id", "date"], keep=False)
    summary["duplicate_count"] = int(duplicates.sum())
    if summary["duplicate_count"] > 0:
        summary["warnings"].append(f"{summary['duplicate_count']} duplicate observation records found.")

    # 4. Missing values across key fields
    key_fields = ["mobility", "nutrition", "participation", "activity"]
    missing_vals = df[key_fields].isna().sum().sum()
    summary["missing_value_count"] = int(missing_vals)
    if summary["missing_value_count"] > 0:
        summary["warnings"].append(f"{summary['missing_value_count']} missing values detected in vital domains.")

    # 5. Invalid numeric ranges
    invalid_num = 0
    numeric_checks = [
        ("mobility", 0.0, 10.0),
        ("nutrition", 0.0, 100.0),
        ("participation", 0.0, 10.0),
        ("activity", 0.0, 10.0),
    ]
    for col, min_val, max_val in numeric_checks:
        numeric_series = pd.to_numeric(df[col], errors="coerce")
        out_of_range = (numeric_series < min_val) | (numeric_series > max_val)
        invalid_num += int(out_of_range.fillna(False).sum())

    summary["invalid_value_count"] = invalid_num
    if invalid_num > 0:
        summary["warnings"].append(f"{invalid_num} values fall outside expected domain ranges.")

    # Distinct patients
    valid_patients = df.loc[~missing_ids, "patient_id"].nunique()
    summary["total_patients"] = int(valid_patients)

    # Valid if no critical missing columns
    summary["valid"] = len(summary["errors"]) == 0
    return summary["valid"], summary
