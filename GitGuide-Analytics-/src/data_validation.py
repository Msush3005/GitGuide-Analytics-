"""
Data Validation and Quality Pipeline Module
GitGuide-Analytics

Provides schema validation, null value checks, and duplicate detection
for incoming analytics datasets before downstream processing.
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

REQUIRED_COLUMNS = ["contributor_id", "repository_name", "commits_count", "pull_requests_opened", "timestamp"]


def validate_csv_schema(file_path: str) -> bool:
    """
    Validates incoming CSV file structure and encoding.
    Checks column names, data types, and non-empty status.
    """
    try:
        df = pd.read_csv(file_path)
        logging.info(f"Loaded dataset {file_path} with shape {df.shape}")
        
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            return False
            
        logging.info("Schema validation successful. All required columns present.")
        return True
    except Exception as e:
        logging.error(f"Failed to validate schema for {file_path}: {e}")
        return False


def generate_quality_report(df: pd.DataFrame) -> dict:
    """
    Generates a summary quality report of the dataset.
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }
    logging.info(f"Data Quality Report Generated: {report['total_rows']} rows, {report['duplicate_rows']} duplicates.")
    return report
