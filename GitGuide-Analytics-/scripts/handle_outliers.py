"""
Outlier Detection and Handling Pipeline
GitGuide-Analytics

Detects extreme values and anomalies using Z-score and Interquartile Range (IQR) methods.
Applies capping/Winsorization and binary flagging strategies, logs all transformations
in an audit file, and exports cleaned datasets.

Execution:
    python scripts/handle_outliers.py
"""

import os
import sys
import pandas as pd
import numpy as np
from scipy import stats


def detect_outliers_zscore(df, column, threshold=3.0):
    """
    Detect outliers as values beyond ±threshold standard deviations from the mean.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Numerical column to analyze.
        threshold (float): Z-score cut-off threshold (default is 3.0).
        
    Returns:
        tuple: (DataFrame with zscore column added, outliers DataFrame).
    """
    df_out = df.copy()
    z_col = f"{column}_zscore"
    
    # Calculate absolute Z-score
    df_out[z_col] = np.abs(stats.zscore(df_out[column]))
    z_outliers = df_out[df_out[z_col] > threshold]
    
    print(f"\n--- Z-Score Outlier Detection ({column}) ---")
    print(f"Threshold: ±{threshold} standard deviations")
    print(f"Z-Score outliers detected: {len(z_outliers)}")
    if len(z_outliers) > 0:
        print(z_outliers[['customer_id', column, z_col]].to_string(index=False))
        
    return df_out, z_outliers


def detect_outliers_iqr(df, column, multiplier=1.5):
    """
    Detect outliers beyond Q1 - multiplier*IQR and Q3 + multiplier*IQR.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Numerical column to analyze.
        multiplier (float): IQR multiplier factor (default is 1.5).
        
    Returns:
        tuple: (DataFrame with is_outlier_iqr column added, lower_bound, upper_bound).
    """
    df_out = df.copy()
    q1 = df_out[column].quantile(0.25)
    q3 = df_out[column].quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    flag_col = f"is_outlier_iqr_{column}"
    df_out[flag_col] = (df_out[column] < lower_bound) | (df_out[column] > upper_bound)
    
    print(f"\n--- IQR Outlier Detection ({column}) ---")
    print(f"Q1 (25th percentile): {q1:.2f}")
    print(f"Q3 (75th percentile): {q3:.2f}")
    print(f"IQR: {iqr:.2f}")
    print(f"Lower Bound: {lower_bound:.2f}")
    print(f"Upper Bound: {upper_bound:.2f}")
    print(f"IQR Outliers detected: {df_out[flag_col].sum()}")
    
    return df_out, lower_bound, upper_bound


def cap_outliers(df, column, lower, upper):
    """
    Cap/Winsorize extreme values at lower and upper boundary thresholds.
    
    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Target column to cap.
        lower (float): Lower capping boundary.
        upper (float): Upper capping boundary.
        
    Returns:
        pd.DataFrame: DataFrame with capped column.
    """
    df_capped = df.copy()
    capped_col = f"{column}_capped"
    df_capped[capped_col] = df_capped[column].clip(lower=lower, upper=upper)
    
    print(f"\n--- Capping Outliers ({column}) ---")
    print(f"Before: min={df_capped[column].min():.2f}, max={df_capped[column].max():.2f}")
    print(f"After:  min={df_capped[capped_col].min():.2f}, max={df_capped[capped_col].max():.2f}")
    
    return df_capped


def flag_combined_outliers(df, columns):
    """
    Combine Z-score and IQR flags into a single binary anomaly column.
    
    Args:
        df (pd.DataFrame): Input DataFrame with individual outlier flags.
        columns (list): Numerical columns being evaluated.
        
    Returns:
        pd.DataFrame: DataFrame with 'is_outlier' binary flag.
    """
    df_flagged = df.copy()
    
    # Combined condition across evaluated columns
    is_outlier_condition = pd.Series(False, index=df_flagged.index)
    
    for col in columns:
        iqr_col = f"is_outlier_iqr_{col}"
        z_col = f"{col}_zscore"
        if iqr_col in df_flagged.columns:
            is_outlier_condition |= df_flagged[iqr_col]
        if z_col in df_flagged.columns:
            is_outlier_condition |= (df_flagged[z_col] > 3.0)
            
    df_flagged['is_outlier'] = is_outlier_condition
    
    normal = df_flagged[~df_flagged['is_outlier']]
    anomalies = df_flagged[df_flagged['is_outlier']]
    
    print(f"\n--- Combined Binary Outlier Flagging ---")
    print(f"Normal records: {len(normal)}")
    print(f"Anomalies:      {len(anomalies)}")
    
    return df_flagged


def create_cleaning_log(log_records, output_path):
    """
    Export transformation decisions to a structured CSV audit log.
    
    Args:
        log_records (list): List of transformation dictionary records.
        output_path (str): File path for saving the log CSV.
        
    Returns:
        pd.DataFrame: The saved audit log DataFrame.
    """
    log_df = pd.DataFrame(log_records)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    log_df.to_csv(output_path, index=False)
    print(f"\n✓ Cleaning log successfully saved to {output_path}")
    print(log_df.to_string(index=False))
    return log_df


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_file = os.path.join(base_dir, "data", "raw", "outlier_data.csv")
    output_processed = os.path.join(base_dir, "data", "processed", "outliers_treated.csv")
    output_log = os.path.join(base_dir, "output", "cleaning_log.csv")

    os.makedirs(os.path.dirname(output_processed), exist_ok=True)

    print("==============================================================")
    print("RUNNING OUTLIER DETECTION AND HANDLING PIPELINE")
    print("==============================================================\n")

    # Load raw data
    print("Step 1: Loading raw dataset...")
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} records from {input_file}")
    print(df.to_string(index=False))

    cleaning_log_records = []
    current_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    # Step 2: Revenue Outlier Detection & Capping
    print("\nStep 2: Processing revenue column...")
    df, z_outliers_rev = detect_outliers_zscore(df, 'revenue', threshold=3.0)
    df, lower_rev, upper_rev = detect_outliers_iqr(df, 'revenue', multiplier=1.5)
    df = cap_outliers(df, 'revenue', lower_rev, upper_rev)
    
    cleaning_log_records.append({
        'column': 'revenue',
        'method': 'IQR',
        'action': 'cap',
        'threshold_lower': round(lower_rev, 2),
        'threshold_upper': round(upper_rev, 2),
        'affected_rows': int(df[f"is_outlier_iqr_revenue"].sum()),
        'date': current_time
    })

    # Step 3: Age Outlier Detection & Capping
    print("\nStep 3: Processing age column...")
    df, z_outliers_age = detect_outliers_zscore(df, 'age', threshold=3.0)
    df, lower_age, upper_age = detect_outliers_iqr(df, 'age', multiplier=1.5)
    df = cap_outliers(df, 'age', lower_age, upper_age)
    
    cleaning_log_records.append({
        'column': 'age',
        'method': 'IQR_and_ZScore',
        'action': 'cap',
        'threshold_lower': round(lower_age, 2),
        'threshold_upper': round(upper_age, 2),
        'affected_rows': int(df[f"is_outlier_iqr_age"].sum()),
        'date': current_time
    })

    # Step 4: Combined Binary Flagging
    print("\nStep 4: Creating combined binary anomaly flag...")
    df = flag_combined_outliers(df, ['revenue', 'age'])

    # Step 5: Save Processed Data & Log
    print("\nStep 5: Saving outputs...")
    df.to_csv(output_processed, index=False)
    print(f"✓ Processed dataset saved to {output_processed}")

    create_cleaning_log(cleaning_log_records, output_log)
    print("==============================================================")
