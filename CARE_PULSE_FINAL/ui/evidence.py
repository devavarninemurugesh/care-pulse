"""
Explainable Evidence & Data Freshness View for CARE PULSE.
Provides detailed 14d vs 7d domain trend evidence, supporting activity & incident context,
freshness status, and uncertainty confidence levels.
"""

import streamlit as st
from security import get_current_user_info, filter_authorized_patients
from ui.components import (
    render_header,
    render_disclaimer,
    get_risk_badge_html,
    get_freshness_badge_html,
    get_confidence_badge_html
)

def render_evidence_page():
    render_header("Evidence & Data Freshness", "Explainable justification and signal freshness for patient decline risk.")
    render_disclaimer()

    processed_data = st.session_state.get("processed_data")
    if not processed_data or not processed_data.get("patient_summaries"):
        st.info("No dataset available. Please upload data on the Upload Data page.")
        return

    user_info = get_current_user_info()
    all_summaries = processed_data["patient_summaries"]

    target_summaries = all_summaries
    if not target_summaries:
        st.warning("No patient records available in dataset.")
        return

    patient_ids = [p["patient_id"] for p in target_summaries]

    # Pre-selection from Dashboard drill-down button
    pre_selected = st.session_state.get("selected_patient_id")
    default_idx = 0
    if pre_selected and pre_selected in patient_ids:
        default_idx = patient_ids.index(pre_selected)

    selected_pid = st.selectbox("🔍 Select Patient for Evidence Breakdown", patient_ids, index=default_idx)
    st.session_state["selected_patient_id"] = selected_pid

    p = next((item for item in target_summaries if item["patient_id"] == selected_pid), None)
    if not p:
        st.warning("Selected patient evidence not found.")
        return

    st.markdown("---")

    # 1. Flag Summary Banner
    col_a, col_b = st.columns([1.8, 1.2])

    with col_a:
        st.markdown(f"### Why was Patient `{p['patient_id']}` Flagged?")
        st.markdown(f"**CARE PULSE Signal:** {get_risk_badge_html(p['risk_category'])}", unsafe_allow_html=True)
        st.markdown(f"**Single-Metric Baseline:** `{p['baseline_status']}` ({p['baseline_trigger_reason']})")
        st.markdown(f"**Functional Decline Score:** **{p['decline_score']} / 100**")

    with col_b:
        st.markdown("#### ⏳ Freshness & Uncertainty")
        st.markdown(f"**Freshness Status:** {get_freshness_badge_html(p['freshness'], p['days_since_last'])}", unsafe_allow_html=True)
        st.markdown(f"**Confidence Level:** {get_confidence_badge_html(p['confidence_level'])}", unsafe_allow_html=True)
        st.markdown(f"**Reason:** {p['confidence_reason']}")

    st.markdown("---")

    # 2. Domain Trend Evidence (14d vs 7d)
    st.markdown("### 📊 Primary Domain Comparison (14-Day Baseline vs 7-Day Average)")

    trends = p.get("trends", {})
    t_cols = st.columns(3)

    primary_domains = [
        ("mobility", "Mobility (0-10)"),
        ("nutrition", "Nutrition (0-100)"),
        ("participation", "Participation (0-10)")
    ]

    for idx, (dom_key, dom_label) in enumerate(primary_domains):
        d_info = trends.get(dom_key, {})
        with t_cols[idx]:
            recent = d_info.get("recent_avg", "N/A")
            baseline = d_info.get("baseline_avg", "N/A")
            pct = d_info.get("pct_change", 0.0)
            
            st.metric(
                label=dom_label,
                value=f"{recent}" if recent is not None else "Missing",
                delta=f"{pct}% vs 14d baseline ({baseline})" if recent is not None else "Missing Data",
                delta_color="inverse" if pct < 0 else "normal"
            )

    st.markdown("---")

    # 3. Supporting Context (Activity & Incidents)
    st.markdown("### 📋 Supporting Context (Activity & Incident History)")
    col_sup1, col_sup2 = st.columns(2)

    with col_sup1:
        act_info = trends.get("activity", {})
        act_recent = act_info.get('recent_avg')
        act_base = act_info.get('baseline_avg')
        st.write(f"**Daily Activity Level:** 7d avg `{act_recent if act_recent is not None else 'N/A'}` vs 14d baseline `{act_base if act_base is not None else 'N/A'}` ({act_info.get('direction', '→ Stable')})")

    with col_sup2:
        st.write(f"**Safety Incidents:** `{p['recent_incidents']}` recent incident(s) in 7d window ({p['total_incidents']} total)")

    st.markdown("---")

    # 4. Data Quality & Uncertainty Communication
    st.markdown("### 🛡️ Data Quality & Uncertainty Assessment")
    
    dq_col1, dq_col2 = st.columns(2)
    with dq_col1:
        st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">Signal Freshness & Completeness</div>
                <div style="font-size: 0.88rem; color: #334155;">
                    • <strong>Days Elapsed:</strong> {p['days_since_last']} day(s) since last observation record.<br/>
                    • <strong>Freshness Rating:</strong> {p['freshness']}<br/>
                    • <strong>Total Records Logged:</strong> {p['total_records']} daily entries.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with dq_col2:
        st.markdown(f"""
            <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px;">
                <div style="font-weight: 700; color: #0f172a; margin-bottom: 6px;">Clinical Staff Action Guidance</div>
                <div style="font-size: 0.88rem; color: #334155;">
                    • <strong>Confidence Rating:</strong> {p['confidence_level']}<br/>
                    • <strong>Explanation:</strong> {p['confidence_reason']}<br/>
                    • <strong>Recommendation:</strong> Requires human review. Fresh caregiver observation recommended if data is stale.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 5. Signal Checklist
    st.markdown("### 🔍 Detailed Signal Evidence Checklist")
    for factor in p["contributing_factors"]:
        st.markdown(f"✓ **{factor}**")

