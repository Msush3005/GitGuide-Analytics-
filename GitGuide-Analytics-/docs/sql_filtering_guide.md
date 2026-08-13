# Technical Guide: SQL Filtering, Grouping & Aggregation

This guide details the SQL query execution order, `WHERE` vs `HAVING` semantic distinctions, `GROUP BY` aggregation mechanics, query optimization strategies, and window function percentage share calculations.

---

## 1. WHERE vs. HAVING Distinction: When Each Applies

| Feature | WHERE Clause | HAVING Clause |
| :--- | :--- | :--- |
| **Execution Order Stage** | Stage 1: Evaluated **BEFORE** `GROUP BY` | Stage 2: Evaluated **AFTER** `GROUP BY` |
| **Target Filter** | Individual raw rows | Aggregated group summary metrics |
| **Allowed Expressions** | Raw column predicates (`amount > 0`, `status = 'completed'`) | Aggregate functions (`SUM(amount) > 10000`, `COUNT(*) >= 5`) |
| **Primary Purpose** | Data quality filtering & scope reduction | Business rule thresholding on group summary metrics |

### Conceptual Rule
- Use **WHERE** to filter out invalid or irrelevant raw records before grouping.
- Use **HAVING** to filter calculated summary metrics after groups are formed.

---

## 2. GROUP BY Semantics & Aggregation Units

The `GROUP BY` clause transforms the granularity of query results:
- **Row Granularity $\rightarrow$ Group Granularity**: Collapses all rows sharing identical dimension values (e.g. `customer_type`, `month`) into a single summary row.
- **Aggregation Functions**: Calculates metrics per group (`COUNT(DISTINCT customer_id)`, `SUM(amount)`, `AVG(amount)`).
- **Multi-Dimension Grouping**: When grouping by `c.customer_type, c.industry`, the unit of aggregation becomes every unique pair of customer type and industry.

---

## 3. Query Optimization: Why WHERE Before GROUP BY is Faster

Filtering in `WHERE` before `GROUP BY` delivers massive query performance speedups:
1. **Reduces Input Volume**: If a table has 10,000,000 raw transaction rows, applying `WHERE transaction_date >= '2024-01-01'` might drop 8,000,000 rows immediately.
2. **Lowers Memory & CPU Overhead**: The database query engine performs hash grouping or sort operations on only 2,000,000 rows instead of 10,000,000.
3. **Optimized Index Usage**: `WHERE` clauses leverage B-Tree indexes on date or status columns directly.

---

## 4. HAVING Filter Business Rule Examples

Use `HAVING` when filtering on aggregated business metrics:
- **High-Value Accounts**: `HAVING SUM(amount) > 10000`
- **Frequent Buyers**: `HAVING COUNT(*) >= 5`
- **Large Customer Segments**: `HAVING COUNT(DISTINCT customer_id) >= 100`

---

## 5. Percentage Share Computation using SQL Window Functions

To compute each segment's revenue as a percentage of total revenue without running subqueries:

```sql
SELECT 
    c.customer_type,
    ROUND(SUM(t.amount), 2) as segment_revenue,
    ROUND(100.0 * SUM(t.amount) / SUM(SUM(t.amount)) OVER (), 2) as revenue_share_pct
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.status = 'completed'
GROUP BY c.customer_type
ORDER BY segment_revenue DESC;
```

`SUM(SUM(t.amount)) OVER ()` computes the grand total revenue across all groups, allowing direct percentage division in one clean pass.
