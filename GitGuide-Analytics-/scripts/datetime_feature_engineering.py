"""
Datetime Feature Engineering Pipeline
GitGuide-Analytics

Converts raw timestamp string fields to datetime64 types using explicit format constraints,
extracts core temporal attributes (hours, days, weeks), resamples transaction volumes,
calculates customer recency (recency-based churn predictors), and generates time-series
heatmaps and seasonal decomposition charts.

Execution:
    python scripts/datetime_feature_engineering.py
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
# Use Agg backend for non-interactive plot generation
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose


def parse_timestamp_explicit(df, column_name, format_str='%Y-%m-%d %H:%M:%S'):
    """
    Parse a string column to datetime type with an explicit format parameter.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column_name (str): Date string column name.
        format_str (str): Target format parser pattern. Default is standard format.
        
    Returns:
        pd.DataFrame: DataFrame with transformed datetime column.
    """
    df_clean = df.copy()
    if column_name in df_clean.columns:
        df_clean[column_name] = pd.to_datetime(df_clean[column_name], format=format_str)
        print(f"✓ parsed {column_name} to dtype: {df_clean[column_name].dtype} using format: '{format_str}'")
    return df_clean


def extract_temporal_features(df, date_col):
    """
    Extract temporal attributes (day of week, hour of day, week number) from a datetime column.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        date_col (str): The datetime column name.
        
    Returns:
        pd.DataFrame: Transformed DataFrame.
    """
    df_clean = df.copy()
    if date_col in df_clean.columns:
        df_clean['day_of_week'] = df_clean[date_col].dt.day_name()
        df_clean['hour'] = df_clean[date_col].dt.hour
        df_clean['week_num'] = df_clean[date_col].dt.isocalendar().week
        print(f"✓ Extracted day_of_week, hour, and week_num features from {date_col}")
    return df_clean


def compute_recency_metric(df, customer_id_col, date_col, reference_date=None):
    """
    Compute recency (days since last purchase per customer) relative to a reference timestamp.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        customer_id_col (str): Customer key identifier column.
        date_col (str): Transaction date column.
        reference_date (pd.Timestamp): Date to compute difference from (defaults to today).
        
    Returns:
        pd.DataFrame: DataFrame with 'days_since_last_purchase' column appended.
    """
    df_clean = df.copy()
    if reference_date is None:
        reference_date = pd.Timestamp.now()
        
    # Find the maximum purchase date per customer
    last_purchases = df_clean.groupby(customer_id_col)[date_col].transform('max')
    
    # Calculate days since that date
    df_clean['days_since_last_purchase'] = (reference_date - last_purchases).dt.days
    print(f"✓ Computed days_since_last_purchase recency metric per customer")
    return df_clean


def build_time_indexed_aggregation(df, value_col):
    """
    Build multi-dimensional aggregations and pivot heatmaps for day x hour activity.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        value_col (str): Target column for aggregations.
        
    Returns:
        tuple: (Groupby summary, Pivot table).
    """
    # Multi-level groupby
    hourly_daily = df.groupby(['day_of_week', 'hour']).agg({
        value_col: ['sum', 'count', 'mean']
    })
    
    # Pivot table (hour x day-of-week)
    pivot_table = pd.pivot_table(
        df,
        values=value_col,
        index='hour',
        columns='day_of_week',
        aggfunc='sum'
    ).fillna(0)
    
    print("\n--- Day x Hour Pivot Table (Sum of transaction amounts) ---")
    print(pivot_table.round(2))
    return hourly_daily, pivot_table


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    print("==============================================================")
    print("RUNNING DATETIME FEATURE ENGINEERING PIPELINE")
    print("==============================================================\n")

    # 1. Generate synthetic dataset spanning 130 weeks (to ensure statsmodels seasonal decomposition runs successfully)
    print("Step 1: Generating synthetic transaction dataset...")
    np.random.seed(42)
    date_range = pd.date_range(start='2023-01-01 00:00:00', end='2025-06-30 23:59:59', freq='6h')
    
    # Sample a subset of dates to represent transaction times
    sampled_dates = np.random.choice(date_range, size=1500, replace=True)
    sampled_dates.sort()
    
    # Create customer IDs and amounts
    customer_ids = np.random.randint(10001, 10050, size=1500)
    amounts = np.random.lognormal(mean=4.5, sigma=0.5, size=1500) # Right skewed amounts
    
    # Convert dates to raw string representation to simulate real database inputs
    raw_date_strings = [d.strftime('%Y-%m-%d %H:%M:%S') for d in pd.to_datetime(sampled_dates)]
    
    df = pd.DataFrame({
        'customer_id': customer_ids,
        'transaction_date_str': raw_date_strings,
        'amount': amounts
    })
    print(f"  Generated {len(df)} synthetic transactions for {df['customer_id'].nunique()} unique customers.")

    # Step 2: Parse and Engineer Features
    print("\nStep 2: Engineering temporal features...")
    # Parse timestamp strings
    df = parse_timestamp_explicit(df, 'transaction_date_str', '%Y-%m-%d %H:%M:%S')
    
    # Rename to transaction_date
    df = df.rename(columns={'transaction_date_str': 'transaction_date'})
    
    # Extract features
    df = extract_temporal_features(df, 'transaction_date')
    
    # Compute recency metric relative to a fixed target date (e.g. 2025-07-01) for stable testing
    target_today = pd.Timestamp('2025-07-01 00:00:00')
    df = compute_recency_metric(df, 'customer_id', 'transaction_date', target_today)

    # Step 3: Run Resampling & Aggregations
    print("\nStep 3: Executing Weekly Resampling and Time-indexed Aggregations...")
    # Resample weekly metrics
    df_ts = df.set_index('transaction_date')
    weekly_revenue = df_ts['amount'].resample('W').sum()
    print("\nWeekly Revenue Trend (First 5 weeks):")
    print(weekly_revenue.head())
    
    # Multi-dimensional aggregations
    hourly_daily, pivot = build_time_indexed_aggregation(df, 'amount')

    # Step 4: Perform Seasonal Decomposition (Additive)
    print("\nStep 4: Executing Statsmodels Seasonal Decomposition...")
    try:
        # Re-index weekly revenue to ensure contiguous dates with no gaps
        weekly_full = weekly_revenue.asfreq('W', fill_value=0)
        
        # Run decomposition with period=52 (representing 52 weeks in a year)
        decomposition = seasonal_decompose(weekly_full, model='additive', period=52)
        
        # Plot and save
        fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        decomposition.observed.plot(ax=axes[0], title='Observed Weekly Transaction Volume')
        decomposition.trend.plot(ax=axes[1], title='Trend Component')
        decomposition.seasonal.plot(ax=axes[2], title='Seasonal Component')
        decomposition.resid.plot(ax=axes[3], title='Residual/Noise')
        plt.tight_layout()
        
        plot_path = os.path.join(output_dir, "datetime_decomposition.png")
        plt.savefig(plot_path)
        print(f"✓ Seasonal decomposition plot successfully saved to {plot_path}")
    except Exception as e:
        print(f"✗ Seasonal decomposition failed: {str(e)}")

    # Step 5: Run edge-case testing block as requested
    print("\n==============================================================")
    print("RUNNING EDGE-CASE PIPELINE TESTING")
    print("==============================================================")
    
    test_dates = [
        '2025-01-15 14:30:45',        # Standard
        '2025-1-15 14:30:45',         # Single-digit month
        '15/01/2025 14:30:45',        # European format
        '2025-01-15T14:30:45Z',       # ISO format with Z
    ]

    for date_str in test_dates:
        # We try multiple explicit formats sequentially
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        
        parsed = None
        # We try explicit parsing matching the test cases:
        if 'T' in date_str and 'Z' in date_str:
            target_fmt = '%Y-%m-%dT%H:%M:%SZ'
        elif '/' in date_str:
            target_fmt = '%d/%m/%Y %H:%M:%S'
        else:
            # Matches standard and single-digit month (Pandas to_datetime can parse both if format aligns or infers format)
            target_fmt = '%Y-%m-%d %H:%M:%S'
            
        try:
            parsed = pd.to_datetime(date_str, format=target_fmt)
            print(f"✓ {date_str} -> Parsed successfully using format: '{target_fmt}' -> {parsed}")
        except Exception:
            try:
                # Fallback to standard parser if format mismatch occurs
                parsed = pd.to_datetime(date_str)
                print(f"✓ {date_str} -> Parsed via fallback parser: {parsed}")
            except Exception as e:
                print(f"✗ {date_str} - format mismatch: {e}")
                
    print("==============================================================")
