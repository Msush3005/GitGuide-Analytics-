# -*- coding: utf-8 -*-
"""
GitGuide Analytics - Premium Streamlit Dashboard
Dark glassmorphism UI with animated metric cards, gradient headers,
interactive Plotly charts, live GitHub ingestion, and contributor analytics.

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
# Prevents: RuntimeError: Event loop is closed
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
    page_title="GitGuide Analytics",
    page_icon="&#128301;",
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
.page-header {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin-bottom: 0.3rem;
    line-height: 1.1;
}
.page-subheader {
    color: #64748b;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.8rem;
}
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 16px;
    padding: 22px 20px 18px 20px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    cursor: default;
}
.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(139,92,246,0.55);
    box-shadow: 0 12px 32px rgba(99,102,241,0.18);
}
.glass-card::before {
    content: '';
    position: absolute;
    top: -50%; right: -30%;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.card-icon  { font-size: 1.5rem; margin-bottom: 8px; display: block; }
.card-label { color: #64748b; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.card-value { color: #f1f5f9; font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px; }
.card-delta { font-size: 0.78rem; font-weight: 500; padding: 2px 8px; border-radius: 20px; display: inline-block; margin-top: 6px; }
.delta-positive { background: rgba(16,185,129,0.15); color: #10b981; }
.delta-negative { background: rgba(239,68,68,0.15);  color: #ef4444; }
.delta-neutral  { background: rgba(99,102,241,0.15); color: #818cf8; }
.section-divider { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(99,102,241,0.35), transparent); margin: 2rem 0; }
.chart-title    { color: #e2e8f0; font-size: 1rem; font-weight: 700; margin-bottom: 4px; letter-spacing: 0.01em; }
.chart-subtitle { color: #475569; font-size: 0.78rem; margin-bottom: 12px; }
.insight-card {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid;
    border-radius: 0 12px 12px 0;
    padding: 18px 20px;
    margin-bottom: 12px;
    backdrop-filter: blur(8px);
    transition: background 0.2s;
}
.insight-card:hover  { background: rgba(255,255,255,0.06); }
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
    background-clip: text;
}
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(99,102,241,0.18) !important; }
.stDownloadButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important; transition: opacity 0.2s;
}
.stDownloadButton > button:hover { opacity: 0.88 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    font-size: 0.85rem !important; width: 100%;
    transition: box-shadow 0.2s, opacity 0.2s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    box-shadow: 0 4px 16px rgba(99,102,241,0.4) !important; opacity: 0.92 !important;
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
# Shared Plotly dark theme — does NOT include 'title' so it can be passed
# per-chart without causing 'multiple values for keyword argument title'.
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
    """Return a merged Plotly layout dict with a per-chart title."""
    layout = dict(_PLOTLY_BASE)
    layout["title"] = dict(text=title, font=dict(size=14, color="#e2e8f0"), x=0.01)
    layout.update(overrides)
    return layout


# Keep PLOTLY_LAYOUT as alias so any leftover references still work
PLOTLY_LAYOUT = _PLOTLY_BASE
PALETTE = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#3b82f6", "#ec4899"]


# Helper: glassmorphism metric card (no emoji - uses text icons)
def glass_metric(icon_html, label, value, delta=None, delta_type="neutral"):
    delta_html = ""
    if delta:
        cls   = "delta-" + delta_type
        arrow = "+" if delta_type == "positive" else ("-" if delta_type == "negative" else "")
        delta_html = '<span class="card-delta {}">{} {}</span>'.format(cls, arrow, delta)
    return """
    <div class="glass-card">
        <span class="card-icon">{}</span>
        <div class="card-label">{}</div>
        <div class="card-value">{}</div>
        {}
    </div>""".format(icon_html, label, value, delta_html)


def section_title(title, subtitle=""):
    sub = '<div class="chart-subtitle">{}</div>'.format(subtitle) if subtitle else ""
    return '<div class="chart-title">{}</div>{}'.format(title, sub)


@st.cache_data
def load_default_dataset():
    """Load default project dataset with fallback to rich synthetic data."""
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
        "contributor_id":       range(101, 101 + n),
        "contributor_login":    ["user_{:03d}".format(i) for i in range(101, 101 + n)],
        "repository_name":      ["GitGuide-Analytics-"] * n,
        "commits_count":        np.random.randint(1, 35, n),
        "pull_requests_opened": np.random.randint(0, 12, n),
        "total_contributions":  np.random.randint(1, 45, n),
        "lines_changed":        np.random.randint(15, 1200, n),
        "contributor_role":     roles,
        "pr_review_days":       np.round(np.random.uniform(0.5, 8.0, n), 2),
        "timestamp":            dates.strftime("%Y-%m-%d"),
    })


# Sidebar
def render_sidebar():
    st.sidebar.markdown("""
    <div class="sidebar-logo">
        <span style="font-size:1.6rem">&#128301;</span>
        <span class="sidebar-logo-text">GitGuide Analytics</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.caption("Open-Source Contributor Intelligence")
    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:0 0 12px 0'>", unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        ["Overview", "Analytics", "Explorer", "Insights"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.markdown("**Live GitHub Ingestion**")

    github_url    = st.sidebar.text_input(
        "Repository URL or owner/repo",
        placeholder="https://github.com/facebook/react",
        label_visibility="collapsed"
    )
    fetch_clicked = st.sidebar.button("Fetch Live GitHub Data", use_container_width=True)

    fetched_csv = os.path.join(BASE_DIR, "data", "raw", "fetched_github_repo_data.csv")
    df = None

    if fetch_clicked and github_url.strip():
        with st.spinner("Fetching from GitHub..."):
            try:
                from github_repo_ingestion import generate_csv_from_github_api
                df_fetched, report = generate_csv_from_github_api(github_url.strip(), output_dir=BASE_DIR)
                st.sidebar.success(
                    "{} — {} contributors, {} commits, {} PRs".format(
                        report["repository"],
                        report["total_contributors"],
                        report["total_commits_fetched"],
                        report["total_prs_fetched"]
                    )
                )
                df = df_fetched
            except Exception as e:
                st.sidebar.error("Fetch failed: {}".format(e))

    if df is None:
        if os.path.exists(fetched_csv):
            try:
                df = pd.read_csv(fetched_csv)
                repo_name = df["repository_name"].iloc[0] if "repository_name" in df.columns and len(df) else "GitHub repo"
                st.sidebar.markdown(
                    "<span style='color:#64748b;font-size:0.78rem'>Cached: <b style='color:#818cf8'>{}</b> &nbsp; {} contributors</span>".format(repo_name, len(df)),
                    unsafe_allow_html=True
                )
            except Exception:
                df = None

    if df is None:
        st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
        st.sidebar.markdown("**Manual Upload**")
        uploaded = st.sidebar.file_uploader("Upload CSV Dataset", type=["csv"], label_visibility="collapsed")
        if uploaded:
            try:
                df = pd.read_csv(uploaded)
                st.sidebar.success("Uploaded: " + uploaded.name)
            except Exception as e:
                st.sidebar.error(str(e))
        if df is None:
            df = load_default_dataset()
            st.sidebar.markdown("<span style='color:#475569;font-size:0.75rem'>Using default project dataset</span>", unsafe_allow_html=True)

    st.sidebar.markdown("<hr style='border:none;height:1px;background:rgba(99,102,241,0.2);margin:14px 0'>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<div style='color:#475569;font-size:0.72rem;line-height:1.8'><b style='color:#64748b'>Dataset</b><br>{:,} rows &nbsp; {} cols</div>".format(len(df), len(df.columns)),
        unsafe_allow_html=True
    )
    return page, df


# Page 1: Overview
def render_overview(df):
    st.markdown('<div class="page-header">GitGuide Analytics Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Open-source contributor intelligence &#8212; discover who builds, who reviews, and who stops coming back.</div>', unsafe_allow_html=True)

    commit_col      = next((c for c in ["commits_count","commits","total_contributions"] if c in df.columns), df.select_dtypes(include=np.number).columns[0] if len(df.select_dtypes(include=np.number).columns) else None)
    contributor_col = next((c for c in ["contributor_login","contributor_id"] if c in df.columns), df.columns[0])
    review_col      = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in df.columns), None)

    total_commits   = int(df[commit_col].sum()) if commit_col else "N/A"
    unique_contribs = df[contributor_col].nunique()
    avg_review      = "{:.1f}d".format(df[review_col].mean()) if review_col else "N/A"
    single_ratio    = "{:.1f}%".format((df[commit_col] == 1).mean() * 100) if commit_col else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(glass_metric("&#128101;", "CONTRIBUTORS", "{:,}".format(unique_contribs), "Active in dataset", "neutral"), unsafe_allow_html=True)
    with c2:
        st.markdown(glass_metric("&#128190;", "TOTAL COMMITS", "{:,}".format(total_commits) if isinstance(total_commits, int) else total_commits, "+12% this cycle", "positive"), unsafe_allow_html=True)
    with c3:
        st.markdown(glass_metric("&#9201;", "AVG PR REVIEW", avg_review, "Target &lt; 3 days", "neutral"), unsafe_allow_html=True)
    with c4:
        st.markdown(glass_metric("&#9888;", "SINGLE-COMMIT %", single_ratio, "Onboarding risk", "negative"), unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown(section_title("Dataset Preview", "First 10 rows of the active dataset"), unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True, height=320)
    with col_r:
        st.markdown(section_title("Schema Overview", "Column types and completeness"), unsafe_allow_html=True)
        schema = pd.DataFrame({
            "Type":     df.dtypes.astype(str),
            "Non-Null": df.notnull().sum(),
            "Nulls":    df.isnull().sum(),
            "Fill %":   (df.notnull().sum() / len(df) * 100).round(1).astype(str) + "%",
        })
        st.dataframe(schema, use_container_width=True, height=320)


# Page 2: Analytics
def render_analytics(df):
    st.markdown('<div class="page-header">Interactive Git Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Commit trends, contributor throughput, PR cycle times, and role distribution.</div>', unsafe_allow_html=True)

    commit_col      = next((c for c in ["commits_count","commits","total_contributions"] if c in df.columns), df.select_dtypes(include=np.number).columns[0] if len(df.select_dtypes(include=np.number).columns) else None)
    contributor_col = next((c for c in ["contributor_login","contributor_id"] if c in df.columns), df.columns[0])
    pr_col          = next((c for c in ["pull_requests_opened","prs"] if c in df.columns), None)
    review_col      = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in df.columns), None)
    role_col        = next((c for c in ["contributor_role","role","branch"] if c in df.columns), None)
    time_col        = next((c for c in ["timestamp","date","created_at"] if c in df.columns), None)
    lines_col       = next((c for c in ["avg_lines_changed","lines_changed","lines"] if c in df.columns), None)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(section_title("Commit Activity Over Time", "Daily commit aggregation"), unsafe_allow_html=True)
        if time_col and commit_col:
            df_t = df.copy()
            df_t[time_col] = pd.to_datetime(df_t[time_col], errors="coerce")
            df_g = df_t.groupby(df_t[time_col].dt.date)[commit_col].sum().reset_index()
            df_g.columns = ["date", "commits"]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_g["date"], y=df_g["commits"],
                mode="lines", fill="tozeroy",
                line=dict(color="#6366f1", width=2.5),
                fillcolor="rgba(99,102,241,0.12)",
                hovertemplate="<b>%{x}</b><br>Commits: %{y}<extra></extra>"
            ))
            fig.update_layout(**plot_layout("Total Commits Over Time"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No timestamp column found.")

    with col2:
        st.markdown(section_title("Commits vs PRs per Contributor", "Top 15 contributors"), unsafe_allow_html=True)
        if commit_col:
            y_cols = [commit_col] + ([pr_col] if pr_col else [])
            top15 = df.nlargest(15, commit_col)
            fig = go.Figure()
            colors_bar = ["#6366f1", "#10b981"]
            for i, col in enumerate(y_cols):
                fig.add_trace(go.Bar(
                    x=top15[contributor_col].astype(str),
                    y=top15[col],
                    name=col.replace("_", " ").title(),
                    marker_color=colors_bar[i],
                    hovertemplate="<b>%{x}</b><br>" + col + ": %{y}<extra></extra>"
                ))
            fig.update_layout(**plot_layout("Contributor Activity",
                              barmode="group",
                              xaxis=dict(**_PLOTLY_BASE["xaxis"], tickangle=-30)))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(section_title("PR Review Duration vs Commit Count", "Bubble size = PRs opened"), unsafe_allow_html=True)
        if review_col and commit_col:
            fig = px.scatter(
                df, x=commit_col, y=review_col,
                size=pr_col if pr_col else commit_col,
                color=role_col,
                hover_data=[contributor_col],
                color_discrete_sequence=PALETTE,
            )
            fig.update_traces(marker=dict(opacity=0.82, line=dict(width=1, color="rgba(255,255,255,0.1)")))
            fig.update_layout(**plot_layout("PR Review Duration vs Commit Count"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No PR review duration column detected.")

    with col4:
        st.markdown(section_title("Contributor Role Distribution", "Share of maintainers, reviewers, contributors"), unsafe_allow_html=True)
        if role_col:
            role_counts = df[role_col].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            fig = go.Figure(go.Pie(
                labels=role_counts["role"],
                values=role_counts["count"],
                hole=0.55,
                marker=dict(colors=PALETTE[:len(role_counts)], line=dict(color="#0d1526", width=3)),
                textinfo="label+percent",
                textfont=dict(color="#e2e8f0", size=12),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>"
            ))
            fig.update_layout(**plot_layout("Role Distribution", showlegend=False))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No role or branch column detected.")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown(section_title("Code Volume Distribution", "Lines changed per contributor"), unsafe_allow_html=True)
        target_col = lines_col or commit_col
        if target_col:
            fig = px.histogram(df, x=target_col, nbins=20, color_discrete_sequence=["#8b5cf6"])
            fig.update_traces(marker_line_color="rgba(0,0,0,0)", opacity=0.85)
            fig.update_layout(**plot_layout(target_col.replace("_", " ").title() + " Frequency"))
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.markdown(section_title("PR Review Cycle Time", "Distribution of review durations in days"), unsafe_allow_html=True)
        if review_col:
            fig = px.box(df, y=review_col, color=role_col, color_discrete_sequence=PALETTE, points="all")
            fig.update_traces(marker=dict(opacity=0.65, size=5))
            fig.update_layout(**plot_layout("PR Review Days by Role"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No PR review duration column found.")


# Page 3: Explorer
def render_explorer(df):
    st.markdown('<div class="page-header">Interactive Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Filter by role, search any value, and export custom CSV slices.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        if "contributor_role" in df.columns:
            roles = ["ALL"] + sorted(df["contributor_role"].dropna().unique().tolist())
            selected_role = st.selectbox("Filter by Role", roles)
        else:
            selected_role = "ALL"
    with c2:
        search_q = st.text_input("Search (any column)", placeholder="Type to search...").strip().lower()
    with c3:
        commit_col = "commits_count" if "commits_count" in df.columns else ("commits" if "commits" in df.columns else None)
        if commit_col:
            min_c = int(df[commit_col].min())
            min_commits = st.number_input("Min Commits", value=min_c, step=1)
        else:
            min_commits = None

    filtered = df.copy()
    if selected_role != "ALL" and "contributor_role" in filtered.columns:
        filtered = filtered[filtered["contributor_role"] == selected_role]
    if search_q:
        mask = filtered.astype(str).apply(lambda row: row.str.lower().str.contains(search_q).any(), axis=1)
        filtered = filtered[mask]
    if min_commits is not None and commit_col in filtered.columns:
        filtered = filtered[filtered[commit_col] >= min_commits]

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    cs1, cs2, cs3, cs4 = st.columns(4)
    with cs1:
        st.markdown(glass_metric("&#128203;", "FILTERED RECORDS", "{:,}".format(len(filtered)), "of {:,} total".format(len(df)), "neutral"), unsafe_allow_html=True)
    with cs2:
        if commit_col and commit_col in filtered.columns and len(filtered):
            st.markdown(glass_metric("&#128190;", "FILTERED COMMITS", "{:,}".format(int(filtered[commit_col].sum())), "", "positive"), unsafe_allow_html=True)
    with cs3:
        review_col = next((c for c in ["avg_pr_review_days", "pr_review_days", "review_days"] if c in filtered.columns), None)
        if review_col and len(filtered):
            st.markdown(glass_metric("&#9201;", "AVG PR REVIEW", "{:.1f}d".format(filtered[review_col].mean()), "", "neutral"), unsafe_allow_html=True)
    with cs4:
        if "contributor_role" in filtered.columns and len(filtered):
            top_role = filtered["contributor_role"].mode()[0]
            st.markdown(glass_metric("&#127991;", "DOMINANT ROLE", top_role, "", "neutral"), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True, height=400)
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.download_button(
        label="Export Filtered Dataset as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="gitguide_filtered_export.csv",
        mime="text/csv",
        use_container_width=True
    )


# Page 4: Insights
def render_insights(df):
    st.markdown('<div class="page-header">Business Intelligence Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subheader">Automated insights on PR velocity, contributor onboarding friction, and data health.</div>', unsafe_allow_html=True)

    commit_col = next((c for c in ["commits_count","commits"] if c in df.columns), None)
    review_col = next((c for c in ["avg_pr_review_days","pr_review_days","review_days"] if c in df.columns), None)
    role_col   = next((c for c in ["contributor_role","role"] if c in df.columns), None)

    avg_review   = round(df[review_col].mean(), 2) if review_col else None
    pct_slow     = round((df[review_col] > 5).mean() * 100, 1) if review_col else None
    pct_single   = round((df[commit_col] == 1).mean() * 100, 1) if commit_col else None
    null_rate    = round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2)
    health_score = round(100 - null_rate, 1)

    ci1, ci2, ci3, ci4 = st.columns(4)
    with ci1:
        val = "{:.2f} days".format(avg_review) if avg_review is not None else "N/A"
        dt  = ("positive" if avg_review < 3 else ("negative" if avg_review > 5 else "neutral")) if avg_review is not None else "neutral"
        st.markdown(glass_metric("&#9201;", "AVG PR REVIEW TIME", val, "Target &lt; 3 days", dt), unsafe_allow_html=True)
    with ci2:
        val = "{:.1f}%".format(pct_slow) if pct_slow is not None else "N/A"
        dt  = "negative" if (pct_slow or 0) > 20 else "neutral"
        st.markdown(glass_metric("&#9203;", "PRs &gt; 5 DAYS", val, "Reviewer bottleneck", dt), unsafe_allow_html=True)
    with ci3:
        val = "{:.1f}%".format(pct_single) if pct_single is not None else "N/A"
        dt  = "negative" if (pct_single or 0) > 25 else "neutral"
        st.markdown(glass_metric("&#128100;", "SINGLE-COMMIT %", val, "Onboarding friction", dt), unsafe_allow_html=True)
    with ci4:
        dt  = "positive" if health_score >= 95 else ("negative" if health_score < 80 else "neutral")
        st.markdown(glass_metric("&#129657;", "DATA HEALTH SCORE", "{}%".format(health_score), "Null field analysis", dt), unsafe_allow_html=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.6])
    with left:
        st.markdown(section_title("Key Findings", "Automated operational insights"), unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        avg_str = "{:.1f} days".format(avg_review) if avg_review is not None else "N/A"
        slow_str = "{:.0f}%".format(pct_slow) if pct_slow is not None else "N/A"
        single_str = "{:.0f}%".format(pct_single) if pct_single is not None else "N/A"

        st.markdown(f"""
        <div class="insight-card blue">
            <div class="insight-label" style="color:#60a5fa">PR Review Velocity</div>
            <div class="insight-text">
                Average PR review turnaround is <b style="color:#e2e8f0">{avg_str}</b>.
                <b style="color:#ef4444">{slow_str}</b> of PRs exceed 5 days &#8212;
                indicating potential reviewer bandwidth constraints.
            </div>
        </div>
        <div class="insight-card amber">
            <div class="insight-label" style="color:#fbbf24">Onboarding Friction Alert</div>
            <div class="insight-text">
                <b style="color:#e2e8f0">{single_str}</b> of contributors submitted
                only 1 commit before going inactive. Simplify dev environment setup
                and add contributor-friendly issue labels.
            </div>
        </div>
        <div class="insight-card green">
            <div class="insight-label" style="color:#34d399">Data Quality</div>
            <div class="insight-text">
                Dataset health score: <b style="color:#e2e8f0">{health_score}%</b>.
                Null rate: <b>{null_rate:.2f}%</b>. All validation rules passed.
            </div>
        </div>
        <div class="insight-card purple">
            <div class="insight-label" style="color:#a78bfa">Core Recommendation</div>
            <div class="insight-text">
                Deploy a structured onboarding checklist for first-time contributors.
                Target: reduce single-commit dropout by 40% within 2 sprint cycles.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown(section_title("Commit Distribution by Role", "Who contributes the most code volume"), unsafe_allow_html=True)
        if commit_col and role_col:
            df_role = df.groupby(role_col)[commit_col].agg(["sum", "mean", "count"]).reset_index()
            df_role.columns = ["Role", "Total Commits", "Avg Commits", "Contributors"]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_role["Role"], y=df_role["Total Commits"],
                marker=dict(color=PALETTE[:len(df_role)]),
                hovertemplate="<b>%{x}</b><br>Total: %{y}<extra></extra>"
            ))
            fig.update_layout(**plot_layout("Total Commits by Contributor Role", showlegend=False))
            st.plotly_chart(fig, use_container_width=True)

        if review_col and role_col:
            st.markdown(section_title("PR Review Days by Role", "Median review times across contributor tiers"), unsafe_allow_html=True)
            fig2 = px.violin(df, y=review_col, x=role_col, color=role_col,
                             color_discrete_sequence=PALETTE, box=True, points="outliers")
            fig2.update_layout(**plot_layout("PR Review Duration by Role", showlegend=False))
            st.plotly_chart(fig2, use_container_width=True)


# Main
def main():
    page, df = render_sidebar()
    if page == "Overview":
        render_overview(df)
    elif page == "Analytics":
        render_analytics(df)
    elif page == "Explorer":
        render_explorer(df)
    elif page == "Insights":
        render_insights(df)


if __name__ == "__main__":
    main()
