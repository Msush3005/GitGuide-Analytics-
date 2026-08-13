-- Table: agg_daily_metrics
-- Purpose: Pre-aggregated daily metric summary table for high-performance dashboard queries
-- Refresh Strategy: Scheduled batch ETL / nightly scheduled script
-- Used By: Executive KPI cards, daily revenue trend charts, fast reporting layer
--
-- Columns:
-- aggregation_date: Date grain of aggregated summary (YYYY-MM-DD)
-- metric_name: Name of pre-computed metric (e.g., 'total_revenue', 'order_count')
-- metric_value: Calculated numerical aggregate value
-- row_count: Count of raw transaction rows aggregated into summary
-- updated_at: Timestamp recording when pre-aggregation was executed

CREATE TABLE IF NOT EXISTS agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC(12,2),
    row_count INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (aggregation_date, metric_name)
);

-- Population Query
INSERT OR REPLACE INTO agg_daily_metrics (aggregation_date, metric_name, metric_value, row_count, updated_at)
SELECT 
    DATE(o.order_date) as aggregation_date, 
    'total_revenue' as metric_name, 
    ROUND(SUM(o.order_amount), 2) as metric_value, 
    COUNT(*) as row_count, 
    CURRENT_TIMESTAMP as updated_at 
FROM orders o 
GROUP BY DATE(o.order_date);
