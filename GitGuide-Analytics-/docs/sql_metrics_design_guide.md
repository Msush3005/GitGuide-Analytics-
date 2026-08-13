# Technical Guide: SQL Business Metrics Query Design

This guide details metric architecture in SQL, conditional aggregation patterns, retention cohort CTEs, rolling 7-day active user windows, and version-controlled metric management.

---

## 1. Why SQL Metrics Beat Python Scripts

| Dimension | Python Script Metrics | SQL Database Metrics |
| :--- | :--- | :--- |
| **Single Source of Truth** | Definitions diverge across notebooks and local CSV files | Single version-controlled `.sql` file queried by all teams |
| **Tool Accessibility** | Limited to Python/Jupyter users | Accessible by Python, R, Tableau, PowerBI, and Metabase |
| **Performance** | Transfers raw rows over network to calculate in Python memory | Computes aggregation inside database engine; returns final numbers |
| **Auditability** | Difficult to trace historical pandas mutations | Clean, version-controlled SQL logic committed to Git |

---

## 2. Conditional Aggregation with `CASE WHEN`

Conditional aggregation computes multi-segment metrics in a single database scan:

```sql
SELECT 
    DATE(u.created_at) as signup_date,
    COUNT(*) as total_signups,
    COUNT(CASE WHEN u.email_verified_at IS NOT NULL THEN 1 END) as verified_users,
    COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) as paying_customers,
    ROUND(100.0 * COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) / COUNT(*), 1) as conversion_pct
FROM users u
GROUP BY DATE(u.created_at);
```

*Key Benefit*: Eliminates the need for multiple `WHERE` clauses or separate queries.

---

## 3. Retention Cohort Analysis in SQL

Cohort analysis tracks how customer groups retain over time using Common Table Expressions (CTEs):

```sql
WITH customer_cohorts AS (
    SELECT customer_id, STRFTIME('%Y-%m-01', MIN(transaction_date)) as cohort_month
    FROM transactions GROUP BY customer_id
),
monthly_activity AS (
    SELECT DISTINCT customer_id, STRFTIME('%Y-%m-01', transaction_date) as activity_month
    FROM transactions
)
SELECT 
    c.cohort_month,
    a.activity_month,
    COUNT(DISTINCT c.customer_id) as retained_customers
FROM customer_cohorts c
JOIN monthly_activity a ON c.customer_id = a.customer_id
GROUP BY c.cohort_month, a.activity_month;
```

---

## 4. Rolling 7-Day Active Users (7D WAU)

Advanced time-window aggregation using self-joins:

```sql
SELECT 
    DATE(t1.transaction_date) as snapshot_date,
    COUNT(DISTINCT t2.customer_id) as rolling_7d_active_users
FROM transactions t1
JOIN transactions t2 ON t2.transaction_date BETWEEN DATE(t1.transaction_date, '-6 days') AND DATE(t1.transaction_date)
GROUP BY DATE(t1.transaction_date);
```

---

## 5. Safely Extending Metric Definitions

When adding new metrics (e.g., adding `startup_users` to MAU):
1. **Append-Only Columns**: Add new metrics as additional SELECT expressions without altering existing column names or data types.
2. **Version-Controlled `.sql` Files**: Maintain queries under `/queries/` in Git. Modifying the file updates all downstream Python and BI dashboard callers automatically.
3. **Automated Assertion Testing**: Run `validate_metrics()` in Python CI/CD pipelines to catch nulls or out-of-bound values before deployment.
