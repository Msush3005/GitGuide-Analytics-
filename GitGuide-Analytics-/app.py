# -*- coding: utf-8 -*-
"""
GitGuide Analytics - Interactive Multi-Step Dashboard
Streamlit Session State & Workflow Persistence (Lesson 2.54)

Demonstrates st.session_state initialization, multi-step workflow memory,
descriptive key naming, inline documentation, and clean state reset mechanisms.

Usage:
    streamlit run app.py
"""

import os
import sys
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

# Page config
st.set_page_config(
    page_title="GitGuide Analytics - Session State & Workflow Persistence",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Task 1, 2 & 5: Initialise Session State with Descriptive Keys and Safe Initialization
# Inline comments explain the purpose of each key (Task 5)

# "selected_segment" - stores the user's segment/role choice from Step 1 so it survives reruns when unrelated widgets change.
if "selected_segment" not in st.session_state:
    st.session_state["selected_segment"] = "All"

# "workflow_step" - tracks which step the user has completed in the multi-step analytics workflow (Step 1 -> Step 2).
if "workflow_step" not in st.session_state:
    st.session_state["workflow_step"] = 1

# "analysis_result" - caches computed metrics/results from Step 2 so they do not recompute when unrelated widgets are adjusted.
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# "computed_revenue" - stores total calculated contributions/revenue for the selected segment.
if "computed_revenue" not in st.session_state:
    st.session_state["computed_revenue"] = 0.0

# "filter_date_start" - stores active start date filter across page navigation and widget interactions.
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
    transition: transform 0.25s ease, border-color 0.25s ease;
}
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,0.55);
}
.card-icon  { font-size: 1.5rem; margin-bottom: 8px; display: block; }
.card-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.card-value { color: #f1f5f9; font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.card-delta { font-size: 0.78rem; font-weight: 500; padding: 2px 8px; border-radius: 20px; display: inline-block; margin-top: 6px; }
.delta-positive { background: rgba(16,185,129,0.15); color: #10b981; }
.delta-negative { background: rgba(239,68,68,0.15);  color: #ef4444; }
.delta-neutral  { background: rgba(99,102,241,0.15); color: #818cf8; }
.insight-card {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid;
    border-radius: 0 12px 12px 0;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.insight-card.blue   { border-color: #3b82f6; }
.insight-card.purple { border-color: #8b5cf6; }
.insight-card.green  { border-color: #10b981; }
.insight-card.amber  { border-color: #f59e0b; }
.sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 4px 0 12px 0; }
.sidebar-logo-text {
    font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(99,102,241,0.18) !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; width: 100%;
}
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
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
def load_default_dataset():
    processed_path = os.path.join(BASE_DIR, "output", "processed.csv")
    raw_path       = os.path.join(BASE_DIR, "data", "raw", "sample.csv")
    if os.path.exists(processed_path):
        return pd.read_csv(processed_path)
    if os.path.exists(raw_path):
        return pd.read_csv(raw_path)
    np.random.seed(42)
    n = 20
    roles = ["Maintainer"] * 3 + ["Reviewer"] * 5 + ["Contributor"] * 12
    np.random.shuffle(roles)
    dates = pd.date_range("2026-01-01", periods=n, freq="3D")
    return pd.DataFrame({
        "contributor_id": range(101, 101 + n),
        "contributor_login": [f"user_{i:03d}" for i in range(101, 101 + n)],
        "repository_name": ["GitGuide-Analytics-"] * n,
        "commits_count": np.random.randint(1, 35, n),
        "pull_requests_opened": np.random.randint(0, 12, n),
        "total_contributions": np.random.randint(1, 45, n),
        "lines_changed": np.random.randint(15, 1200, n),
        "contributor_role": roles,
        "pr_review_days": np.round(np.random.uniform(0.5, 8.0, n), 2),
        "timestamp": dates.strftime("%Y-%m-%d"),
    })

def handle_file_upload(uploaded_file):
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload CSV or JSON.")
                st.stop()
            if len(df) == 0:
                st.warning("Uploaded file is empty.")
                st.stop()
            st.success(f"Loaded: {uploaded_file.name} ({len(df):,} rows)")
            return df
        except Exception as e:
            st.error(f"Could not read file. ({e})")
            st.stop()
    return None

# Sidebar Navigation & Session State Reset Engine (Task 4)
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
        ["Overview", "Guided Workflow", "Trends", "Data Explorer", "Insights"],
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

    # Date range filter
    time_col = next((c for c in ["timestamp", "date", "created_at"] if c in df.columns), None)
    if time_col:
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            min_date = df[time_col].min().date()
            max_date = df[time_col].max().date()
            date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date))
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_d, end_d = date_range
                st.session_state["filter_date_start"] = str(start_d)
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df[time_col]).dt.date >= start_d) &
                    (pd.to_datetime(filtered_df[time_col]).dt.date <= end_d)
                ]
        except Exception:
            pass

    # Multi-select role filter
    role_col = next((c for c in ["contributor_role", "role", "segment"] if c in df.columns), None)
    if role_col:
        all_roles = sorted(df[role_col].dropna().unique().tolist())
        selected_roles = st.sidebar.multiselect("Contributor Roles", options=all_roles, default=all_roles)
        filtered_df = filtered_df[filtered_df[role_col].isin(selected_roles)]

    # Task 4: Reset Workflow & Session State Button
    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    if st.sidebar.button("Reset Workflow & State"):
        for key in ["selected_segment", "workflow_step", "analysis_result", "computed_revenue", "filter_date_start"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    if len(filtered_df) == 0:
        st.warning("No data matches the current filter selection. Try broadening your criteria or clicking 'Reset Workflow & State'.")
        st.stop()

    st.sidebar.markdown(f"<div style='color:#475569;font-size:0.72rem;'><b style='color:#818cf8'>Filtered Scope</b>: {len(filtered_df):,} of {len(df):,} rows</div>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='color:#64748b;font-size:0.7rem;'>Active Workflow Step: <b>Step {st.session_state['workflow_step']}</b></div>", unsafe_allow_html=True)

    return page, filtered_df, df

# Task 3: Multi-Step Guided Workflow Engine using st.session_state
def render_guided_workflow(df):
    st.title("Multi-Step Guided Workflow")
    st.header("Analytical Continuity Engine")
    st.markdown("Demonstrates how `st.session_state` carries context forward across widget interactions.")
    
    st.divider()

    # Step 1: Select Segment / Contributor Role
    st.header("Step 1: Select Segment or Role")
    role_col = next((c for c in ["contributor_role", "role", "segment"] if c in df.columns), None)
    
    if role_col:
        options = ["All"] + sorted(df[role_col].dropna().unique().tolist())
    else:
        options = ["All", "Enterprise", "Mid-Market", "SMB"]

    # Read session state to set widget index (keeps widget in sync)
    current_selected = st.session_state["selected_segment"]
    default_idx = options.index(current_selected) if current_selected in options else 0

    segment_choice = st.selectbox(
        "Choose a segment/role for deep-dive analysis",
        options=options,
        index=default_idx
    )

    if st.button("Confirm Segment Selection"):
        st.session_state["selected_segment"] = segment_choice
        st.session_state["workflow_step"] = 2
        st.success(f"Segment confirmed: {segment_choice}. Proceeding to Step 2...")

    st.divider()

    # Step 2: Show Analysis (Only if Step 1 is confirmed and completed)
    if st.session_state["workflow_step"] >= 2:
        st.header("Step 2: Segment Velocity & Contribution Analysis")
        chosen_seg = st.session_state["selected_segment"]
        st.info(f"Analysing Segment Context: **{chosen_seg}** (Persisted across reruns via `st.session_state`) ")

        if chosen_seg == "All" or role_col not in df.columns:
            analysis_df = df
        else:
            analysis_df = df[df[role_col] == chosen_seg]

        commit_col = next((c for c in ["commits_count", "commits", "total_contributions"] if c in analysis_df.columns), None)
        
        if commit_col and len(analysis_df):
            total_rev = int(analysis_df[commit_col].sum())
            st.session_state["computed_revenue"] = float(total_rev)
            st.session_state["analysis_result"] = f"Total commits for {chosen_seg}: {total_rev:,}"

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Commits", f"{total_rev:,}")
            with col2:
                st.metric("Contributors Count", f"{len(analysis_df):,}")
            with col3:
                avg_c = total_rev / len(analysis_df) if len(analysis_df) else 0
                st.metric("Avg Commits / Contributor", f"{avg_c:.1f}")

            st.subheader(f"Data Preview for {chosen_seg}")
            st.dataframe(analysis_df, use_container_width=True, height=250)
        else:
            st.warning(f"No records found for segment: {chosen_seg}")
    else:
        st.warning("Step 2 is locked. Please confirm your segment selection in Step 1 above to unlock Step 2.")

# Section: Overview
def render_overview(filtered_df, full_df):
    st.title("Business Overview & Overview Metrics")
    
    st.header("Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    commit_col      = next((c for c in ["commits_count","commits","total_contributions"] if c in filtered_df.columns), filtered_df.select_dtypes(include=np.number).columns[0] if len(filtered_df.select_dtypes(include=np.number).columns) else None)
    contributor_col = next((c for c in ["contributor_login","contributor_id"] if c in filtered_df.columns), filtered_df.columns[0])
    review_col      = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in filtered_df.columns), None)

    total_commits   = int(filtered_df[commit_col].sum()) if commit_col else "N/A"
    unique_contribs = filtered_df[contributor_col].nunique()
    avg_review      = f"{filtered_df[review_col].mean():.1f}d" if review_col else "N/A"
    single_ratio    = f"{(filtered_df[commit_col] == 1).mean() * 100:.1f}%" if commit_col else "N/A"
    lines_sum       = f"{filtered_df['avg_lines_changed'].sum():,}" if 'avg_lines_changed' in filtered_df.columns else "N/A"

    with col1:
        st.metric("Contributors", f"{unique_contribs:,}")
    with col2:
        st.metric("Total Commits", f"{total_commits:,}" if isinstance(total_commits, int) else total_commits)
    with col3:
        st.metric("Avg PR Review", avg_review)
    with col4:
        st.metric("Single-Commit %", single_ratio)
    with col5:
        st.metric("Lines Changed", lines_sum)

    st.divider()

    st.subheader("Session State Inspection & Persistence Audit")
    state_table = pd.DataFrame({
        "Session State Key": list(st.session_state.keys()),
        "Stored Value": [str(v) for v in st.session_state.values()]
    })
    st.dataframe(state_table, use_container_width=True)

# Section: Trends
def render_trends(filtered_df):
    st.title("Trend Analysis")
    st.header("Activity Trends")

    commit_col = next((c for c in ["commits_count","commits","total_contributions"] if c in filtered_df.columns), filtered_df.select_dtypes(include=np.number).columns[0] if len(filtered_df.select_dtypes(include=np.number).columns) else None)
    time_col   = next((c for c in ["timestamp","date","created_at"] if c in filtered_df.columns), None)

    if time_col and commit_col:
        df_t = filtered_df.copy()
        df_t[time_col] = pd.to_datetime(df_t[time_col], errors="coerce")
        df_g = df_t.groupby(df_t[time_col].dt.date)[commit_col].sum().reset_index()
        df_g.columns = ["date", "commits"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_g["date"], y=df_g["commits"], mode="lines", fill="tozeroy", line=dict(color="#6366f1", width=2.5)))
        fig.update_layout(**plot_layout("Filtered Daily Commit Trend"))
        st.plotly_chart(fig, use_container_width=True)

# Section: Data Explorer
def render_explorer(filtered_df):
    st.title("Data Explorer")
    st.dataframe(filtered_df, use_container_width=True, height=350)
    st.download_button("Download Filtered CSV", data=filtered_df.to_csv(index=False).encode("utf-8"), file_name="filtered_data.csv", mime="text/csv")

# Section: Insights Report
def render_insights(filtered_df):
    st.title("Business Insights Report")
    st.write(f"Active Workflow Context: Step {st.session_state['workflow_step']} | Selected Segment: {st.session_state['selected_segment']}")

# Main Controller
def main():
    page, filtered_df, full_df = render_sidebar()
    if page == "Overview":
        render_overview(filtered_df, full_df)
    elif page == "Guided Workflow":
        render_guided_workflow(full_df)
    elif page == "Trends":
        render_trends(filtered_df)
    elif page == "Data Explorer":
        render_explorer(filtered_df)
    elif page == "Insights":
        render_insights(filtered_df)

if __name__ == "__main__":
    main()
