"""
Alerts & Flagged Patients View for CARE PULSE.
Provides categorized early decline alerts, scores, trends, key reasons, and freshness indicators.
"""

import streamlit as st
from ui.components import (
    render_header,
    render_disclaimer,
    get_risk_badge_html,
    get_freshness_badge_html,
    get_confidence_badge_html
)

def render_alerts_page():
    render_header("Decline Risk Alerts", "Prioritized signals for patients requiring staff review.")
    render_disclaimer()

    processed_data = st.session_state.get("processed_data")
    if not processed_data or not processed_data.get("patient_summaries"):
        st.info("No dataset available. Please upload data on the Upload Data page.")
        return

    patient_summaries = processed_data["patient_summaries"]

    urgent_patients = [p for p in patient_summaries if p["risk_category"] == "Urgent Review"]
    needs_patients = [p for p in patient_summaries if p["risk_category"] == "Needs Review"]
    well_patients = [p for p in patient_summaries if p["risk_category"] == "Doing Well"]
    missing_stale = [p for p in patient_summaries if p["risk_category"] in ["Missing Information", "Data May Be Old"]]

    tab1, tab2, tab3, tab4 = st.tabs([
        f"🚨 Urgent Review ({len(urgent_patients)})",
        f"⚠️ Needs Review ({len(needs_patients)})",
        f"✅ Doing Well ({len(well_patients)})",
        f"⏳ Missing / Stale ({len(missing_stale)})"
    ])

    def _render_alert_list(patients_list, alert_type="urgent"):
        if not patients_list:
            st.info("No patient records in this category.")
            return

        for p in patients_list:
            with st.container():
                border_color = '#dc2626' if alert_type=='urgent' else ('#d97706' if alert_type=='needs' else ('#16a34a' if alert_type=='well' else '#94a3b8'))
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-left: 5px solid {border_color}; padding: 16px 20px; border-radius: 8px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">Patient {p['patient_id']}</span>
                                &nbsp;&nbsp; {get_risk_badge_html(p['risk_category'])}
                                &nbsp;&nbsp; {get_freshness_badge_html(p['freshness'], p['days_since_last'])}
                                &nbsp;&nbsp; {get_confidence_badge_html(p['confidence_level'])}
                            </div>
                            <div style="text-align: right;">
                                <span style="font-size: 1.25rem; font-weight: 800; color: #0f172a;">{p['decline_score']} / 100</span>
                                <div style="font-size: 0.78rem; color: #64748b;">Decline Score</div>
                            </div>
                        </div>
                        <div style="margin-top: 10px; font-size: 0.88rem; color: #334155;">
                            <strong>Primary Signal Factors (14d vs 7d):</strong>
                            <ul style="margin-top: 4px; margin-bottom: 4px; padding-left: 20px;">
                                {''.join(f'<li>{factor}</li>' for factor in p['contributing_factors'])}
                            </ul>
                        </div>
                        <div style="font-size: 0.78rem; color: #64748b; margin-top: 6px;">
                            Last Observation: <strong>{p['latest_date']}</strong> &bull; Single Baseline Status: <strong>{p['baseline_status']}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with tab1:
        _render_alert_list(urgent_patients, "urgent")

    with tab2:
        _render_alert_list(needs_patients, "needs")

    with tab3:
        _render_alert_list(well_patients, "well")

    with tab4:
        _render_alert_list(missing_stale, "stale")
