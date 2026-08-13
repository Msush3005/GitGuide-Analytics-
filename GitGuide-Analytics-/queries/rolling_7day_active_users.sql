-- queries/rolling_7day_active_users.sql
-- Rolling 7-Day Active Users (7D WAU): advanced time-window aggregation
SELECT 
    DATE(t1.transaction_date) as snapshot_date,
    COUNT(DISTINCT t2.customer_id) as rolling_7d_active_users
FROM transactions t1
JOIN transactions t2 ON t2.transaction_date BETWEEN DATE(t1.transaction_date, '-6 days') AND DATE(t1.transaction_date)
WHERE t1.transaction_date >= DATE('now', '-30 days')
GROUP BY DATE(t1.transaction_date)
ORDER BY snapshot_date DESC;
