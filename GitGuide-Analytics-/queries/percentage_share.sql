-- queries/percentage_share.sql
-- Percentage Share Computation: calculating segment revenue as % share of total revenue using SQL window functions
SELECT 
    c.customer_type,
    ROUND(SUM(t.amount), 2) as segment_revenue,
    ROUND(100.0 * SUM(t.amount) / SUM(SUM(t.amount)) OVER (), 2) as revenue_share_pct
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-1 year')
  AND t.status = 'completed'
GROUP BY c.customer_type
ORDER BY segment_revenue DESC;
