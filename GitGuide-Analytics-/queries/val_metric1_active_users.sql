-- queries/val_metric1_active_users.sql
-- Metric 1: Active Users (Rolling 30-day window)
-- Purpose: Counts distinct users who logged in at least once in the past 30 days
SELECT COUNT(DISTINCT user_id) as active_users 
FROM logins 
WHERE login_date >= DATE('now', '-30 days');
