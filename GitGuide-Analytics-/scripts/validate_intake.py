"""
Dataset Intake Validation Script
GitGuide-Analytics

Validates incoming raw datasets for format consistency, schema completeness, 
file encoding, and general ingestion readiness before any processing or 
transformation occurs.

Execution:
    python scripts/validate_intake.py
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import chardet

# Expected columns for customer transaction dataset
EXPECTED_COLUMNS = ['customer_id', 'customer_name', 'transaction_amount', 'transaction_date']


def validate_file_exists(filepath):
    """
    Check if file exists at the specified path and contains data.
    
    Input:
        filepath (str): Absolute or relative path to the file.
        
    Output:
        tuple (bool, str): (True, success message) or (False, error message).
        
    Assumptions & Constraints:
        - The filepath must be a valid string pointing to a file (not a directory).
        - A file with 0 bytes is considered empty and invalid.
    """
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"
    
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    
    return True, "File exists and has content"


def validate_file_format(filepath, allowed_formats=['csv', 'json', 'xlsx']):
    """
    Check if the file extension is among the supported formats.
    
    Input:
        filepath (str): Filepath of the dataset.
        allowed_formats (list): List of allowed lower-case file extensions.
        
    Output:
        tuple (bool, str): (True, validation message) or (False, error message).
        
    Assumptions & Constraints:
        - Supported formats default to CSV, JSON, and XLSX.
        - Check is case-insensitive.
    """
    extension = filepath.split('.')[-1].lower()
    
    if extension not in allowed_formats:
        return False, f"Unsupported format: {extension}. Allowed: {allowed_formats}"
    
    return True, f"Format valid: {extension}"


def validate_schema(df, expected_columns):
    """
    Compare the columns of the loaded DataFrame against the expected column list.
    
    Input:
        df (pd.DataFrame): The loaded dataset DataFrame.
        expected_columns (list): List of expected column names.
        
    Output:
        tuple (bool, str): (True, validation message) or (False, detailed schema issues).
        
    Assumptions & Constraints:
        - The input must be a valid Pandas DataFrame.
        - Reports both missing columns and extra (unexpected) columns.
        - Column order changes are not flagged as failures, but missing/extra ones are.
    """
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)
    
    issues = []
    if missing:
        issues.append(f"Missing columns: {list(missing)}")
    if extra:
        issues.append(f"Unexpected columns: {list(extra)}")
    
    if not issues:
        return True, f"Schema valid: {len(df.columns)} columns present"
    return False, " | ".join(issues)


def detect_encoding(filepath):
    """
    Detect the encoding of a file using raw byte analysis to prevent load crashes.
    
    Input:
        filepath (str): Filepath of the target dataset.
        
    Output:
        tuple (str, str): (Detected encoding string, verbose message detailing confidence).
        
    Assumptions & Constraints:
        - Reads up to 10,000 bytes for encoding detection to maintain speed.
        - Falls back to 'utf-8' if detection fails or confidence is too low.
    """
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(10000))
    
    encoding = result.get('encoding', 'utf-8')
    confidence = result.get('confidence', 0)
    
    # If encoding detection fails, fallback safely to utf-8
    if encoding is None:
        encoding = 'utf-8'
        confidence = 0.0
        
    return encoding, f"Detected: {encoding} (confidence: {confidence:.1%})"


def capture_dataset_stats(filepath, df):
    """
    Capture raw file size and loaded DataFrame dimensions for pipeline baselines.
    
    Input:
        filepath (str): Filepath of the dataset.
        df (pd.DataFrame): The loaded dataset DataFrame.
        
    Output:
        dict: Summary statistics including rows, columns, file_size_mb, and bytes.
        
    Assumptions & Constraints:
        - Assumes df is a loaded Pandas DataFrame.
        - MB conversion uses base 1024.
    """
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = file_size_bytes / (1024 * 1024)
    row_count = len(df)
    col_count = len(df.columns)
    
    return {
        'rows': row_count,
        'columns': col_count,
        'file_size_mb': round(file_size_mb, 5),  # Precision for small test files
        'bytes': file_size_bytes
    }


def generate_intake_report(filepath, expected_columns):
    """
    Perform all dataset validations and output a structured JSON validation report.
    
    Input:
        filepath (str): Filepath of the dataset to validate.
        expected_columns (list): The reference column schema.
        
    Output:
        dict: The final report dictionary.
        
    Assumptions & Constraints:
        - Output directory 'output/' must exist (it will be created if missing).
        - Saves the validation results as JSON in 'output/intake_report.json'.
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'filepath': filepath,
        'validations': {}
    }
    
    # Task 1: Check existence & non-emptiness
    file_exists, msg = validate_file_exists(filepath)
    report['validations']['file_exists'] = msg
    if not file_exists:
        print(f"✗ Validation Failed: {msg}")
        return report
    
    # Task 2: Check format extension
    format_valid, msg = validate_file_format(filepath)
    report['validations']['format'] = msg
    if not format_valid:
        print(f"✗ Validation Failed: {msg}")
        return report
        
    # Task 3: Detect encoding
    encoding, encoding_msg = detect_encoding(filepath)
    report['validations']['encoding'] = encoding_msg
    
    # Load data for detailed validation checks
    try:
        df = pd.read_csv(filepath, encoding=encoding)
    except Exception as e:
        report['validations']['schema'] = f"Failed to load CSV: {str(e)}"
        print(f"✗ Load Error: {e}")
        return report
    
    # Task 4: Check column schema completeness
    schema_valid, schema_msg = validate_schema(df, expected_columns)
    report['validations']['schema'] = schema_msg
    
    # Task 5: Capture statistics
    stats = capture_dataset_stats(filepath, df)
    report['statistics'] = stats
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Save report to file
    with open('output/intake_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
        
    print(f"✓ Validation completed successfully for: {filepath}")
    print(f"✓ Report generated at: output/intake_report.json")
    return report


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 checkmarks cleanly on Windows environments
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve target dataset relative path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sample_file = os.path.join(base_dir, "data", "raw", "sample.csv")
    
    print(f"Starting intake validation on dataset: {sample_file}")
    
    try:
        report_data = generate_intake_report(sample_file, EXPECTED_COLUMNS)
        # Print a pretty summary of validations
        print("\n=== Validation Report Summary ===")
        print(json.dumps(report_data, indent=2))
    except Exception as err:
        print(f"Pipeline Intake Validation Failed: {err}", file=sys.stderr)
        sys.exit(1)
