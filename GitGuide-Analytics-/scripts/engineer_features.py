"""
Business Feature Engineering & Customer Segmentation Pipeline
GitGuide-Analytics

Engineers contextual business features from raw operational metrics:
1. Ratio Features: Normalizes activity and spending by time and volume.
2. Binned Features: Segment customers using pd.cut (fixed ranges) and pd.qcut (quantiles).
3. Composite Scores: Constructs RFM (Recency, Frequency, Monetary) health scores.

Execution:
    python scripts/engineer_features.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np


def generate_synthetic_customer_activity(output_path, num_records=1000):
    """
    Generate synthetic customer activity metrics for feature engineering.
    
    Args:
        output_path (str): CSV destination path.
        num_records (int): Number of customer rows to generate (default 1000).
        
    Returns:
        pd.DataFrame: Generated raw DataFrame.
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    customer_ids = np.arange(1001, 1001 + num_records)
    days_as_customer = np.random.randint(30, 1095, size=num_records)  # 1 month to 3 years
    total_transactions = np.random.randint(1, 120, size=num_records)
    total_spent = np.round(np.random.uniform(50.0, 10000.0, size=num_records), 2)
    days_since_last_purchase = np.random.randint(1, 365, size=num_records)

    df_raw = pd.DataFrame({
        'customer_id': customer_ids,
        'days_as_customer': days_as_customer,
        'total_transactions': total_transactions,
        'total_spent': total_spent,
        'days_since_last_purchase': days_since_last_purchase
    })

    df_raw.to_csv(output_path, index=False)
    print(f"✓ Generated raw customer activity dataset ({num_records} records) at: {output_path}")
    return df_raw


def create_ratio_features(df):
    """
    Construct time-normalized and volume-normalized ratio features.
    
    Ratios:
        - transactions_per_month: total_transactions / (days_as_customer / 30)
        - avg_spend_per_transaction: total_spent / total_transactions
        - lifetime_value_per_month: total_spent / (days_as_customer / 30)
        
    Args:
        df (pd.DataFrame): Input DataFrame with raw metrics.
        
    Returns:
        pd.DataFrame: DataFrame with engineered ratio features.
    """
    df_feat = df.copy()

    # Time normalization factor (months)
    months = df_feat['days_as_customer'] / 30.0

    # 1. Transactions per month
    df_feat['transactions_per_month'] = np.round(df_feat['total_transactions'] / months, 2)

    # 2. Average spend per transaction
    df_feat['avg_spend_per_transaction'] = np.round(df_feat['total_spent'] / df_feat['total_transactions'], 2)

    # 3. Lifetime value per month
    df_feat['lifetime_value_per_month'] = np.round(df_feat['total_spent'] / months, 2)

    print("\n--- Step 1: Engineered Ratio Features ---")
    print(df_feat[['customer_id', 'transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month']].head().to_string(index=False))

    return df_feat


def create_binned_features(df):
    """
    Apply fixed-range binning (pd.cut) and quantile binning (pd.qcut).
    
    Bins:
        - engagement_bin_equal: pd.cut on transactions_per_month (low: 0-2, medium: 2-10, high: >10)
        - spend_tier_quantile: pd.qcut on total_spent (tier_1 to tier_4)
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with binned features.
    """
    df_binned = df.copy()

    # 1. Fixed-range binning for engagement tier
    df_binned['engagement_bin_equal'] = pd.cut(
        df_binned['transactions_per_month'],
        bins=[0, 2, 10, np.inf],
        labels=['low', 'medium', 'high'],
        include_lowest=True
    )

    # 2. Equal-frequency quantile binning for spend tier
    df_binned['spend_tier_quantile'] = pd.qcut(
        df_binned['total_spent'],
        q=4,
        labels=['tier_1', 'tier_2', 'tier_3', 'tier_4']
    )

    print("\n--- Step 2: Binned Categorical Tiers ---")
    print("Engagement Tier Counts (pd.cut):")
    print(df_binned['engagement_bin_equal'].value_counts().to_string())
    print("\nSpend Tier Counts (pd.qcut):")
    print(df_binned['spend_tier_quantile'].value_counts().to_string())

    return df_binned


def compute_rfm_composite_score(df):
    """
    Compute RFM (Recency, Frequency, Monetary) 5-quantile scores and aggregate rfm_score.
    
    Scores:
        - recency_score: qcut on days_since_last_purchase (reverse labels: 5,4,3,2,1)
        - frequency_score: qcut on total_transactions (labels: 1,2,3,4,5)
        - monetary_score: qcut on total_spent (labels: 1,2,3,4,5)
        - rfm_score: sum of recency + frequency + monetary scores
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with RFM scores.
    """
    df_rfm = df.copy()

    # 1. Recency Score (lower days = higher score)
    df_rfm['recency_score'] = pd.qcut(
        df_rfm['days_since_last_purchase'],
        q=5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # 2. Frequency Score (higher transactions = higher score, using rank method='first' for smooth quantiles)
    df_rfm['frequency_score'] = pd.qcut(
        df_rfm['total_transactions'].rank(method='first'),
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # 3. Monetary Score (higher spend = higher score)
    df_rfm['monetary_score'] = pd.qcut(
        df_rfm['total_spent'],
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # 4. Composite RFM Score
    df_rfm['rfm_score'] = (
        df_rfm['recency_score'] +
        df_rfm['frequency_score'] +
        df_rfm['monetary_score']
    )

    print("\n--- Step 3: Composite RFM Scores ---")
    print(df_rfm[['customer_id', 'recency_score', 'frequency_score', 'monetary_score', 'rfm_score']].head().to_string(index=False))
    print(f"\nRFM Score Summary (Min: {df_rfm['rfm_score'].min()}, Max: {df_rfm['rfm_score'].max()}, Mean: {df_rfm['rfm_score'].mean():.2f})")

    return df_rfm


def export_feature_report(df, report_path):
    """
    Export feature distribution summary statistics to JSON report.
    
    Args:
        df (pd.DataFrame): Processed DataFrame with engineered features.
        report_path (str): Destination path for JSON report.
        
    Returns:
        dict: Summary report content.
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    ratio_cols = ['transactions_per_month', 'avg_spend_per_transaction', 'lifetime_value_per_month']
    stats_summary = {}

    for col in ratio_cols:
        stats_summary[col] = {
            'mean': round(float(df[col].mean()), 2),
            'std': round(float(df[col].std()), 2),
            'min': round(float(df[col].min()), 2),
            'max': round(float(df[col].max()), 2)
        }

    report = {
        'total_records': len(df),
        'ratio_feature_stats': stats_summary,
        'engagement_tier_distribution': df['engagement_bin_equal'].value_counts().to_dict(),
        'spend_tier_distribution': df['spend_tier_quantile'].value_counts().to_dict(),
        'rfm_score_stats': {
            'min': int(df['rfm_score'].min()),
            'max': int(df['rfm_score'].max()),
            'mean': round(float(df['rfm_score'].mean()), 2),
            'median': round(float(df['rfm_score'].median()), 2)
        }
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Saved feature engineering audit report to: {report_path}")
    return report


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "customer_activity.csv")
    processed_path = os.path.join(base_dir, "data", "processed", "engineered_features.csv")
    report_path = os.path.join(base_dir, "output", "feature_engineering_report.json")

    print("==============================================================")
    print("RUNNING BUSINESS FEATURE ENGINEERING & SEGMENTATION PIPELINE")
    print("==============================================================\n")

    # Step 1: Generate or load raw customer activity
    df_raw = generate_synthetic_customer_activity(raw_path, num_records=1000)

    # Step 2: Ratio Features
    df_ratios = create_ratio_features(df_raw)

    # Step 3: Binned Features (pd.cut & pd.qcut)
    df_binned = create_binned_features(df_ratios)

    # Step 4: Composite RFM Scores
    df_rfm = compute_rfm_composite_score(df_binned)

    # Step 5: Save Processed Data & Export Audit Report
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df_rfm.to_csv(processed_path, index=False)
    print(f"\n✓ Saved processed engineered features dataset to: {processed_path}")

    export_feature_report(df_rfm, report_path)
    print("==============================================================")
