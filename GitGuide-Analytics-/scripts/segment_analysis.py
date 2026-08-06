import os
import json
import numpy as np
import pandas as pd


def generate_segment_dataset(num_rows=1000, filepath="data/raw/customer_churn_segment.csv"):
    """
    Generates synthetic customer churn and revenue dataset aligned with the real scenario:
    - Enterprise (5% of base): ~1% churn rate, high revenue contribution (~70%)
    - SMB (40% of base): ~12% churn rate, moderate revenue contribution
    - Startups (55% of base): ~8% churn rate, lower individual revenue
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic customer dataset with {num_rows} records...")
        np.random.seed(42)

        # Distribute segments according to scenario ratios
        types = np.random.choice(
            ['Enterprise', 'SMB', 'Startup'],
            size=num_rows,
            p=[0.05, 0.40, 0.55]
        )
        products = np.random.choice(
            ['Cloud Pro', 'Analytics Suite', 'Enterprise Core'],
            size=num_rows,
            p=[0.35, 0.40, 0.25]
        )

        customer_ids = [f"CUST_{i:05d}" for i in range(1, num_rows + 1)]
        revenue_list = []
        churn_list = []
        tickets_list = []

        for ctype in types:
            if ctype == 'Enterprise':
                revenue = np.random.normal(loc=14000, scale=2000)
                churn = 1 if np.random.rand() < 0.01 else 0
                tickets = np.random.poisson(lam=1.2)
            elif ctype == 'SMB':
                revenue = np.random.normal(loc=1000, scale=200)
                churn = 1 if np.random.rand() < 0.12 else 0
                tickets = np.random.poisson(lam=4.5)
            else:  # Startup
                revenue = np.random.normal(loc=500, scale=100)
                churn = 1 if np.random.rand() < 0.08 else 0
                tickets = np.random.poisson(lam=2.8)

            revenue_list.append(round(max(revenue, 100.0), 2))
            churn_list.append(churn)
            tickets_list.append(max(tickets, 0))

        df_raw = pd.DataFrame({
            'customer_id': customer_ids,
            'customer_type': types,
            'product': products,
            'revenue': revenue_list,
            'churn': churn_list,
            'support_tickets': tickets_list
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset created successfully at {filepath}.")
    else:
        print(f"Loading dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)

    return df_raw


def task1_single_level_groupby(df):
    """
    Task 1: Single-Level GroupBy with Multiple Aggregations
    Computes churn rate, total revenue, customer count, and average support tickets per customer_type.
    """
    print("\n--- Task 1: Single-Level GroupBy with Multiple Aggregations ---")
    segment_metrics = df.groupby('customer_type').agg({
        'churn': 'mean',
        'revenue': 'sum',
        'customer_id': 'count',
        'support_tickets': 'mean'
    })
    segment_metrics.columns = [
        'churn_rate', 'total_revenue', 'customer_count', 'avg_support_tickets'
    ]
    print(segment_metrics)
    return segment_metrics


def task2_multi_level_groupby(df):
    """
    Task 2: Multi-Level GroupBy across customer_type and product dimensions.
    """
    print("\n--- Task 2: Multi-Level GroupBy (customer_type & product) ---")
    product_segment = df.groupby(['customer_type', 'product']).agg({
        'revenue': 'sum',
        'customer_id': 'count'
    })
    product_segment.columns = ['total_revenue', 'customer_count']
    product_segment_pivot = product_segment.unstack()
    print(product_segment_pivot)
    return product_segment, product_segment_pivot


def task3_pivot_table(df):
    """
    Task 3: 2D Pivot Table summarizing revenue by customer_type (rows) and product (columns).
    """
    print("\n--- Task 3: Pivot Table (customer_type vs product revenue) ---")
    pivot = pd.pivot_table(
        df,
        values='revenue',
        index='customer_type',
        columns='product',
        aggfunc='sum'
    )
    print(pivot)
    return pivot


def task4_rank_and_identify_performers(segment_metrics):
    """
    Task 4: Rank segments by churn rate and calculate revenue contribution % of total.
    """
    print("\n--- Task 4: Segment Ranking & Revenue Contribution ---")
    # Rank segments by churn (1 = lowest churn / best performance)
    segment_metrics['churn_rank'] = segment_metrics['churn_rate'].rank()
    
    # Sort worst churn first
    worst_first = segment_metrics.sort_values('churn_rate', ascending=False)
    print("Worst Churn Segments First:")
    print(worst_first)

    # Compute percentage contribution of total revenue
    segment_metrics['revenue_contribution'] = (
        segment_metrics['total_revenue'] / segment_metrics['total_revenue'].sum() * 100
    )
    print("\nRevenue Contribution & Churn Rate:")
    print(segment_metrics[['revenue_contribution', 'churn_rate']])
    return segment_metrics


def task5_surface_actionable_insights(segment_metrics):
    """
    Task 5: Surface Actionable Segment Insights and export to CSV.
    """
    print("\n--- Task 5: Surface Actionable Segment Insights ---")
    insights = []
    for segment in segment_metrics.index:
        row = segment_metrics.loc[segment]
        insight = {
            'segment': segment,
            'customer_count': int(row['customer_count']),
            'churn_rate': f"{row['churn_rate']:.1%}",
            'total_revenue': f"${row['total_revenue']:.0f}",
            'revenue_contribution': f"{row['revenue_contribution']:.1f}%",
            'action': ''
        }

        if row['churn_rate'] > 0.10:
            insight['action'] = 'HIGH PRIORITY: Churn above 10%. Investigate pain points.'
        elif row['churn_rate'] < 0.02:
            insight['action'] = 'Healthy. Maintain current service level.'
        else:
            insight['action'] = 'Monitor. No immediate action needed.'

        insights.append(insight)

    insights_df = pd.DataFrame(insights)
    print(insights_df.to_string(index=False))

    os.makedirs("output", exist_ok=True)
    output_path = "output/segment_insights.csv"
    insights_df.to_csv(output_path, index=False)
    print(f"\nSaved segment insights report to: {output_path}")
    return insights_df


def main():
    print("=" * 60)
    print("  GroupBy Aggregation & Segment Insights Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Ingest data
    df = generate_segment_dataset()

    # Execute Tasks 1 - 5
    segment_metrics = task1_single_level_groupby(df)
    product_segment, product_segment_pivot = task2_multi_level_groupby(df)
    pivot = task3_pivot_table(df)
    segment_metrics = task4_rank_and_identify_performers(segment_metrics)
    insights_df = task5_surface_actionable_insights(segment_metrics)

    # Save summary json and pivot output
    segment_metrics.to_csv("data/processed/segmented_customers.csv")
    pivot.to_csv("output/segment_pivot.csv")

    print("\n[SUCCESS] GroupBy Aggregation & Segment Insights Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
