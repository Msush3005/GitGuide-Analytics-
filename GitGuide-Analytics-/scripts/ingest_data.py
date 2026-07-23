"""
Multi-Format Data Ingestion Pipeline
GitGuide-Analytics

Ingests datasets of diverse formats (CSV, JSON, nested files) into analysis-ready
Pandas DataFrames. Supports explicit delimiters, custom character encodings, 
nested JSON structure flattening, and fallback encoding strategies.

Execution:
    python scripts/ingest_data.py
"""

import os
import sys
import json
import pandas as pd


def ingest_csv(filepath, delimiter=',', encoding='utf-8', dtype_dict=None):
    """
    Load CSV file with explicit parameters and print basic confirmation metrics.
    
    Args:
        filepath (str): Path to the target CSV file.
        delimiter (str): Field separator character. Default is ','.
        encoding (str): Text file character encoding. Default is 'utf-8'.
        dtype_dict (dict): Dictionary mapping column names to target pandas types.
        
    Returns:
        pd.DataFrame: Loaded Pandas DataFrame.
        
    Assumptions & Constraints:
        - The file must exist and contain valid tabular formatting.
        - If character decoding fails, raises UnicodeDecodeError.
    """
    try:
        df = pd.read_csv(
            filepath,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )
        print(f"✓ CSV loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise
    except UnicodeDecodeError as e:
        print(f"Encoding error: Could not decode with {encoding}")
        print("Try: latin-1, iso-8859-1, or cp1252")
        raise


def ingest_json(filepath, is_nested=False):
    """
    Load JSON dataset, automatically flattening nested structures if requested.
    
    Args:
        filepath (str): Path to the JSON dataset file.
        is_nested (bool): If True, flattens nested elements into tabular form.
        
    Returns:
        pd.DataFrame: Pandas DataFrame with nested dictionary data expanded.
        
    Assumptions & Constraints:
        - The file must be structured as valid JSON.
        - Nested dictionary flattening maps sub-keys using dot notation (e.g. parent.child).
    """
    try:
        # Load nested structure using standard JSON parser for reliable normalization
        if is_nested:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.json_normalize(data)
            print("✓ Nested JSON flattened to tabular format")
        else:
            df = pd.read_json(filepath)
            
        print(f"✓ JSON loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise
    except Exception as e:
        print(f"JSON load failed: {str(e)}")
        raise


def ingest_csv_with_fallback(filepath, delimiters=[','], fallback_encodings=None):
    """
    Load CSV with a sequential fallback strategy trying multiple encodings and delimiters.
    
    Args:
        filepath (str): Path to target CSV file.
        delimiters (list): Delimiters to try in sequence. Default is [','].
        fallback_encodings (list): Character encodings to try. Default covers common types.
        
    Returns:
        pd.DataFrame: Successfully parsed Pandas DataFrame.
        
    Assumptions & Constraints:
        - Safely bypasses Unicode decoding and parsing errors until a combination works.
    """
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                print(f"✓ Successfully loaded with delimiter='{delimiter}', encoding='{encoding}'")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
                
    raise ValueError(f"Could not load {filepath} with any encoding/delimiter combination")


def document_ingestion(df, source_file):
    """
    Print a structured audit report detailing row count, column shapes, datatypes, and head values.
    
    Args:
        df (pd.DataFrame): The ingested Pandas DataFrame.
        source_file (str): The filename/path of the data source.
        
    Returns:
        pd.DataFrame: The original DataFrame unchanged.
    """
    print(f"\n{'='*60}")
    print(f"INGESTION REPORT: {source_file}")
    print(f"{'='*60}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"\nColumn Names & Data Types:")
    print(df.dtypes)
    print(f"\nNull Values Per Column:")
    print(df.isnull().sum())
    print(f"\nFirst 3 Rows:")
    print(df.head(3).to_string())
    print(f"{'='*60}\n")
    return df


if __name__ == "__main__":
    # Configure stdout to handle UTF-8 console output
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve absolute paths relative to the repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    csv_input = os.path.join(base_dir, "data", "raw", "customers.csv")
    json_input = os.path.join(base_dir, "data", "raw", "transactions.json")
    
    csv_output = os.path.join(base_dir, "data", "processed", "customers_ingested.csv")
    json_output = os.path.join(base_dir, "data", "processed", "transactions_ingested.csv")

    # Create target directories if they don't exist
    os.makedirs(os.path.dirname(csv_output), exist_ok=True)

    print("Starting multi-format ingestion...\n")
    
    try:
        # Load CSV with explicit parameters
        csv_df = ingest_csv(
            csv_input,
            delimiter=',',
            encoding='utf-8'
        )
        document_ingestion(csv_df, "customers.csv")
        
        # Load JSON with flattening
        json_df = ingest_json(
            json_input,
            is_nested=True
        )
        document_ingestion(json_df, "transactions.json")
        
        # Save ingested results
        csv_df.to_csv(csv_output, index=False)
        json_df.to_csv(json_output, index=False)
        
        print("\n✓ All data ingested and saved to processed/")
        
    except Exception as err:
        print(f"Ingestion Pipeline Failed: {err}", file=sys.stderr)
        sys.exit(1)
