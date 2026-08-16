"""SQLite database integration utilities for the analytics workflow.

This module demonstrates the core assignment workflow:
- create a SQLAlchemy engine
- load a cleaned DataFrame as a SQL table
- validate schema and row counts
- execute queries and return results as pandas DataFrames
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
from sqlalchemy import create_engine, inspect


def create_sqlite_engine(database_path: Union[str, Path] = "analytics.db") -> Any:
    """Create and return a SQLite SQLAlchemy engine.

    Parameters:
        database_path (str | Path): File path for the SQLite database.

    Returns:
        sqlalchemy.Engine: Database engine ready for queries and writes.
    """
    db_path = str(Path(database_path)).replace("\\", "/")
    if db_path.startswith("sqlite://"):
        engine = create_engine(db_path)
    else:
        if Path(db_path).is_absolute():
            db_url = f"sqlite:///{db_path.lstrip('/')}"
        else:
            db_url = f"sqlite:///{Path(db_path).resolve().as_posix().lstrip('/')}"
        engine = create_engine(db_url)
    return engine


def load_cleaned_data_to_database(
    df: pd.DataFrame,
    table_name: str,
    database_path: Union[str, Path] = "analytics.db",
    if_exists: str = "replace",
) -> Any:
    """Load a cleaned DataFrame to a SQL table and validate the insert.

    Parameters:
        df (pd.DataFrame): Cleaned data to persist to the database.
        table_name (str): Name of the SQL table to create or replace.
        database_path (str | Path): SQLite database file location.
        if_exists (str): SQLAlchemy pandas option for existing table handling.

    Returns:
        sqlalchemy.Engine: Engine with the table loaded and validated.
    """
    if df is None or df.empty:
        raise ValueError("DataFrame is empty; cannot load to database.")

    engine = create_sqlite_engine(database_path)
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)

    row_count = pd.read_sql(f"SELECT COUNT(*) AS ct FROM {table_name}", engine)
    rows_loaded = int(row_count.iloc[0]["ct"])
    if rows_loaded != len(df):
        raise ValueError(
            f"Row validation failed for table '{table_name}': expected {len(df)}, loaded {rows_loaded}"
        )

    print(f"✓ Loaded {rows_loaded} rows to {table_name}")
    return engine


def validate_table_schema(engine: Any, table_name: str) -> List[Dict[str, Any]]:
    """Inspect and return the schema for a database table.

    Parameters:
        engine (sqlalchemy.Engine): Active SQLAlchemy engine.
        table_name (str): Database table name.

    Returns:
        list[dict]: List of column metadata dictionaries including name, type, nullable.
    """
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  {col['name']:20} {str(col['type']):15} {'NOT NULL' if col['nullable'] is False else ''}")
    return columns


def query_database(engine: Any, query: str) -> pd.DataFrame:
    """Execute a SELECT query and return the result as a DataFrame."""
    result = pd.read_sql(query, engine)
    return result


if __name__ == "__main__":
    import os

    base_dir = Path(__file__).resolve().parents[1]
    database_path = base_dir / "analytics.db"

    sample_df = pd.DataFrame(
        [
            {
                "customer_id": 1,
                "email": "alice@example.com",
                "signup_date": "2025-01-15",
                "customer_type": "Enterprise",
                "lifetime_value": 1500.5,
            },
            {
                "customer_id": 2,
                "email": "bob@example.com",
                "signup_date": "2025-02-20",
                "customer_type": "Consumer",
                "lifetime_value": 900.25,
            },
        ]
    )

    engine = load_cleaned_data_to_database(sample_df, "customers_cleaned", database_path)
    print(engine)
    schema = validate_table_schema(engine, "customers_cleaned")
    print("TABLE SCHEMA:")
    for col in schema:
        print(col)

    results = query_database(engine, "SELECT * FROM customers_cleaned WHERE customer_type = 'Enterprise'")
    print(results.head())

    summary = query_database(
        engine,
        """
        SELECT customer_type, COUNT(*) AS count, AVG(lifetime_value) AS avg_ltv
        FROM customers_cleaned
        GROUP BY customer_type
        ORDER BY avg_ltv DESC
        """,
    )
    print(summary)
