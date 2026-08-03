"""
Relational Data Merging & Join Validation Pipeline
GitGuide-Analytics

Executes relational joins across customer and order tables, validates row count deltas,
identifies unmatched keys and orphaned records, compares join strategies (Inner, Left,
Right, Outer), detects column collision suffixes, and logs join decision metrics.

Execution:
    python scripts/merge_datasets.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np


def generate_synthetic_datasets(customers_path, orders_path):
    """
    Generate synthetic customer (1,000 rows) and order (5,000 rows) datasets
    with deliberate unmatched keys for testing join validation.
    
    Args:
        customers_path (str): Output CSV path for customer table.
        orders_path (str): Output CSV path for orders table.
        
    Returns:
        tuple: (df_customers, df_orders).
    """
    np.random.seed(42)
    os.makedirs(os.path.dirname(customers_path), exist_ok=True)
    os.makedirs(os.path.dirname(orders_path), exist_ok=True)

    # 1. Customers Table (1,000 rows: customer_id 1 to 1000)
    customer_ids = np.arange(1, 1001)
    segments = np.random.choice(['B2B', 'B2C', 'SMB'], size=1000, p=[0.3, 0.5, 0.2])
    names = [f"Customer_{cid}" for cid in customer_ids]
    signup_dates = pd.date_range(start='2024-01-01', periods=1000, freq='D').strftime('%Y-%m-%d')

    df_customers = pd.DataFrame({
        'customer_id': customer_ids,
        'customer_name': names,
        'customer_segment': segments,
        'signup_date': signup_dates
    })

    # 2. Orders Table (5,000 rows: customer_id range 50 to 1050)
    # IDs 1-49 in customers have no orders (unmatched left)
    # IDs 1001-1050 in orders do not exist in customers (orphaned right)
    order_ids = np.arange(5001, 10001)
    order_customer_ids = np.random.choice(np.arange(50, 1051), size=5000)
    amounts = np.round(np.random.uniform(10.0, 500.0, size=5000), 2)
    order_dates = pd.date_range(start='2025-01-01', periods=5000, freq='h').strftime('%Y-%m-%d %H:%M:%S')

    df_orders = pd.DataFrame({
        'order_id': order_ids,
        'customer_id': order_customer_ids,
        'order_amount': amounts,
        'order_date': order_dates
    })

    # Save to disk
    df_customers.to_csv(customers_path, index=False)
    df_orders.to_csv(orders_path, index=False)

    print("✓ Generated raw synthetic datasets:")
    print(f"  - Customers: {len(df_customers)} rows ({customers_path})")
    print(f"  - Orders:    {len(df_orders)} rows ({orders_path})")
    return df_customers, df_orders


def execute_explicit_join(df_left, df_right, join_key='customer_id', how='left'):
    """
    Perform explicit join with row count logging and change calculation.
    
    Args:
        df_left (pd.DataFrame): Left table (Customers).
        df_right (pd.DataFrame): Right table (Orders).
        join_key (str): Common key column.
        how (str): Join strategy ('left', 'inner', 'right', 'outer').
        
    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    left_count = len(df_left)
    right_count = len(df_right)

    df_merged = pd.merge(df_left, df_right, on=join_key, how=how)
    merged_count = len(df_merged)
    delta = merged_count - left_count

    print(f"\n--- Task 1: Explicit {how.upper()} Join with Row Count Validation ---")
    print(f"Left table ({'df_customers'}):  {left_count} rows")
    print(f"Right table ({'df_orders'}):    {right_count} rows")
    print(f"Merged result:                  {merged_count} rows")
    print(f"Row count change (Merged - Left): {delta:+d} rows")

    return df_merged


def detect_unmatched_keys(df_left, df_right, join_key='customer_id', output_dir='output'):
    """
    Detect and export unmatched keys for both left and right tables.
    
    Args:
        df_left (pd.DataFrame): Left table.
        df_right (pd.DataFrame): Right table.
        join_key (str): Common join key.
        output_dir (str): Output folder for CSV diagnostic files.
        
    Returns:
        tuple: (unmatched_left, unmatched_right).
    """
    os.makedirs(output_dir, exist_ok=True)

    unmatched_customers = df_left[~df_left[join_key].isin(df_right[join_key])].copy()
    unmatched_orders = df_right[~df_right[join_key].isin(df_left[join_key])].copy()

    path_left = os.path.join(output_dir, "unmatched_customers.csv")
    path_right = os.path.join(output_dir, "unmatched_orders.csv")

    unmatched_customers.to_csv(path_left, index=False)
    unmatched_orders.to_csv(path_right, index=False)

    print(f"\n--- Task 2: Unmatched Keys Detection ---")
    print(f"Customers without orders (Unmatched Left):  {len(unmatched_customers)}")
    print(f"Orphaned orders without customers (Right):   {len(unmatched_orders)}")
    print(f"✓ Saved unmatched customers log: {path_left}")
    print(f"✓ Saved orphaned orders log:     {path_right}")

    return unmatched_customers, unmatched_orders


def compare_join_types(df_left, df_right, join_key='customer_id'):
    """
    Compare record counts across all four fundamental join strategies.
    
    Args:
        df_left (pd.DataFrame): Left table.
        df_right (pd.DataFrame): Right table.
        join_key (str): Common join key.
        
    Returns:
        dict: Join type row counts dictionary.
    """
    inner = pd.merge(df_left, df_right, on=join_key, how='inner')
    left = pd.merge(df_left, df_right, on=join_key, how='left')
    right = pd.merge(df_left, df_right, on=join_key, how='right')
    outer = pd.merge(df_left, df_right, on=join_key, how='outer')

    results = {
        'inner': len(inner),
        'left': len(left),
        'right': len(right),
        'outer': len(outer)
    }

    print(f"\n--- Task 3: Compare Join Types ---")
    print(f"Inner: {results['inner']} | Left: {results['left']} | Right: {results['right']} | Outer: {results['outer']}")
    return results


def validate_column_duplication(df_merged, join_key='customer_id'):
    """
    Inspect merged column names for suffix collisions (_x, _y) and measure key cardinality distribution.
    
    Args:
        df_merged (pd.DataFrame): Merged result DataFrame.
        join_key (str): Primary join key column name.
    """
    print(f"\n--- Task 4: Validate No Unexpected Duplication ---")
    print("Merged DataFrame Columns:")
    print(list(df_merged.columns))

    # Check for column suffix collisions
    suffix_cols = [col for col in df_merged.columns if col.endswith('_x') or col.endswith('_y')]
    if suffix_cols:
        print(f"⚠ Warning: Column collisions detected: {suffix_cols}")
    else:
        print("✓ No unexpected column suffix conflicts detected.")

    # Calculate key counts
    key_counts = df_merged[join_key].value_counts()
    print(f"Max orders per customer: {key_counts.max()}")
    print(f"Customers with 1+ orders in result: {(key_counts > 0).sum()}")


def document_join_decision(df_left, df_right, df_merged, unmatched_left, unmatched_right, join_key='customer_id', how='left', report_path='output/join_report.json'):
    """
    Document all join metrics and business reasoning into a structured JSON report.
    
    Args:
        df_left (pd.DataFrame): Left table.
        df_right (pd.DataFrame): Right table.
        df_merged (pd.DataFrame): Merged DataFrame.
        unmatched_left (pd.DataFrame): Unmatched left records.
        unmatched_right (pd.DataFrame): Unmatched right records.
        join_key (str): Key column used.
        how (str): Join strategy applied.
        report_path (str): File path for saving JSON report.
        
    Returns:
        dict: The audit report dictionary.
    """
    join_report = {
        'join_type': how,
        'left_table': 'customers',
        'right_table': 'orders',
        'join_key': join_key,
        'left_rows': len(df_left),
        'right_rows': len(df_right),
        'result_rows': len(df_merged),
        'unmatched_left': len(unmatched_left),
        'unmatched_right': len(unmatched_right),
        'reasoning': 'Left join preserves all customer records regardless of order history. Unmatched customers represent registered users with zero orders.'
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(join_report, f, indent=2)

    print(f"\n--- Task 5: Document Join Decision ---")
    print(json.dumps(join_report, indent=2))
    print(f"\n✓ Saved join decision audit report to {report_path}")
    return join_report


if __name__ == "__main__":
    # Ensure stdout handles UTF-8 console output (checkmarks)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Resolve paths relative to repository root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    customers_path = os.path.join(base_dir, "data", "raw", "customers_merge.csv")
    orders_path = os.path.join(base_dir, "data", "raw", "orders_merge.csv")
    merged_output_path = os.path.join(base_dir, "data", "processed", "merged_customer_orders.csv")
    report_path = os.path.join(base_dir, "output", "join_report.json")
    output_dir = os.path.join(base_dir, "output")

    print("==============================================================")
    print("RUNNING RELATIONAL DATA MERGING & JOIN VALIDATION PIPELINE")
    print("==============================================================\n")

    # Step 1: Generate or load raw synthetic datasets
    df_customers, df_orders = generate_synthetic_datasets(customers_path, orders_path)

    # Step 2: Execute Task 1 - Explicit Left Join
    df_merged = execute_explicit_join(df_customers, df_orders, join_key='customer_id', how='left')

    # Step 3: Execute Task 2 - Detect Unmatched Keys
    unmatched_cust, unmatched_ord = detect_unmatched_keys(df_customers, df_orders, join_key='customer_id', output_dir=output_dir)

    # Step 4: Execute Task 3 - Compare Join Types
    compare_join_types(df_customers, df_orders, join_key='customer_id')

    # Step 5: Execute Task 4 - Validate No Unexpected Duplication
    validate_column_duplication(df_merged, join_key='customer_id')

    # Step 6: Execute Task 5 - Document Join Decision Report
    document_join_decision(df_customers, df_orders, df_merged, unmatched_cust, unmatched_ord, join_key='customer_id', how='left', report_path=report_path)

    # Step 7: Export Processed Merged Data
    os.makedirs(os.path.dirname(merged_output_path), exist_ok=True)
    df_merged.to_csv(merged_output_path, index=False)
    print(f"\n✓ Final merged dataset saved to {merged_output_path}")
    print("==============================================================")
