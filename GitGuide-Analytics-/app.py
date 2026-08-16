# -*- coding: utf-8 -*-
"""
GitGuide Analytics - Streamlit Dashboard
Dataset Upload & Dynamic Preview System (Lesson 2.52)

Accepts CSV and JSON files, validates them, and displays a dynamic preview
with column summary, descriptive statistics, and downstream exploration.

Usage:
    streamlit run app.py
"""

import os
import sys
import asyncio
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
    page_title="GitGuide Analytics - Data Upload & Preview",
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

# Task 1 & 4: File Upload & Validation with st.file_uploader
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
            st.error(f"Could not read this file. Please check the format and try again. ({e})")
            st.stop()
    return None

# Sidebar Navigation & Upload Trigger
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
        ["Overview", "Trends", "Data Explorer", "Insights"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.header("Dataset Upload")

    # Task 1: st.file_uploader
    uploaded_file = st.sidebar.file_uploader("Upload your dataset", type=["csv", "json"])
    df = handle_file_upload(uploaded_file)

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.header("Live GitHub Ingestion")

    github_url = st.sidebar.text_input("Repository URL or owner/repo", placeholder="https://github.com/facebook/react", label_visibility="collapsed")
    fetch_clicked = st.sidebar.button("Fetch Live GitHub Data")

    fetched_csv = os.path.join(BASE_DIR, "data", "raw", "fetched_github_repo_data.csv")

    if fetch_clicked and github_url.strip():
        with st.spinner("Fetching from GitHub..."):
            try:
                from github_repo_ingestion import generate_csv_from_github_api
                df_fetched, report = generate_csv_from_github_api(github_url.strip(), output_dir=BASE_DIR)
                st.sidebar.success(f"{report['repository']} — {report['total_contributors']} contributors")
                df = df_fetched
            except Exception as e:
                st.sidebar.error(f"Fetch failed: {e}")

    if df is None and os.path.exists(fetched_csv):
        try:
            df = pd.read_csv(fetched_csv)
        except Exception:
            df = None

    if df is None:
        df = load_default_dataset()

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<div style='color:#475569;font-size:0.72rem;'><b style='color:#64748b'>Dataset Scope</b>: {len(df):,} rows, {len(df.columns)} cols</div>", unsafe_allow_html=True)
    
    return page, df

# Section 1: Overview & Automatic Preview (Task 2, 3 & 5)
def render_overview(df):
    st.title("Business Overview & Dataset Preview")
    
    # Task 2: Dataset Preview metrics
    st.header("Dataset Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", str(len(df.columns)))
    with col3:
        total_cells = df.shape[0] * df.shape[1] if len(df) > 0 else 1
        null_pct = (df.isnull().sum().sum() / total_cells) * 100
        st.metric("Null %", f"{null_pct:.1f}%")

    st.divider()

    # Task 2: First 10 Rows
    st.subheader("First 10 Rows")
    st.dataframe(df.head(10), use_container_width=True, height=300)

    st.divider()

    # Task 2: Column Summary
    st.subheader("Column Summary")
    summary = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str).values,
        "Non-Null": df.notnull().sum().values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().sum() / len(df) * 100).round(1).values
    })
    st.dataframe(summary, use_container_width=True, height=250)

    st.divider()

    # Task 3: Display Basic Statistics
    st.subheader("Descriptive Statistics")
    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        st.dataframe(num_df.describe(), use_container_width=True)
    else:
        st.info("No numeric columns available for descriptive statistics.")

    st.divider()

    # Task 5: Downstream Exploration Demonstration
    st.subheader("Quick Exploration")
    numeric_cols = num_df.columns.tolist()
    if numeric_cols:
        selected_col = st.selectbox("Select a column to visualise", numeric_cols)
        st.bar_chart(df[selected_col].value_counts().head(20))
    else:
        st.info("Upload dataset with numeric columns for instant chart exploration.")

    with st.expander("About This Upload & Preview System"):
        st.write("""
        * **Accepted File Formats**: CSV (`.csv`) and JSON (`.json`).
        * **Parsing**: File bytes are automatically converted to a Pandas DataFrame in memory without manual preprocessing.
        * **Null Audit**: Null % represents total missing cells across all columns divided by total grid cells.
        * **Error Handling**: Malformed or empty files show user-friendly error notifications without displaying Python tracebacks.
        """)

# Section 2: Trends
def render_trends(df):
    st.title("Trend Analysis")
    st.header("Activity & Velocity Trends")
    st.subheader("Time-Series Exploration")
    
    commit_col = next((c for c in ["commits_count","commits","total_contributions"] if c in df.columns), df.select_dtypes(include=np.number).columns[0] if len(df.select_dtypes(include=np.number).columns) else None)
    contributor_col = next((c for c in ["contributor_login","contributor_id"] if c in df.columns), df.columns[0])
    time_col   = next((c for c in ["timestamp","date","created_at"] if c in df.columns), None)
    role_col   = next((c for c in ["contributor_role","role","branch"] if c in df.columns), None)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Commit Activity Over Time")
        if time_col and commit_col:
            df_t = df.copy()
            df_t[time_col] = pd.to_datetime(df_t[time_col], errors="coerce")
            df_g = df_t.groupby(df_t[time_col].dt.date)[commit_col].sum().reset_index()
            df_g.columns = ["date", "commits"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_g["date"], y=df_g["commits"], mode="lines", fill="tozeroy", line=dict(color="#6366f1", width=2.5)))
            fig.update_layout(**plot_layout("Daily Commit Trend"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timestamp column detected in dataset.")

    with col2:
        st.subheader("Role Contribution Share")
        if role_col:
            role_counts = df[role_col].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            fig = go.Figure(go.Pie(labels=role_counts["role"], values=role_counts["count"], hole=0.55, marker=dict(colors=PALETTE[:len(role_counts)])))
            fig.update_layout(**plot_layout("Role Breakdown", showlegend=False))
            st.plotly_chart(fig, use_container_width=True)

# Section 3: Data Explorer
def render_explorer(df):
    st.title("Data Explorer")
    st.header("Interactive Data Filtering")
    st.subheader("Search & Filter Active Dataset")

    c1, c2 = st.columns(2)
    with c1:
        if "contributor_role" in df.columns:
            roles = ["ALL"] + sorted(df["contributor_role"].dropna().unique().tolist())
            selected_role = st.selectbox("Filter by Role", roles)
        else:
            selected_role = "ALL"
    with c2:
        search_q = st.text_input("Search keyword", placeholder="Search...").strip().lower()

    filtered = df.copy()
    if selected_role != "ALL" and "contributor_role" in filtered.columns:
        filtered = filtered[filtered["contributor_role"] == selected_role]
    if search_q:
        mask = filtered.astype(str).apply(lambda row: row.str.lower().str.contains(search_q).any(), axis=1)
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, height=350)
    st.download_button("Download CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="exported_data.csv", mime="text/csv")

# Section 4: Insights Report
def render_insights(df):
    st.title("Business Insights Report")
    st.header("Executive Summary")
    st.subheader("Automated Dataset Health & Bottleneck Report")

    commit_col = next((c for c in ["commits_count","commits"] if c in df.columns), None)
    review_col = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in df.columns), None)

    avg_review = round(df[review_col].mean(), 2) if review_col else None
    pct_single = round((df[commit_col] == 1).mean() * 100, 1) if commit_col else None
    null_rate  = round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2)

    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        st.metric("Avg Review Days", f"{avg_review:.1f}d" if avg_review is not None else "N/A")
    with ci2:
        st.metric("Single-Commit %", f"{pct_single:.1f}%" if pct_single is not None else "N/A")
    with ci3:
        st.metric("Null Rate", f"{null_rate}%")

# Main Controller
def main():
    page, df = render_sidebar()
    if page == "Overview":
        render_overview(df)
    elif page == "Trends":
        render_trends(df)
    elif page == "Data Explorer":
        render_explorer(df)
    elif page == "Insights":
        render_insights(df)

if __name__ == "__main__":
    main()
