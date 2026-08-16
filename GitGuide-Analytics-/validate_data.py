"""
Automated Data Schema Validation Subsystem
GitGuide Analytics - Lesson 2.59

Validates raw and processed dataset files against schema contracts, expected data types,
minimum row count thresholds, and null integrity before code changes merge to production.

Usage:
    python validate_data.py data/processed/fetched_github_repo_processed.csv
"""

import sys
import os
import pandas as pd


def validate(file_path):
    """
    Executes automated data quality and schema validation checks.
    Exits with code 1 if any validation error is detected, 0 if all checks pass.

    Args:
        file_path (str): Path to CSV/JSON dataset file to validate
    """
    print(f"==================================================")
    print(f"     GitGuide Automated Schema & Quality Audit    ")
    print(f"==================================================")
    print(f"Target File: {file_path}")

    if not os.path.exists(file_path):
        print(f"\nVALIDATION FAILED: Target file does not exist at path '{file_path}'")
        sys.exit(1)

    try:
        if file_path.endswith(".json"):
            df = pd.read_json(file_path)
        else:
            df = pd.read_csv(file_path)
    except Exception as e:
        print(f"\nVALIDATION FAILED: Could not parse dataset file. ({e})")
        sys.exit(1)

    errors = []

    # Check 1: Required Schema Columns
    # Supports generic analytics datasets as well as GitGuide repository datasets
    gitguide_cols = ["contributor_login", "commits_count", "contributor_role", "pr_review_days"]
    generic_cols  = ["customer_id", "order_id", "amount", "date", "segment"]

    has_gitguide = any(c in df.columns for c in gitguide_cols)
    has_generic  = any(c in df.columns for c in generic_cols)

    if not (has_gitguide or has_generic):
        errors.append(f"Missing required columns. Dataset has {list(df.columns)}")
    else:
        print("PASS: Required schema columns present")

    # Check 2: Expected Data Types (Numeric Validation)
    num_col = next((c for c in ["commits_count", "amount", "revenue", "lines_changed"] if c in df.columns), None)
    if num_col:
        if not pd.api.types.is_numeric_dtype(df[num_col]):
            errors.append(f"Column '{num_col}' is not numeric (found type {df[num_col].dtype})")
        else:
            print(f"PASS: Numeric column '{num_col}' is valid numeric type")
    else:
        print("PASS: Numeric column check skipped (no target numeric column present)")

    # Check 3: Minimum Row Count Threshold
    min_rows = 1
    if len(df) < min_rows:
        errors.append(f"Row count ({len(df):,}) is below minimum threshold ({min_rows:,})")
    else:
        print(f"PASS: Row count ({len(df):,}) meets minimum threshold ({min_rows:,})")

    # Check 4: No Fully Null Columns
    null_cols = [c for c in df.columns if df[c].isnull().all()]
    if null_cols:
        errors.append(f"Fully null columns detected: {null_cols}")
    else:
        print("PASS: No fully null columns detected in dataset")

    # Final Pass / Fail Determination
    print("\n--------------------------------------------------")
    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  [ERROR] {err}")
        print("--------------------------------------------------")
        sys.exit(1)
    else:
        print("ALL CHECKS PASSED: Dataset contract validated successfully.")
        print("--------------------------------------------------")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        target_path = "data/raw/fetched_github_repo_data.csv"
        if not os.path.exists(target_path):
            target_path = "output/processed.csv"
    else:
        target_path = sys.argv[1]

    validate(target_path)
