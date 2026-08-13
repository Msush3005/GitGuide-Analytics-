-- queries/left_join_validation.sql
-- LEFT JOIN: All customers with their orders (retains customers with 0 orders, multiplies customers with >1 order)
SELECT 
    c.customer_id,
    c.customer_type,
    COUNT(DISTINCT o.order_id) as order_count,
    ROUND(COALESCE(SUM(o.order_amount), 0), 2) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_type
ORDER BY total_spent DESC;
