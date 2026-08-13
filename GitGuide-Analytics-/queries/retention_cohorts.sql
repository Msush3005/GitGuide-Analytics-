-- queries/retention_cohorts.sql
-- Monthly Customer Retention Cohorts: CTE calculating signup cohort vs active transaction months
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        STRFTIME('%Y-%m-01', MIN(transaction_date)) as cohort_month
    FROM transactions
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT DISTINCT
        customer_id,
        STRFTIME('%Y-%m-01', transaction_date) as activity_month
    FROM transactions
)
SELECT 
    c.cohort_month,
    a.activity_month,
    COUNT(DISTINCT c.customer_id) as retained_customers
FROM customer_cohorts c
JOIN monthly_activity a ON c.customer_id = a.customer_id
GROUP BY c.cohort_month, a.activity_month
ORDER BY c.cohort_month DESC, a.activity_month ASC;
