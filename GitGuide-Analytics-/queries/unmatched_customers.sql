-- queries/unmatched_customers.sql
-- Customers with NO orders (retained by LEFT JOIN, filtered where right table key IS NULL)
SELECT 
    c.customer_id,
    c.customer_type,
    c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.signup_date;
