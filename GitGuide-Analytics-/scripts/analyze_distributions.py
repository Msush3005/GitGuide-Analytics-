"""
Distribution Analysis, Statistical Profiling & Visual Segmentation Pipeline
GitGuide-Analytics

Analyzes statistical distributions of customer revenue and transaction metrics:
1. Calculates Mean, Median, Skewness, and Kurtosis using scipy.stats.
2. Generates business interpretation flags (Mean vs. Median suitability, heavy-tail risks).
3. Plots combined Histogram & KDE density visualizations.
4. Compares High-Value (>= Q3) vs. Low-Value (<= Q1) customer spend distributions.

Execution:
    python scripts/analyze_distributions.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from scipy import stats

# Ensure non-interactive backend for headless plot generation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


def generate_bimodal_revenue_dataset(output_path, num_records=5000):
    """
    Generate synthetic bimodal & right-skewed revenue dataset (5,000 records).
    Simulates 80% small SMB accounts and 20% large Enterprise accounts.
    
    Args:
        output_path (str): File destination path.
        num_records (int): Number of customer rows (default 5000).
        
    Returns:
        pd.DataFrame: Generated raw DataFrame.
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    n_smb = int(num_records * 0.8)
    n_enterprise = num_records - n_smb

    # 80% SMB customers (mean ~$350, right-skewed)
    smb_revenue = np.random.exponential(scale=350.0, size=n_smb) + 50.0
    
    # 20% Enterprise customers (mean ~$25,000, higher variance)
    enterprise_revenue = np.random.normal(loc=25000.0, scale=4000.0, size=n_enterprise)

    revenue = np.concatenate([smb_revenue, enterprise_revenue])
    np.random.shuffle(revenue)
    revenue = np.round(revenue, 2)

    customer_ids = np.arange(200001, 200001 + num_records)

    df_raw = pd.DataFrame({
        'customer_id': customer_ids,
        'revenue': revenue
    })

    df_raw.to_csv(output_path, index=False)
    print(f"✓ Generated bimodal revenue dataset ({num_records:,} records) at: {output_path}")
    return df_raw


def compute_distribution_statistics(df, column='revenue'):
    """
    Compute statistical distribution metrics (mean, median, std, skewness, kurtosis).
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column name.
        
    Returns:
        dict: Detailed statistics dictionary.
    """
    data = df[column].dropna()

    mean_val = float(data.mean())
    median_val = float(data.median())
    std_val = float(data.std())
    min_val = float(data.min())
    max_val = float(data.max())
    q1_val = float(data.quantile(0.25))
    q3_val = float(data.quantile(0.75))

    skewness = float(stats.skew(data))
    kurtosis = float(stats.kurtosis(data))  # Fisher's kurtosis (normal == 0, excess > 3 is heavy-tailed)

    # Business Interpretation Logic
    skew_interpretation = "Symmetric distribution."
    if abs(skewness) > 1.0:
        skew_interpretation = "Highly skewed distribution; median is preferred over mean."
    elif abs(skewness) > 0.5:
        skew_interpretation = "Moderately skewed distribution."

    kurt_interpretation = "Normal tail distribution."
    if kurtosis > 3.0:
        kurt_interpretation = "Heavy-tailed distribution (leptokurtic); high probability of extreme outliers."

    print(f"\n--- Statistical Distribution Profiling ({column}) ---")
    print(f"Mean:     ${mean_val:,.2f}")
    print(f"Median:   ${median_val:,.2f}")
    print(f"Std Dev:  ${std_val:,.2f}")
    print(f"Min / Max: ${min_val:,.2f} / ${max_val:,.2f}")
    print(f"Q1 / Q3:  ${q1_val:,.2f} / ${q3_val:,.2f}")
    print(f"Skewness: {skewness:.2f} ({skew_interpretation})")
    print(f"Kurtosis: {kurtosis:.2f} ({kurt_interpretation})")

    stats_dict = {
        'column': column,
        'count': len(data),
        'mean': round(mean_val, 2),
        'median': round(median_val, 2),
        'std': round(std_val, 2),
        'min': round(min_val, 2),
        'max': round(max_val, 2),
        'q1_25th': round(q1_val, 2),
        'q3_75th': round(q3_val, 2),
        'skewness': round(skewness, 2),
        'kurtosis': round(kurtosis, 2),
        'skewness_interpretation': skew_interpretation,
        'kurtosis_interpretation': kurt_interpretation
    }

    return stats_dict


def plot_distribution_shape(df, column='revenue', output_path='output/distribution_plots.png'):
    """
    Plot and save combined Histogram and KDE density curve showing distribution shape.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column.
        output_path (str): Image destination path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    mean_val = df[column].mean()
    median_val = df[column].median()

    plt.figure(figsize=(12, 6))
    sns.histplot(df[column], kde=True, bins=50, color='indigo', stat='density', alpha=0.6)

    plt.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: ${mean_val:,.2f}')
    plt.axvline(median_val, color='green', linestyle='-', linewidth=2, label=f'Median: ${median_val:,.2f}')

    plt.title(f'Customer {column.capitalize()} Distribution (Histogram + KDE Density)', fontsize=14, fontweight='bold')
    plt.xlabel(f'{column.capitalize()} ($)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(fontsize=11)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✓ Saved distribution plot to: {output_path}")


def plot_segment_comparison(df, column='revenue', output_path='output/segment_distribution_comparison.png'):
    """
    Partition customers into High-Value (>= Q3) and Low-Value (<= Q1) segments
    and plot overlapping comparative distributions.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column.
        output_path (str): Image destination path.
        
    Returns:
        pd.DataFrame: DataFrame with segment_tier column added.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_seg = df.copy()

    q1 = df_seg[column].quantile(0.25)
    q3 = df_seg[column].quantile(0.75)

    # Segment classification
    conditions = [
        (df_seg[column] >= q3),
        (df_seg[column] <= q1)
    ]
    choices = ['high_value', 'low_value']
    df_seg['segment_tier'] = np.select(conditions, choices, default='mid_value')

    high_value = df_seg[df_seg['segment_tier'] == 'high_value']
    low_value = df_seg[df_seg['segment_tier'] == 'low_value']

    plt.figure(figsize=(12, 6))
    sns.kdeplot(high_value[column], color='darkgreen', fill=True, alpha=0.4, label=f'High-Value (>= ${q3:,.2f}, n={len(high_value)})')
    sns.kdeplot(low_value[column], color='crimson', fill=True, alpha=0.4, label=f'Low-Value (<= ${q1:,.2f}, n={len(low_value)})')

    plt.title('Customer Segment Spend Distribution Comparison (High-Value vs. Low-Value)', fontsize=14, fontweight='bold')
    plt.xlabel('Revenue ($)', fontsize=12)
    plt.ylabel('Density', fontsize=12)
    plt.legend(fontsize=11)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"✓ Saved segment comparison plot to: {output_path}")

    return df_seg


def export_distribution_report(stats_dict, df_processed, report_path, processed_path):
    """
    Export distribution audit log to JSON and processed dataset to CSV.
    
    Args:
        stats_dict (dict): Statistical profiling results.
        df_processed (pd.DataFrame): Processed DataFrame with segment tiers.
        report_path (str): JSON report path.
        processed_path (str): CSV output path.
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    # Save processed CSV
    df_processed.to_csv(processed_path, index=False)
    print(f"\n✓ Saved processed dataset to: {processed_path}")

    # Add segment counts to audit report
    stats_dict['segment_distribution'] = df_processed['segment_tier'].value_counts().to_dict()

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(stats_dict, f, indent=2)

    print(f"✓ Saved statistical distribution audit report to: {report_path}")
    print(json.dumps(stats_dict, indent=2))


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "bimodal_revenue_dataset.csv")
    processed_path = os.path.join(base_dir, "data", "processed", "distribution_analyzed_data.csv")
    plot_dist_path = os.path.join(base_dir, "output", "distribution_plots.png")
    plot_comp_path = os.path.join(base_dir, "output", "segment_distribution_comparison.png")
    report_path = os.path.join(base_dir, "output", "distribution_analysis_report.json")

    print("==============================================================")
    print("RUNNING DISTRIBUTION ANALYSIS & STATISTICAL PROFILING PIPELINE")
    print("==============================================================\n")

    # Step 1: Generate or load bimodal dataset
    df_raw = generate_bimodal_revenue_dataset(raw_path, num_records=5000)

    # Step 2: Compute statistical profiling & skewness/kurtosis
    stats_dict = compute_distribution_statistics(df_raw, column='revenue')

    # Step 3: Plot distribution shape (Histogram + KDE)
    plot_distribution_shape(df_raw, column='revenue', output_path=plot_dist_path)

    # Step 4: Compare High-Value vs. Low-Value customer segments
    df_processed = plot_segment_comparison(df_raw, column='revenue', output_path=plot_comp_path)

    # Step 5: Export JSON report and CSV output
    export_distribution_report(stats_dict, df_processed, report_path, processed_path)
    print("==============================================================")
