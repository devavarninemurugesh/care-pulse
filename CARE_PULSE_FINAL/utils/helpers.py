import streamlit as st
from typing import Dict, Any, Optional

def apply_custom_css():
    """Injects modern, clean healthcare CSS styling into Streamlit."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

            /* Global Clean Layout */
            html, body, [class*="css"], .stApp {
                font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
                background-color: #f8fafc;
                color: #0f172a;
            }

            /* Header titles */
            .header-title {
                color: #0f172a;
                font-weight: 800;
                font-size: 2.1rem;
                letter-spacing: -0.025em;
                margin-bottom: 0.2rem;
            }

            .header-subtitle {
                color: #64748b;
                font-size: 1rem;
                font-weight: 500;
                margin-bottom: 1.5rem;
            }

            /* Simple & Clean Card */
            .care-card {
                background: #ffffff;
                border-radius: 14px;
                padding: 1.2rem 1.4rem;
                box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
                border: 1px solid #e2e8f0;
                margin-bottom: 1rem;
            }

            /* Status Badges */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 0.35rem 0.85rem;
                border-radius: 9999px;
                font-weight: 700;
                font-size: 0.84rem;
            }

            .badge-doing-well { background: #dcfce7; color: #15803d; }
            .badge-needs-review { background: #ffedd5; color: #9a3412; }
            .badge-urgent-review { background: #fee2e2; color: #b91c1c; }
            .badge-missing-info { background: #fef9c3; color: #854d0e; }
            .badge-data-old { background: #f1f5f9; color: #475569; }

            /* Simple Disclaimer Banner */
            .disclaimer-card {
                background: #eff6ff;
                border-left: 4px solid #2563eb;
                padding: 0.85rem 1.1rem;
                border-radius: 10px;
                color: #1e40af;
                font-size: 0.88rem;
                font-weight: 500;
                margin-top: 0.75rem;
                margin-bottom: 1.25rem;
            }

            /* Sidebar Styling */
            section[data-testid="stSidebar"] {
                background-color: #ffffff !important;
                border-right: 1px solid #e2e8f0;
            }

            /* User Profile Card */
            .user-profile-card {
                background: #ffffff;
                border-radius: 14px;
                padding: 1rem;
                color: #0f172a;
                box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
                border: 1px solid #e2e8f0;
                margin-bottom: 1rem;
            }

            .user-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #2563eb;
                color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                font-size: 1rem;
            }

            .role-pill {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 9999px;
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                margin-top: 2px;
            }

            .role-caregiver { background: #dcfce7; color: #15803d; }
            .role-supervisor { background: #e0f2fe; color: #0369a1; }
            .role-staff { background: #fef3c7; color: #b45309; }
            .role-admin { background: #fee2e2; color: #b91c1c; }

            /* Aligned Sidebar Radio Navigation */
            div[data-testid="stRadio"] > label {
                font-weight: 800 !important;
                color: #64748b !important;
                font-size: 0.78rem !important;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
                display: block;
            }

            /* Hide radio circles in sidebar navigation */
            section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
                display: none !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"] label {
                background: transparent !important;
                border-radius: 10px !important;
                padding: 9px 12px !important;
                margin-bottom: 3px !important;
                border: 1px solid transparent !important;
                transition: all 0.15s ease !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                color: #475569 !important;
                display: flex !important;
                align-items: center !important;
                cursor: pointer !important;
                width: 100% !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
                background: #f1f5f9 !important;
                color: #0f172a !important;
            }

            /* Active Selected Navigation Item */
            section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"],
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
                background: #2563eb !important;
                color: #ffffff !important;
                font-weight: 700 !important;
            }

            section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p,
            section[data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] span,
            section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
                color: #ffffff !important;
            }
        </style>
    """, unsafe_allow_html=True)


def render_status_badge(status_label: str, status_icon: str) -> str:
    """Returns simple HTML for a status badge."""
    css_class = "badge-doing-well"
    if "Urgent" in status_label:
        css_class = "badge-urgent-review"
    elif "Needs" in status_label or "Change" in status_label:
        css_class = "badge-needs-review"
    elif "Missing" in status_label:
        css_class = "badge-missing-info"
    elif "Old" in status_label:
        css_class = "badge-data-old"

    return f'<span class="status-badge {css_class}">{status_icon} {status_label}</span>'


def init_session_state():
    """Initializes Streamlit session state for role-based authentication."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.full_name = None
        st.session_state.selected_patient_id = "P001"


def login_user(username: str, role: str, full_name: str, user_id: str):
    """Sets session state on successful login."""
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.full_name = full_name
    st.session_state.user_id = user_id


def logout_user():
    """Resets session state on logout."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.full_name = None
    st.session_state.user_id = None
