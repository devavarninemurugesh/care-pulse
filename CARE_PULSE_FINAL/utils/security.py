import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from utils.database import query_to_dataframe

# Centralized Permission Matrix
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "Caregiver": [
        "patient.view_assigned",
        "patient.register_assigned",  # Caregiver patient self-registration with auto-assignment
        "observation.create",
        "observation.view_assigned",
        "incident.view_assigned",
        "alert.view_assigned"
    ],
    "Supervisor": [
        "patient.view_supervised",
        "observation.view_supervised",
        "observation.review",
        "evidence.view",
        "review.manage",
        "incident.view_supervised",
        "alert.view_supervised"
    ],
    "Authorized Staff": [
        "patient.view_all",
        "patient.create",
        "patient.edit",
        "observation.create",
        "observation.view_all",
        "evidence.view",
        "incident.view_all",
        "csv.upload"
    ],
    "Admin": [
        "patient.view_all",
        "patient.create",
        "patient.edit",
        "patient.deactivate",
        "patient.reassign",
        "observation.create",
        "observation.view_all",
        "observation.review",
        "evidence.view",
        "review.manage",
        "incident.view_all",
        "csv.upload",
        "user.manage",
        "role.manage",
        "system.settings"
    ]
}


def has_permission(role: str, permission_code: str) -> bool:
    """
    Centralized Permission Checker:
    Returns True if the specified role holds the requested permission code.
    """
    if not role or role not in ROLE_PERMISSIONS:
        return False
    return permission_code in ROLE_PERMISSIONS[role]


# Helper Alias Functions
def can_register_patient(role: str) -> bool:
    return has_permission(role, "patient.create") or has_permission(role, "patient.register_assigned")

def can_edit_patient(role: str) -> bool:
    return has_permission(role, "patient.edit")

def can_deactivate_patient(role: str) -> bool:
    return has_permission(role, "patient.deactivate")

def can_reassign_caregiver(role: str) -> bool:
    return has_permission(role, "patient.reassign")


def check_patient_access(user_id: str, role: str, patient_id: str, db_path: Optional[str] = None) -> Tuple[bool, int, str]:
    """
    Backend Data Access Checker (403 Forbidden Protection):
    Verifies whether a user is authorized to view or modify a specific patient record.
    Returns: (is_authorized: bool, http_status_code: int, message: str)
    """
    if not role or not user_id or not patient_id:
        return False, 403, "Access Denied — Missing user identity or patient ID."

    # Admin, Authorized Staff, Supervisor have system/supervised patient access
    if has_permission(role, "patient.view_all") or has_permission(role, "patient.view_supervised"):
        return True, 200, "Authorized"

    # Caregiver: Access is restricted ONLY to patients assigned to them
    if has_permission(role, "patient.view_assigned"):
        query = "SELECT patient_id FROM patients WHERE patient_id = ? AND assigned_caregiver_id = ?"
        params = (patient_id, user_id)
        df = query_to_dataframe(query, params, db_path=db_path) if db_path else query_to_dataframe(query, params)
        
        if not df.empty:
            return True, 200, "Authorized"
        else:
            return False, 403, f"403 Forbidden: You do not have permission to access patient record '{patient_id}'. This care recipient is not assigned to you."

    return False, 403, "403 Forbidden: Role unauthorized for patient operations."


def can_access_patient(user_id: str, role: str, patient_id: str, db_path: Optional[str] = None) -> bool:
    """Boolean helper alias for check_patient_access."""
    is_auth, _, _ = check_patient_access(user_id, role, patient_id, db_path=db_path)
    return is_auth


def filter_assigned_patients_df(user_id: str, role: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters a patient DataFrame based on role data isolation rules.
    - Caregivers only receive rows assigned to them.
    - Other roles receive full DataFrame.
    """
    if df.empty:
        return df

    if role == "Caregiver":
        if "assigned_caregiver_id" in df.columns:
            return df[df["assigned_caregiver_id"] == user_id].reset_index(drop=True)
    return df
