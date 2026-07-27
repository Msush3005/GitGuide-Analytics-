"""
String Cleaning and Text Standardization Pipeline
GitGuide-Analytics

Processes unstructured string fields in data pipelines by trimming whitespaces,
standardizing casing, removing special symbols, mapping category variations,
and preserving target schemas.

Execution:
    python scripts/string_cleaning_pipeline.py
"""

import os
import sys
import pandas as pd
import numpy as np


def strip_all_strings(df):
    """
    Trim leading and trailing whitespace from all string columns in the DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        
    Returns:
        pd.DataFrame: DataFrame with trimmed string values.
    """
    df_clean = df.copy()
    string_cols = df_clean.select_dtypes(include=['object']).columns
    
    print("\n--- Whitespace Trimming Log ---")
    for col in string_cols:
        before = df_clean[col].nunique()
        df_clean[col] = df_clean[col].astype(str).str.strip()
        after = df_clean[col].nunique()
        print(f"  ✓ {col}: unique count reduced from {before} → {after}")
        
    return df_clean


def normalize_casing(df, columns_to_lower):
    """
    Standardize letter casing to lowercase for target categorical columns.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        columns_to_lower (list): List of column names to lowercase.
        
    Returns:
        pd.DataFrame: DataFrame with normalized casing.
    """
    df_clean = df.copy()
    
    print("\n--- Casing Normalization Log ---")
    for col in columns_to_lower:
        if col in df_clean.columns:
            before_unique = df_clean[col].nunique()
            df_clean[col] = df_clean[col].astype(str).str.lower()
            after_unique = df_clean[col].nunique()
            print(f"  ✓ Normalized {col} to lowercase (unique count: {before_unique} → {after_unique})")
            
    return df_clean


def remove_special_characters(df, columns):
    """
    Wipe non-alphanumeric and special characters from target columns using regex.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        columns (list): Columns to strip of special symbols.
        
    Returns:
        pd.DataFrame: DataFrame without special characters.
    """
    df_clean = df.copy()
    pattern = '[^a-zA-Z0-9 ]'
    
    print("\n--- Special Character Removal Log ---")
    for col in columns:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.replace(pattern, '', regex=True)
            print(f"  ✓ Cleared special characters from {col} using pattern: {pattern}")
            
    return df_clean


def clean_text_column(series, lowercase=True, strip=True, 
                     remove_special=False, mapping=None):
    """
    Reusable text cleaning function for any string pandas Series with null handling.
    
    Args:
        series (pd.Series): Target series containing strings.
        lowercase (bool): Convert values to lowercase.
        strip (bool): Strip leading/trailing whitespaces.
        remove_special (bool): Strip non-alphanumeric characters.
        mapping (dict): Canonical dictionary values mapping.
        
    Returns:
        pd.Series: Standardized clean Series.
    """
    # Create copy and preserve null locations
    result = series.copy()
    
    # Audit null values
    null_count = result.isna().sum()
    if null_count > 0:
        print(f"  [Warning] Column contains {null_count} null/NaN values")
        
    # Convert series to string type for operation, preserving actual NaNs
    mask_notnull = result.notnull()
    
    if strip:
        result.loc[mask_notnull] = result.loc[mask_notnull].astype(str).str.strip()
        
    if lowercase:
        result.loc[mask_notnull] = result.loc[mask_notnull].astype(str).str.lower()
        
    if remove_special:
        result.loc[mask_notnull] = result.loc[mask_notnull].astype(str).str.replace('[^a-zA-Z0-9 ]', '', regex=True)
        
    if mapping:
        # Standardize input keys to lowercase for robust matching
        lowercase_mapping = {k.lower(): v for k, v in mapping.items()}
        
        def apply_map(val):
            if pd.isna(val):
                return val
            val_str = str(val).strip().lower()
            return lowercase_mapping.get(val_str, val)
            
        result = result.apply(apply_map)
        
    return result


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_file = os.path.join(base_dir, "data", "processed", "cleaned_strings.csv")

    # Create processed directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print("==============================================================")
    print("RUNNING STRING CLEANING PIPELINE")
    print("==============================================================\n")

    # 1. Generate messy synthetic dataset
    print("Step 1: Loading raw messy dataset...")
    raw_data = {
        'product_name': [' Electronics ', 'electronics', 'ELECTRONICS', '  Software  ', 'software', 'SOFTWARE', ' Electronics ', 'electronics', 'ELECTRONICS', '  Software  '],
        'cust_segment': ['B2B', 'b2b', 'b 2 b', 'small medium enterprise', 'sme', 'smb', 'corp', 'ent', 'enterprise', 'B2B'],
        'location': ['São Paulo', 'Montréal', 'New York', 'São Paulo', 'Montréal', 'New York', 'São Paulo', 'Montréal', 'New York', 'São Paulo']
    }
    df = pd.DataFrame(raw_data)
    df_original = df.copy()

    print("\nInitial Data Dtypes & Unique Counts:")
    print(df.dtypes)
    for col in df.columns:
        print(f"  {col} unique values: {df[col].unique().tolist()}")

    # Define canonical mappings (3 categories with at least 3 variations each)
    segment_map = {
        'b2b': 'B2B',
        'b 2 b': 'B2B',
        'b2 b': 'B2B',
        'business-to-business': 'B2B',
        'sme': 'SMB',
        'small medium enterprise': 'SMB',
        'smb': 'SMB',
        'small-to-medium business': 'SMB',
        'enterprise': 'Enterprise',
        'corp': 'Enterprise',
        'corporate': 'Enterprise',
        'ent': 'Enterprise'
    }

    # Step 2: Apply string cleaning pipeline transformations
    print("\nStep 2: Processing columns with clean_text_column function...")
    
    # Product Name: Lowercase & Strip (casing normalization + trim whitespace)
    print("\nProcessing product_name (lowercase=True, strip=True):")
    df['product_name'] = clean_text_column(df['product_name'], lowercase=True, strip=True)
    
    # Location: Strip special international characters (São Paulo -> So Paulo, Montréal -> Montral)
    print("\nProcessing location (lowercase=False, strip=True, remove_special=True):")
    df['location'] = clean_text_column(df['location'], lowercase=False, strip=True, remove_special=True)
    
    # Customer Segment: Map variations to standard canonical forms
    print("\nProcessing cust_segment (lowercase=True, strip=True, mapping=segment_map):")
    df['cust_segment'] = clean_text_column(df['cust_segment'], lowercase=True, strip=True, mapping=segment_map)

    # Step 3: Compare results before and after
    print("\nStep 3: Comparing Value Counts Before vs After...")
    
    print("\n--- Product Name Consolidation ---")
    print("BEFORE:")
    print(df_original['product_name'].value_counts())
    print("AFTER:")
    print(df['product_name'].value_counts())
    
    print("\n--- Location Consolidation (Accented Characters Removed) ---")
    print("BEFORE:")
    print(df_original['location'].value_counts())
    print("AFTER:")
    print(df['location'].value_counts())
    
    print("\n--- Segment Mapping Consolidation ---")
    print("BEFORE:")
    print(df_original['cust_segment'].value_counts())
    print("AFTER:")
    print(df['cust_segment'].value_counts())

    # Save cleaned data to CSV
    df.to_csv(output_file, index=False)
    print(f"\n✓ Cleaned data saved to {output_file}")

    # Step 4: Run edge-case testing block as requested
    print("\n==============================================================")
    print("RUNNING EDGE-CASE PIPELINE TESTING")
    print("==============================================================")
    
    test_cases = [
        '  Product A  ',      # Leading/trailing spaces
        'PRODUCT B',         # All caps
        'Product_C',         # Special char
        None,                # Null value
        ''                   # Empty string
    ]

    test_series = pd.Series(test_cases)
    result_series = clean_text_column(test_series, lowercase=True, strip=True, remove_special=True)
    
    print("\nTest Input Series:")
    print(test_series.tolist())
    print("\nStandardized Output Series:")
    print(result_series.tolist())
    print("==============================================================")
