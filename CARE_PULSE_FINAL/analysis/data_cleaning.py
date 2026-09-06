from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np

def clean_and_inspect_dataframe(df: pd.DataFrame, strict_reject_zero_or_missing: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Cleans and standardizes an observation DataFrame and tracks rejected/invalid rows.
    Rejects rows missing patient_id/date, duplicate dates, OR rows with missing/no values or 0s in domain columns.
    Returns (cleaned_df, rejected_df, stats_dict).
    """
    empty_rejected = pd.DataFrame(columns=["patient_id", "date", "rejection_reason"])
    empty_stats = {"total_rows": 0, "valid_rows": 0, "rejected_rows": 0, "total_patients": 0}

    if df is None or df.empty:
        return pd.DataFrame(), empty_rejected, empty_stats

    raw_df = df.copy()
    raw_df.columns = [str(c).strip().lower() for c in raw_df.columns]

    if "patient_id" not in raw_df.columns or "date" not in raw_df.columns:
        missing_cols = [col for col in ["patient_id", "date"] if col not in raw_df.columns]
        rejected_copy = raw_df.copy()
        rejected_copy["rejection_reason"] = f"Missing column: {', '.join(missing_cols)}"
        return pd.DataFrame(), rejected_copy, {
            "total_rows": len(raw_df),
            "valid_rows": 0,
            "rejected_rows": len(raw_df),
            "total_patients": 0
        }

    # 1. Missing patient_id
    missing_id_mask = raw_df["patient_id"].isna() | (raw_df["patient_id"].astype(str).str.strip() == "")

    # 2. Invalid date
    parsed_dates = pd.to_datetime(raw_df["date"], errors="coerce")
    invalid_date_mask = parsed_dates.isna()

    # 3. Duplicate observations (keep the last chronological/occurring entry as valid)
    valid_candidate_mask = (~missing_id_mask) & (~invalid_date_mask)
    duplicate_mask = valid_candidate_mask & raw_df.duplicated(subset=["patient_id", "date"], keep="last")

    # 4. Domain columns check for missing / zero values
    domain_cols = ["mobility", "nutrition", "participation", "activity"]
    check_cols = [col for col in domain_cols if col in raw_df.columns]

    missing_val_mask = pd.Series(False, index=raw_df.index)
    zero_val_mask = pd.Series(False, index=raw_df.index)

    if strict_reject_zero_or_missing and check_cols:
        for idx in raw_df.index:
            for col in check_cols:
                val = raw_df.loc[idx, col]
                if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() in ["none", "nan", "null"]:
                    missing_val_mask.loc[idx] = True
                else:
                    num_val = pd.to_numeric(val, errors="coerce")
                    if pd.isna(num_val) or num_val == 0:
                        zero_val_mask.loc[idx] = True

    # Combine masks for rejections
    rejected_mask = missing_id_mask | invalid_date_mask | duplicate_mask
    if strict_reject_zero_or_missing:
        rejected_mask = rejected_mask | missing_val_mask | zero_val_mask

    # Build rejected DataFrame
    rejected_df = raw_df[rejected_mask].copy()
    reasons = []
    for idx in rejected_df.index:
        r_reasons = []
        if missing_id_mask.loc[idx]:
            r_reasons.append("Missing Patient ID")
        if invalid_date_mask.loc[idx]:
            r_reasons.append("Invalid / Unparseable Date")
        if duplicate_mask.loc[idx]:
            r_reasons.append("Duplicate record for same patient and date")

        # Check missing or zero columns for this row
        row_missing = []
        row_zero = []
        for col in check_cols:
            val = raw_df.loc[idx, col]
            if pd.isna(val) or str(val).strip() == "" or str(val).strip().lower() in ["none", "nan", "null"]:
                row_missing.append(col)
            else:
                num_val = pd.to_numeric(val, errors="coerce")
                if pd.isna(num_val):
                    row_missing.append(col)
                elif num_val == 0:
                    row_zero.append(col)

        if row_missing:
            r_reasons.append(f"No/Missing value in column(s): {', '.join(row_missing)}")
        if row_zero:
            r_reasons.append(f"Zero / invalid value in column(s): {', '.join(row_zero)}")

        reasons.append("; ".join(r_reasons))

    rejected_df["rejection_reason"] = reasons

    # Build valid DataFrame
    valid_raw = raw_df[~rejected_mask].copy()
    valid_raw["patient_id"] = valid_raw["patient_id"].astype(str).str.strip()
    valid_raw["date"] = parsed_dates[~rejected_mask]

    # Numeric columns cleaning & clipping
    numeric_cols = {
        "mobility": (0.0, 10.0),
        "nutrition": (0.0, 100.0),
        "participation": (0.0, 10.0),
        "activity": (0.0, 10.0),
        "incident": (0, 1)
    }

    for col, (min_val, max_val) in numeric_cols.items():
        if col in valid_raw.columns:
            valid_raw[col] = pd.to_numeric(valid_raw[col], errors="coerce")
            if valid_raw[col].isna().any():
                valid_raw[col] = valid_raw.groupby("patient_id")[col].transform(lambda x: x.fillna(x.median()))
                valid_raw[col] = valid_raw[col].fillna(valid_raw[col].median()).fillna(min_val)
            valid_raw[col] = valid_raw[col].clip(lower=min_val, upper=max_val)

    if "notes" not in valid_raw.columns:
        valid_raw["notes"] = "Regular observation logged."
    else:
        valid_raw["notes"] = valid_raw["notes"].fillna("No specific notes recorded.")

    cleaned_df = valid_raw.sort_values(by=["patient_id", "date"]).reset_index(drop=True)

    stats = {
        "total_rows": len(raw_df),
        "valid_rows": len(cleaned_df),
        "rejected_rows": len(rejected_df),
        "total_patients": int(cleaned_df["patient_id"].nunique()) if not cleaned_df.empty else 0
    }

    return cleaned_df, rejected_df, stats

def clean_observation_dataframe(df: pd.DataFrame, strict_reject_zero_or_missing: bool = False) -> pd.DataFrame:
    """
    Cleans and standardizes an observation DataFrame (backward-compatible interface).
    """
    cleaned_df, _, _ = clean_and_inspect_dataframe(df, strict_reject_zero_or_missing=strict_reject_zero_or_missing)
    return cleaned_df


