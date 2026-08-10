# Technical Guide: KPI Architecture & Metric Design

This guide details the theoretical foundation, mathematical derivation, target-setting frameworks, governance, and schema evolution strategies for enterprise Key Performance Indicators (KPIs).

---

## 1. What Makes a Metric a KPI vs. Raw Output Numbers

- **Raw Metric**:
  - *Example*: Total Revenue = $\$100,000$, Transactions = $500$, Customers = $1,000$.
  - *Characteristics*: Raw counts or totals without context, targets, or directional guidance.
- **Key Performance Indicator (KPI)**:
  - *Example*: Revenue per Customer = $\$100.00$ (Target Range: $\$90 - \$110$).
  - *Characteristics*: Ratios, rates, or standardized metrics connected directly to strategic business goals with clear target bounds and ownership.

---

## 2. Formula Derivation from Data Schemas

Building a trustworthy KPI requires translating business intent into explicit SQL / Python logic:

### Monthly Active Users (MAU)
- **Business Intent**: Count distinct customer accounts actively engaging with the product in a rolling 30-day window.
- **Python Derivation**:
  ```python
  def calculate_mau(df, days=30):
      cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
      return df[df['transaction_date'] >= cutoff]['customer_id'].nunique()
  ```

---

## 3. Target Setting Methodology

Establishing effective KPI target ranges (`min` to `max` bounds):

1. **Historical Baseline**: Analyze prior 6-12 month performance distributions to set realistic lower bounds (`min`).
2. **OKR & Stretch Targets**: Incorporate strategic growth targets to establish ambitious upper bounds (`max`).
3. **Automated Alerting**: Any value falling below `min` triggers operational intervention, while values exceeding `max` signal potential data anomalies or unexpected growth.

---

## 4. KPI Reference Document & Single Source of Truth

When Finance, Sales, and Product calculate metrics independently, definitions diverge (e.g. Finance counting email signups while Sales counts paying accounts). 

A version-controlled `kpi_reference.md` establishes a **Single Source of Truth** by enforcing:
- Explicit metric definitions and formulas.
- Documented data source tables and columns.
- Assigned metric owners and update frequencies.

---

## 5. Managing Schema Evolution & Pipeline Changes

When underlying database schemas evolve (e.g. `amount` renamed to `gross_amount` or splitting `transactions` into `orders` and `payments`):

1. **Abstraction Layer**: Encapsulate calculation logic inside reusable module functions (`kpis/kpi_functions.py`).
2. **Backward-Compatible Data Mappings**: Update internal function code to support legacy and new column names without changing function signatures.
3. **Historical Data Restatement**: Restate historical baseline data when definitions change to preserve valid Year-over-Year (YoY) comparisons.
