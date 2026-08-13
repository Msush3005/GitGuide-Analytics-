-- queries/opt_task3_cte_refactoring.sql
-- Refactored Query 3: Structures complex nested subquery into modular, testable CTEs.
-- Performance & Maintenance Rationale:
-- 1. Step 1 (recent_transactions): Filters transaction scope early.
-- 2. Step 2 (customer_with_segment): Joins customer tier dimensions cleanly.
-- 3. Step 3 (segment_metrics): Computes aggregate metrics at segment granularity.
WITH recent_transactions AS (
    -- Step 1: Filter to recent valid transactions
    SELECT 
        transaction_id,
        amount,
        customer_id
    FROM transactions
    WHERE transaction_date >= DATE('now', '-1 year')
),
customer_with_segment AS (
    -- Step 2: Join to customer tier data
    SELECT 
        rt.transaction_id,
        rt.amount,
        c.customer_type as customer_segment
    FROM recent_transactions rt
    JOIN customers c ON rt.customer_id = c.customer_id
),
segment_metrics AS (
    -- Step 3: Calculate segment-level aggregate metrics
    SELECT 
        customer_segment,
        COUNT(DISTINCT transaction_id) as transaction_count,
        ROUND(AVG(amount), 2) as avg_transaction_value,
        ROUND(SUM(amount), 2) as total_revenue
    FROM customer_with_segment
    GROUP BY customer_segment
)
SELECT 
    customer_segment,
    avg_transaction_value,
    transaction_count,
    total_revenue
FROM segment_metrics
ORDER BY avg_transaction_value DESC;
