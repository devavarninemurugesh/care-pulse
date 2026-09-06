import os
import pandas as pd
import streamlit as st
from utils.validation import validate_csv_dataframe, REQUIRED_COLUMNS
from analysis.data_cleaning import clean_and_inspect_dataframe
from analysis.pipeline import process_dataset
from ui.components import render_header, render_disclaimer

def render_upload_page():
    render_header("Upload Patient Data", "Upload one CSV file. CARE PULSE validates and analyzes it directly in memory.")
    render_disclaimer()

    # Format guidance matching reference design
    st.markdown("### CSV format")
    st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 12px 16px; border-radius: 8px; font-family: monospace; font-size: 0.9rem; color: #1e293b; margin-bottom: 8px;">
            patient_id,date,mobility,nutrition,participation,activity,incident,notes
        </div>
        <div style="font-size: 0.82rem; color: #64748b; margin-bottom: 20px;">
            Mobility and participation: 0–10 · Nutrition: 0–100 · Activity: 0–10 · Incident: Yes/No or 0/1
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], label_visibility="collapsed")

    # Read & process uploaded file directly
    if uploaded_file is not None:
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_uploaded_file_key") != file_key:
            try:
                raw_df = pd.read_csv(uploaded_file)
                is_valid, summary = validate_csv_dataframe(raw_df)

                if is_valid:
                    cleaned_df, rejected_df, stats = clean_and_inspect_dataframe(raw_df)
                    processed = process_dataset(cleaned_df)

                    st.session_state["raw_csv_df"] = raw_df
                    st.session_state["cleaned_df"] = cleaned_df
                    st.session_state["rejected_df"] = rejected_df
                    st.session_state["clean_stats"] = stats
                    st.session_state["processed_data"] = processed
                    st.session_state["last_file_name"] = uploaded_file.name
                    st.session_state["last_uploaded_file_key"] = file_key
                    st.session_state["is_custom_upload"] = True
                    st.session_state["validation_summary"] = summary
                else:
                    st.error("❌ Schema Validation Failed")
                    if summary["errors"]:
                        for err in summary["errors"]:
                            st.error(f"• {err}")
            except Exception as e:
                st.error(f"Failed to read CSV file: {str(e)}")

    # Render metrics and readiness status if dataset is loaded
    if st.session_state.get("clean_stats") and st.session_state.get("processed_data"):
        stats = st.session_state["clean_stats"]
        processed = st.session_state["processed_data"]
        metrics = processed["metrics"]
        file_name = st.session_state.get("last_file_name", "Uploaded CSV")

        st.markdown("<br/>", unsafe_allow_html=True)

        # 4 Key Metrics Cards (Rows, Valid, Rejected, Patients)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: left;">
                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Rows</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a;">{stats['total_rows']:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: left;">
                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Valid</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a;">{stats['valid_rows']:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: left;">
                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Rejected</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a;">{stats['rejected_rows']:,}</div>
                </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; text-align: left;">
                    <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Patients</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: #0f172a;">{stats['total_patients']:,}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        # Expander for view rejected rows
        with st.expander("› View rejected rows"):
            rejected_df = st.session_state.get("rejected_df")
            if rejected_df is not None and not rejected_df.empty:
                st.markdown(f"**{len(rejected_df):,} rows were rejected during validation/cleaning:**")
                st.dataframe(rejected_df, use_container_width=True)
            else:
                st.info("✓ No rejected rows found. All records passed validation!")

        # Success Banner
        st.markdown(f"""
            <div style="background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; padding: 14px 18px; border-radius: 8px; font-weight: 600; font-size: 0.95rem; margin-top: 16px; margin-bottom: 20px;">
                ✓ <strong>{file_name}</strong> is ready for analysis. (Date Range: {metrics['date_range']})
            </div>
        """, unsafe_allow_html=True)

        # Open Dashboard button
        col_b1, col_b2 = st.columns([1.5, 3])
        with col_b1:
            if st.button("Open Dashboard", type="primary", use_container_width=True):
                st.session_state["active_page"] = "Dashboard"
                st.rerun()

        if st.session_state.get("is_custom_upload"):
            with col_b2:
                if st.button("🔄 Reset to Default Sample Data"):
                    app_dir = os.path.dirname(os.path.dirname(__file__))
                    LOCAL_10_CSV = os.path.join(app_dir, "sample_10_patients.csv")
                    if os.path.exists(LOCAL_10_CSV):
                        df_local = pd.read_csv(LOCAL_10_CSV)
                        st.session_state["raw_csv_df"] = df_local
                        c_df, r_df, st_map = clean_and_inspect_dataframe(df_local)
                        st.session_state["cleaned_df"] = c_df
                        st.session_state["rejected_df"] = r_df
                        st.session_state["clean_stats"] = st_map
                        st.session_state["processed_data"] = process_dataset(c_df)
                        st.session_state["last_file_name"] = os.path.basename(LOCAL_10_CSV)
                        st.session_state["is_custom_upload"] = False
                        st.session_state.pop("last_uploaded_file_key", None)
                        st.rerun()

