"""
CARE PULSE — Home-Care Early Decline Detection
Main Streamlit Application Entry Point.
"""

import os
import pandas as pd
import streamlit as st
from analysis.pipeline import process_dataset
from analysis.data_cleaning import clean_and_inspect_dataframe
from security import (
    DEMO_USERS,
    ROLES,
    get_current_user_info,
    get_current_user_role,
    can_access_page,
    render_403_unauthorized
)

# Configure Streamlit Page
st.set_page_config(
    page_title="CARE PULSE — Home-Care Early Decline Detection",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

from ui.styles import apply_custom_styles
from ui.upload import render_upload_page
from ui.dashboard import render_dashboard
from ui.patients import render_patients_page
from ui.alerts import render_alerts_page
from ui.evidence import render_evidence_page
from ui.experiment_page import render_experiment_page

# Apply Custom Styling
apply_custom_styles()

# Auto-initialize session state with main care.csv dataset if not already present
CARE_CSV_PATH = os.path.join(os.path.dirname(__file__), "care.csv")
LOCAL_10_CSV = os.path.join(os.path.dirname(__file__), "sample_10_patients.csv")
SAMPLE_CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "sample_patients.csv")

if "processed_data" not in st.session_state or st.session_state["processed_data"] is None:
    target_path = CARE_CSV_PATH if os.path.exists(CARE_CSV_PATH) else (LOCAL_10_CSV if os.path.exists(LOCAL_10_CSV) else SAMPLE_CSV_PATH)
    if os.path.exists(target_path):
        try:
            df_local = pd.read_csv(target_path)
            st.session_state["raw_csv_df"] = df_local
            cleaned_df, rejected_df, stats = clean_and_inspect_dataframe(df_local)
            st.session_state["cleaned_df"] = cleaned_df
            st.session_state["rejected_df"] = rejected_df
            st.session_state["clean_stats"] = stats
            st.session_state["processed_data"] = process_dataset(cleaned_df)
            st.session_state["last_file_name"] = os.path.basename(target_path)
            st.session_state["is_custom_upload"] = False
        except Exception as e:
            st.error(f"Error loading main CSV file: {e}")

if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = "admin_01"

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# Sidebar Header & Demo User Switcher
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <div style="background: #2563eb; width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: white;">
                🩺
            </div>
            <div>
                <div style="font-size: 1.25rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em;">CARE PULSE</div>
                <div style="font-size: 0.75rem; font-weight: 600; color: #64748b;">Early Decline Detection</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 1. Demo User & Role Switcher
    st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #475569; margin-bottom: 6px;'>👤 DEMO USER & ROLE SWITCHER</div>", unsafe_allow_html=True)
    user_keys = list(DEMO_USERS.keys())
    current_uid = st.session_state.get("current_user_id", "admin_01")
    curr_idx = user_keys.index(current_uid) if current_uid in user_keys else 3

    selected_uid = st.selectbox(
        "Select Active User Profile",
        user_keys,
        index=curr_idx,
        format_func=lambda uid: DEMO_USERS[uid]["name"],
        label_visibility="collapsed"
    )
    st.session_state.current_user_id = selected_uid
    u_info = DEMO_USERS[selected_uid]
    st.session_state.user_role = u_info["role"]

    # Display Active User Profile Badge
    st.markdown(f"""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; padding: 8px 12px; border-radius: 6px; font-size: 0.75rem; color: #1e40af; margin-top: 6px;">
            <strong>Role:</strong> {u_info['role']}<br/>
            <strong>Scope:</strong> {u_info['description']}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Navigation Menu per Role
    st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #475569; margin-bottom: 6px;'>NAVIGATION</div>", unsafe_allow_html=True)
    
    user_role = get_current_user_role()
    if user_role == "Caregiver":
        nav_options = ["📊 Dashboard", "👥 Patients", "🔔 Alerts", "🔍 Evidence"]
    elif user_role == "Supervisor":
        nav_options = ["📊 Dashboard", "👥 Patients", "🔔 Alerts", "🔍 Evidence"]
    elif user_role == "Authorized Staff":
        nav_options = ["📊 Dashboard", "📤 Upload Data", "👥 Patients", "🔔 Alerts", "🔍 Evidence", "🧪 Experiment & Evaluation"]
    else:  # Admin
        nav_options = [
            "📊 Dashboard",
            "📤 Upload Data",
            "👥 Patients",
            "🔔 Alerts",
            "🔍 Evidence",
            "🧪 Experiment & Evaluation"
        ]

    current_page = st.session_state.get("active_page", "Dashboard")
    
    # Map current_page to valid index
    default_idx = 0
    for idx, opt in enumerate(nav_options):
        clean_name = opt.split(" ", 1)[-1]
        if clean_name == current_page or opt == current_page:
            default_idx = idx
            break

    selected_raw = st.radio("Navigation Menu", nav_options, index=default_idx, label_visibility="collapsed")
    selected_clean = selected_raw.split(" ", 1)[-1]
    st.session_state.active_page = selected_clean

    st.markdown("---")

    # Dataset Status Indicator
    if st.session_state.get("processed_data"):
        m = st.session_state["processed_data"]["metrics"]
        file_name = st.session_state.get("last_file_name", "Dataset Loaded")
        is_custom = st.session_state.get("is_custom_upload", False)
        status_label = "Uploaded CSV Loaded" if is_custom else "Main Dataset (care.csv)"
        st.markdown(f"""
            <div style="background: #f1f5f9; padding: 10px; border-radius: 8px; font-size: 0.78rem; color: #334155;">
                🟢 <strong>{status_label}:</strong><br/>
                <span style="font-weight: 700; color: #0f172a; word-break: break-all;">{file_name}</span><br/>
                {m['total_patients']} Patients ({m['total_observations']:,} rows)
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: #fef2f2; padding: 10px; border-radius: 8px; font-size: 0.78rem; color: #991b1b;">
                ⚪ <strong>No CSV Loaded</strong>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 0.7rem; color: #94a3b8;">
            <strong>Observational Support Prototype:</strong><br/>
            Decision-support prototype. Final clinical decisions belong to authorized human staff. Never autonomously diagnoses or prescribes.
        </div>
    """, unsafe_allow_html=True)

# Main Page Routing with Dual-Layer RBAC Check
page = st.session_state.active_page
current_role = get_current_user_role()

if not can_access_page(current_role, page):
    render_403_unauthorized(f"the {page} page")
else:
    if page == "Dashboard":
        render_dashboard()
    elif page == "Upload Data":
        render_upload_page()
    elif page == "Patients":
        render_patients_page()
    elif page == "Alerts":
        render_alerts_page()
    elif page == "Evidence":
        render_evidence_page()
    elif page == "Experiment & Evaluation":
        render_experiment_page()

