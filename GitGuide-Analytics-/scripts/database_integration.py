import os
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, inspect, text


def generate_sample_cleaned_data(num_records=1000):
    """
    Generates synthetic cleaned customer dataset for database loading.
    """
    np.random.seed(42)
    df_clean = pd.DataFrame({
        'customer_id': range(1001, 1001 + num_records),
        'customer_name': [f"Customer_{i}" for i in range(1001, 1001 + num_records)],
        'customer_type': np.random.choice(['Enterprise', 'SMB', 'Startup'], size=num_records, p=[0.15, 0.45, 0.40]),
        'email': [f"user_{i}@company.com" for i in range(1001, 1001 + num_records)],
        'signup_date': pd.date_range(start='2024-01-01', periods=num_records, freq='8h').strftime('%Y-%m-%d'),
        'lifetime_value': np.round(np.random.exponential(scale=15000, size=num_records) + 1000, 2),
        'churn': np.random.choice([0, 1], size=num_records, p=[0.92, 0.08])
    })
    return df_clean


def task1_setup_database_connection(database_path="analytics.db"):
    """
    Task 1: Setup Database Connection using SQLAlchemy.
    Documents connection strings for SQLite and PostgreSQL.
    """
    print("\n--- Task 1: Setup Database Connection ---")
    connection_string = f"sqlite:///{database_path}"
    engine = create_engine(connection_string)

    # Document PostgreSQL connection string (without hardcoded credentials)
    pg_example = "postgresql://<username>:<password>@<host>:5432/<database_name>"
    print(f"  - SQLite Connection String : {connection_string}")
    print(f"  - PostgreSQL String Format : {pg_example}")

    # Test Connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("  [SUCCESS] Database connection verified successfully!")

    return engine


def task2_load_cleaned_dataframe(df_clean, engine, table_name="customers_cleaned"):
    """
    Task 2: Load Cleaned DataFrame as Table.
    """
    print(f"\n--- Task 2: Load Cleaned DataFrame to Table '{table_name}' ---")
    df_clean.to_sql(table_name, engine, if_exists='replace', index=False)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"  - Existing Database Tables : {tables}")

    count_df = pd.read_sql(f"SELECT COUNT(*) as row_count FROM {table_name}", engine)
    row_count = count_df.iloc[0]['row_count']
    print(f"  - Rows Loaded to '{table_name}' : {row_count:,} rows")

    return row_count


def task3_validate_schema(engine, table_name="customers_cleaned"):
    """
    Task 3: Validate Table Schema & Data Types.
    """
    print(f"\n--- Task 3: Validate Table Schema for '{table_name}' ---")
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)

    print("TABLE SCHEMA INSPECTION:")
    schema_report = []
    for col in columns:
        col_name = col['name']
        col_type = str(col['type'])
        nullable = "NOT NULL" if not col.get('nullable', True) else "NULLABLE"
        schema_report.append(f"  - {col_name:20} : {col_type:15} ({nullable})")
        print(schema_report[-1])

    expected_types = {
        'customer_id': 'INTEGER',
        'email': 'VARCHAR',
        'signup_date': 'DATE',
        'lifetime_value': 'FLOAT',
        'customer_type': 'VARCHAR'
    }

    print("\nDATATYPE VALIDATION REPORT:")
    for col_name, expected_type in expected_types.items():
        actual_type = [c['type'] for c in columns if c['name'] == col_name][0]
        actual_str = str(actual_type).upper()

        # Flexible check across SQL dialects (INTEGER/BIGINT/VARCHAR/TEXT/FLOAT/REAL)
        is_valid = (
            expected_type in actual_str or 
            ('INTEGER' in expected_type and ('BIGINT' in actual_str or 'INT' in actual_str or 'INTEGER' in actual_str)) or
            ('VARCHAR' in expected_type and ('TEXT' in actual_str or 'VARCHAR' in actual_str)) or
            ('DATE' in expected_type and ('TEXT' in actual_str or 'DATE' in actual_str)) or
            ('FLOAT' in expected_type and ('REAL' in actual_str or 'FLOAT' in actual_str or 'DECIMAL' in actual_str))
        )
        status = "[PASS]" if is_valid else "[FAIL]"
        print(f"  {status} {col_name:18} : Actual={actual_str:<12} | Expected={expected_type}")

    os.makedirs("output", exist_ok=True)
    with open("output/sql_schema_validation.txt", "w") as f:
        f.write("\n".join(schema_report))

    return columns


def task4_query_and_return_results(engine, table_name="customers_cleaned"):
    """
    Task 4: Analytical SQL Query Execution and Pandas Integration.
    """
    print(f"\n--- Task 4: Query Database Table and Return DataFrames ---")

    # 1. Simple Filtered SELECT Query
    query_enterprise = f"SELECT * FROM {table_name} WHERE customer_type = 'Enterprise'"
    results_enterprise = pd.read_sql(query_enterprise, engine)
    print(f"  - Simple Query (Enterprise Customers): Retrieved {len(results_enterprise)} rows")
    print(results_enterprise.head(3))

    # 2. Complex Aggregation Query
    query_agg = f"""
    SELECT 
        customer_type, 
        COUNT(*) as customer_count, 
        ROUND(AVG(lifetime_value), 2) as avg_ltv,
        ROUND(AVG(churn) * 100, 2) as churn_rate_pct
    FROM {table_name} 
    GROUP BY customer_type 
    ORDER BY avg_ltv DESC
    """
    summary = pd.read_sql(query_agg, engine)
    print("\n  - Aggregation Query (Segment Overview):")
    print(summary)

    os.makedirs("output", exist_ok=True)
    summary.to_csv("output/sql_query_summary.csv", index=False)
    print("Saved aggregation query results to output/sql_query_summary.csv")

    return summary


def load_cleaned_data_to_database(df, table_name, database_path='analytics.db'):
    """
    Task 5: Repeatable Pipeline Function to Load Cleaned Data to SQL Database.

    Parameters:
    -----------
    df : pandas.DataFrame
        Cleaned Pandas DataFrame to write to SQL.
    table_name : str
        Name of target table in SQL database.
    database_path : str, default 'analytics.db'
        Filepath to target SQLite database file.

    Returns:
    --------
    sqlalchemy.engine.Engine
        Active SQLAlchemy database engine instance for downstream querying.
    """
    engine = create_engine(f"sqlite:///{database_path}")
    df.to_sql(table_name, engine, if_exists='replace', index=False)

    # Validate Row Count
    count_df = pd.read_sql(f"SELECT COUNT(*) as ct FROM {table_name}", engine)
    rows_loaded = count_df.iloc[0]['ct']
    print(f"  [OK] [REPEATABLE FUNCTION] Successfully loaded {rows_loaded:,} rows to '{table_name}' in '{database_path}'")

    return engine


def main():
    print("=" * 60)
    print("  SQL Environment & Database Integration Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df_clean = generate_sample_cleaned_data(num_records=1000)

    # Task 1: Setup Connection
    engine = task1_setup_database_connection("analytics.db")

    # Task 2: Load DataFrame
    task2_load_cleaned_dataframe(df_clean, engine, "customers_cleaned")

    # Task 3: Schema Validation
    task3_validate_schema(engine, "customers_cleaned")

    # Task 4: Analytical Query Execution
    task4_query_and_return_results(engine, "customers_cleaned")

    # Task 5: Repeatable Pipeline Function Test
    print("\n--- Task 5: Testing Repeatable Loading Pipeline Function ---")
    engine_repeatable = load_cleaned_data_to_database(df_clean, "customers_cleaned", "analytics.db")

    # Verify query using returned engine
    quick_test = pd.read_sql("SELECT customer_type, COUNT(*) as ct FROM customers_cleaned GROUP BY customer_type", engine_repeatable)
    print(quick_test)

    print("\n[SUCCESS] SQL Environment & Database Integration Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
