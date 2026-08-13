-- queries/val_metric3_churn_fixed.sql
-- Metric 3: Refactored Fixed Churn Query (Explicit Date Range Boundaries)
-- Fix Description: Uses explicit YYYY-MM-DD month boundaries ensuring year + month context alignment.
SELECT COUNT(DISTINCT c1.customer_id) as churned_customers 
FROM ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= DATE('now', 'start of month', '-1 month')
      AND order_date < DATE('now', 'start of month')
      AND order_amount > 0 
) c1 
LEFT JOIN ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= DATE('now', 'start of month')
      AND order_date < DATE('now', 'start of month', '+1 month')
) c2 ON c1.customer_id = c2.customer_id 
WHERE c2.customer_id IS NULL;
