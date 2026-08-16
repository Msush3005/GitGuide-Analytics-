# -*- coding: utf-8 -*-
"""
GitGuide Analytics - Streamlit Interactive Dashboard
Filters & Interactive Widgets (Lesson 2.53)

Wires date pickers, multi-select dropdowns, range sliders, and radio buttons
to filter DataFrames dynamically with meaningful defaults, empty state warnings,
and a 1-click Reset Filters button.

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
    page_title="GitGuide Analytics - Interactive Dashboard",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
.insight-card.red    { border-color: #ef4444; }
.insight-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 5px; }
.insight-text  { color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; }
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
                st.error("Unsupported file type. Please upload a CSV or JSON file.")
                st.stop()

            if len(df) == 0:
                st.warning("The uploaded file is empty. Please check your dataset.")
                st.stop()

            st.success(f"Loaded: {uploaded_file.name} ({len(df):,} rows, {len(df.columns)} columns)")
            return df
        except Exception as e:
            st.error(f"Could not read this file. ({e})")
            st.stop()
    return None

# Task 1, 2, 3, 4 & 5: Sidebar Navigation & Filter Wiring Engine
def render_sidebar():
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <span style="font-size:1.6rem">&#128301;</span>
        <span class="sidebar-logo-text">GitGuide Analytics</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    
    # Widget 1: Navigation Radio (Radio Button)
    page = st.sidebar.radio(
        "Select Section",
        ["Overview", "Trends", "Data Explorer", "Insights"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.header("Dataset Upload & Source")

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

    # Filter Chain Implementation (Task 1 & Task 3: Meaningful Defaults)
    filtered_df = df.copy()

    # Widget 2: Date Range Picker (Task 1)
    time_col = next((c for c in ["timestamp", "date", "created_at"] if c in df.columns), None)
    if time_col:
        try:
            df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
            min_date = df[time_col].min().date()
            max_date = df[time_col].max().date()
            
            # Meaningful Default: Full date range
            date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date))
            
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_d, end_d = date_range
                filtered_df = filtered_df[
                    (pd.to_datetime(filtered_df[time_col]).dt.date >= start_d) &
                    (pd.to_datetime(filtered_df[time_col]).dt.date <= end_d)
                ]
        except Exception:
            pass

    # Widget 3: Multi-Select Categorical Filter (Task 1 & Task 3)
    role_col = next((c for c in ["contributor_role", "role", "segment"] if c in df.columns), None)
    if role_col:
        all_roles = sorted(df[role_col].dropna().unique().tolist())
        # Meaningful Default: All options selected
        selected_roles = st.sidebar.multiselect("Contributor Roles", options=all_roles, default=all_roles)
        filtered_df = filtered_df[filtered_df[role_col].isin(selected_roles)]

    # Widget 4: Range Slider for Numeric Threshold (Task 1 & Task 3)
    commit_col = next((c for c in ["commits_count", "commits", "total_contributions", "revenue"] if c in df.columns), None)
    if commit_col and pd.api.types.is_numeric_dtype(df[commit_col]):
        min_c = int(df[commit_col].min())
        max_c = int(df[commit_col].max())
        if min_c < max_c:
            # Meaningful Default: Full numeric range
            min_val, max_val = st.sidebar.slider("Commits Threshold Range", min_value=min_c, max_value=max_c, value=(min_c, max_c))
            filtered_df = filtered_df[(filtered_df[commit_col] >= min_val) & (filtered_df[commit_col] <= max_val)]

    # Task 5: Reset Filters Button
    if st.sidebar.button("Reset Filters"):
        st.rerun()

    # Task 4: Empty Filter Combinations Handling
    if len(filtered_df) == 0:
        st.warning("No data matches the current filter selection. Try broadening your criteria or clicking 'Reset Filters'.")
        st.stop()

    st.sidebar.markdown(f"<div style='color:#475569;font-size:0.72rem;'><b style='color:#818cf8'>Filtered Scope</b>: {len(filtered_df):,} of {len(df):,} rows</div>", unsafe_allow_html=True)
    
    return page, filtered_df, df

# Section 1: Overview
def render_overview(filtered_df, full_df):
    st.title("Business Overview & Dataset Preview")
    
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
        st.metric("Contributors", f"{unique_contribs:,}", f"of {full_df[contributor_col].nunique():,} total")
    with col2:
        st.metric("Total Commits", f"{total_commits:,}" if isinstance(total_commits, int) else total_commits)
    with col3:
        st.metric("Avg PR Review", avg_review)
    with col4:
        st.metric("Single-Commit %", single_ratio)
    with col5:
        st.metric("Lines Changed", lines_sum)

    st.divider()

    st.header("Dataset Overview & Filtered Preview")
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.subheader(f"Filtered Data (Showing Top {min(10, len(filtered_df))} Rows)")
        st.dataframe(filtered_df.head(10), use_container_width=True, height=300)
    with col_r:
        st.subheader("Schema Integrity Audit")
        schema = pd.DataFrame({
            "Type": filtered_df.dtypes.astype(str),
            "Non-Null": filtered_df.notnull().sum(),
            "Nulls": filtered_df.isnull().sum(),
            "Fill %": (filtered_df.notnull().sum() / len(filtered_df) * 100).round(1).astype(str) + "%",
        })
        st.dataframe(schema, use_container_width=True, height=300)

    st.divider()

    st.subheader("Descriptive Statistics")
    num_df = filtered_df.select_dtypes(include="number")
    if not num_df.empty:
        st.dataframe(num_df.describe(), use_container_width=True)
    else:
        st.info("No numeric columns available for descriptive statistics.")

    with st.expander("Filter Chain & Reset Guide"):
        st.write("""
        * **Date Picker**: Filters time-series data using custom start and end boundaries.
        * **Multi-Select**: Filters categorical roles dynamically. Default includes all items.
        * **Range Slider**: Sets numeric threshold boundaries.
        * **Reset Button**: Restores all filters to default dataset scope in 1 click.
        """)

# Section 2: Trends
def render_trends(filtered_df):
    st.title("Trend Analysis")
    st.header("Activity & Velocity Trends")
    st.subheader("Reactive Time-Series Exploration")
    
    commit_col = next((c for c in ["commits_count","commits","total_contributions"] if c in filtered_df.columns), filtered_df.select_dtypes(include=np.number).columns[0] if len(filtered_df.select_dtypes(include=np.number).columns) else None)
    contributor_col = next((c for c in ["contributor_login","contributor_id"] if c in filtered_df.columns), filtered_df.columns[0])
    time_col   = next((c for c in ["timestamp","date","created_at"] if c in filtered_df.columns), None)
    role_col   = next((c for c in ["contributor_role","role","branch"] if c in filtered_df.columns), None)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Commit Activity Over Time")
        if time_col and commit_col:
            df_t = filtered_df.copy()
            df_t[time_col] = pd.to_datetime(df_t[time_col], errors="coerce")
            df_g = df_t.groupby(df_t[time_col].dt.date)[commit_col].sum().reset_index()
            df_g.columns = ["date", "commits"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_g["date"], y=df_g["commits"], mode="lines", fill="tozeroy", line=dict(color="#6366f1", width=2.5)))
            fig.update_layout(**plot_layout("Filtered Daily Commit Trend"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timestamp column detected.")

    with col2:
        st.subheader("Role Breakdown")
        if role_col:
            role_counts = filtered_df[role_col].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            fig = go.Figure(go.Pie(labels=role_counts["role"], values=role_counts["count"], hole=0.55, marker=dict(colors=PALETTE[:len(role_counts)])))
            fig.update_layout(**plot_layout("Filtered Role Distribution", showlegend=False))
            st.plotly_chart(fig, use_container_width=True)

# Section 3: Data Explorer
def render_explorer(filtered_df):
    st.title("Data Explorer")
    st.header("Interactive Search & Export")

    search_q = st.text_input("Search (keyword across all columns)", placeholder="Type to search...").strip().lower()
    df_search = filtered_df.copy()
    if search_q:
        mask = df_search.astype(str).apply(lambda row: row.str.lower().str.contains(search_q).any(), axis=1)
        df_search = df_search[mask]

    st.subheader(f"Filtered Results ({len(df_search):,} records)")
    st.dataframe(df_search, use_container_width=True, height=350)
    st.download_button("Download Filtered CSV", data=df_search.to_csv(index=False).encode("utf-8"), file_name="filtered_data.csv", mime="text/csv")

# Section 4: Insights Report
def render_insights(filtered_df):
    st.title("Business Insights Report")
    st.header("Automated Intelligence Summary")

    commit_col = next((c for c in ["commits_count","commits"] if c in filtered_df.columns), None)
    review_col = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in filtered_df.columns), None)

    avg_review = round(filtered_df[review_col].mean(), 2) if review_col else None
    pct_single = round((filtered_df[commit_col] == 1).mean() * 100, 1) if commit_col else None

    ci1, ci2 = st.columns(2)
    with ci1:
        st.metric("Avg PR Review", f"{avg_review:.1f}d" if avg_review is not None else "N/A")
    with ci2:
        st.metric("Single-Commit Dropout %", f"{pct_single:.1f}%" if pct_single is not None else "N/A")

# Main Controller
def main():
    page, filtered_df, full_df = render_sidebar()
    if page == "Overview":
        render_overview(filtered_df, full_df)
    elif page == "Trends":
        render_trends(filtered_df)
    elif page == "Data Explorer":
        render_explorer(filtered_df)
    elif page == "Insights":
        render_insights(filtered_df)

if __name__ == "__main__":
    main()
