import os
import matplotlib.pyplot as plt
import pandas as pd


def generate_dashboard_charts(output_dir="output"):
    """
    Generates static PNG charts for Level 2 (Trends) and Level 3 (Segments) sections.
    """
    os.makedirs(output_dir, exist_ok=True)

    months = pd.date_range("2024-01-01", periods=12, freq="ME")
    months_labels = months.strftime("%b")
    revenue = [4.2, 4.5, 4.8, 4.6, 5.0, 5.1, 4.9, 4.7, 5.2, 5.4, 5.5, 5.2]
    active_cust = [2100, 2150, 2220, 2280, 2350, 2400, 2420, 2450, 2470, 2480, 2490, 2500]
    churned_cust = [120, 115, 110, 105, 100, 98, 102, 105, 95, 90, 88, 85]
    aov_vals = [132, 134, 135, 138, 140, 141, 142, 140, 143, 144, 146, 145]

    # Chart 1: Revenue Trend Line Chart with Target Line
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(months_labels, revenue, marker="o", linewidth=2.5, color="#1f77b4", label="Actual Revenue")
    ax1.axhline(y=5.0, color="#2ca02c", linestyle="--", linewidth=1.8, label="Target: $5.0M")
    ax1.set_title("Monthly Revenue Trend (2024)", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Revenue ($M)", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper left")
    plt.tight_layout()
    chart1_path = os.path.join(output_dir, "revenue_trend.png")
    fig1.savefig(chart1_path, dpi=300)
    plt.close(fig1)
    print(f"Generated: {chart1_path}")

    # Chart 2: Active vs. Churned Customers Dual Line Chart
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.plot(months_labels, active_cust, marker="s", linewidth=2.5, color="#1f77b4", label="Active Customers")
    ax2_sub = ax2.twinx()
    ax2_sub.plot(months_labels, churned_cust, marker="^", linewidth=2.5, color="#d62728", label="Churned Customers")
    ax2.set_title("Active vs. Churned Customers Trend (2024)", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Month", fontsize=12)
    ax2.set_ylabel("Active Customers", fontsize=12, color="#1f77b4")
    ax2_sub.set_ylabel("Churned Customers", fontsize=12, color="#d62728")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    chart2_path = os.path.join(output_dir, "customer_metrics_trend.png")
    fig2.savefig(chart2_path, dpi=300)
    plt.close(fig2)
    print(f"Generated: {chart2_path}")

    # Chart 3: Average Order Value (AOV) Trend
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    ax3.plot(months_labels, aov_vals, marker="D", linewidth=2.5, color="#ff7f0e", label="AOV ($)")
    ax3.axhline(y=140.0, color="#1f77b4", linestyle=":", linewidth=1.5, label="Benchmark: $140")
    ax3.set_title("Average Order Value (AOV) Trend (2024)", fontsize=14, fontweight="bold")
    ax3.set_xlabel("Month", fontsize=12)
    ax3.set_ylabel("AOV ($)", fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc="lower right")
    plt.tight_layout()
    chart3_path = os.path.join(output_dir, "aov_trend.png")
    fig3.savefig(chart3_path, dpi=300)
    plt.close(fig3)
    print(f"Generated: {chart3_path}")

    # Chart 4: Revenue by Segment Horizontal Bar Chart
    segments = ["Enterprise", "Mid-Market", "SMB", "Starter"]
    segment_revenue = [2.1, 1.5, 1.0, 0.6]
    segment_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    fig4, ax4 = plt.subplots(figsize=(10, 5))
    bars = ax4.barh(segments, segment_revenue, color=segment_colors)
    ax4.set_xlabel("Revenue ($M)", fontsize=12)
    ax4.set_title("Revenue by Customer Segment", fontsize=14, fontweight="bold")
    for bar, val in zip(bars, segment_revenue):
        ax4.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2, f"${val}M", va="center", fontsize=11, fontweight="bold")
    ax4.set_xlim(0, 2.6)
    plt.tight_layout()
    chart4_path = os.path.join(output_dir, "revenue_by_segment.png")
    fig4.savefig(chart4_path, dpi=300)
    plt.close(fig4)
    print(f"Generated: {chart4_path}")

    print("\n[SUCCESS] All dashboard chart assets generated successfully!")


if __name__ == "__main__":
    generate_dashboard_charts()
