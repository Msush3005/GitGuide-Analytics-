"""
Data Quality and Business Rule Validation Pipeline
GitGuide-Analytics

Evaluates incoming datasets against range checks, null constraints, regex format patterns,
and multi-column business logic rules. Isolates failed records to an audit file and outputs
clean records for downstream analytics pipelines.

Execution:
    python scripts/validate_rules.py
"""

import os
import sys
import pandas as pd
import numpy as np


def validate_range_checks(df):
    """
    Perform range checks on numerical and date columns.
    
    Rules:
        - valid_age: 0 <= age <= 150
        - valid_price: price >= 0
        - valid_birth_date: birth_date between 1920-01-01 and current date.
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with range check boolean flags added.
    """
    df_val = df.copy()
    
    # 1. Age range check
    df_val['valid_age'] = (df_val['age'] >= 0) & (df_val['age'] <= 150)
    
    # 2. Price range check
    df_val['valid_price'] = df_val['price'] >= 0
    
    # 3. Birth date range check
    # Convert birth_date to datetime for robust comparison
    birth_dt = pd.to_datetime(df_val['birth_date'], errors='coerce')
    now = pd.Timestamp.now()
    min_date = pd.Timestamp('1920-01-01')
    df_val['valid_birth_date'] = (birth_dt >= min_date) & (birth_dt <= now)
    
    print("\n--- Task 1: Range Checks ---")
    print(f"Invalid ages (0 <= age <= 150):           {(~df_val['valid_age']).sum()}")
    print(f"Invalid prices (price >= 0):             {(~df_val['valid_price']).sum()}")
    print(f"Invalid birth dates (1920 <= date <= now): {(~df_val['valid_birth_date']).sum()}")
    
    return df_val


def validate_null_constraints(df):
    """
    Enforce non-null constraints on mandatory identifier columns.
    
    Rules:
        - valid_customer_id: customer_id is not null
        - valid_email: email is not null
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with null constraint boolean flags added.
    """
    df_val = df.copy()
    
    df_val['valid_customer_id'] = df_val['customer_id'].notna()
    df_val['valid_email'] = df_val['email'].notna()
    
    print("\n--- Task 2: Null Constraints ---")
    print(f"Missing customer IDs: {(~df_val['valid_customer_id']).sum()}")
    print(f"Missing emails:       {(~df_val['valid_email']).sum()}")
    
    return df_val


def validate_format_patterns(df):
    r"""
    Validate string formatting using regex pattern matching.
    
    Rules:
        - valid_email_format: email contains '@'
        - valid_phone: phone matches exactly 10 digits (r'^\d{10}$')
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with format validation boolean flags added.
    """
    df_val = df.copy()
    
    # Check email pattern
    df_val['valid_email_format'] = df_val['email'].astype(str).str.contains('@', na=False) & df_val['valid_email']
    
    # Check phone pattern (exactly 10 numeric digits)
    df_val['valid_phone'] = df_val['phone'].astype(str).str.match(r'^\d{10}$', na=False)
    
    print("\n--- Task 3: Format Pattern Validation ---")
    print(f"Invalid email formats: {(~df_val['valid_email_format']).sum()}")
    print(f"Invalid phone numbers: {(~df_val['valid_phone']).sum()}")
    
    return df_val


def validate_business_rules(df):
    """
    Validate multi-column temporal and business rules.
    
    Rules:
        - valid_date_order: end_date >= start_date
        
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with business rule boolean flags added.
    """
    df_val = df.copy()
    
    start_dt = pd.to_datetime(df_val['start_date'], errors='coerce')
    end_dt = pd.to_datetime(df_val['end_date'], errors='coerce')
    
    df_val['valid_date_order'] = (end_dt >= start_dt)
    
    print("\n--- Task 4: Business Rule Validation ---")
    print(f"Invalid date ranges (end_date < start_date): {(~df_val['valid_date_order']).sum()}")
    
    return df_val


def generate_validation_report(df, failures_output_path, clean_output_path):
    """
    Aggregate validation checks, isolate failed records, and export clean data.
    
    Args:
        df (pd.DataFrame): Input DataFrame with all validation flags.
        failures_output_path (str): File path for saving failed records CSV.
        clean_output_path (str): File path for saving clean records CSV.
        
    Returns:
        tuple: (clean_df, failures_df).
    """
    df_val = df.copy()
    
    validation_cols = [
        'valid_age', 'valid_price', 'valid_birth_date',
        'valid_customer_id', 'valid_email', 'valid_email_format',
        'valid_phone', 'valid_date_order'
    ]
    
    # A record passes if all validation checks evaluate to True
    df_val['passes_all_checks'] = df_val[validation_cols].all(axis=1)
    
    # Isolate failures and clean records
    failures = df_val[~df_val['passes_all_checks']].copy()
    df_clean = df_val[df_val['passes_all_checks']].copy()
    
    # Create parent output directories
    os.makedirs(os.path.dirname(failures_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(clean_output_path), exist_ok=True)
    
    # Save files
    failures.to_csv(failures_output_path, index=False)
    df_clean.to_csv(clean_output_path, index=False)
    
    print("\n" + "="*70)
    print("TASK 5: VALIDATION REPORT SUMMARY")
    print("="*70)
    print(f"Total Records Analyzed: {len(df_val)}")
    print(f"Passed All Checks:     {df_val['passes_all_checks'].sum()} ({(df_val['passes_all_checks'].sum()/len(df_val)*100):.1f}%)")
    print(f"Failed Validation:     {(~df_val['passes_all_checks']).sum()} ({((~df_val['passes_all_checks']).sum()/len(df_val)*100):.1f}%)")
    
    print("\nFailed Validation Breakdown by Rule:")
    for col in validation_cols:
        failed_count = (~df_val[col]).sum()
        print(f"  - {col:20s}: {failed_count} failures")
        
    print(f"\n✓ Isolated failure records saved to: {failures_output_path}")
    print(f"✓ Valid clean records saved to:     {clean_output_path}")
    print("="*70)
    
    return df_clean, failures


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_file = os.path.join(base_dir, "data", "raw", "quality_test.csv")
    failures_output = os.path.join(base_dir, "output", "validation_failures.csv")
    clean_output = os.path.join(base_dir, "data", "processed", "validated_clean_data.csv")

    print("Starting data quality & business rule validation...\n")
    
    try:
        # Load raw data
        df_raw = pd.read_csv(input_file)
        
        # Step 1: Range checks
        df_validated = validate_range_checks(df_raw)
        
        # Step 2: Null constraints
        df_validated = validate_null_constraints(df_validated)
        
        # Step 3: Format pattern validation
        df_validated = validate_format_patterns(df_validated)
        
        # Step 4: Business rules validation
        df_validated = validate_business_rules(df_validated)
        
        # Step 5: Report generation & failure isolation
        generate_validation_report(df_validated, failures_output, clean_output)
        
    except Exception as err:
        print(f"Validation Pipeline Failed: {err}", file=sys.stderr)
        sys.exit(1)
