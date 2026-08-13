-- queries/val_metric2_aov.sql
-- Metric 2: Average Order Value (AOV)
-- Purpose: Calculates mean order amount across all completed transaction orders
SELECT ROUND(AVG(order_amount), 2) as aov 
FROM orders;
