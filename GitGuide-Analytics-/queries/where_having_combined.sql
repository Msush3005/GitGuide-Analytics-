-- queries/where_having_combined.sql
-- Real-world query combining WHERE (data quality / date window) AND HAVING (segment metric thresholds):
-- WHERE Filters: Valid transactions (status='completed', amount > 0, past 1 year).
-- HAVING Filters: High-volume, high-value customer segments (COUNT >= 10 customers, SUM > $30,000).
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    ROUND(SUM(t.amount), 2) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-1 year') -- WHERE: valid date window
  AND t.status = 'completed'                       -- WHERE: quality check
  AND t.amount > 0                                 -- WHERE: positive transaction amount
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 10        -- HAVING: minimum segment sample size
   AND SUM(t.amount) > 30000                       -- HAVING: business revenue threshold
ORDER BY segment_revenue DESC;
