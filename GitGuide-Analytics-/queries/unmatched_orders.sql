-- queries/unmatched_orders.sql
-- Orders with NO matching customer (orphaned records where foreign key customer_id does not exist in customers table)
SELECT 
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_amount
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
ORDER BY o.order_date;
