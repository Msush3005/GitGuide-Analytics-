"""
High-Performance Vectorized Operations & Benchmarking Pipeline
GitGuide-Analytics

Replaces slow Python iterative loops with C-compiled NumPy array vectorization.
Measures execution timing across large datasets (100,000+ records), calculates speedup factors,
and integrates optimized normalized features into Pandas DataFrames.

Execution:
    python scripts/vectorized_performance.py
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np


def generate_large_revenue_dataset(output_path, num_records=100000):
    """
    Generate synthetic large revenue dataset (100,000 records) for benchmarking.
    
    Args:
        output_path (str): File destination path.
        num_records (int): Number of rows to generate (default 100,000).
        
    Returns:
        pd.DataFrame: Raw generated DataFrame.
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    customer_ids = np.arange(100001, 100001 + num_records)
    revenue = np.round(np.random.exponential(scale=500.0, size=num_records) + 10.0, 2)
    transaction_count = np.random.randint(1, 250, size=num_records)

    df_raw = pd.DataFrame({
        'customer_id': customer_ids,
        'revenue': revenue,
        'transaction_count': transaction_count
    })

    df_raw.to_csv(output_path, index=False)
    print(f"✓ Generated large revenue dataset ({num_records:,} records) at: {output_path}")
    return df_raw


def min_max_normalize_loop(df, column='revenue'):
    """
    Compute Min-Max Normalization using slow Python iterative loops (Baseline).
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column name.
        
    Returns:
        list: Normalized values.
    """
    min_val = df[column].min()
    max_val = df[column].max()
    denom = max_val - min_val

    normalized = []
    for val in df[column]:
        normalized.append((val - min_val) / denom)

    return normalized


def min_max_normalize_vectorized(df, column='revenue'):
    """
    Compute Min-Max Normalization using fast C-compiled NumPy array vectorization.
    
    Formula: (arr - arr.min()) / (arr.max() - arr.min())
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column name.
        
    Returns:
        np.ndarray: Vectorized normalized array.
    """
    revenue_array = df[column].values
    min_val = revenue_array.min()
    max_val = revenue_array.max()

    normalized = (revenue_array - min_val) / (max_val - min_val)
    return normalized


def z_score_normalize_vectorized(df, column='revenue'):
    """
    Compute Z-Score Normalization using fast NumPy array vectorization.
    
    Formula: (arr - arr.mean()) / arr.std()
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column name.
        
    Returns:
        np.ndarray: Vectorized Z-score array.
    """
    revenue_array = df[column].values
    mean_val = revenue_array.mean()
    std_val = revenue_array.std()

    z_scores = (revenue_array - mean_val) / std_val
    return z_scores


def benchmark_performance(df, column='revenue'):
    """
    Benchmark and compare execution timing between Python loops and NumPy vectorization.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target numerical column.
        
    Returns:
        tuple: (df_processed, benchmark_results_dict).
    """
    df_proc = df.copy()

    print(f"\n--- Benchmarking Operations on {len(df_proc):,} Rows ---")

    # 1. Measure Python Loop Min-Max Normalization
    start = time.time()
    loop_norm = min_max_normalize_loop(df_proc, column)
    loop_time = time.time() - start

    # 2. Measure NumPy Vectorized Min-Max Normalization
    start = time.time()
    vec_norm = min_max_normalize_vectorized(df_proc, column)
    vec_minmax_time = time.time() - start

    # 3. Measure NumPy Vectorized Z-Score Normalization
    start = time.time()
    vec_zscore = z_score_normalize_vectorized(df_proc, column)
    vec_zscore_time = time.time() - start

    # Integrate vectorized results back into DataFrame
    df_proc['revenue_normalized'] = np.round(vec_norm, 6)
    df_proc['revenue_zscore'] = np.round(vec_zscore, 6)

    speedup = loop_time / vec_minmax_time if vec_minmax_time > 0 else 0.0

    print(f"1. Python Loop Min-Max Time:        {loop_time:.6f} seconds")
    print(f"2. NumPy Vectorized Min-Max Time:    {vec_minmax_time:.6f} seconds")
    print(f"3. NumPy Vectorized Z-Score Time:   {vec_zscore_time:.6f} seconds")
    print(f"✓ NumPy Vectorization Speedup:      {speedup:.1f}x faster than Python loop!")

    benchmark_results = {
        'total_records': len(df_proc),
        'loop_execution_time_seconds': round(loop_time, 6),
        'vectorized_minmax_time_seconds': round(vec_minmax_time, 6),
        'vectorized_zscore_time_seconds': round(vec_zscore_time, 6),
        'speedup_factor': round(speedup, 1)
    }

    return df_proc, benchmark_results


def export_benchmark_report(df_processed, benchmark_results, report_path, processed_path):
    """
    Export benchmark audit log to JSON and processed dataset to CSV.
    
    Args:
        df_processed (pd.DataFrame): Processed DataFrame.
        benchmark_results (dict): Benchmark metrics dictionary.
        report_path (str): Destination path for JSON report.
        processed_path (str): Destination path for CSV processed dataset.
    """
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    # Save processed CSV
    df_processed.to_csv(processed_path, index=False)
    print(f"\n✓ Saved processed dataset ({len(df_processed):,} records) to: {processed_path}")

    # Save JSON report
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, indent=2)

    print(f"✓ Saved performance benchmark report to: {report_path}")
    print(json.dumps(benchmark_results, indent=2))


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "large_revenue_dataset.csv")
    processed_path = os.path.join(base_dir, "data", "processed", "vectorized_optimized_features.csv")
    report_path = os.path.join(base_dir, "output", "performance_benchmark_report.json")

    print("==============================================================")
    print("RUNNING HIGH-PERFORMANCE VECTORIZED OPERATIONS & BENCHMARKING")
    print("==============================================================\n")

    # Step 1: Generate or load large dataset (100,000 records)
    df_raw = generate_large_revenue_dataset(raw_path, num_records=100000)

    # Step 2 & 3: Run benchmarking & vectorized normalizations
    df_processed, benchmark_results = benchmark_performance(df_raw, column='revenue')

    # Step 4: Export results
    export_benchmark_report(df_processed, benchmark_results, report_path, processed_path)
    print("==============================================================")
