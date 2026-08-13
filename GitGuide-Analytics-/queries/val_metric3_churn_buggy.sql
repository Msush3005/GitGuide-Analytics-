-- queries/val_metric3_churn_buggy.sql
-- Metric 3: Unoptimized Buggy Churn Query (Stripping Year Context)
-- Bug Description: STRFTIME('%m') extracts month number (1-12) but strips year context.
-- Across year boundaries (e.g. Dec 2024 vs Jan 2025), month number matching compares Jan 2024 instead of Jan 2025!
SELECT COUNT(DISTINCT c1.customer_id) as churned_customers 
FROM ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE STRFTIME('%m', order_date) = STRFTIME('%m', DATE('now', '-1 month'))
      AND order_amount > 0 
) c1 
LEFT JOIN ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE STRFTIME('%m', order_date) = STRFTIME('%m', DATE('now'))
) c2 ON c1.customer_id = c2.customer_id 
WHERE c2.customer_id IS NULL;
