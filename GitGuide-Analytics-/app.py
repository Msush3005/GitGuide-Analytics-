# -*- coding: utf-8 -*-
"""
GitGuide Analytics - Real-Time Dashboard & Alert System
Lesson 2.56: Alert Monitoring & Metric Threshold Detection

Features:
- Decoupled threshold configuration in alert_config.py
- Dynamic threshold evaluation on filtered_df
- Visual alerts via st.error (critical) and st.warning (warning)
- Reactive recalculation on filter changes
- Detailed plain-language risk descriptions and metric limits

Usage:
    streamlit run app.py
"""

import os
import sys
import io
import asyncio
from datetime import datetime, date
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Python 3.12+ / 3.13 asyncio fix for Windows
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

import streamlit as st

# Path setup
BASE_DIR    = os.path.abspath(os.path.dirname(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import threshold configuration engine (Task 3: Thresholds stored in config file)
from alert_config import ALERT_THRESHOLDS, check_alerts

# Page config
st.set_page_config(
    page_title="GitGuide Alert Monitoring & Real-Time Dashboard",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialise Session State (Lesson 2.54)
if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "computed_revenue" not in st.session_state:
    st.session_state["computed_revenue"] = 0.0
if "filter_date_start" not in st.session_state:
    st.session_state["filter_date_start"] = None

# Global CSS - dark glassmorphism design system
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 40%, #0f1b30 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1526 0%, #111827 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 22px 20px 18px 20px;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.glass-card:hover {
    border-color: rgba(139,92,246,0.55);
}
.card-icon  { font-size: 1.5rem; margin-bottom: 8px; display: block; }
.card-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.card-value { color: #f1f5f9; font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 4px 0 12px 0; }
.sidebar-logo-text {
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(99,102,241,0.18) !important; }
</style>
""", unsafe_allow_html=True)

# Plotly shared dark theme
_PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(255,255,255,0.02)",
    font=dict(family="Inter", color="#94a3b8", size=12),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(color="#64748b")),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False, tickfont=dict(color="#64748b")),
    margin=dict(t=42, b=32, l=16, r=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
    hoverlabel=dict(bgcolor="#1e293b", bordercolor="rgba(99,102,241,0.4)", font=dict(color="#e2e8f0")),
)

def plot_layout(title="", **overrides):
    layout = dict(_PLOTLY_BASE)
    layout["title"] = dict(text=title, font=dict(size=14, color="#e2e8f0"), x=0.01)
    layout.update(overrides)
    return layout

PLOTLY_LAYOUT = _PLOTLY_BASE
PALETTE = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899"]

@st.cache_data
def parse_uploaded_bytes(file_bytes, file_name):
    buffer = io.BytesIO(file_bytes)
    if file_name.endswith(".csv"):
        return pd.read_csv(buffer)
    elif file_name.endswith(".json"):
        return pd.read_json(buffer)
    else:
        raise ValueError("Unsupported file format")

@st.cache_data
def load_default_dataset():
    processed_path = os.path.join(BASE_DIR, "output", "processed.csv")
    raw_path       = os.path.join(BASE_DIR, "data", "raw", "sample.csv")
    if os.path.exists(processed_path):
        return pd.read_csv(processed_path)
    if os.path.exists(raw_path):
        return pd.read_csv(raw_path)
    np.random.seed(42)
    n = 25
    roles = ["Maintainer"] * 4 + ["Reviewer"] * 6 + ["Contributor"] * 15
    np.random.shuffle(roles)
    dates = pd.date_range("2026-01-01", periods=n, freq="2D")
    return pd.DataFrame({
        "contributor_id": range(101, 101 + n),
        "contributor_login": [f"user_{i:03d}" for i in range(101, 101 + n)],
        "repository_name": ["GitGuide-Analytics-"] * n,
        "commits_count": np.random.randint(1, 45, n),
        "pull_requests_opened": np.random.randint(0, 15, n),
        "total_contributions": np.random.randint(1, 60, n),
        "lines_changed": np.random.randint(20, 1500, n),
        "contributor_role": roles,
        "pr_review_days": np.round(np.random.uniform(0.4, 7.5, n), 2),
        "timestamp": dates.strftime("%Y-%m-%d"),
    })

def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            df = parse_uploaded_bytes(file_bytes, uploaded_file.name)
            if len(df) == 0:
                st.warning("Uploaded file is empty. Please check your data.")
                st.stop()
            st.success(f"Cached & Loaded: {uploaded_file.name} ({len(df):,} rows)")
            return df
        except Exception as e:
            st.error(f"Could not read file format. ({e})")
            st.stop()
    return None

# Task 1, 2, 4 & 5: Visual Alert Display Engine
def render_alert_banner(filtered_df):
    """
    Computes business metrics from filtered_df, checks them against ALERT_THRESHOLDS,
    and displays visual warnings at the top of the dashboard.
    """
    commit_col = next((c for c in ["commits_count", "commits", "total_contributions"] if c in filtered_df.columns), None)
    review_col = next((c for c in ["avg_pr_review_days", "pr_review_days", "review_days"] if c in filtered_df.columns), None)
    lines_col  = next((c for c in ["avg_lines_changed", "lines_changed", "lines"] if c in filtered_df.columns), None)

    single_pct = ((filtered_df[commit_col] == 1).mean() * 100) if commit_col and len(filtered_df) else 0.0
    avg_rev    = filtered_df[review_col].mean() if review_col and len(filtered_df) else 0.0
    avg_lines  = filtered_df[lines_col].mean() if lines_col and len(filtered_df) else 0.0
    total_cells = filtered_df.shape[0] * filtered_df.shape[1] if len(filtered_df) > 0 else 1
    null_pct   = (filtered_df.isnull().sum().sum() / total_cells) * 100

    current_metrics = {
        "single_commit_dropout": single_pct,
        "avg_pr_review_days": avg_rev,
        "null_percentage": null_pct,
        "avg_lines_changed": avg_lines
    }

    triggered_alerts = check_alerts(current_metrics, ALERT_THRESHOLDS)

    if triggered_alerts:
        st.header("🚨 Active Operational Threshold Alerts")
        for alert in triggered_alerts:
            # Task 4: Complete alert message format (Metric, Value, Threshold, Plain-language risk description)
            alert_text = (
                f"ALERT: {alert['metric']} is {alert['value']:.1f} "
                f"(threshold limit: {alert['threshold']:.1f}). {alert['message']}"
            )
            # Task 2: Visual Alert with st.error (critical) or st.warning (warning)
            if alert["severity"] == "critical":
                st.error(alert_text)
            else:
                st.warning(alert_text)
        st.divider()

# Sidebar Navigation & Filter Engine
def render_sidebar():
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <span style="font-size:1.6rem">&#128301;</span>
        <span class="sidebar-logo-text">GitGuide Analytics</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Select Section",
        ["Real-Time Dashboard", "Guided Workflow", "Trends & Distributions", "Data Explorer"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.header("Dataset Upload")

    uploaded_file = st.sidebar.file_uploader("Upload dataset (CSV/JSON)", type=["csv", "json"])
    df = handle_file_upload(uploaded_file)

    if df is None:
        fetched_csv = os.path.join(BASE_DIR, "data", "raw", "fetched_github_repo_data.csv")
        if os.path.exists(fetched_csv):
            try:
                df = pd.read_csv(fetched_csv)
            except Exception:
                df = None

    if df is None:
        df = load_default_dataset()

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.header("Interactive Filters")

    filtered_df = df.copy()

    time_col = next((c for c in ["timestamp", "date", "created_at"] if c in df.columns), None)
    if time_col:
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            min_d = df[time_col].min().date()
            max_d = df[time_col].max().date()
            date_range = st.sidebar.date_input("Date Range", value=(min_d, max_d))
            if isinstance(date_range, tuple) and len(date_range) == 2:
                s_date, e_date = date_range
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df[time_col]).dt.date >= s_date) &
                    (pd.to_datetime(filtered_df[time_col]).dt.date <= e_date)
                ]
        except Exception:
            pass

    role_col = next((c for c in ["contributor_role", "role", "segment", "category"] if c in df.columns), None)
    if role_col:
        all_opts = sorted(df[role_col].dropna().unique().tolist())
        selected_opts = st.sidebar.multiselect("Category / Role Filter", options=all_opts, default=all_opts)
        filtered_df = filtered_df[filtered_df[role_col].isin(selected_opts)]

    commit_col = next((c for c in ["commits_count", "commits", "revenue", "total_contributions"] if c in df.columns), None)
    if commit_col and pd.api.types.is_numeric_dtype(df[commit_col]):
        min_v = int(df[commit_col].min())
        max_v = int(df[commit_col].max())
        if min_v < max_v:
            min_sel, max_sel = st.sidebar.slider("Numeric Range Threshold", min_value=min_v, max_value=max_v, value=(min_v, max_v))
            filtered_df = filtered_df[(filtered_df[commit_col] >= min_sel) & (filtered_df[commit_col] <= max_sel)]

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    if st.sidebar.button("Reset All Filters"):
        for key in ["selected_segment", "workflow_step", "analysis_result", "computed_revenue"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    if len(filtered_df) == 0:
        st.warning("No data matches current filters. Broaden your selection.")
        st.stop()

    st.sidebar.markdown(f"<div style='color:#475569;font-size:0.72rem;'><b style='color:#818cf8'>Filtered Scope</b>: {len(filtered_df):,} of {len(df):,} rows</div>", unsafe_allow_html=True)

    return page, filtered_df, df

# Real-Time KPI Dashboard with Alert Monitoring
def render_realtime_kpi_dashboard(filtered_df, full_df):
    st.title("Real-Time Operational KPI Dashboard")
    
    # Task 5: Recalculates alerts dynamically whenever filters change filtered_df
    render_alert_banner(filtered_df)

    st.header("Live Business & Contributor Intelligence")
    
    num_cols = filtered_df.select_dtypes(include="number").columns.tolist()
    primary_num = next((c for c in ["commits_count", "revenue", "total_contributions", "lines_changed"] if c in filtered_df.columns), num_cols[0] if num_cols else None)
    entity_col  = next((c for c in ["contributor_login", "customer_id", "user_id", "contributor_id"] if c in filtered_df.columns), filtered_df.columns[0])

    total_val = filtered_df[primary_num].sum() if primary_num else 0
    avg_val   = filtered_df[primary_num].mean() if primary_num else 0
    row_count = len(filtered_df)
    unique_entities = filtered_df[entity_col].nunique() if entity_col else 0
    
    total_cells = filtered_df.shape[0] * filtered_df.shape[1] if len(filtered_df) > 0 else 1
    null_pct    = (filtered_df.isnull().sum().sum() / total_cells) * 100
    quality_score = 100.0 - null_pct

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Volume", f"{int(total_val):,}" if primary_num else "N/A")
    with c2:
        st.metric("Avg per Unit", f"{avg_val:.1f}" if primary_num else "N/A")
    with c3:
        st.metric("Active Records", f"{row_count:,}")
    with c4:
        st.metric("Unique Entities", f"{unique_entities:,}")
    with c5:
        st.metric("Data Quality", f"{quality_score:.1f}%")

    st.divider()

    st.header("Visual Analytics & Distributions")

    time_col = next((c for c in ["timestamp", "date", "created_at"] if c in filtered_df.columns), None)
    role_col = next((c for c in ["contributor_role", "role", "segment", "category"] if c in filtered_df.columns), None)

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Chart 1: Activity Trend Over Time (Line Chart)")
        if time_col and primary_num:
            df_t = filtered_df.copy()
            df_t[time_col] = pd.to_datetime(df_t[time_col], errors="coerce")
            df_g = df_t.groupby(df_t[time_col].dt.date)[primary_num].sum().reset_index()
            df_g.columns = ["Date", "Volume"]
            st.line_chart(df_g.set_index("Date"))
        else:
            st.info("No date column detected for line trend.")

    with col_right:
        st.subheader("Chart 2: Comparison by Category (Bar Chart)")
        if role_col and primary_num:
            df_cat = filtered_df.groupby(role_col)[primary_num].sum().reset_index()
            df_cat.columns = ["Category", "Volume"]
            st.bar_chart(df_cat.set_index("Category"))
        else:
            st.info("No category column detected for bar comparison.")

    st.divider()

    st.subheader("Chart 3: Metric Value Distribution (Plotly Histogram)")
    if primary_num:
        fig_hist = px.histogram(
            filtered_df, x=primary_num, nbins=30,
            color_discrete_sequence=["#8b5cf6"],
            title=f"Distribution Frequency for '{primary_num}'"
        )
        fig_hist.update_layout(**plot_layout(f"Distribution Frequency for '{primary_num}'"))
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No numerical column available for distribution histogram.")

def render_guided_workflow(df):
    st.title("Multi-Step Guided Workflow")
    st.write(f"Active Session Step: Step {st.session_state['workflow_step']}")

def render_trends_page(filtered_df):
    st.title("Trends & Detailed Distributions")
    st.dataframe(filtered_df.head(20), use_container_width=True)

def render_explorer(filtered_df):
    st.title("Data Explorer")
    st.dataframe(filtered_df, use_container_width=True, height=350)
    st.download_button("Export CSV", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="filtered_export.csv", mime="text/csv")

# Main Controller
def main():
    page, filtered_df, full_df = render_sidebar()
    if page == "Real-Time Dashboard":
        render_realtime_kpi_dashboard(filtered_df, full_df)
    elif page == "Guided Workflow":
        render_guided_workflow(full_df)
    elif page == "Trends & Distributions":
        render_trends_page(filtered_df)
    elif page == "Data Explorer":
        render_explorer(filtered_df)

if __name__ == "__main__":
    main()
