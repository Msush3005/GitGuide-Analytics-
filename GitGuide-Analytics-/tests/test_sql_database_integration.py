import pandas as pd

from src.sql_database_integration import (
    create_sqlite_engine,
    load_cleaned_data_to_database,
    query_database,
    validate_table_schema,
)


def test_database_workflow(tmp_path):
    df = pd.DataFrame(
        [
            {
                "customer_id": 1,
                "email": "alice@example.com",
                "signup_date": "2025-01-15",
                "customer_type": "Enterprise",
                "lifetime_value": 1500.50,
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

    database_path = tmp_path / "analytics.db"
    engine = create_sqlite_engine(database_path)

    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")

    engine = load_cleaned_data_to_database(df, "customers_cleaned", database_path)

    row_count = pd.read_sql("SELECT COUNT(*) AS row_count FROM customers_cleaned", engine)
    assert row_count.iloc[0]["row_count"] == 2

    schema = validate_table_schema(engine, "customers_cleaned")
    assert any(col["name"] == "customer_id" for col in schema)
    assert any(col["name"] == "email" for col in schema)
    assert any(col["name"] == "signup_date" for col in schema)

    enterprise_rows = query_database(
        engine,
        "SELECT * FROM customers_cleaned WHERE customer_type = 'Enterprise'",
    )
    assert len(enterprise_rows) == 1
    assert enterprise_rows.iloc[0]["email"] == "alice@example.com"

    summary = query_database(
        engine,
        """
        SELECT customer_type, COUNT(*) AS count, AVG(lifetime_value) AS avg_ltv
        FROM customers_cleaned
        GROUP BY customer_type
        ORDER BY avg_ltv DESC
        """,
    )
    assert set(summary["customer_type"]) == {"Enterprise", "Consumer"}
    assert summary["count"].sum() == 2
