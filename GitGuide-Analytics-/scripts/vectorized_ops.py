import os
import time
import json
import numpy as np
import pandas as pd


def generate_benchmark_dataset(num_rows=100000, filepath="data/raw/revenue_data.csv"):
    """
    Generates a synthetic revenue dataset for performance benchmarking.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating benchmark dataset with {num_rows:,} rows at {filepath}...")
        np.random.seed(42)
        customer_ids = [f"CUST_{i:06d}" for i in range(1, num_rows + 1)]
        revenue = np.random.exponential(scale=5000, size=num_rows) + 50.0
        df_raw = pd.DataFrame({
            "customer_id": customer_ids,
            "revenue": np.round(revenue, 2)
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset generated successfully ({len(df_raw):,} rows).")
    else:
        print(f"Loading existing benchmark dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)
    return df_raw


def task1_min_max_normalization(df):
    """
    Task 1: Min-Max Normalization using NumPy Vectorization.
    Formula: (x - min) / (max - min)
    Produces values scaled between 0 and 1.
    """
    revenue_array = df['revenue'].values
    normalized_np = (revenue_array - revenue_array.min()) / (
        revenue_array.max() - revenue_array.min()
    )
    return normalized_np


def task2_z_score_normalization(df):
    """
    Task 2: Z-Score Normalization using NumPy Vectorization.
    Formula: (x - mean) / std
    Produces values centered at 0 with standard deviation of 1.
    """
    revenue_array = df['revenue'].values
    z_scores = (revenue_array - revenue_array.mean()) / revenue_array.std()
    return z_scores


def task3_bulk_ranking(df):
    """
    Task 3: Bulk Ranking / Scoring using NumPy.
    Ranks customers by revenue in descending order (1 = highest revenue).
    Uses np.argsort for vectorized indexing.
    """
    revenue_array = df['revenue'].values
    rankings = np.argsort(-revenue_array)  # Negative for descending order
    revenue_rank = np.empty_like(rankings)
    revenue_rank[rankings] = np.arange(1, len(rankings) + 1)
    return revenue_rank


def task4_time_performance_comparison(df):
    """
    Task 4: Time Performance Comparison between Python Loop and NumPy Vectorization.
    Measures execution time of min-max scaling across both approaches.
    """
    print("\n--- Task 4: Time Performance Comparison ---")

    # 1. Python Loop Version
    start = time.time()
    result_loop = []
    rev_min = df['revenue'].min()
    rev_max = df['revenue'].max()
    rev_range = rev_max - rev_min
    for val in df['revenue']:
        result_loop.append((val - rev_min) / rev_range)
    loop_time = time.time() - start

    # 2. NumPy Vectorized Version
    start = time.time()
    revenue_array = df['revenue'].values
    result_np = (revenue_array - revenue_array.min()) / (
        revenue_array.max() - revenue_array.min()
    )
    np_time = time.time() - start

    speedup = loop_time / np_time if np_time > 0 else 0

    print(f"Loop Execution Time  : {loop_time:.4f} seconds")
    print(f"NumPy Execution Time : {np_time:.4f} seconds")
    print(f"Speedup Factor       : {speedup:.0f}x faster")

    metrics = {
        "dataset_rows": len(df),
        "loop_time_seconds": round(loop_time, 6),
        "numpy_time_seconds": round(np_time, 6),
        "speedup_factor": round(speedup, 1)
    }

    return metrics, result_np


def task5_integrate_back_to_dataframe(df, normalized_np, z_scores, revenue_rank):
    """
    Task 5: Integrate NumPy computed arrays back into the Pandas DataFrame as new columns.
    Prints final shape and data types for verification.
    """
    print("\n--- Task 5: Integrate Back to DataFrame ---")
    df['revenue_normalized'] = normalized_np
    df['revenue_zscore'] = z_scores
    df['revenue_rank'] = revenue_rank

    print(f"Shape: {df.shape}")
    print(f"Dtypes:\n{df.dtypes}")
    return df


def main():
    print("=" * 60)
    print("  NumPy Vectorised Computation Workflow - Execution")
    print("=" * 60)

    # Prepare Directories
    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Step 0: Ingest dataset
    df = generate_benchmark_dataset(num_rows=100000)

    # Step 1: Min-Max Normalization
    print("\n[Task 1] Executing Vectorized Min-Max Normalization...")
    normalized_np = task1_min_max_normalization(df)

    # Step 2: Z-Score Normalization
    print("[Task 2] Executing Vectorized Z-Score Normalization...")
    z_scores = task2_z_score_normalization(df)

    # Step 3: Bulk Ranking / Scoring
    print("[Task 3] Executing Bulk Ranking/Scoring...")
    revenue_rank = task3_bulk_ranking(df)

    # Step 4: Performance Comparison
    metrics, _ = task4_time_performance_comparison(df)

    # Step 5: Integration Back to DataFrame
    df_final = task5_integrate_back_to_dataframe(df, normalized_np, z_scores, revenue_rank)

    # Save Output Artifacts
    output_csv = "data/processed/vectorized_revenue.csv"
    output_json = "output/vectorization_performance.json"

    df_final.to_csv(output_csv, index=False)
    with open(output_json, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"\nSaved processed data to: {output_csv}")
    print(f"Saved performance metrics to: {output_json}")
    print("\n[SUCCESS] NumPy Vectorised Computation Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
