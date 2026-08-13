import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect, text


def ensure_filtering_database(database_path="analytics.db"):
    """
    Ensures 'customers' (with 'industry') and 'transactions' (with 'status') tables exist in analytics.db.
    """
    engine = create_engine(f"sqlite:///{database_path}")
    np.random.seed(42)

    # 1. Customers Table with industry
    num_customers = 500
    industries = ['Fintech', 'Healthcare', 'E-commerce', 'SaaS', 'EdTech']
    start_date = pd.Timestamp.now() - pd.Timedelta(days=365)

    df_customers = pd.DataFrame({
        'customer_id': range(1001, 1001 + num_customers),
        'customer_name': [f"Customer_{i}" for i in range(1001, 1001 + num_customers)],
        'customer_type': np.random.choice(['Enterprise', 'SMB', 'Startup'], size=num_customers, p=[0.15, 0.45, 0.40]),
        'industry': np.random.choice(industries, size=num_customers, p=[0.25, 0.20, 0.25, 0.20, 0.10]),
        'signup_date': pd.date_range(start=start_date, periods=num_customers, freq='16h').strftime('%Y-%m-%d')
    })
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)

    # 2. Transactions Table with status
    num_tx = 3500
    dates = pd.date_range(start=start_date, end=pd.Timestamp.now(), periods=num_tx)
    cids = np.random.choice(df_customers['customer_id'].values, size=num_tx)
    amounts = np.round(np.random.exponential(scale=300, size=num_tx) + 15, 2)
    statuses = np.random.choice(['completed', 'failed', 'pending'], size=num_tx, p=[0.90, 0.07, 0.03])

    df_transactions = pd.DataFrame({
        'transaction_id': [f"TX_{i:06d}" for i in range(1, num_tx + 1)],
        'customer_id': cids,
        'transaction_date': dates.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': amounts,
        'status': statuses
    })
    df_transactions.to_sql('transactions', engine, if_exists='replace', index=False)

    print(f"[SUCCESS] Prepared database '{database_path}' with updated 'customers' & 'transactions' tables.")
    return engine


def load_query(query_name, queries_dir="queries"):
    """
    Loads raw SQL query string from .sql file in queries directory.
    """
    filepath = os.path.join(queries_dir, f"{query_name}.sql")
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"SQL file not found: {filepath}")
    with open(filepath, "r") as f:
        return f.read()


def execute_and_export(query_name, engine, output_dir="output"):
    """
    Loads, executes, displays, and exports SQL query.
    """
    query_sql = load_query(query_name)
    df_result = pd.read_sql(query_sql, engine)

    print(f"\n--- Execution Output: '{query_name}.sql' ---")
    print(f"Retrieved {len(df_result)} rows:")
    print(df_result.head(5))

    os.makedirs(output_dir, exist_ok=True)
    out_csv = os.path.join(output_dir, f"{query_name}.csv")
    df_result.to_csv(out_csv, index=False)
    print(f"Saved report to: {out_csv}")

    assert not df_result.empty, f"[ERROR] Query '{query_name}.sql' returned an empty DataFrame!"
    return df_result


def main():
    print("=" * 60)
    print("  SQL Filtering, Grouping & Aggregation Engine")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("queries", exist_ok=True)

    engine = ensure_filtering_database("analytics.db")

    # Task 1: WHERE Filtering
    task1_df = execute_and_export('where_filtering', engine)

    # Task 2: GROUP BY & Aggregation
    task2_df = execute_and_export('group_by_aggregation', engine)

    # Task 3: HAVING Filtering
    task3_df = execute_and_export('having_filtering', engine)

    # Task 4: WHERE + HAVING Combined
    task4_df = execute_and_export('where_having_combined', engine)

    # Task 5: ORDER BY & Ranking
    task5_df = execute_and_export('order_by_ranking', engine)

    # Bonus: Percentage Share Computation
    task6_df = execute_and_export('percentage_share', engine)

    print("\n[SUCCESS] SQL Filtering, Grouping & Aggregation Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
