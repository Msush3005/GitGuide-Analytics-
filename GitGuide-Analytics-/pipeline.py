"""
Automated Data Pipeline Execution Subsystem
GitGuide Analytics - Lesson 2.58

Single-script automated pipeline executing four sequential stages:
1. Ingest: Load raw CSV/JSON dataset.
2. Clean: Validate required schema, handle null values, coerce numeric types.
3. Aggregate: Compute role and segment-level summary statistics.
4. Output: Export cleaned dataset and aggregated metrics with timestamped verification logging.

Usage:
    python pipeline.py --input data/raw/sample.csv --output output
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import pandas as pd
import numpy as np

# Configure logging with ISO timestamps and level formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GitGuidePipeline")


def ingest(file_path):
    """Stage 1: Load raw data file into DataFrame."""
    logger.info(f"Stage 1 [Ingest]: Loading raw dataset from: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"Input file not found at path: {file_path}")
        raise FileNotFoundError(f"Input file does not exist: {file_path}")

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    else:
        df = pd.read_csv(file_path)

    logger.info(f"Stage 1 [Ingest] Complete: Successfully ingested {len(df):,} rows and {len(df.columns)} columns.")
    return df


def clean(df):
    """Stage 2: Clean, validate schema, and coerce numeric columns."""
    logger.info("Stage 2 [Clean]: Validating schema and filtering invalid records...")
    initial_count = len(df)

    # Resolve required columns dynamically
    id_col = next((c for c in ["contributor_id", "contributor_login", "customer_id", "user_id"] if c in df.columns), df.columns[0])
    num_col = next((c for c in ["commits_count", "commits", "total_contributions", "amount", "revenue"] if c in df.columns), None)

    # Drop missing primary identifiers
    df = df.dropna(subset=[id_col]).copy()

    if num_col:
        df[num_col] = pd.to_numeric(df[num_col], errors="coerce")
        df = df[df[num_col] > 0]

    final_count = len(df)
    removed = initial_count - final_count
    logger.info(f"Stage 2 [Clean] Complete: {initial_count:,} -> {final_count:,} rows retained ({removed:,} invalid records removed).")
    return df


def aggregate(df):
    """Stage 3: Compute role and segment-level summary statistics."""
    logger.info("Stage 3 [Aggregate]: Computing role and segment metrics...")
    
    role_col = next((c for c in ["contributor_role", "role", "segment", "category"] if c in df.columns), None)
    commit_col = next((c for c in ["commits_count", "commits", "total_contributions", "amount"] if c in df.columns), None)
    review_col = next((c for c in ["avg_pr_review_days", "pr_review_days", "review_days"] if c in df.columns), None)

    if role_col and commit_col:
        agg_dict = {
            "total_volume": (commit_col, "sum"),
            "record_count": (commit_col, "count"),
            "avg_volume": (commit_col, "mean")
        }
        if review_col:
            agg_dict["avg_review_days"] = (review_col, "mean")
            
        agg_df = df.groupby(role_col).agg(**agg_dict).reset_index()
    else:
        num_cols = df.select_dtypes(include=np.number).columns
        agg_df = df.describe().T.reset_index()

    logger.info(f"Stage 3 [Aggregate] Complete: Generated metrics across {len(agg_df):,} categories.")
    return agg_df


def output(cleaned_df, agg_df, output_dir):
    """Stage 4: Export cleaned data and aggregated metrics to output directory."""
    logger.info(f"Stage 4 [Output]: Writing output files to directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    cleaned_path = os.path.join(output_dir, "cleaned_data.csv")
    agg_path = os.path.join(output_dir, "aggregated_metrics.csv")

    cleaned_df.to_csv(cleaned_path, index=False)
    agg_df.to_csv(agg_path, index=False)

    logger.info(f"Wrote cleaned dataset ({len(cleaned_df):,} rows) to: {cleaned_path}")
    logger.info(f"Wrote aggregated metrics ({len(agg_df):,} rows) to: {agg_path}")
    logger.info("Pipeline execution completed successfully.")


def run_pipeline(input_path, output_dir):
    """Runs the end-to-end data pipeline."""
    start_time = datetime.now()
    logger.info(f"Starting GitGuide Analytics Pipeline execution at {start_time.isoformat()}")

    raw_df = ingest(input_path)
    cleaned_df = clean(raw_df)
    agg_df = aggregate(cleaned_df)
    output(cleaned_df, agg_df, output_dir)

    elapsed = (datetime.now() - start_time).total_seconds()
    logger.info(f"Total pipeline execution time: {elapsed:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitGuide Analytics Automated Data Pipeline")
    parser.add_argument("--input", required=True, help="Path to raw input CSV/JSON file")
    parser.add_argument("--output", default="output", help="Directory path to save output files")
    args = parser.parse_args()

    run_pipeline(args.input, args.output)
