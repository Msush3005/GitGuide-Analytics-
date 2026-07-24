"""
Explicit Data Type Enforcement Script
GitGuide-Analytics

Enforces type safety across data pipelines by casting columns, standardizing string
dates to proper datetime formats, stripping currency formatting to numeric floats,
and mapping binary flags to boolean values.

Execution:
    python scripts/enforce_types.py
"""

import os
import sys
import pandas as pd
import numpy as np


def cast_columns_to_types(df, type_mapping):
    """
    Explicitly cast columns to correct dtypes and return a conversion log.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        type_mapping (dict): Dict of {column: target_dtype}.
        
    Returns:
        tuple: (DataFrame with corrected types, conversion log dict).
        
    Assumptions & Constraints:
        - Columns in type_mapping that are missing from df will be warned but not crash.
    """
    df_typed = df.copy()
    conversion_log = {}
    
    for col, target_dtype in type_mapping.items():
        if col not in df.columns:
            print(f"Warning: Column {col} not found in DataFrame")
            continue
            
        original_dtype = df[col].dtype
        
        try:
            df_typed[col] = df_typed[col].astype(target_dtype)
            conversion_log[col] = {
                'from': str(original_dtype),
                'to': str(target_dtype),
                'status': 'success'
            }
            print(f"✓ {col}: {original_dtype} → {target_dtype}")
        except Exception as e:
            conversion_log[col] = {
                'from': str(original_dtype),
                'to': str(target_dtype),
                'status': 'failed',
                'error': str(e)
            }
            print(f"✗ {col}: Conversion failed - {e}")
            raise
            
    return df_typed, conversion_log


def convert_string_dates_to_datetime(df, date_columns, date_format=None):
    """
    Convert string columns to datetime with explicit format constraints.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        date_columns (list): List of column names containing dates.
        date_format (str): Datetime format string (e.g., '%Y-%m-%d').
        
    Returns:
        pd.DataFrame: DataFrame with datetime columns converted.
        
    Assumptions & Constraints:
        - Specifying the date_format string prevents date parsing ambiguities.
    """
    df_typed = df.copy()
    
    for col in date_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
            
        try:
            if date_format:
                df_typed[col] = pd.to_datetime(df_typed[col], format=date_format)
            else:
                df_typed[col] = pd.to_datetime(df_typed[col])
                
            print(f"✓ {col}: Converted to datetime")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            print(f"  Sample values: {df[col].head(3).tolist()}")
            print(f"  Expected format: {date_format}")
            raise
            
    return df_typed


def convert_currency_to_float(df, currency_columns):
    """
    Strip currency symbols and convert columns to float.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        currency_columns (list): List of column names with currency values.
        
    Returns:
        pd.DataFrame: DataFrame with clean numeric columns.
        
    Assumptions & Constraints:
        - Strips '$' and ',' format characters from strings.
        - Coerces unconvertible values to NaN.
    """
    df_typed = df.copy()
    
    for col in currency_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
            
        try:
            # Strip common formatting parameters
            df_typed[col] = (df_typed[col]
                            .astype(str)
                            .str.replace('[$,]', '', regex=True)
                            .str.strip())
            
            df_typed[col] = pd.to_numeric(df_typed[col], errors='coerce')
            
            # Warn on conversion anomalies
            failed_conversions = df_typed[col].isnull().sum() - df[col].isnull().sum()
            if failed_conversions > 0:
                print(f"⚠ {col}: {failed_conversions} values could not be converted to numeric")
                
            print(f"✓ {col}: Stripped symbols, converted to float")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            raise
            
    return df_typed


def convert_integers_to_boolean(df, boolean_columns):
    """
    Convert binary integer representation flags or strings to proper boolean types.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        boolean_columns (list): List of columns containing binary flags.
        
    Returns:
        pd.DataFrame: DataFrame with bool columns.
        
    Assumptions & Constraints:
        - Handles integer flags (0/1), string labels ('yes'/'no', 'true'/'false').
    """
    df_typed = df.copy()
    
    for col in boolean_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
            
        try:
            unique_vals = df[col].unique()
            print(f"  {col} unique values: {unique_vals}")
            
            # Map object mappings if columns arrive as strings
            if df[col].dtype == 'object':
                mapping = {
                    'yes': True, 'no': False,
                    'y': True, 'n': False,
                    'true': True, 'false': False,
                    '1': True, '0': False,
                    1: True, 0: False,
                    True: True, False: False
                }
                df_typed[col] = df_typed[col].map(mapping)
            else:
                df_typed[col] = df_typed[col].astype(bool)
                
            print(f"✓ {col}: Converted to boolean")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            raise
            
    return df_typed


def compare_dtypes(df_original, df_typed):
    """
    Compare column datatypes before and after execution and save report.
    
    Args:
        df_original (pd.DataFrame): Input raw DataFrame.
        df_typed (pd.DataFrame): Processed DataFrame.
        
    Returns:
        pd.DataFrame: Summary comparison DataFrame.
    """
    comparison = pd.DataFrame({
        'column': df_original.columns,
        'dtype_before': df_original.dtypes.values,
        'dtype_after': df_typed.dtypes.values,
        'changed': (df_original.dtypes != df_typed.dtypes).values
    })
    
    print("\n" + "="*70)
    print("DTYPE CONVERSION SUMMARY")
    print("="*70)
    print(comparison.to_string(index=False))
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save report
    comparison.to_csv('output/dtype_conversion_report.csv', index=False)
    print("\nReport saved to output/dtype_conversion_report.csv")
    print("="*70)
    
    return comparison


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    input_file = os.path.join(base_dir, "data", "raw", "untyped_data.csv")
    output_file = os.path.join(base_dir, "data", "processed", "typed_data.csv")

    # Create processed directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("Starting data type enforcement...\n")
    
    try:
        # Load raw data
        df = pd.read_csv(input_file)
        
        print("="*70)
        print("BEFORE TYPE CONVERSION")
        print("="*70)
        print(df.dtypes)
        print(f"\nSample data:")
        print(df.head(3))
        
        df_typed = df.copy()
        
        # 1. Convert string dates to datetime
        print("\n1. Converting date columns...")
        df_typed = convert_string_dates_to_datetime(
            df_typed,
            ['transaction_date', 'signup_date'],
            date_format='%Y-%m-%d'
        )
        
        # 2. Convert currency columns (warns/bypasses missing 'revenue')
        print("\n2. Converting currency columns...")
        df_typed = convert_currency_to_float(
            df_typed,
            ['amount', 'revenue']
        )
        
        # 3. Convert boolean columns (warns/bypasses missing 'is_premium')
        print("\n3. Converting boolean columns...")
        df_typed = convert_integers_to_boolean(
            df_typed,
            ['is_active', 'is_premium']
        )
        
        # 4. Compare dtypes before/after
        print("\n4. Comparing before/after types...")
        print("="*70)
        print("AFTER TYPE CONVERSION")
        print("="*70)
        print(df_typed.dtypes)
        print(f"\nSample data:")
        print(df_typed.head(3))
        
        # Save comparison report
        compare_dtypes(df, df_typed)
        
        # Save typed output data
        df_typed.to_csv(output_file, index=False)
        print(f"\n✓ Typed data saved to {output_file}")
        
    except Exception as err:
        print(f"Data Type Enforcement Failed: {err}", file=sys.stderr)
        sys.exit(1)
