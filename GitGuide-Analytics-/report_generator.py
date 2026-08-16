"""
Structured Report Generator Subsystem
GitGuide Analytics

Generates formatted executive intelligence reports from analysis DataFrames
with three required sections: KPI Summary, Key Findings, and Recommended Actions.
"""

from datetime import datetime
import pandas as pd
import numpy as np


def generate_report(df, report_date=None):
    """
    Generate a structured text report from analysis output.

    Args:
        df (pd.DataFrame): Input dataset / filtered DataFrame
        report_date (str or date, optional): Report timestamp

    Returns:
        str: Multi-section formatted plain-text executive summary
    """
    if report_date is None:
        report_date = datetime.now().strftime("%Y-%m-%d")

    # Column resolution logic
    commit_col = next((c for c in ["commits_count", "commits", "total_contributions", "revenue"] if c in df.columns), df.select_dtypes(include=np.number).columns[0] if len(df.select_dtypes(include=np.number).columns) else None)
    entity_col = next((c for c in ["contributor_login", "customer_id", "user_id", "contributor_id"] if c in df.columns), df.columns[0])
    review_col = next((c for c in ["avg_pr_review_days", "pr_review_days", "review_days"] if c in df.columns), None)
    role_col   = next((c for c in ["contributor_role", "role", "segment", "category"] if c in df.columns), None)

    # Compute key metrics
    total_vol = int(df[commit_col].sum()) if commit_col and len(df) else 0
    avg_vol   = float(df[commit_col].mean()) if commit_col and len(df) else 0.0
    active_entities = df[entity_col].nunique() if entity_col and len(df) else len(df)
    avg_review = float(df[review_col].mean()) if review_col and len(df) else 0.0

    lines = []
    lines.append("==================================================")
    lines.append("            WEEKLY ANALYTICS REPORT               ")
    lines.append("==================================================")
    lines.append(f"Date: {report_date}")
    lines.append(f"Dataset Scope: {len(df):,} records analyzed")
    lines.append("")

    # Section 1: KPI Summary
    lines.append("== KPI SUMMARY ==")
    lines.append(f"Total Volume / Contributions: {total_vol:,}")
    lines.append(f"Active Entities / Contributors: {active_entities:,}")
    lines.append(f"Average Volume per Unit: {avg_vol:.1f}")
    if review_col:
        lines.append(f"Average PR Review Latency: {avg_review:.1f} days")
    lines.append("")

    # Section 2: Key Finding
    lines.append("== KEY FINDING ==")
    if role_col and commit_col and len(df):
        top_segment = df.groupby(role_col)[commit_col].sum().idxmax()
        top_volume  = df.groupby(role_col)[commit_col].sum().max()
        lines.append(f"Top performing segment: '{top_segment}' with {top_volume:,} total contributions.")
    else:
        lines.append("Top performing segment: General Cohort.")

    if commit_col and len(df):
        single_commit_ratio = (df[commit_col] == 1).mean() * 100
        lines.append(f"Single-contribution drop-off rate: {single_commit_ratio:.1f}%.")
    if review_col and avg_review > 3.0:
        lines.append(f"ALERT: Average PR review latency ({avg_review:.1f} days) exceeds 3-day target.")
    lines.append("")

    # Section 3: Recommended Action
    lines.append("== RECOMMENDED ACTION ==")
    lines.append("1. Enforce a 24-hour PR triage SLA to reduce contributor drop-off.")
    lines.append("2. Reallocate engineering review capacity to high-volume categories.")
    lines.append("3. Deploy automated onboarding checklists for first-time contributors.")

    return "\n".join(lines)


if __name__ == "__main__":
    test_df = pd.DataFrame({
        "contributor_login": ["alice", "bob", "charlie"],
        "commits_count": [40, 15, 1],
        "contributor_role": ["Maintainer", "Reviewer", "Contributor"],
        "avg_pr_review_days": [0.8, 2.4, 5.1]
    })
    report_out = generate_report(test_df, "2026-08-16")
    print(report_out)
