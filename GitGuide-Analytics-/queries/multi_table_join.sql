-- queries/multi_table_join.sql
-- 4-Table Join: Connecting customers, orders, order_items, and products
SELECT 
    c.customer_id,
    c.customer_type,
    o.order_id,
    o.order_date,
    oi.product_id,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    ROUND(oi.quantity * oi.unit_price, 2) as line_total
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE c.customer_type = 'Enterprise'
ORDER BY o.order_date DESC;
