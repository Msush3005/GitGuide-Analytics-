-- queries/revenue_by_segment.sql
-- Monthly Revenue per Customer Segment: computing 5 metrics per segment over rolling 12 months
SELECT 
    c.customer_type,
    STRFTIME('%Y-%m-01', t.transaction_date) as month,
    COUNT(DISTINCT t.transaction_id) as order_count,
    ROUND(SUM(t.amount), 2) as monthly_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    ROUND(SUM(t.amount) / COUNT(DISTINCT t.customer_id), 2) as revenue_per_customer
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-12 months')
GROUP BY c.customer_type, STRFTIME('%Y-%m-01', t.transaction_date)
ORDER BY month DESC, monthly_revenue DESC;
