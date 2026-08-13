-- queries/order_by_ranking.sql
-- Surface top performers: GROUP BY customer_type & industry, RANK() OVER (ORDER BY revenue DESC), LIMIT 20
SELECT 
    c.customer_type,
    c.industry,
    COUNT(DISTINCT t.customer_id) as customers,
    ROUND(SUM(t.amount), 2) as total_revenue,
    ROUND(AVG(t.amount), 2) as avg_order,
    RANK() OVER (ORDER BY SUM(t.amount) DESC) as revenue_rank
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-1 year')
  AND t.status = 'completed'
GROUP BY c.customer_type, c.industry
HAVING COUNT(DISTINCT t.customer_id) >= 5
ORDER BY total_revenue DESC
LIMIT 20;
