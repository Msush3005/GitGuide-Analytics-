import os
import time
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text


def ensure_relational_tables(database_path="analytics.db"):
    """
    Ensures relational tables exist in analytics.db for data layer views.
    """
    engine = create_engine(f"sqlite:///{database_path}")
    np.random.seed(42)

    # 1. Customers
    num_customers = 1000
    df_customers = pd.DataFrame({
        'customer_id': range(1001, 1001 + num_customers),
        'customer_name': [f"Customer_{i}" for i in range(1001, 1001 + num_customers)],
        'customer_type': np.random.choice(['Enterprise', 'Mid-Market', 'SMB', 'Starter'], size=num_customers, p=[0.15, 0.25, 0.40, 0.20]),
        'signup_date': pd.date_range(start='2024-01-01', periods=num_customers, freq='8h').strftime('%Y-%m-%d')
    })
    df_customers.to_sql('customers', engine, if_exists='replace', index=False)

    # 2. Orders
    num_orders = 5000
    start_date = pd.Timestamp.now() - pd.Timedelta(days=90)
    order_dates = pd.date_range(start=start_date, end=pd.Timestamp.now(), periods=num_orders)
    cids = np.random.choice(df_customers['customer_id'].values, size=num_orders)
    amounts = np.round(np.random.exponential(scale=180, size=num_orders) + 15, 2)

    df_orders = pd.DataFrame({
        'order_id': range(50001, 50001 + num_orders),
        'customer_id': cids,
        'order_date': order_dates.strftime('%Y-%m-%d %H:%M:%S'),
        'order_amount': amounts
    })
    df_orders.to_sql('orders', engine, if_exists='replace', index=False)

    # 3. Products
    num_products = 500
    df_products = pd.DataFrame({
        'product_id': range(201, 201 + num_products),
        'product_name': [f"Product_{pid}" for pid in range(201, 201 + num_products)],
        'category': np.random.choice(['Software', 'Cloud Storage', 'Analytics', 'Security'], size=num_products)
    })
    df_products.to_sql('products', engine, if_exists='replace', index=False)

    # 4. Order Items
    num_items = 8000
    df_order_items = pd.DataFrame({
        'item_id': range(90001, 90001 + num_items),
        'order_id': np.random.choice(df_orders['order_id'].values, size=num_items),
        'product_id': np.random.choice(df_products['product_id'].values, size=num_items),
        'quantity': np.random.randint(1, 5, size=num_items),
        'unit_price': np.round(np.random.uniform(25.0, 450.0, size=num_items), 2)
    })
    df_order_items.to_sql('order_items', engine, if_exists='replace', index=False)

    print(f"[SUCCESS] Database '{database_path}' populated with relational base tables.")
    return engine


def task1_create_views(engine):
    """
    Task 1: Create SQL Views (vw_active_customers & vw_product_performance).
    """
    print("\n--- Task 1: Create SQL Views ---")

    view1_sql = """
    CREATE VIEW IF NOT EXISTS vw_active_customers AS 
    SELECT 
        c.customer_id, 
        c.customer_name, 
        c.customer_type as segment, 
        COUNT(DISTINCT o.order_id) as order_count_30d, 
        ROUND(COALESCE(SUM(o.order_amount), 0), 2) as revenue_30d, 
        MAX(o.order_date) as last_order_date, 
        CAST(JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) AS INTEGER) as days_since_order 
    FROM customers c 
    LEFT JOIN orders o ON c.customer_id = o.customer_id 
      AND o.order_date >= DATE('now', '-30 days') 
    GROUP BY c.customer_id, c.customer_name, c.customer_type;
    """

    view2_sql = """
    CREATE VIEW IF NOT EXISTS vw_product_performance AS 
    SELECT 
        p.product_id,
        p.product_name,
        p.category,
        COUNT(DISTINCT oi.order_id) as total_orders,
        COALESCE(SUM(oi.quantity), 0) as total_units_sold,
        ROUND(COALESCE(SUM(oi.quantity * oi.unit_price), 0), 2) as total_product_revenue,
        ROUND(COALESCE(AVG(oi.unit_price), 0), 2) as avg_unit_price,
        COUNT(DISTINCT o.customer_id) as unique_buyers
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o ON oi.order_id = o.order_id
    GROUP BY p.product_id, p.product_name, p.category;
    """

    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS vw_active_customers"))
        conn.execute(text(view1_sql))
        conn.execute(text("DROP VIEW IF EXISTS vw_product_performance"))
        conn.execute(text(view2_sql))

    active_customers = pd.read_sql("SELECT * FROM vw_active_customers LIMIT 10", engine)
    product_perf = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 10", engine)

    print("  - View 1 (vw_active_customers) Columns:", active_customers.columns.tolist())
    print("  - View 2 (vw_product_performance) Columns:", product_perf.columns.tolist())

    os.makedirs("output", exist_ok=True)
    active_customers.to_csv("output/vw_active_customers_summary.csv", index=False)
    product_perf.to_csv("output/vw_product_performance_summary.csv", index=False)

    return active_customers, product_perf


def task2_create_preaggregated_table(engine):
    """
    Task 2: Create and Populate Pre-Aggregated Summary Table (agg_daily_metrics).
    """
    print("\n--- Task 2: Create Pre-Aggregated Summary Table ---")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS agg_daily_metrics (
        aggregation_date DATE,
        metric_name VARCHAR(100),
        metric_value NUMERIC(12,2),
        row_count INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (aggregation_date, metric_name)
    );
    """

    populate_sql = """
    INSERT OR REPLACE INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
    SELECT 
        DATE(o.order_date) as aggregation_date, 
        'total_revenue' as metric_name, 
        ROUND(SUM(o.order_amount), 2) as metric_value, 
        COUNT(*) as row_count, 
        CURRENT_TIMESTAMP as updated_at 
    FROM orders o 
    GROUP BY DATE(o.order_date);
    """

    with engine.begin() as conn:
        conn.execute(text(create_table_sql))
        conn.execute(text(populate_sql))

    agg_data = pd.read_sql("SELECT * FROM agg_daily_metrics ORDER BY aggregation_date DESC LIMIT 10", engine)
    print(f"  - Aggregated {len(agg_data)} daily metric summary rows.")
    print(agg_data.head(3))

    t0 = time.time()
    result = pd.read_sql("SELECT metric_name, SUM(metric_value) as total FROM agg_daily_metrics GROUP BY metric_name", engine)
    elapsed_ms = (time.time() - t0) * 1000
    print(f"  - Pre-Aggregated Table Query Time: {elapsed_ms:.2f} ms (Instant dashboard load)")

    os.makedirs("output", exist_ok=True)
    agg_data.to_csv("output/agg_daily_metrics_summary.csv", index=False)
    return agg_data


def task3_query_clean_data_layer(engine):
    """
    Task 3: Query Views & Aggregated Tables from Python (Simulating Streamlit Dashboard).
    """
    print("\n--- Task 3: Query Clean Data Layer from Python ---")

    # 1. Top 20 Active Customers
    active_cust_df = pd.read_sql("""
    SELECT customer_id, customer_name, revenue_30d, days_since_order 
    FROM vw_active_customers 
    WHERE days_since_order <= 30 
    ORDER BY revenue_30d DESC 
    LIMIT 20
    """, engine)
    print("1. Top Active Customers (last 30 days):")
    print(active_cust_df.head(3))

    # 2. Product Performance View
    custom_result = pd.read_sql("SELECT * FROM vw_product_performance ORDER BY total_product_revenue DESC LIMIT 20", engine)
    print("\n2. Top Products by Revenue:")
    print(custom_result.head(3))

    # 3. Pre-Aggregated Daily Metrics Table
    agg_result = pd.read_sql("""
    SELECT aggregation_date, metric_name, metric_value 
    FROM agg_daily_metrics 
    WHERE aggregation_date >= DATE('now', '-30 days') 
    ORDER BY aggregation_date DESC
    """, engine)
    print("\n3. Daily Aggregated Metrics (last 30 days):")
    print(agg_result.head(3))

    # 4. Revenue by Segment from View
    active_by_segment = pd.read_sql("""
    SELECT 
        segment, 
        COUNT(*) as customer_count, 
        ROUND(SUM(revenue_30d), 2) as total_segment_revenue, 
        ROUND(AVG(revenue_30d), 2) as avg_customer_revenue 
    FROM vw_active_customers 
    GROUP BY segment 
    ORDER BY total_segment_revenue DESC
    """, engine)
    print("\n4. Revenue by Segment (from vw_active_customers):")
    print(active_by_segment)

    return active_cust_df, custom_result, agg_result, active_by_segment


def main():
    print("=" * 60)
    print("  SQL Views & Aggregation Layer Design Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("database/views", exist_ok=True)
    os.makedirs("database/aggregations", exist_ok=True)

    engine = ensure_relational_tables("analytics.db")

    task1_create_views(engine)
    task2_create_preaggregated_table(engine)
    task3_query_clean_data_layer(engine)

    print("\n[SUCCESS] SQL Views & Aggregation Layer Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
