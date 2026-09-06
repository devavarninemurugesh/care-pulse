"""
Patient Detail View for CARE PULSE.
Provides deep-dive patient trajectory analytics, 14d vs 7d trend breakdown, Plotly graphs, and observation logs.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from security import get_current_user_info, filter_authorized_patients, can_access_patient
from ui.components import (
    render_header,
    render_disclaimer,
    get_risk_badge_html,
    get_freshness_badge_html,
    get_confidence_badge_html
)

def render_patients_page():
    render_header("Patient Detail Analysis", "Deep-dive trajectory, vital trends, and evidence for individual patients.")
    render_disclaimer()

    processed_data = st.session_state.get("processed_data")
    if not processed_data or not processed_data.get("patient_summaries"):
        st.info("No patient data available. Please load a dataset on the Upload Data page.")
        return

    user_info = get_current_user_info()
    all_summaries = processed_data["patient_summaries"]
    df = processed_data["df"]

    target_summaries = all_summaries
    if not target_summaries:
        st.warning("No patient records available in dataset.")
        return

    patient_ids = [p["patient_id"] for p in target_summaries]

    # Handle pre-selected patient from Dashboard drill-down
    pre_selected = st.session_state.get("selected_patient_id")
    default_idx = 0
    if pre_selected and pre_selected in patient_ids:
        default_idx = patient_ids.index(pre_selected)

    selected_pid = st.selectbox("👤 Select Patient ID", patient_ids, index=default_idx)
    st.session_state["selected_patient_id"] = selected_pid

    patient_info = next((p for p in target_summaries if p["patient_id"] == selected_pid), None)
    if not patient_info:
        st.warning("Selected patient not found.")
        return

    # Filter patient DataFrame
    patient_obs = df[df["patient_id"] == selected_pid].sort_values("date").reset_index(drop=True)

    # 1. Current Status Overview Header
    st.markdown("---")
    col1, col2, col3 = st.columns([1.2, 1.2, 1.6])

    with col1:
        st.markdown(f"### Patient `{selected_pid}`")
        st.markdown(f"**CARE PULSE Signal:** {get_risk_badge_html(patient_info['risk_category'])}", unsafe_allow_html=True)
        st.markdown(f"**Freshness:** {get_freshness_badge_html(patient_info['freshness'], patient_info['days_since_last'])}", unsafe_allow_html=True)
        st.markdown(f"**Confidence:** {get_confidence_badge_html(patient_info['confidence_level'])}", unsafe_allow_html=True)

    with col2:
        score = patient_info['decline_score']
        st.metric("Functional Decline Score", f"{score} / 100", delta=patient_info['overall_trend'], delta_color="inverse" if "Declining" in patient_info['overall_trend'] else "normal")
        st.write(f"**Single Baseline:** `{patient_info['baseline_status']}`")

    with col3:
        st.markdown("#### Primary Domains (14d vs 7d)")
        trends = patient_info["trends"]
        m1, m2 = st.columns(2)
        with m1:
            st.write(f"Mobility: **{trends.get('mobility', {}).get('direction', '→ Stable')}**")
            st.write(f"Nutrition: **{trends.get('nutrition', {}).get('direction', '→ Stable')}**")
        with m2:
            st.write(f"Participation: **{trends.get('participation', {}).get('direction', '→ Stable')}**")
            st.write(f"Activity (sup): **{trends.get('activity', {}).get('direction', '→ Stable')}**")

    st.markdown("---")

    # 2. Plotly Interactive Trend Graphs
    st.markdown("### 📈 Functional Domain Trajectory Over Time")
    
    if not patient_obs.empty:
        fig = go.Figure()
        
        if "mobility" in patient_obs.columns:
            fig.add_trace(go.Scatter(x=patient_obs["date"], y=patient_obs["mobility"], mode="lines+markers", name="Mobility (0-10)"))
        if "activity" in patient_obs.columns:
            fig.add_trace(go.Scatter(x=patient_obs["date"], y=patient_obs["activity"], mode="lines+markers", name="Activity (0-10)"))
        if "participation" in patient_obs.columns:
            fig.add_trace(go.Scatter(x=patient_obs["date"], y=patient_obs["participation"], mode="lines+markers", name="Participation (0-10)"))
        if "nutrition" in patient_obs.columns:
            fig.add_trace(go.Scatter(x=patient_obs["date"], y=patient_obs["nutrition"] / 10.0, mode="lines+markers", name="Nutrition (/10)"))

        fig.update_layout(
            title=f"Observation Trajectory History for Patient {selected_pid}",
            xaxis_title="Observation Date",
            yaxis_title="Domain Score / Level",
            yaxis=dict(range=[0, 10.5]),
            hovermode="x unified",
            height=380,
            margin=dict(t=40, b=30, l=30, r=30)
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 3. Recent Observations Log Table
    st.markdown("### 📝 Daily Observation History Log")
    if not patient_obs.empty:
        disp_cols = [c for c in ["date", "mobility", "nutrition", "participation", "activity", "incident", "notes"] if c in patient_obs.columns]
        recent_records = patient_obs.sort_values("date", ascending=False)
        st.dataframe(recent_records[disp_cols], use_container_width=True, hide_index=True)

