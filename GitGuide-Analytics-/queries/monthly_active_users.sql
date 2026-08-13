-- queries/monthly_active_users.sql
-- Monthly Active Users (MAU): distinct customers with transactions in rolling 12 months with segment breakdown
SELECT 
    STRFTIME('%Y-%m-01', t.transaction_date) as month,
    COUNT(DISTINCT t.customer_id) as active_users,
    COUNT(DISTINCT CASE WHEN c.customer_type = 'Enterprise' THEN t.customer_id END) as enterprise_users,
    COUNT(DISTINCT CASE WHEN c.customer_type = 'SMB' THEN t.customer_id END) as smb_users,
    COUNT(DISTINCT CASE WHEN c.customer_type = 'Startup' THEN t.customer_id END) as startup_users
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= DATE('now', '-12 months')
GROUP BY STRFTIME('%Y-%m-01', t.transaction_date)
ORDER BY month DESC;
