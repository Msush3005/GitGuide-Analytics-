# Cross-Layer Discrepancy & Root Cause Analysis Report

## 1. Executive Summary & Audit Observations

During our automated cross-layer validation audit between the SQL view data layer and Python analytical notebooks, we discovered a significant **26.5% computation drift** in the **Monthly Customer Churn** metric:

- **Buggy SQL Query Result**: 50 churned customers
- **Python Notebook Result**: 68 churned customers
- **Discrepancy Delta**: 18 customers (26.5% percent difference)

---

## 2. Root Cause Investigation & Hand Computation

### Step 1: Hand Computation on Sample Subset
To isolate which computational layer reflected true business logic, we extracted raw order logs for a sample customer subset (Customers 1001 to 1050) across Month N-1 and Month N:
```python
# Hand computation sample subset
sample_orders = orders_df[(orders_df['customer_id'] >= 1001) & (orders_df['customer_id'] <= 1050)]
manual_churn = set(sample_orders[m_n1]['customer_id']) - set(sample_orders[m_n]['customer_id'])
print(f"Manual Churn Count: {len(manual_churn)}")
```
- **Manual Sample Count**: 7 churned customers (matching Python logic).

### Step 2: Code Inspection & Root Cause Identification
- **Root Cause**: The unoptimized SQL query used `STRFTIME('%m', order_date)` to compare month numbers (`1` to `12`).
- **Year Context Stripping**: Extracting only the month number strips the year context (`YYYY`). When crossing year boundaries (e.g. comparing December 2024 to January 2025), comparing month number `01` matched transactions from **January 2024** instead of **January 2025**, filtering out active returning customers and corrupting the churn count.

---

## 3. Fix Applied & Post-Fix Validation

### Refactored SQL Query (`val_metric3_churn_fixed.sql`)
We updated the SQL query to use explicit date range boundaries (`start of month` SQLite modifiers):

```sql
SELECT COUNT(DISTINCT c1.customer_id) as churned_customers 
FROM ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= DATE('now', 'start of month', '-1 month') 
      AND order_date < DATE('now', 'start of month') 
      AND order_amount > 0 
) c1 
LEFT JOIN ( 
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date >= DATE('now', 'start of month') 
) c2 ON c1.customer_id = c2.customer_id 
WHERE c2.customer_id IS NULL;
```

### Post-Fix Audit Result
- **Refactored SQL Result**: 68 churned customers
- **Python Result**: 68 churned customers
- **Discrepancy Delta**: **0 customers (0.00% percent difference — PASS)**

---

## 4. Answers to Follow-Up Questions (Task 5)

### Q: Why is manual investigation necessary when a validation script flags a discrepancy? What is the risk of auto-fixing based on a tolerance threshold alone?

1. **Tolerance Thresholds Catch Divergence, Not Correctness**:
   A validation script can detect that SQL and Python disagree, but it cannot know *which* layer is mathematically or logically correct. Auto-fixing by automatically overwriting SQL with Python (or vice versa) runs a 50% risk of standardizing on the wrong, corrupted metric!

2. **Creeping Silent Drift**:
   Small discrepancies (e.g. 0.05% diff caused by rounding or timezone mismatches) can accumulate over time into massive financial errors if ignored or automatically masked.

3. **Root Cause Resolution Prevents Systemic Pipeline Failures**:
   Manual investigation identifies *why* the divergence happened (e.g., year-stripping date functions, missing NULL handlers, or inconsistent timezone conversions). Fixing the root cause permanently repairs upstream data pipelines rather than applying superficial band-aids.
===================================================================
