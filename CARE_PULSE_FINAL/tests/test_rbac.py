"""
Unit tests for CARE PULSE Role-Based Access Control (RBAC) and Security Module.
Tests role permissions, page accessibility, patient assignment filtering, and 403 authorization logic.
"""

import pytest
import pandas as pd
from security import (
    ROLE_CAREGIVER,
    ROLE_SUPERVISOR,
    ROLE_AUTHORIZED_STAFF,
    ROLE_ADMIN,
    DEMO_USERS,
    has_permission,
    can_access_page,
    can_access_patient,
    filter_authorized_patients,
    filter_authorized_df,
    PERM_UPLOAD_DATA,
    PERM_RUN_EXPERIMENT,
    PERM_MANAGE_SYSTEM,
    PERM_VIEW_EVIDENCE
)

def test_rbac_permissions():
    # Caregiver permissions check
    assert has_permission(ROLE_CAREGIVER, PERM_VIEW_EVIDENCE) is True
    assert has_permission(ROLE_CAREGIVER, PERM_UPLOAD_DATA) is False
    assert has_permission(ROLE_CAREGIVER, PERM_RUN_EXPERIMENT) is False

    # Supervisor permissions check
    assert has_permission(ROLE_SUPERVISOR, PERM_VIEW_EVIDENCE) is True
    assert has_permission(ROLE_SUPERVISOR, PERM_MANAGE_SYSTEM) is False

    # Authorized Staff permissions check
    assert has_permission(ROLE_AUTHORIZED_STAFF, PERM_UPLOAD_DATA) is True
    assert has_permission(ROLE_AUTHORIZED_STAFF, PERM_RUN_EXPERIMENT) is True
    assert has_permission(ROLE_AUTHORIZED_STAFF, PERM_MANAGE_SYSTEM) is False

    # Admin permissions check
    assert has_permission(ROLE_ADMIN, PERM_MANAGE_SYSTEM) is True
    assert has_permission(ROLE_ADMIN, PERM_UPLOAD_DATA) is True

def test_page_access_control():
    assert can_access_page(ROLE_CAREGIVER, "Dashboard") is True
    assert can_access_page(ROLE_CAREGIVER, "Upload Data") is False
    assert can_access_page(ROLE_CAREGIVER, "Experiment & Evaluation") is False

    assert can_access_page(ROLE_AUTHORIZED_STAFF, "Upload Data") is True
    assert can_access_page(ROLE_AUTHORIZED_STAFF, "Experiment & Evaluation") is True

    assert can_access_page(ROLE_ADMIN, "Upload Data") is True
    assert can_access_page(ROLE_ADMIN, "Experiment & Evaluation") is True

def test_patient_assignment_access():
    caregiver_info = DEMO_USERS["caregiver_01"]
    staff_info = DEMO_USERS["staff_01"]

    # All profiles have access to all patients
    assert can_access_patient(caregiver_info, "P001") is True
    assert can_access_patient(caregiver_info, "P002") is True
    assert can_access_patient(caregiver_info, "P003") is True

    # Staff can access all patients
    assert can_access_patient(staff_info, "P003") is True
    assert can_access_patient(staff_info, "P999") is True

def test_filter_authorized_patients():
    sample_summaries = [
        {"patient_id": "P001", "decline_score": 10},
        {"patient_id": "P002", "decline_score": 20},
        {"patient_id": "P003", "decline_score": 30},
        {"patient_id": "P005", "decline_score": 40},
    ]

    cg_info = DEMO_USERS["caregiver_01"]
    filtered_cg = filter_authorized_patients(sample_summaries, cg_info)
    assert len(filtered_cg) == 4
    cg_pids = [p["patient_id"] for p in filtered_cg]
    assert "P001" in cg_pids
    assert "P002" in cg_pids
    assert "P005" in cg_pids
    assert "P003" in cg_pids

    admin_info = DEMO_USERS["admin_01"]
    filtered_admin = filter_authorized_patients(sample_summaries, admin_info)
    assert len(filtered_admin) == 4

def test_filter_authorized_df():
    df = pd.DataFrame({
        "patient_id": ["P001", "P002", "P003", "P005"],
        "date": ["2026-05-01"] * 4,
        "mobility": [8.0, 7.5, 6.0, 8.5]
    })

    cg_info = DEMO_USERS["caregiver_01"]
    filtered_df = filter_authorized_df(df, cg_info)
    assert len(filtered_df) == 4
    assert "P003" in filtered_df["patient_id"].values
