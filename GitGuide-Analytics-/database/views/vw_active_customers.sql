-- View: vw_active_customers
-- Purpose: Encapsulates single source of truth for rolling 30-day active customer metrics
-- Business Metric: Active customers with transactions in the past 30 days
-- Updated: Automatically recalculated on query execution
-- Used By: Executive dashboard, customer success retention reports, churn risk analysis
--
-- Columns:
-- customer_id: Unique customer primary key
-- customer_name: Customer display name
-- segment: Customer segment tier (Enterprise, Mid-Market, SMB, Starter)
-- order_count_30d: Count of distinct orders placed in last 30 days
-- revenue_30d: Total gross order revenue in last 30 days
-- last_order_date: Most recent transaction timestamp
-- days_since_order: Days elapsed between current date and last order date

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
