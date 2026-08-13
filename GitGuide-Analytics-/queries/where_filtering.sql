-- queries/where_filtering.sql
-- Filter data quality issues BEFORE grouping:
-- 1. transaction_date >= DATE('now', '-1 year'): Date range filter to exclude legacy historical records
-- 2. amount > 0: Logical validity filter to exclude refunds and zero-dollar system tests
-- 3. transaction_status = 'completed': Quality filter to exclude failed/cancelled transactions
SELECT 
    t.customer_id,
    ROUND(SUM(t.amount), 2) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions t
WHERE t.transaction_date >= DATE('now', '-1 year')
  AND t.amount > 0
  AND t.status = 'completed'
GROUP BY t.customer_id
ORDER BY annual_revenue DESC;
