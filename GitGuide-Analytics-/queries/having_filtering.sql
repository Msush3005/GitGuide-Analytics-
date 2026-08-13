-- queries/having_filtering.sql
-- Filter GROUPS after aggregation:
-- WHERE filters rows before grouping; HAVING filters aggregated group metrics.
-- HAVING SUM(amount) > 4000 filters for high-value customer accounts (> $4,000).
-- HAVING COUNT(*) >= 5 filters for frequent repeat buyers (5+ orders).
SELECT 
    t.customer_id,
    COUNT(*) as transaction_count,
    ROUND(SUM(t.amount), 2) as annual_revenue
FROM transactions t
WHERE t.transaction_date >= DATE('now', '-1 year')
  AND t.status = 'completed'
GROUP BY t.customer_id
HAVING SUM(t.amount) > 4000
   AND COUNT(*) >= 5
ORDER BY annual_revenue DESC;
