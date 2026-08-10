import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_behavioral_dataset(num_rows=1000, filepath="data/raw/customer_behavioral_data.csv"):
    """
    Generates synthetic customer behavioral dataset with 3 segments:
    - Enterprise (5% of base): High LTV (~$150k), low churn (~1%), low support tickets (~1.2), long retention (~1250 days)
    - SMB (40% of base): Moderate LTV (~$8k), high churn (~12%), high support tickets (~4.5), moderate retention (~420 days)
    - Startup (55% of base): Lower LTV (~$2k), moderate churn (~8%), moderate support tickets (~2.8), lower retention (~280 days)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic customer behavioral dataset ({num_rows} records)...")
        np.random.seed(42)

        types = np.random.choice(
            ['Enterprise', 'SMB', 'Startup'],
            size=num_rows,
            p=[0.05, 0.40, 0.55]
        )

        customer_ids = [f"CUST_{i:05d}" for i in range(1, num_rows + 1)]
        ltv_list = []
        churn_list = []
        tickets_list = []
        retention_list = []

        for ctype in types:
            if ctype == 'Enterprise':
                ltv = np.random.normal(loc=150000, scale=15000)
                churn = 1 if np.random.rand() < 0.01 else 0
                tickets = np.random.poisson(lam=1.2)
                retention = np.random.normal(loc=1250, scale=100)
            elif ctype == 'SMB':
                ltv = np.random.normal(loc=8000, scale=1000)
                churn = 1 if np.random.rand() < 0.12 else 0
                tickets = np.random.poisson(lam=4.5)
                retention = np.random.normal(loc=420, scale=60)
            else:  # Startup
                ltv = np.random.normal(loc=2000, scale=300)
                churn = 1 if np.random.rand() < 0.08 else 0
                tickets = np.random.poisson(lam=2.8)
                retention = np.random.normal(loc=280, scale=40)

            ltv_list.append(round(max(ltv, 500.0), 2))
            churn_list.append(churn)
            tickets_list.append(max(tickets, 0))
            retention_list.append(round(max(retention, 30.0), 1))

        df_raw = pd.DataFrame({
            'customer_id': customer_ids,
            'customer_type': types,
            'lifetime_value': ltv_list,
            'churn': churn_list,
            'support_tickets': tickets_list,
            'retention_days': retention_list
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset created successfully at {filepath}.")
    else:
        print(f"Loading dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)

    return df_raw


def task1_define_segments_and_compute_metrics(df):
    """
    Task 1: Define Segments and Compute 4+ Metrics per Segment.
    """
    print("\n--- Task 1: Segment Metrics & Sample Sizes ---")
    segment_metrics = df.groupby('customer_type').agg({
        'lifetime_value': 'mean',
        'churn': 'mean',
        'support_tickets': 'mean',
        'retention_days': 'mean',
        'customer_id': 'count'
    })
    segment_metrics.columns = ['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention', 'count']
    print(segment_metrics)
    return segment_metrics


def task2_summary_statistics_table(segment_metrics):
    """
    Task 2: Summary Statistics Table with Rankings and Readable Formatting.
    """
    print("\n--- Task 2: Formatted Summary Statistics & Segment Rankings ---")
    segment_summary = segment_metrics.copy()
    segment_summary['ltv_rank'] = segment_summary['avg_ltv'].rank(ascending=False)
    segment_summary['churn_rank'] = segment_summary['churn_rate'].rank(ascending=True)

    formatted_summary = segment_summary.copy()
    formatted_summary['formatted_ltv'] = formatted_summary['avg_ltv'].apply(lambda x: f"${x:,.0f}")
    formatted_summary['formatted_churn'] = formatted_summary['churn_rate'].apply(lambda x: f"{x:.1%}")
    formatted_summary['formatted_retention'] = formatted_summary['avg_retention'].apply(lambda x: f"{x:.0f} days")

    display_cols = ['formatted_ltv', 'ltv_rank', 'formatted_churn', 'churn_rank', 'formatted_retention', 'count']
    print(formatted_summary[display_cols])
    return formatted_summary


def task3_visual_comparison_heatmap(segment_metrics):
    """
    Task 3: Visual Comparison Heatmap across segments.
    Exports visualization to output/segment_heatmap.png.
    """
    print("\n--- Task 3: Visual Comparison Heatmap ---")
    os.makedirs("output", exist_ok=True)
    
    # Try importing seaborn, fallback to matplotlib if unavailable
    try:
        import seaborn as sns
        plt.figure(figsize=(9, 5))
        # Display actual values as annotations while scaling values for color mapping
        heat_data = segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention']].copy()
        
        # Min-max scale per column for color map contrast
        heat_data_scaled = (heat_data - heat_data.min()) / (heat_data.max() - heat_data.min())
        
        sns.heatmap(
            heat_data_scaled,
            annot=heat_data.to_numpy(),
            fmt=".1f",
            cmap="RdYlGn",
            cbar_kws={'label': 'Metric Level (Red=Low/High-Churn, Green=Favorable)'}
        )
        plt.title("Segment Comparison Heatmap", fontsize=14, fontweight="bold")
        plt.tight_layout()
        plot_path = "output/segment_heatmap.png"
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"Saved Seaborn heatmap visualization to: {plot_path}")
    except Exception as e:
        print(f"Seaborn heatmap generation warning ({e}), fallback to Matplotlib...")
        fig, ax = plt.subplots(figsize=(9, 5))
        heat_data = segment_metrics[['avg_ltv', 'churn_rate', 'avg_tickets', 'avg_retention']].copy()
        cax = ax.matshow(heat_data.values, cmap='RdYlGn')
        fig.colorbar(cax)
        ax.set_xticks(range(len(heat_data.columns)))
        ax.set_yticks(range(len(heat_data.index)))
        ax.set_xticklabels(heat_data.columns)
        ax.set_yticklabels(heat_data.index)
        plt.title("Segment Comparison Matrix", fontsize=14, fontweight="bold")
        plot_path = "output/segment_heatmap.png"
        plt.savefig(plot_path, dpi=300)
        plt.close()
        print(f"Saved Matplotlib matrix visualization to: {plot_path}")


def task4_top_and_bottom_performers(segment_metrics):
    """
    Task 4: Identify Top and Bottom Performing Segments.
    """
    print("\n--- Task 4: Top and Bottom Performer Analysis ---")
    top_segment = segment_metrics['avg_ltv'].idxmax()
    top_value = segment_metrics.loc[top_segment, 'avg_ltv']

    high_churn = segment_metrics['churn_rate'].idxmax()
    high_churn_val = segment_metrics.loc[high_churn, 'churn_rate']

    best_retention = segment_metrics['avg_retention'].idxmax()
    best_retention_val = segment_metrics.loc[best_retention, 'avg_retention']

    performer_text = f"""TOP & BOTTOM PERFORMER ANALYSIS SUMMARY:
- HIGHEST VALUE SEGMENT   : {top_segment} (${top_value:,.0f} Avg LTV)
- HIGHEST CHURN SEGMENT   : {high_churn} ({high_churn_val:.1%} Churn Rate)
- BEST RETENTION SEGMENT  : {best_retention} ({best_retention_val:.0f} Days Avg Retention)
"""
    print(performer_text)
    return performer_text


def task5_business_facing_insights(segment_metrics, performer_text):
    """
    Task 5: Surface Business-Facing Insights & Action Recommendations.
    Saves output report to output/segment_behavior_summary.txt.
    """
    print("\n--- Task 5: Business-Facing Segment Insights ---")
    business_summary = f"""============================================================
BEHAVIOURAL ANALYSIS & USER SEGMENTATION REPORT
============================================================

1. {performer_text}

2. SEGMENT STRATEGY SUMMARY & ACTION RECOMMENDATIONS:

Enterprise Segment (5% of customer base, ${segment_metrics.loc['Enterprise', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['Enterprise', 'churn_rate']:.1%} churn, {segment_metrics.loc['Enterprise', 'avg_retention']:.0f} days retention):
- Highest value and strongest retention segment with low churn risk.
- Action: Maintain high-touch account management, provide dedicated Customer Success Managers, and prioritize enterprise feature requests.

SMB Segment (40% of customer base, ${segment_metrics.loc['SMB', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['SMB', 'churn_rate']:.1%} churn, {segment_metrics.loc['SMB', 'avg_retention']:.0f} days retention):
- Middle-value segment suffering from an alarming {segment_metrics.loc['SMB', 'churn_rate']:.1%} churn rate and high support ticket load ({segment_metrics.loc['SMB', 'avg_tickets']:.1f} tickets/cust).
- Action: HIGH PRIORITY INTERVENTION — Improve onboarding workflows, introduce self-service support tools, and offer affordable premium support packages.

Startup Segment (55% of customer base, ${segment_metrics.loc['Startup', 'avg_ltv']:,.0f} LTV, {segment_metrics.loc['Startup', 'churn_rate']:.1%} churn, {segment_metrics.loc['Startup', 'avg_retention']:.0f} days retention):
- Highest volume, lower individual value segment with moderate churn.
- Action: Deploy automated self-service documentation, community forums, and automated email nurturing sequences to minimize support costs.
============================================================
"""
    print(business_summary)

    os.makedirs("output", exist_ok=True)
    report_path = "output/segment_behavior_summary.txt"
    with open(report_path, "w") as f:
        f.write(business_summary)
    print(f"Saved segment behavior summary report to: {report_path}")

    return business_summary


def main():
    print("=" * 60)
    print("  Behavioural Analysis & User Segmentation Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_behavioral_dataset()
    segment_metrics = task1_define_segments_and_compute_metrics(df)
    formatted_summary = task2_summary_statistics_table(segment_metrics)
    task3_visual_comparison_heatmap(segment_metrics)
    performer_text = task4_top_and_bottom_performers(segment_metrics)
    task5_business_facing_insights(segment_metrics, performer_text)

    segment_metrics.to_csv("data/processed/segment_behavior_metrics.csv")
    print("\n[SUCCESS] Behavioural Analysis & User Segmentation Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
