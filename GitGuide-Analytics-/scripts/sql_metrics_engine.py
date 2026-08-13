import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect, text


def generate_sql_metrics_database(database_path="analytics.db"):
    """
    Populates SQLite database 'analytics.db' with synthetic 'customers', 'transactions',
    and 'users' tables for SQL business metrics query execution.
    """
    engine = create_engine(f"sqlite:///{database_path}")
    np.random.seed(42)

    # 1. Customers Table (500 customers)
    num_customers = 500
    start_date = pd.Timestamp.now() - pd.Timedelta(days=365)
    df_customers = pd.DataFrame({
        'customer_id': range(1001, 1001 + num_customers),
        'customer_name': [f"Customer_{i}" for i in range(1001, 1001 + num_customers)],
        'customer_type': np.random.choice(['Enterprise', 'SMB', 'Startup'], size=num_customers, p=[0.15, 0.45, 0.40]),
        'signup_date': pd.date_range(start=start_date, periods=num_customers, freq='16h').strftime('%Y-%m-%d')
    })
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)

    # 2. Transactions Table (3,000 transactions over 12 months)
    num_tx = 3000
    dates = pd.date_range(start=start_date, end=pd.Timestamp.now(), periods=num_tx)
    cids = np.random.choice(df_customers['customer_id'].values, size=num_tx)
    amounts = np.round(np.random.exponential(scale=250, size=num_tx) + 20, 2)

    df_transactions = pd.DataFrame({
        'transaction_id': [f"TX_{i:06d}" for i in range(1, num_tx + 1)],
        'customer_id': cids,
        'transaction_date': dates.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': amounts,
        'status': np.random.choice(['SUCCESS', 'FAILED'], size=num_tx, p=[0.98, 0.02])
    })
    # Keep successful transactions
    df_transactions = df_transactions[df_transactions['status'] == 'SUCCESS']
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)

    # 3. Users Conversion Funnel Table (800 users over 90 days)
    num_users = 800
    user_created = pd.date_range(start=pd.Timestamp.now() - pd.Timedelta(days=85), periods=num_users, freq='2h')
    
    email_verified = []
    first_purchase = []
    for dt in user_created:
        is_verified = np.random.rand() < 0.75
        is_purchased = is_verified and (np.random.rand() < 0.60)
        
        email_verified.append((dt + pd.Timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S') if is_verified else None)
        first_purchase.append((dt + pd.Timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S') if is_purchased else None)

    df_users = pd.DataFrame({
        'user_id': range(5001, 5001 + num_users),
        'created_at': user_created.strftime('%Y-%m-%d %H:%M:%S'),
        'email_verified_at': email_verified,
        'first_purchase_at': first_purchase
    })
    df_users.to_sql('users', engine, if_exists='replace', index=False)

    print(f"[SUCCESS] Database '{database_path}' populated with tables: 'customers', 'transactions', 'users'.")
    return engine


def load_query(query_name, queries_dir="queries"):
    """
    Task 4 Helper: Loads raw SQL query from a .sql file in the queries directory.

    Parameters:
    -----------
    query_name : str
        Base filename of the query without .sql extension.
    queries_dir : str, default 'queries'
        Directory containing .sql files.

    Returns:
    --------
    str
        Raw SQL query string ready for execution.
    """
    filepath = os.path.join(queries_dir, f"{query_name}.sql")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"SQL query file not found at: {filepath}")

    with open(filepath, "r") as f:
        query_sql = f.read()

    return query_sql


def task4_execute_shared_queries(engine):
    """
    Task 4: Load and execute shared SQL metric queries from Python.
    """
    print("\n--- Task 4: Load & Execute Shared SQL Queries from Python ---")

    # 1. Monthly Active Users Query
    mau_sql = load_query('monthly_active_users')
    mau_df = pd.read_sql(mau_sql, engine)
    print("1. Monthly Active Users (MAU) Metric:")
    print(mau_df.head(5))

    # 2. Revenue by Segment Query
    revenue_sql = load_query('revenue_by_segment')
    revenue_df = pd.read_sql(revenue_sql, engine)
    print("\n2. Revenue by Segment Metric:")
    print(revenue_df.head(6))

    # 3. Conversion Funnel Query
    funnel_sql = load_query('conversion_funnel')
    funnel_df = pd.read_sql(funnel_sql, engine)
    print("\n3. Conversion Funnel Metric:")
    print(funnel_df.head(5))

    # Export to output/ directory
    os.makedirs("output", exist_ok=True)
    mau_df.to_csv("output/mau_metrics.csv", index=False)
    revenue_df.to_csv("output/revenue_segment_metrics.csv", index=False)
    funnel_df.to_csv("output/conversion_funnel_metrics.csv", index=False)

    return mau_df, revenue_df, funnel_df


def task5_validate_metrics(mau_df, revenue_df, funnel_df):
    """
    Task 5: Validate Metric Computation Integrity across all DataFrames.
    """
    print("\n--- Task 5: Metric Assertion Validation ---")

    # 1. Check for null values
    assert mau_df.isnull().sum().sum() == 0, "[ERROR] MAU DataFrame contains null values!"
    assert revenue_df.isnull().sum().sum() == 0, "[ERROR] Revenue DataFrame contains null values!"
    assert funnel_df.isnull().sum().sum() == 0, "[ERROR] Funnel DataFrame contains null values!"
    print("  [PASS] Null Value Assertion: 0 nulls detected across all metric DataFrames.")

    # 2. Check value ranges
    assert (revenue_df['monthly_revenue'] > 0).all(), "[ERROR] Monthly revenue <= 0 detected!"
    assert (funnel_df['conversion_pct'] >= 0).all() and (funnel_df['conversion_pct'] <= 100).all(), "[ERROR] Conversion % out of valid range [0, 100]!"
    print("  [PASS] Value Range Assertion: Revenue > $0 and Conversion % in [0%, 100%].")

    # 3. Check logical consistency
    for idx, row in revenue_df.iterrows():
        assert row['order_count'] > 0, f"[ERROR] Zero orders in row {idx}!"
        assert row['monthly_revenue'] > 0, f"[ERROR] Zero revenue in row {idx}!"
    print("  [PASS] Logical Consistency Assertion: Order count and revenue > 0 per segment.")

    print("\n  [OK] All metric assertions validated successfully!")
    return True


def main():
    print("=" * 60)
    print("  SQL Business Metrics Query Design Engine")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("queries", exist_ok=True)

    engine = generate_sql_metrics_database("analytics.db")
    mau_df, revenue_df, funnel_df = task4_execute_shared_queries(engine)
    task5_validate_metrics(mau_df, revenue_df, funnel_df)

    print("\n[SUCCESS] SQL Business Metrics Query Design Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
