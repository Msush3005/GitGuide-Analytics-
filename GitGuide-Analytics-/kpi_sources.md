# KPI Data Lineage & Computation Documentation

This document records the exact data lineage, SQL views, and validation checks for the five executive KPI summary cards displayed on the Sales Performance Dashboard.

---

## 1. Data Lineage & Metric Definitions

### KPI 1: Total Revenue
- **Source Object**: `agg_daily_metrics` (Pre-aggregated table) / `orders` base table
- **SQL Query**:
  ```sql
  SELECT ROUND(SUM(order_amount), 2) as current_revenue 
  FROM orders 
  WHERE order_date >= DATE('now', 'start of month') 
    AND order_date < DATE('now', 'start of month', '+1 month');
  ```
- **Validation**: Cross-checked with Python Pandas sum of Month N orders ($5,200,000.00).
- **Directional Logic**: Standard (Up = Green `#10b981`, Down = Red `#ef4444`).

---

### KPI 2: Active Users
- **Source Object**: `vw_active_customers` (SQL View) / `logins` base table
- **SQL Query**:
  ```sql
  SELECT COUNT(DISTINCT user_id) as active_users 
  FROM logins 
  WHERE login_date >= DATE('now', '-30 days');
  ```
- **Validation**: Cross-checked with Python `logins_df.nunique()` (2,500 users).
- **Directional Logic**: Standard (Up = Green `#10b981`, Down = Red `#ef4444`).

---

### KPI 3: Average Order Value (AOV)
- **Source Object**: `orders` base table / `vw_product_performance`
- **SQL Query**:
  ```sql
  SELECT ROUND(AVG(order_amount), 2) as aov 
  FROM orders 
  WHERE order_date >= DATE('now', 'start of month');
  ```
- **Validation**: Cross-checked with Python `orders_df['order_amount'].mean()` ($45.00).
- **Directional Logic**: Standard (Up = Green `#10b981`, Down = Red `#ef4444`).

---

### KPI 4: Customer Churn Rate (Inverted Metric)
- **Source Object**: `orders` base table / `vw_active_customers`
- **SQL Query**:
  ```sql
  SELECT COUNT(DISTINCT c1.customer_id) as churned 
  FROM (SELECT DISTINCT customer_id FROM orders WHERE order_date >= DATE('now', 'start of month', '-1 month') AND order_date < DATE('now', 'start of month')) c1 
  LEFT JOIN (SELECT DISTINCT customer_id FROM orders WHERE order_date >= DATE('now', 'start of month')) c2 ON c1.customer_id = c2.customer_id 
  WHERE c2.customer_id IS NULL;
  ```
- **Validation**: Cross-checked with Python set difference calculation (5.2% churn).
- **Directional Logic**: **Inverted Metric** (Down = Green `#10b981`, Up = Red `#ef4444`). Streamlit uses `delta_color='inverse'`.

---

### KPI 5: Customer Satisfaction (CSAT)
- **Source Object**: `customer_surveys` base table / `csat_summary`
- **SQL Query**:
  ```sql
  SELECT ROUND(AVG(rating), 1) as avg_csat 
  FROM customer_surveys 
  WHERE survey_date >= DATE('now', 'start of month');
  ```
- **Validation**: Cross-checked with Python mean survey rating (4.2 / 5.0).
- **Directional Logic**: Standard (Up = Green `#10b981`, Down = Red `#ef4444`).

---

## 2. Technical Follow-Up Q&A: Auto-Updating KPI Systems

### Question
*When a new dataset is uploaded, how do you design the KPI system so that values automatically update without requiring code changes?*

---

### Architectural Solution
To ensure KPI values update automatically when new data is uploaded without touching Python or SQL code:

1. **Use Dynamic Date Expressions Instead of Hardcoded Dates**:
   Avoid writing static date strings like `'2024-01-01'`. Use database-native dynamic functions like `DATE('now', 'start of month')` or `CURRENT_DATE - INTERVAL 30 DAY`.

2. **Source KPIs from SQL Views & Aggregated Tables**:
   Dashboards query `vw_active_customers` or `agg_daily_metrics`. As new rows flow into the database, SQL views automatically recalculate metrics on every query execution.

3. **Scheduled Automated ETL Refresh Jobs**:
   Set up nightly cron or dbt orchestration jobs that re-populate `agg_daily_metrics` whenever new transaction batches land in the data warehouse.

4. **Streamlit Cache Invalidation**:
   In Streamlit, use `@st.cache_data(ttl=3600)` with a 1-hour time-to-live or add an automated `updated_at` polling trigger that invalidates cache when table modification timestamps change.
