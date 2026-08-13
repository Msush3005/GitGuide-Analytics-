-- queries/group_by_aggregation.sql
-- Group by 2+ dimensions (customer_type, month) using 4 aggregate functions:
-- WHERE filters invalid rows before grouping occurs.
SELECT 
    c.customer_type,
    STRFTIME('%Y-%m-01', t.transaction_date) as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(*) as transaction_count,
    ROUND(SUM(t.amount), 2) as monthly_revenue,
    ROUND(AVG(t.amount), 2) as avg_transaction
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-1 year')
  AND t.amount > 0
  AND t.status = 'completed'
GROUP BY c.customer_type, STRFTIME('%Y-%m-01', t.transaction_date)
ORDER BY month DESC, monthly_revenue DESC;
