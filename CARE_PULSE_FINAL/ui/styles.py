"""
Modern visual styling and custom CSS for CARE PULSE UI.
"""

import streamlit as st

def apply_custom_styles():
    """
    Injects custom CSS for clean, professional modern visual styling.
    """
    st.markdown("""
        <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #0f172a;
        }

        /* Main Container Background */
        .stApp {
            background-color: #f8fafc;
        }

        /* Metric Card Styles */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .metric-card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .metric-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 4px;
        }
        .metric-sub {
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 2px;
        }

        /* Risk Badges */
        .badge-urgent {
            background-color: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }
        .badge-needs {
            background-color: #fffbebf;
            color: #d97706;
            border: 1px solid #fef3c7;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }
        .badge-well {
            background-color: #f0fdf4;
            color: #16a34a;
            border: 1px solid #bbf7d0;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-block;
        }
        .badge-stale {
            background-color: #f3f4f6;
            color: #6b7280;
            border: 1px solid #e5e7eb;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.75rem;
            display: inline-block;
        }

        /* Header Section */
        .app-header {
            margin-bottom: 24px;
        }
        .app-title {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.025em;
        }
        .app-subtitle {
            font-size: 0.95rem;
            color: #64748b;
            margin-top: 2px;
        }

        /* Decision Banner Disclaimer */
        .disclaimer-box {
            background-color: #eff6ff;
            border-left: 4px solid #2563eb;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 0.82rem;
            color: #1e40af;
            margin-bottom: 20px;
        }

        /* Patient Detail Cards */
        .detail-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
