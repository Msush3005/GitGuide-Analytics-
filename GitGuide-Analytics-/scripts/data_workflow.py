"""
Production Data Workflow Pipeline Script
GitGuide-Analytics

Converts exploratory notebook logic into a modular, production-ready script.
Separates ingestion, processing/transformation, and output export stages.

Execution:
    python scripts/data_workflow.py
"""

import os
import sys
import pandas as pd


def ingest_data(filepath: str) -> pd.DataFrame:
    """
    Ingest raw data from a CSV or JSON file into a Pandas DataFrame.

    Parameters:
        filepath (str): Path to the input data file.

    Returns:
        pd.DataFrame: Loaded Pandas DataFrame containing raw dataset.

    Assumptions & Constraints:
        - The input file must exist and be accessible.
        - Supported formats: CSV (default) or JSON.
        - File must contain headers on the first row.
    """
    # Verify that the specified input file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Ingestion failed: Input file '{filepath}' does not exist. "
            f"Please verify the filepath."
        )

    # Ingest file based on file extension
    if filepath.endswith(".json"):
        df = pd.read_json(filepath)
    else:
        df = pd.read_csv(filepath)

    print(f"Loaded raw dataset from '{filepath}' (Rows: {len(df)}, Columns: {len(df.columns)})")
    return df


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw DataFrame into an analysis-ready dataset.

    Operations Performed:
        1. Removes duplicate rows.
        2. Imputes missing values in numerical columns with column medians.
        3. Fills missing categorical values with default fallback string.
        4. Calculates a derived analytical feature ('total_contributions').

    Parameters:
        df (pd.DataFrame): Raw DataFrame ingested from source.

    Returns:
        pd.DataFrame: Processed, cleaned, and transformed DataFrame.

    Assumptions & Constraints:
        - Expects numerical columns for contribution counts.
        - Modifies numerical missing values without dropping valid rows.
    """
    # Copy DataFrame to avoid modifying original reference
    df_clean = df.copy()

    # Step 1: Remove exact duplicate rows across all columns
    initial_rows = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    duplicates_removed = initial_rows - len(df_clean)
    print(f"Cleaned dataset: Removed {duplicates_removed} duplicate row(s).")

    # Step 2: Impute missing numerical values using median imputation
    num_cols = df_clean.select_dtypes(include=["number"]).columns
    for col in num_cols:
        if df_clean[col].isnull().sum() > 0:
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)

    # Step 3: Handle missing categorical values
    cat_cols = df_clean.select_dtypes(include=["object", "string"]).columns
    for col in cat_cols:
        if df_clean[col].isnull().sum() > 0:
            df_clean[col] = df_clean[col].fillna("Unknown")

    # Step 4: Calculate derived feature 'total_contributions' (commits + pull requests)
    if "commits_count" in df_clean.columns and "pull_requests_opened" in df_clean.columns:
        df_clean["total_contributions"] = df_clean["commits_count"] + df_clean["pull_requests_opened"]

    return df_clean


def output_results(df: pd.DataFrame, output_path: str) -> None:
    """
    Save processed DataFrame to a CSV destination file and print confirmation.

    Parameters:
        df (pd.DataFrame): Cleaned and transformed DataFrame.
        output_path (str): Filepath where the output CSV should be stored.

    Returns:
        None

    Assumptions & Constraints:
        - Output directory will be automatically created if it does not exist.
        - Overwrites target file if it already exists.
    """
    # Ensure parent output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Save DataFrame to CSV format without index column
    df.to_csv(output_path, index=False)

    # Print required task confirmation metrics
    try:
        print("✓ Data successfully processed")
        print(f"✓ Rows processed: {len(df)}")
        print(f"✓ Output saved to {output_path}")
    except UnicodeEncodeError:
        print("[OK] Data successfully processed")
        print(f"[OK] Rows processed: {len(df)}")
        print(f"[OK] Output saved to {output_path}")


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 checkmarks cleanly on Windows environments
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve relative paths relative to repository root or script location
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    input_file = os.path.join(base_dir, "data", "raw", "sample.csv")
    output_file = os.path.join(base_dir, "output", "processed.csv")

    try:
        # Step 1: Ingest raw data
        raw_data = ingest_data(input_file)

        # Step 2: Transform and clean dataset
        processed_data = process_data(raw_data)

        # Step 3: Export final processed results
        output_results(processed_data, output_file)

    except Exception as error:
        print(f"Pipeline Execution Failed: {error}", file=sys.stderr)
        sys.exit(1)
