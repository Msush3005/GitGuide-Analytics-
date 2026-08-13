"""
Assignment 2.43: SQL Views & Aggregation Layer Design
Submission Python Script
"""
import os
import time
import pandas as pd
from sqlalchemy import create_engine, text

# Connect to analytics database
db_path = 'analytics.db'
engine = create_engine(f"sqlite:///{db_path}")

print("==========================================================")
print("  Task 1: Create SQL Views (vw_active_customers & vw_product_performance)")
print("==========================================================")

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
custom_metric = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 10", engine)

print("View 1 (vw_active_customers) columns:", active_customers.columns.tolist())
print("View 2 (vw_product_performance) columns:", custom_metric.columns.tolist())

print("\n==========================================================")
print("  Task 2: Create & Populate Pre-Aggregated Summary Table (agg_daily_metrics)")
print("==========================================================")

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
print(f"Aggregated {len(agg_data)} rows:")
print(agg_data.head(5))

start = time.time()
result = pd.read_sql("SELECT metric_name, SUM(metric_value) FROM agg_daily_metrics GROUP BY metric_name", engine)
elapsed = time.time() - start
print(f"Query time on pre-aggregated table: {elapsed*1000:.2f}ms")

print("\n==========================================================")
print("  Task 3: Query Clean Data Layer from Python (Dashboard Simulation)")
print("==========================================================")

active_cust_df = pd.read_sql("""
SELECT customer_id, customer_name, revenue_30d, days_since_order 
FROM vw_active_customers 
WHERE days_since_order <= 30 
ORDER BY revenue_30d DESC 
LIMIT 20
""", engine)
print("Top 20 Active Customers (last 30 days):")
print(active_cust_df.head(5))

custom_result = pd.read_sql("SELECT * FROM vw_product_performance LIMIT 20", engine)
print("\nCustom Metric Results (vw_product_performance):")
print(custom_result.head(5))

agg_result = pd.read_sql("""
SELECT aggregation_date, metric_name, metric_value 
FROM agg_daily_metrics 
WHERE aggregation_date >= DATE('now', '-30 days') 
ORDER BY aggregation_date DESC
""", engine)
print("\nDaily Aggregated Metrics (last 30 days):")
print(agg_result.head(5))

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
print("\nRevenue by Segment:")
print(active_by_segment)

print("\n[SUCCESS] Assignment 2.43 Data Layer Execution Completed Successfully!")
