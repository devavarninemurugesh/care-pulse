"""
Centralized Role-Based Access Control (RBAC) and Security Module for CARE PULSE.
Enforces role permissions, demo user mappings, patient population scoping,
and 403 unauthorized access prevention across UI and data layers.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import streamlit as st

# 1. Role Constants
ROLE_CAREGIVER = "Caregiver"
ROLE_SUPERVISOR = "Supervisor"
ROLE_AUTHORIZED_STAFF = "Authorized Staff"
ROLE_ADMIN = "Admin"

ROLES = [ROLE_CAREGIVER, ROLE_SUPERVISOR, ROLE_AUTHORIZED_STAFF, ROLE_ADMIN]

# 2. Permissions Definition
PERM_VIEW_ASSIGNED_PATIENTS = "view_assigned_patients"
PERM_VIEW_ALL_PATIENTS = "view_all_patients"
PERM_ENTER_OBSERVATIONS = "enter_observations"
PERM_VIEW_ALERTS = "view_alerts"
PERM_VIEW_EVIDENCE = "view_evidence"
PERM_UPLOAD_DATA = "upload_data"
PERM_RUN_EXPERIMENT = "run_experiment"
PERM_MANAGE_USERS = "manage_users"
PERM_MANAGE_SYSTEM = "manage_system"

# Role Permission Matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    ROLE_CAREGIVER: [
        PERM_VIEW_ASSIGNED_PATIENTS,
        PERM_VIEW_ALL_PATIENTS,
        PERM_ENTER_OBSERVATIONS,
        PERM_VIEW_ALERTS,
        PERM_VIEW_EVIDENCE,
    ],
    ROLE_SUPERVISOR: [
        PERM_VIEW_ASSIGNED_PATIENTS,
        PERM_VIEW_ALL_PATIENTS,
        PERM_VIEW_ALERTS,
        PERM_VIEW_EVIDENCE,
        PERM_ENTER_OBSERVATIONS,
    ],
    ROLE_AUTHORIZED_STAFF: [
        PERM_VIEW_ASSIGNED_PATIENTS,
        PERM_VIEW_ALL_PATIENTS,
        PERM_VIEW_ALERTS,
        PERM_VIEW_EVIDENCE,
        PERM_ENTER_OBSERVATIONS,
        PERM_UPLOAD_DATA,
        PERM_RUN_EXPERIMENT,
    ],
    ROLE_ADMIN: [
        PERM_VIEW_ASSIGNED_PATIENTS,
        PERM_VIEW_ALL_PATIENTS,
        PERM_VIEW_ALERTS,
        PERM_VIEW_EVIDENCE,
        PERM_ENTER_OBSERVATIONS,
        PERM_UPLOAD_DATA,
        PERM_RUN_EXPERIMENT,
        PERM_MANAGE_USERS,
        PERM_MANAGE_SYSTEM,
    ],
}

# 3. Demo User Profiles (User -> Role -> Assigned Patients)
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "caregiver_01": {
        "name": "Devavarnine M (Caregiver)",
        "role": ROLE_CAREGIVER,
        "patients": "ALL",
        "description": "Primary Caregiver (Access to all patients)"
    },
    "supervisor_01": {
        "name": "Dharshini (Supervisor)",
        "role": ROLE_SUPERVISOR,
        "patients": "ALL",
        "description": "Clinical Supervisor (Access to all patients)"
    },
    "staff_01": {
        "name": "Yuya (Authorized Staff)",
        "role": ROLE_AUTHORIZED_STAFF,
        "patients": "ALL",
        "description": "Authorized Clinical Analyst (Access to all patients)"
    },
    "admin_01": {
        "name": "Swathini C (Admin)",
        "role": ROLE_ADMIN,
        "patients": "ALL",
        "description": "Full System Administrator access"
    }
}

# Page Access Permission Mapping
PAGE_PERMISSIONS: Dict[str, str] = {
    "Dashboard": PERM_VIEW_ASSIGNED_PATIENTS,
    "Upload Data": PERM_UPLOAD_DATA,
    "Patients": PERM_VIEW_ASSIGNED_PATIENTS,
    "Alerts": PERM_VIEW_ALERTS,
    "Evidence": PERM_VIEW_EVIDENCE,
    "Experiment & Evaluation": PERM_RUN_EXPERIMENT,
    "Edge Cases & Quality": PERM_VIEW_EVIDENCE,
    "System Admin": PERM_MANAGE_SYSTEM,
}

def get_current_user_id() -> str:
    """Returns currently selected demo user ID from session state."""
    return st.session_state.get("current_user_id", "admin_01")

def get_current_user_info() -> Dict[str, Any]:
    """Returns profile dictionary of current demo user."""
    uid = get_current_user_id()
    return DEMO_USERS.get(uid, DEMO_USERS["admin_01"])

def get_current_user_role() -> str:
    """Returns effective role string of current user."""
    return get_current_user_info()["role"]

def has_permission(role: str, permission: str) -> bool:
    """Checks if a given role possesses a specific permission."""
    allowed_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in allowed_perms

def can_access_page(role: str, page_name: str) -> bool:
    """Checks if a role can access a specific page."""
    if role == ROLE_ADMIN:
        return True
    required_perm = PAGE_PERMISSIONS.get(page_name)
    if not required_perm:
        return True
    return has_permission(role, required_perm)

def can_access_patient(user_info: Dict[str, Any], patient_id: str) -> bool:
    """
    Data-level access control: checks if current user is authorized to view a specific patient.
    """
    if not user_info:
        return False
    assigned = user_info.get("patients", [])
    if assigned == "ALL":
        return True
    return str(patient_id).strip() in assigned

def filter_authorized_patients(patient_summaries: List[Dict[str, Any]], user_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filters a list of patient summaries based on user patient assignment."""
    if not user_info or not patient_summaries:
        return []
    assigned = user_info.get("patients", [])
    if assigned == "ALL":
        return patient_summaries
    return [p for p in patient_summaries if str(p.get("patient_id")).strip() in assigned]

def filter_authorized_df(df: pd.DataFrame, user_info: Dict[str, Any]) -> pd.DataFrame:
    """Filters an observation DataFrame based on user patient assignment."""
    if df is None or df.empty or not user_info:
        return df
    assigned = user_info.get("patients", [])
    if assigned == "ALL":
        return df
    return df[df["patient_id"].astype(str).str.strip().isin(assigned)].reset_index(drop=True)

def render_403_unauthorized(action_or_page: str = "this resource"):
    """Renders a standard 403 Access Denied warning banner."""
    user_info = get_current_user_info()
    st.markdown(f"""
        <div style="background: #fef2f2; border: 2px solid #ef4444; border-radius: 12px; padding: 30px; text-align: center; margin: 30px 0;">
            <div style="font-size: 3rem; margin-bottom: 8px;">🔒</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #991b1b; margin-bottom: 8px;">403 — Access Denied</div>
            <div style="font-size: 1.0rem; color: #7f1d1d; margin-bottom: 16px;">
                You are logged in as <strong>{user_info['name']}</strong> ({user_info['role']}).<br/>
                Your account is not authorized to access <strong>{action_or_page}</strong>.
            </div>
            <div style="font-size: 0.85rem; color: #b91c1c;">
                Contact your System Administrator or switch to an Authorized demo user profile in the sidebar to access this section.
            </div>
        </div>
    """, unsafe_allow_html=True)
