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
    """Returns HTML badge for data freshness (0-1d Fresh, 2-3d Aging, 4+d Stale, No Data)."""
    if days is None or days < 0 or days >= 900 or freshness == "No Data":
        return '<span style="color: #64748b; font-weight: 700; font-size: 0.8rem;">⚪ No Data</span>'
    elif freshness == "Fresh" or days <= 1:
        return f'<span style="color: #16a34a; font-weight: 700; font-size: 0.8rem;">🟢 Fresh ({days}d ago)</span>'
    elif freshness == "Aging" or days <= 3:
        return f'<span style="color: #d97706; font-weight: 700; font-size: 0.8rem;">🟡 Aging ({days}d ago)</span>'
    elif freshness == "Stale" or days <= 7:
        return f'<span style="color: #dc2626; font-weight: 700; font-size: 0.8rem;">🔴 Stale ({days}d ago)</span>'
    else:
        return f'<span style="color: #991b1b; font-weight: 700; font-size: 0.8rem;">🚨 Very Stale ({days}d ago)</span>'

def get_confidence_badge_html(confidence: str, score: float = None) -> str:
    """Returns HTML badge for uncertainty level and confidence percentage."""
    score_str = f" ({score:.0f}%)" if score is not None else ""
    if confidence == "Good Confidence":
        return f'<span style="background: #f0fdf4; color: #16a34a; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Good Confidence{score_str}</span>'
    elif confidence == "Limited Confidence":
        return f'<span style="background: #fffbe6; color: #d97706; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Limited Confidence{score_str}</span>'
    else:
        return f'<span style="background: #fef2f2; color: #dc2626; padding: 3px 8px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Insufficient Data{score_str}</span>'

def render_decline_score_explanation():
    """Renders expandable UI section explaining the Functional Decline Score formulation."""
    with st.expander("❓ How is the Functional Decline Score calculated?", expanded=False):
        st.markdown("""
        ### Functional Decline Score & Data Quality Formulation

        The **Functional Decline Score (0–100)** is an observational trend signal comparing a patient's **recent 7-day average** against their **14-day historical baseline**.

        #### 🔄 1. Pipeline Flow
        `Baseline Period (14d)` → `Recent Period (7d)` → `Metric-level Changes (%)` → `Weighted Score (0-100)` → `Data Quality Adjustment` → `Review Signal`

        ---

        #### 📐 2. Mathematical / Heuristic Weighting
        Individual domain drops ($\Delta\% = \\frac{\\text{Recent} - \\text{Baseline}}{\\text{Baseline}} \\times 100$) contribute to the total score:

        - **Mobility Decrease** ($\Delta\% < 0$): $\min(|\Delta\%| \\times 1.2, 30.0\\text{ pts})$
        - **Nutrition Intake Decrease** ($\Delta\% < 0$): $\min(|\Delta\%| \\times 0.8, 25.0\\text{ pts})$
        - **Social Participation Drop** ($\Delta\% < 0$): $\min(|\Delta\%| \\times 0.7, 20.0\\text{ pts})$
        - **Daily Activity Drop** ($\Delta\% < 0$): $\min(|\Delta\%| \\times 0.5, 15.0\\text{ pts})$
        - **Safety/Fall Incidents**: $15.0\\text{ pts per recent incident}$ ($\max 30.0\\text{ pts}$)
        - **Data Freshness Adjustment**: $+8.0\\text{ pts}$ if Stale (4–7d), $+15.0\\text{ pts}$ if Very Stale (>7d)

        $$\\text{Final Score} = \\min(\\max(\\sum \\text{Points}, 0.0), 100.0)$$

        ---

        #### 📊 3. Classification Thresholds
        - **🚨 Urgent Review**: Score $\\ge 60.0$ or $\\ge 2$ core domain drops / $\\ge 1$ safety incident
        - **⚠️ Needs Review**: Score $30.0 – 59.9$ or $1$ core domain drop
        - **✅ Doing Well**: Score $< 30.0$ with stable core metrics
        - **⚠️ Missing Information**: Core domains missing or $< 4$ total observation days
        - **⏳ Data May Be Old**: Latest observation record $> 7$ days old

        ---

        #### 🛡️ 4. Data Confidence & Quality Factor
        $$\\text{Data Confidence Score (\\%)} = \\text{Completeness} \\times \\text{Freshness Factor} \\times \\text{Continuity Factor} \\times \\text{History Factor} \\times 100$$

        - **Freshness States**: 🟢 **Fresh** (0–1d, 1.0) | 🟡 **Aging** (2–3d, 0.85) | 🔴 **Stale** (4–7d, 0.50) | 🚨 **Very Stale** (>7d, 0.20)
        - **Observation Gap Warning**: Triggered if a $\\ge 3$-day gap occurs in daily logs ($\times 0.75$).
        - **Insufficient History**: $< 4$ total observations halts score calculation to avoid misleading signals.

        ---

        > ⚠️ **Clinical Decision Support Boundary**:
        > CARE PULSE is purely an observational decision-support tool. It identifies longitudinal functional trends to assist authorized human staff. It **never** provides autonomous medical diagnoses, disease predictions, or treatment prescriptions.
        """, unsafe_allow_html=True)

