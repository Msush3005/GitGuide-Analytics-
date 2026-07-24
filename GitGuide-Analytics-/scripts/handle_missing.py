"""
Missing Value Treatment and Imputation Pipeline
GitGuide-Analytics

Analyzes incomplete records across all columns, applies context-aware 
imputation strategies (median, mode, forward-fill, row dropping), documents
business decisions, and logs comparison metrics.

Execution:
    python scripts/handle_missing.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np


def analyze_missing_values(df):
    """
    Compute null counts and percentages before treatment.
    
    Args:
        df (pd.DataFrame): Input DataFrame before cleaning.
        
    Returns:
        pd.DataFrame: Analysis summary of missing data by column.
    """
    missing_analysis = pd.DataFrame({
        'column': df.columns,
        'null_count': df.isnull().sum().values,
        'null_percentage': (df.isnull().sum() / len(df) * 100).round(2).values,
        'data_type': df.dtypes.values,
        'null_meaning': [
            'Critical customer key' if c == 'customer_id' else
            'Customer contact identifier' if c == 'email' else
            'Transaction dollar amount' if c == 'amount' else
            'Activity quantity volume' if c == 'quantity' else
            'Geographic classification' if c == 'region' else
            'System update timestamp' if c == 'last_updated' else
            'Generic field' for c in df.columns
        ]
    })
    
    print("="*70)
    print("BEFORE IMPUTATION - Missing Value Analysis")
    print("="*70)
    print(missing_analysis.to_string(index=False))
    print(f"\nTotal rows: {len(df)}")
    print(f"Total cells: {len(df) * len(df.columns)}")
    print(f"Missing cells: {df.isnull().sum().sum()}")
    print("="*70)
    
    return missing_analysis


def impute_mean_median(df, numerical_cols, strategy='median'):
    """
    Fill numerical nulls with mean or median.
    
    Args:
        df (pd.DataFrame): DataFrame to impute.
        numerical_cols (list): List of column names to apply strategy.
        strategy (str): Imputation strategy ('mean' or 'median').
        
    Returns:
        pd.DataFrame: Imputed DataFrame.
    """
    df_imputed = df.copy()
    for col in numerical_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            fill_value = df[col].median() if strategy == 'median' else df[col].mean()
            df_imputed[col] = df_imputed[col].fillna(fill_value)
            null_count = df[col].isnull().sum()
            print(f"  ✓ {col}: filled {null_count} nulls with {strategy} ({fill_value:.2f})")
    return df_imputed


def impute_mode(df, categorical_cols):
    """
    Fill categorical nulls with mode (most common value).
    
    Args:
        df (pd.DataFrame): DataFrame to impute.
        categorical_cols (list): List of column names to apply mode imputation.
        
    Returns:
        pd.DataFrame: Imputed DataFrame.
    """
    df_imputed = df.copy()
    for col in categorical_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            # Mode returns a series; select the first value
            mode_series = df[col].mode()
            mode_val = mode_series[0] if not mode_series.empty else "Unknown"
            null_count = df[col].isnull().sum()
            df_imputed[col] = df_imputed[col].fillna(mode_val)
            print(f"  ✓ {col}: filled {null_count} nulls with mode '{mode_val}'")
    return df_imputed


def impute_forward_fill(df, time_series_cols):
    """
    Fill nulls using forward fill (for time-series data).
    
    Args:
        df (pd.DataFrame): DataFrame to impute.
        time_series_cols (list): List of columns to apply forward fill.
        
    Returns:
        pd.DataFrame: Imputed DataFrame.
    """
    df_imputed = df.copy()
    for col in time_series_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            null_count = df[col].isnull().sum()
            # Compatible with modern Pandas versions (ffill replaces fillna(method='ffill'))
            df_imputed[col] = df_imputed[col].ffill()
            print(f"  ✓ {col}: forward-filled {null_count} nulls")
    return df_imputed


def drop_rows_with_nulls(df, critical_cols):
    """
    Drop rows where critical columns are null.
    
    Args:
        df (pd.DataFrame): DataFrame to filter.
        critical_cols (list): List of critical columns.
        
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    rows_before = len(df)
    # Subset only includes columns present in the DataFrame to prevent errors
    cols_to_check = [c for c in critical_cols if c in df.columns]
    df_imputed = df.dropna(subset=cols_to_check)
    rows_dropped = rows_before - len(df_imputed)
    print(f"  ✓ Dropped {rows_dropped} rows with null in: {cols_to_check}")
    return df_imputed


def document_imputation_decisions(df_original, df_imputed):
    """
    Document all imputation decisions with business justification and risk metrics.
    
    Args:
        df_original (pd.DataFrame): Original DataFrame before treatment.
        df_imputed (pd.DataFrame): Final cleaned DataFrame.
        
    Returns:
        dict: The documented decisions dictionary.
    """
    decisions = {
        'customer_id': {
            'column_type': 'primary_identifier',
            'null_count_before': int(df_original['customer_id'].isnull().sum()) if 'customer_id' in df_original.columns else 0,
            'strategy': 'drop_rows',
            'business_reasoning': 'Primary keys uniquely identify entities. Imputing a primary identifier creates invalid records and corrupts joins.',
            'risk_assessment': 'Low - required identifier'
        },
        'email': {
            'column_type': 'categorical_identifier',
            'null_count_before': int(df_original['email'].isnull().sum()) if 'email' in df_original.columns else 0,
            'strategy': 'drop_rows',
            'business_reasoning': 'Email is critical for customer contact and marketing campaigns. Rows without email cannot be used for outreach. Data is incomplete.',
            'risk_assessment': 'Low - only affects small percentage of data'
        },
        'amount': {
            'column_type': 'numerical',
            'null_count_before': int(df_original['amount'].isnull().sum()) if 'amount' in df_original.columns else 0,
            'strategy': 'median_imputation',
            'value_used': float(df_original['amount'].median()) if 'amount' in df_original.columns else None,
            'business_reasoning': 'Median purchase amount is representative of typical transaction. Mean would be skewed by high-value outliers. Maintains distribution integrity.',
            'risk_assessment': 'Low - median is stable metric resistant to outliers'
        },
        'quantity': {
            'column_type': 'numerical',
            'null_count_before': int(df_original['quantity'].isnull().sum()) if 'quantity' in df_original.columns else 0,
            'strategy': 'median_imputation',
            'value_used': float(df_original['quantity'].median()) if 'quantity' in df_original.columns else None,
            'business_reasoning': 'Imputes standard median volume size to complete the dataset without skewing aggregate distribution.',
            'risk_assessment': 'Low'
        },
        'category': {
            'column_type': 'categorical',
            'null_count_before': int(df_original['category'].isnull().sum()) if 'category' in df_original.columns else 0,
            'strategy': 'mode_imputation',
            'value_used': str(df_original['category'].mode()[0]) if 'category' in df_original.columns and not df_original['category'].mode().empty else None,
            'business_reasoning': 'Fills categorical nulls with the most frequent category to represent the standard class.',
            'risk_assessment': 'Low'
        },
        'region': {
            'column_type': 'categorical',
            'null_count_before': int(df_original['region'].isnull().sum()) if 'region' in df_original.columns else 0,
            'strategy': 'mode_imputation',
            'value_used': str(df_original['region'].mode()[0]) if 'region' in df_original.columns and not df_original['region'].mode().empty else None,
            'business_reasoning': 'Fills categorical nulls with the most frequent region location.',
            'risk_assessment': 'Low'
        },
        'last_updated': {
            'column_type': 'datetime_series',
            'null_count_before': int(df_original['last_updated'].isnull().sum()) if 'last_updated' in df_original.columns else 0,
            'strategy': 'forward_fill',
            'business_reasoning': 'For time-series analysis, forward fill preserves temporal continuity. Status typically does not change frequently.',
            'risk_assessment': 'Medium - assumes no change between observations'
        }
    }
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save report to file
    with open('output/imputation_decisions.json', 'w', encoding='utf-8') as f:
        json.dump(decisions, f, indent=2, default=str)
    
    print("✓ Imputation decisions saved to output/imputation_decisions.json")
    return decisions


def validate_imputation(df_original, df_imputed):
    """
    Compare metrics before and after imputation.
    
    Args:
        df_original (pd.DataFrame): Original DataFrame before treatment.
        df_imputed (pd.DataFrame): Cleaned DataFrame after treatment.
        
    Returns:
        pd.DataFrame: Metric comparison table.
    """
    print("\n" + "="*70)
    print("AFTER IMPUTATION - Validation Report")
    print("="*70)
    print(f"Total rows before: {len(df_original)}")
    print(f"Total rows after:  {len(df_imputed)}")
    print(f"Rows removed: {len(df_original) - len(df_imputed)}")
    print(f"\nTotal nulls before: {df_original.isnull().sum().sum()}")
    print(f"Total nulls after:  {df_imputed.isnull().sum().sum()}")
    
    missing_after = pd.DataFrame({
        'column': df_imputed.columns,
        'null_count_after': df_imputed.isnull().sum().values,
        'null_percentage_after': (df_imputed.isnull().sum() / len(df_imputed) * 100).round(2).values
    })
    
    print("\nNull values by column after imputation:")
    print(missing_after.to_string(index=False))
    print("="*70)
    
    return missing_after


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve absolute paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    input_file = os.path.join(base_dir, "data", "raw", "missing_data.csv")
    output_file = os.path.join(base_dir, "data", "processed", "cleaned_data.csv")

    # Create processed directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("Starting missing value treatment...\n")
    
    try:
        # Load data
        df_raw = pd.read_csv(input_file)
        
        # Keep copy of original for reporting
        df_original = df_raw.copy()
        
        # Step 1: Analyze missing before treatment
        print("Step 1: Analyzing missing values...")
        analyze_missing_values(df_raw)
        
        # Step 2: Apply strategy-specific imputation
        print("\nStep 2: Applying imputation strategies...")
        
        # Drop rows with nulls in critical columns
        df_clean = drop_rows_with_nulls(df_raw, ['customer_id', 'email'])
        
        # Impute numerical columns
        df_clean = impute_mean_median(df_clean, ['amount', 'quantity'], strategy='median')
        
        # Impute categorical columns
        df_clean = impute_mode(df_clean, ['category', 'region'])
        
        # Impute time-series columns
        df_clean = impute_forward_fill(df_clean, ['last_updated'])
        
        # Step 3: Document decisions
        print("\nStep 3: Documenting imputation decisions...")
        document_imputation_decisions(df_original, df_clean)
        
        # Step 4: Validate results
        print("\nStep 4: Validating imputation...")
        validate_imputation(df_original, df_clean)
        
        # Save cleaned data
        df_clean.to_csv(output_file, index=False)
        print(f"\n✓ Cleaned data saved to {output_file}")
        
    except Exception as err:
        print(f"Missing Value Treatment Failed: {err}", file=sys.stderr)
        sys.exit(1)
