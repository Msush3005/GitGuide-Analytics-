import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Check if streamlit is available, otherwise define lightweight placeholder for CLI execution
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Ensure output directory exists
os.makedirs("output", exist_ok=True)


def build_dashboard_ui():
    """
    Main Streamlit Application Layout following 4-Level Information Hierarchy.
    """
    if not HAS_STREAMLIT:
        print("[INFO] Streamlit not installed. Running static asset build mode.")
        return

    st.set_page_config(
        page_title="Executive Business Performance Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Executive Business Performance Dashboard")
    st.caption("Human-Centered Dashboard Architecture based on 4-Level Information Hierarchy")

    # =========================================================================
    # LEVEL 1: STATUS (Top Row KPI Summary Cards - 5 Cards Max)
    # Answers: "Are we on track?"
    # =========================================================================
    st.subheader("Level 1: Status & KPI Summary")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Monthly Revenue", value="$5.2M", delta="+12.5% MoM")
    with col2:
        st.metric(label="Active Customers", value="2,500", delta="+5.2% MoM")
    with col3:
        st.metric(label="Avg Order Value", value="$145", delta="+3.1% MoM")
    with col4:
        st.metric(label="Churn Rate", value="4.8%", delta="-1.2% MoM", delta_color="inverse")
    with col5:
        st.metric(label="NPS Score", value="72", delta="+4 pts")

    st.divider()

    # =========================================================================
    # LEVEL 2: TRENDS (Time Series Charts)
    # Answers: "Is performance getting better or worse over time?"
    # =========================================================================
    st.subheader("Level 2: Performance Trends")
    trend_col1, trend_col2 = st.columns(2)

    months = pd.date_range("2024-01-01", periods=12, freq="ME")
    months_labels = months.strftime("%b")
    revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]
    active_cust = [2100, 2150, 2220, 2280, 2350, 2400, 2420, 2450, 2470, 2480, 2490, 2500]
    churned_cust = [120, 115, 110, 105, 100, 98, 102, 105, 95, 90, 88, 85]
    aov_vals = [132, 134, 135, 138, 140, 141, 142, 140, 143, 144, 146, 145]

    with trend_col1:
        st.markdown("##### Monthly Revenue Trend vs. Target ($5.0M)")
        fig1, ax1 = plt.subplots(figsize=(7, 3.5))
        ax1.plot(months_labels, revenue, marker="o", linewidth=2.5, color="#1f77b4", label="Actual Revenue")
        ax1.axhline(y=5.0, color="#2ca02c", linestyle="--", linewidth=1.8, label="Target: $5.0M")
        ax1.set_title("Monthly Revenue Trend (2024)", fontsize=11, fontweight="bold")
        ax1.set_xlabel("Month", fontsize=9)
        ax1.set_ylabel("Revenue ($M)", fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="upper left")
        plt.tight_layout()
        st.pyplot(fig1)

    with trend_col2:
        st.markdown("##### Active vs. Churned Customers Trend")
        fig2, ax2 = plt.subplots(figsize=(7, 3.5))
        ax2.plot(months_labels, active_cust, marker="s", linewidth=2, color="#1f77b4", label="Active Customers")
        ax2_sub = ax2.twinx()
        ax2_sub.plot(months_labels, churned_cust, marker="^", linewidth=2, color="#d62728", label="Churned Customers")
        ax2.set_title("Customer Metrics (Active vs. Churned)", fontsize=11, fontweight="bold")
        ax2.set_xlabel("Month", fontsize=9)
        ax2.set_ylabel("Active Customers", fontsize=9, color="#1f77b4")
        ax2_sub.set_ylabel("Churned Customers", fontsize=9, color="#d62728")
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig2)

    st.divider()

    # =========================================================================
    # LEVEL 3: SEGMENTS (Revenue Breakdown by Customer Tier)
    # Answers: "Which customer segments drive revenue and growth?"
    # =========================================================================
    st.subheader("Level 3: Segment Breakdown")
    seg_col1, seg_col2 = st.columns([1.2, 1])

    segments = ["Enterprise", "Mid-Market", "SMB", "Starter"]
    segment_revenue = [2.1, 1.5, 1.0, 0.6]
    segment_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    with seg_col1:
        st.markdown("##### Revenue Contribution by Customer Segment")
        fig3, ax3 = plt.subplots(figsize=(7, 3.5))
        bars = ax3.barh(segments, segment_revenue, color=segment_colors)
        ax3.set_xlabel("Revenue ($M)", fontsize=9)
        ax3.set_title("Revenue by Customer Segment", fontsize=11, fontweight="bold")
        for bar, val in zip(bars, segment_revenue):
            ax3.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, f"${val}M", va="center", fontsize=10, fontweight="bold")
        ax3.set_xlim(0, 2.6)
        plt.tight_layout()
        st.pyplot(fig3)

    with seg_col2:
        st.markdown("##### Segment Business Takeaways")
        st.info("""
        - **Enterprise**: Generates **40.4% ($2.1M)** of total revenue with highest ACV.
        - **Mid-Market**: Accounts for **28.8% ($1.5M)**, representing fastest MoM growth.
        - **SMB & Starter**: Provide steady volume ($1.6M combined) with low acquisition cost.
        """)

    st.divider()

    # =========================================================================
    # LEVEL 4: DETAIL & PROGRESSIVE DISCLOSURE (Filters & Raw Data Explorer)
    # Answers: "I noticed an anomaly, show me detailed record level data."
    # =========================================================================
    st.subheader("Level 4: Detailed Data Explorer (Progressive Disclosure)")

    st.sidebar.header("🔍 Interactive Filters")
    selected_segment = st.sidebar.selectbox("Customer Segment", ["All", "Enterprise", "Mid-Market", "SMB", "Starter"])
    date_range = st.sidebar.date_input("Date Range Filter", value=(pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31")))

    # Generate synthetic detailed customer table
    np.random.seed(42)
    num_records = 250
    df_detail = pd.DataFrame({
        "customer_id": [f"CUST_{1000 + i}" for i in range(num_records)],
        "segment": np.random.choice(["Enterprise", "Mid-Market", "SMB", "Starter"], size=num_records, p=[0.20, 0.30, 0.35, 0.15]),
        "revenue": np.round(np.random.exponential(scale=12000, size=num_records) + 500, 2),
        "last_activity": pd.date_range("2024-01-01", periods=num_records, freq="36h").strftime("%Y-%m-%d"),
        "churn_risk": np.random.choice(["Low", "Medium", "High"], size=num_records, p=[0.70, 0.20, 0.10])
    })

    if selected_segment != "All":
        filtered_df = df_detail[df_detail["segment"] == selected_segment]
    else:
        filtered_df = df_detail

    st.write(f"Showing **{len(filtered_df):,}** customer records matching filters:")
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered CSV Data",
        data=csv_data,
        file_name="filtered_customer_data.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    build_dashboard_ui()
