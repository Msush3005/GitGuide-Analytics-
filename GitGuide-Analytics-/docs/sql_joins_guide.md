# Technical Guide: SQL Joins & Multi-Table Relational Analysis

This guide details relational database join semantics, row count validation methodologies, unmatched key audit techniques, multi-key join patterns, and join sequence optimization.

---

## 1. INNER vs. LEFT vs. FULL OUTER JOIN Comparison

| Join Type | Semantic Behavior | Result Set Size | Best Use Case |
| :--- | :--- | :--- | :--- |
| **INNER JOIN** | Keeps matched rows only ($\text{Left} \cap \text{Right}$) | $\le \min(\text{Left}, \text{Right})$ | Analyzing active accounts with confirmed purchases |
| **LEFT JOIN** | All left rows + matched right rows ($\text{Left} \cup (\text{Left} \cap \text{Right})$) | $\ge \text{Left}$ | Cohort retention, LTV, auditing missing orders |
| **FULL OUTER JOIN**| All rows from both tables ($\text{Left} \cup \text{Right}$) | $\ge \max(\text{Left}, \text{Right})$ | Auditing database migration gaps and orphaned records |

---

## 2. Row Count Validation: Preventing Silent Duplication

When joining a 1-to-many relationship (e.g., 1 customer with 5 orders):
- **Base Customer Rows**: $1,000$
- **Raw Join Output Rows**: $5,000$
- **Multiplication Factor**: $\frac{5,000}{1,000} = 5.0$ rows/customer

### Why Validation is Critical
If an analyst assumes 1 row per customer after a `LEFT JOIN orders` without running `GROUP BY customer_id`, calculating `SUM(amount)` across duplicate rows will double-count revenue! 

*Validation Rule*: Always inspect row counts before and after joining, and aggregate at the customer level before computing financial metrics.

---

## 3. Detecting Unmatched Keys & Orphaned Records

### Finding Customers with NO Orders
```sql
SELECT c.customer_id, c.customer_type
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

### Finding Orphaned Orders (Invalid Foreign Keys)
```sql
SELECT o.order_id, o.customer_id
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

---

## 4. Multi-Key Joining & Composite Foreign Keys

When joining tables partition-scoped by tenant, store, or region:

```sql
SELECT c.customer_name, o.order_date, o.order_amount
FROM customers c
JOIN orders o 
  ON c.tenant_id = o.tenant_id 
 AND c.customer_id = o.customer_id;
```

*Key Benefit*: Prevents accidental Cartesian cross-product multiplication when primary keys are only unique within a tenant or region partition.

---

## 5. Join Sequence & Order Impact

The order of tables in a multi-table query directly impacts intermediate row volume:
- **Left Table First**: In `customers LEFT JOIN orders LEFT JOIN order_items`, starting with `customers` retains all customer accounts first.
- **Filtering Order**: Applying `WHERE c.customer_type = 'Enterprise'` before downstream `order_items` joins filters the table driving the join tree early, minimizing memory usage.
