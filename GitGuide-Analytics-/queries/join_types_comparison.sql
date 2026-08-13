-- queries/join_types_comparison.sql
-- Table Row Count Comparison Query across Join Types
-- 1. INNER JOIN (matched rows only)
-- 2. LEFT JOIN (all customers + matched orders)
-- 3. FULL OUTER JOIN (all customers + all orders including orphaned)
SELECT 'customers_base' as dataset, COUNT(DISTINCT customer_id) as distinct_keys, COUNT(*) as total_rows FROM customers
UNION ALL
SELECT 'orders_base', COUNT(DISTINCT customer_id), COUNT(*) FROM orders
UNION ALL
SELECT 'inner_join', COUNT(DISTINCT c.customer_id), COUNT(*) FROM customers c INNER JOIN orders o ON c.customer_id = o.customer_id
UNION ALL
SELECT 'left_join', COUNT(DISTINCT c.customer_id), COUNT(*) FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id;
