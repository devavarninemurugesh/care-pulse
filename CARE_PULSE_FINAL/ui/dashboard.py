"""
Main Executive Dashboard View for CARE PULSE.
Displays dataset summary KPIs, functional status breakdown, daily patient trajectory graph, patient trend matrix, and Plotly analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from security import get_current_user_info, filter_authorized_patients
from ui.components import (
    render_header,
    render_disclaimer,
    get_risk_badge_html,
    get_freshness_badge_html,
    get_confidence_badge_html,
    render_decline_score_explanation
)

def render_dashboard():
    user_info = get_current_user_info()
    role_title = f"{user_info['role']} Monitoring Dashboard"
    render_header("CARE PULSE", role_title)
    render_disclaimer()
    render_decline_score_explanation()

    processed_data = st.session_state.get("processed_data")
    if not processed_data or not processed_data.get("patient_summaries"):
        st.markdown("""
            <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 40px; text-align: center; margin-top: 20px;">
                <div style="font-size: 3rem; margin-bottom: 12px;">📤</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #0f172a; margin-bottom: 8px;">No CSV Dataset Analyzed Yet</div>
                <div style="color: #64748b; font-size: 0.95rem; margin-bottom: 24px; max-width: 500px; margin-left: auto; margin-right: auto;">
                    Upload your daily observation CSV file on the Upload Data page to begin early decline analysis, risk scoring, and evidence evaluation.
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        if user_info["role"] in ["Authorized Staff", "Admin"]:
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1])
            with col_btn2:
                if st.button("📤 Go to Upload Data Page", type="primary", use_container_width=True):
                    st.session_state["active_page"] = "Upload Data"
                    st.rerun()
        return

    all_patient_summaries = processed_data["patient_summaries"]
    patient_summaries = filter_authorized_patients(all_patient_summaries, user_info)
    df = processed_data["df"]

    total_assigned_patients = len(patient_summaries)
    total_all_patients = len(all_patient_summaries)
    urgent_count = sum(1 for p in all_patient_summaries if p.get("risk_category") == "Urgent Review")
    needs_count = sum(1 for p in all_patient_summaries if p.get("risk_category") == "Needs Review")
    well_count = sum(1 for p in all_patient_summaries if p.get("risk_category") == "Doing Well")
    stale_count = sum(1 for p in all_patient_summaries if p.get("freshness") in ["Stale", "Very Stale"])

    date_range = processed_data["metrics"].get("date_range", "N/A")

    # User Profile Scope Banner
    st.markdown(f"""
        <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 10px 16px; border-radius: 6px; font-size: 0.85rem; color: #334155; margin-bottom: 16px;">
            <strong>Logged-in Profile:</strong> {user_info['name']} ({user_info['role']}) &nbsp;|&nbsp; <strong>Scope:</strong> Access to all {total_all_patients} dataset patients
        </div>
    """, unsafe_allow_html=True)

    # 1. KPI Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Patients", f"{total_all_patients:,}", delta=f"{date_range}")
    with c2:
        st.metric("✅ Doing Well", f"{well_count:,}")
    with c3:
        st.metric("⚠️ Needs Review", f"{needs_count:,}", delta_color="off")
    with c4:
        st.metric("🚨 Urgent Review", f"{urgent_count:,}", delta_color="inverse")

    st.markdown("---")

    # 2. Risk Distribution & Analytics Charts (Plotly)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 📊 Functional Status Breakdown")
        status_counts = {
            "Doing Well": well_count,
            "Needs Review": needs_count,
            "Urgent Review": urgent_count,
            "Stale / Old Data": stale_count
        }
        df_status = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])

        fig_pie = px.pie(
            df_status,
            names="Status",
            values="Count",
            color="Status",
            color_discrete_map={
                "Doing Well": "#16a34a",
                "Needs Review": "#d97706",
                "Urgent Review": "#dc2626",
                "Stale / Old Data": "#94a3b8"
            },
            hole=0.4
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("### 📈 Top Decline Risk Patients")
        top_risk = all_patient_summaries[:10]
        if top_risk:
            df_top = pd.DataFrame([
                {
                    "Patient ID": p["patient_id"],
                    "Decline Score": p["decline_score"],
                    "Risk Category": p["risk_category"]
                }
                for p in top_risk
            ])

            fig_bar = px.bar(
                df_top,
                x="Patient ID",
                y="Decline Score",
                color="Risk Category",
                color_discrete_map={
                    "Doing Well": "#16a34a",
                    "Needs Review": "#d97706",
                    "Urgent Review": "#dc2626",
                    "Missing Information": "#f59e0b",
                    "Data May Be Old": "#94a3b8"
                },
                text="Decline Score"
            )
            fig_bar.update_layout(yaxis=dict(range=[0, 100]), margin=dict(t=20, b=20, l=20, r=20), height=280)
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # 3. Interactive Daily Patient Observation Trajectory Graph
    st.markdown("### 📈 Daily Patient Observation Trajectory Graph")
    st.write("Select any patient from the dataset to plot their daily longitudinal observation history across Mobility, Activity, Participation, and Nutrition.")
    
    all_pids = [p["patient_id"] for p in all_patient_summaries]
    curr_sel = st.session_state.get("selected_patient_id")
    sel_idx = all_pids.index(curr_sel) if curr_sel in all_pids else 0

    col_graph_sel, _ = st.columns([2, 2])
    with col_graph_sel:
        graph_pid = st.selectbox("👤 Select Patient ID to Plot Daily Graph", all_pids, index=sel_idx, key="dashboard_graph_pid")
        st.session_state["selected_patient_id"] = graph_pid

    p_obs = df[df["patient_id"] == graph_pid].sort_values("date").reset_index(drop=True)
    if not p_obs.empty:
        fig_traj = go.Figure()
        if "mobility" in p_obs.columns:
            fig_traj.add_trace(go.Scatter(x=p_obs["date"], y=p_obs["mobility"], mode="lines+markers", name="Mobility (0-10)", line=dict(width=3, color="#2563eb")))
        if "activity" in p_obs.columns:
            fig_traj.add_trace(go.Scatter(x=p_obs["date"], y=p_obs["activity"], mode="lines+markers", name="Activity (0-10)", line=dict(width=2, color="#059669")))
        if "participation" in p_obs.columns:
            fig_traj.add_trace(go.Scatter(x=p_obs["date"], y=p_obs["participation"], mode="lines+markers", name="Participation (0-10)", line=dict(width=2, color="#d97706")))
        if "nutrition" in p_obs.columns:
            fig_traj.add_trace(go.Scatter(x=p_obs["date"], y=p_obs["nutrition"] / 10.0, mode="lines+markers", name="Nutrition (/10)", line=dict(width=2, color="#7c3aed")))

        fig_traj.update_layout(
            title=f"Daily Functional Observation Trajectory for Patient {graph_pid}",
            xaxis_title="Observation Date",
            yaxis_title="Observation Score (0–10)",
            yaxis=dict(range=[0, 10.5]),
            hovermode="x unified",
            height=360,
            margin=dict(t=40, b=30, l=30, r=30)
        )
        st.plotly_chart(fig_traj, use_container_width=True)

    st.markdown("---")

    # 4. Interactive Patient Functional Trend Matrix with Scope Filter & Drill-down Actions
    st.markdown("### 👥 Patient Functional Trend Matrix")

    # Search & Status Filters
    col_f1, col_f2 = st.columns([2.5, 1.5])
    with col_f1:
        search_term = st.text_input("🔍 Search by Patient ID (e.g. P001, P015...)", "")
    with col_f2:
        risk_filter = st.selectbox("Filter by Status", ["All", "Urgent Review", "Needs Review", "Doing Well", "Missing Information", "Data May Be Old"])

    patient_pool = all_patient_summaries
    filtered_patients = patient_pool

    if search_term:
        filtered_patients = [p for p in filtered_patients if search_term.lower() in p["patient_id"].lower()]
    if risk_filter != "All":
        filtered_patients = [p for p in filtered_patients if p["risk_category"] == risk_filter]

    st.caption(f"Showing **{len(filtered_patients)}** of **{len(patient_pool)}** patients.")

    if not filtered_patients:
        st.info("No matching patient records found.")
        return

    # Render Patient Rows with View Evidence Action
    for p in filtered_patients:
        trends = p["trends"]
        score = p["decline_score"]
        conf_score = p.get("confidence_score", 100.0)
        border_color = '#dc2626' if p['risk_category']=='Urgent Review' else ('#d97706' if p['risk_category']=='Needs Review' else '#16a34a')

        # Stale / Gap warning HTML
        warning_html = ""
        if p.get("freshness") in ["Stale", "Very Stale"]:
            warning_html += f'<div style="background: #fef2f2; border-left: 3px solid #dc2626; color: #991b1b; padding: 6px 10px; border-radius: 4px; font-size: 0.78rem; margin-top: 8px;">⚠️ Observation data is several days old ({p["days_since_last"]}d ago). Trend interpretation confidence is reduced.</div>'
        if p.get("has_gap"):
            warning_html += f'<div style="background: #fffbe6; border-left: 3px solid #d97706; color: #92400e; padding: 6px 10px; border-radius: 4px; font-size: 0.78rem; margin-top: 6px;">{p.get("gap_warning")}</div>'

        # Why this signal factors
        factors_html = "".join([f'<li style="margin-bottom: 2px;">{f}</li>' for f in p.get("contributing_factors", [])])

        with st.container():
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-left: 5px solid {border_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <span style="font-size: 1.15rem; font-weight: 800; color: #0f172a;">Patient {p['patient_id']}</span> &nbsp;
                            {get_risk_badge_html(p['risk_category'])} &nbsp;
                            {get_freshness_badge_html(p['freshness'], p['days_since_last'])} &nbsp;
                            {get_confidence_badge_html(p['confidence_level'], conf_score)}
                        </div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #1e293b;">
                            Decline Score: <span style="font-size: 1.15rem; color: #2563eb;">{score} / 100</span>
                        </div>
                    </div>
                    {warning_html}
                    <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.82rem; color: #475569; flex-wrap: wrap;">
                        <div><strong>Last Obs:</strong> {p.get('latest_date', 'N/A')}</div>
                        <div><strong>Mobility (14d vs 7d):</strong> {trends.get('mobility', {}).get('direction', '→ Stable')}</div>
                        <div><strong>Nutrition:</strong> {trends.get('nutrition', {}).get('direction', '→ Stable')}</div>
                        <div><strong>Participation:</strong> {trends.get('participation', {}).get('direction', '→ Stable')}</div>
                        <div><strong>Activity:</strong> {trends.get('activity', {}).get('direction', '→ Stable')}</div>
                    </div>
                    <div style="margin-top: 8px; font-size: 0.8rem; color: #334155;">
                        <strong>Why this signal?</strong>
                        <ul style="margin: 4px 0 0 16px; padding: 0; color: #475569;">
                            {factors_html}
                        </ul>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_a1, col_a2 = st.columns([1, 4])
            with col_a1:
                if st.button(f"🔍 VIEW EVIDENCE", key=f"btn_ev_{p['patient_id']}", use_container_width=True):
                    st.session_state["selected_patient_id"] = p["patient_id"]
                    st.session_state["active_page"] = "Evidence"
                    st.rerun()
            st.markdown("<br/>", unsafe_allow_html=True)


