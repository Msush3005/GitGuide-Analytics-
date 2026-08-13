-- queries/opt_task1_explicit_columns.sql
-- Refactored Query 1: Replaces SELECT * with explicit column selection.
-- Performance Rationale:
-- 1. Reduces network I/O and RAM overhead by omitting unused columns.
-- 2. Prevents secret PII exposure and breaking changes when database schema evolves.
SELECT 
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.customer_id,
    c.customer_name,
    c.country,
    c.customer_type as account_type
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-1 year')
LIMIT 1000;
