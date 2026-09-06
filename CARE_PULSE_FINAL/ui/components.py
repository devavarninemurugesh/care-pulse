"""
Reusable UI component functions for CARE PULSE.
"""

import streamlit as st

def render_header(title: str, subtitle: str):
    """Renders standardized application page header."""
    st.markdown(f"""
        <div class="app-header">
            <div class="app-title">{title}</div>
            <div class="app-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)

def render_disclaimer():
    """Renders non-medical decision support disclaimer."""
    st.markdown("""
        <div class="disclaimer-box">
            <strong>ℹ️ Clinical Decision Support Prototype:</strong>
            This tool evaluates functional trend signals for early decline detection.
            It does NOT provide medical diagnoses or treatment recommendations. Final clinical decisions belong to authorized human staff.
        </div>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, value: str, subtext: str = ""):
    """Renders a styled KPI metric card."""
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{subtext}</div>
        </div>
    """, unsafe_allow_html=True)

def get_risk_badge_html(risk_category: str) -> str:
    """Returns HTML for risk category badge."""
    if risk_category == "Urgent Review":
        return '<span class="badge-urgent">🚨 Urgent Review</span>'
    elif risk_category == "Needs Review":
        return '<span class="badge-needs">⚠️ Needs Review</span>'
    elif risk_category == "Missing Information":
        return '<span style="background: #fef3c7; color: #92400e; border: 1px solid #fde68a; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem; display: inline-block;">⚠️ Missing Information</span>'
    elif risk_category == "Data May Be Old":
        return '<span style="background: #f3f4f6; color: #4b5563; border: 1px solid #e5e7eb; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem; display: inline-block;">⏳ Data May Be Old</span>'
    else:
        return '<span class="badge-well">✅ Doing Well</span>'

def get_freshness_badge_html(freshness: str, days: int) -> str:
    """Returns HTML badge for data freshness."""
    if freshness == "Fresh":
        return f'<span style="color: #16a34a; font-weight: 700; font-size: 0.8rem;">🟢 Fresh ({days}d ago)</span>'
    elif freshness == "Stale":
        return f'<span style="color: #d97706; font-weight: 700; font-size: 0.8rem;">⚠️ Stale ({days}d ago)</span>'
    else:
        return f'<span style="color: #dc2626; font-weight: 700; font-size: 0.8rem;">🚨 Very Stale ({days}d ago)</span>'

def get_confidence_badge_html(confidence: str) -> str:
    """Returns HTML badge for uncertainty level."""
    if confidence == "Good Confidence":
        return '<span style="background: #f0fdf4; color: #16a34a; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Good Confidence</span>'
    elif confidence == "Limited Confidence":
        return '<span style="background: #fffbe6; color: #d97706; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Limited Confidence</span>'
    else:
        return '<span style="background: #fef2f2; color: #dc2626; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Insufficient Data</span>'
