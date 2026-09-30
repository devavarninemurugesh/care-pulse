"""
Unit tests for CARE PULSE validation utilities.
"""

import pandas as pd
import pytest
from utils.validation import validate_csv_dataframe

def test_valid_csv():
    df = pd.DataFrame({
        "patient_id": ["P001", "P001"],
        "date": ["2026-01-01", "2026-01-02"],
        "mobility": [8.0, 7.5],
        "nutrition": [85.0, 80.0],
        "participation": [8.0, 8.0],
        "activity": [7.0, 7.0],
        "incident": [0, 0],
        "notes": ["Good", "Stable"]
    })
    is_valid, summary = validate_csv_dataframe(df)
    assert is_valid is True
    assert summary["total_rows"] == 2
    assert summary["total_patients"] == 1
    assert len(summary["errors"]) == 0

def test_missing_columns():
    df = pd.DataFrame({
        "patient_id": ["P001"],
        "date": ["2026-01-01"]
    })
    is_valid, summary = validate_csv_dataframe(df)
    assert is_valid is False
    assert "mobility" in summary["missing_columns"]

def test_invalid_dates_and_duplicates():
    df = pd.DataFrame({
        "patient_id": ["P001", "P001", "P001"],
        "date": ["2026-01-01", "2026-01-01", "invalid-date"],
        "mobility": [8.0, 8.0, 7.0],
        "nutrition": [85.0, 85.0, 80.0],
        "participation": [8.0, 8.0, 8.0],
        "activity": [7.0, 7.0, 7.0],
        "incident": [0, 0, 0],
        "notes": ["N1", "N2", "N3"]
    })
    is_valid, summary = validate_csv_dataframe(df)
    assert is_valid is True
    assert summary["duplicate_count"] == 2
    assert summary["invalid_date_count"] == 1

def test_empty_dataframe():
    df = pd.DataFrame()
    is_valid, summary = validate_csv_dataframe(df)
    assert is_valid is False
    assert len(summary["errors"]) > 0

def test_case_6_duplicate_patient_date():
    """TEST 6 — Duplicate patient/date. Expected: CSV validation detects duplicates."""
    df = pd.DataFrame({
        "patient_id": ["P001", "P001"],
        "date": ["2026-09-01", "2026-09-01"],
        "mobility": [8.0, 7.5],
        "nutrition": [85.0, 80.0],
        "participation": [8.0, 8.0],
        "activity": [7.0, 7.0],
        "incident": [0, 0],
        "notes": ["N1", "N2"]
    })
    is_valid, summary = validate_csv_dataframe(df)
    assert summary["duplicate_count"] == 2

def test_case_7_invalid_metric_range():
    """TEST 7 — Invalid metric range (mobility = 15, nutrition = 120). Expected: CSV validation flags invalid range."""
    df = pd.DataFrame({
        "patient_id": ["P001", "P002"],
        "date": ["2026-09-01", "2026-09-02"],
        "mobility": [15.0, 8.0],     # 15.0 exceeds max 10.0
        "nutrition": [85.0, 120.0],   # 120.0 exceeds max 100.0
        "participation": [8.0, 8.0],
        "activity": [7.0, 7.0],
        "incident": [0, 0],
        "notes": ["Invalid mob", "Invalid nut"]
    })
    is_valid, summary = validate_csv_dataframe(df)
    assert summary["invalid_value_count"] >= 2
    assert any("outside expected domain ranges" in w for w in summary["warnings"])
