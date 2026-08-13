# Clean Data Layer Naming Conventions

This document establishes formal naming conventions and architectural design patterns for the database view and pre-aggregated summary layer.

---

## 1. SQL View Conventions (`vw_`)

- **Prefix**: `vw_` (tells readers this object is a dynamic SQL view, not a raw table).
- **Pattern**: `vw_[business_entity]_[metric_scope]`
- **Examples**:
  - `vw_active_customers`: Single source of truth for rolling 30-day customer activity and revenue.
  - `vw_product_performance`: Single source of truth for product-level sales, unit volumes, and unique buyer counts.

### Key Rules for Views
1. **Encapsulate Metric Business Logic**: Views embody official company metric definitions (e.g. active users exclude deleted accounts and include past 30-day orders).
2. **One View per Business Concept**: Focused views prevent monolithic slow views (`vw_everything`).
3. **Save as Version-Controlled `.sql` Files**: All view definitions live in `database/views/` under Git version control with descriptive header comments.

---

## 2. Pre-Aggregated Summary Table Conventions (`agg_`)

- **Prefix**: `agg_` (tells readers this object is a physical pre-computed summary table).
- **Pattern**: `agg_[grain]_[subject]`
- **Examples**:
  - `agg_daily_metrics`: Pre-aggregated daily metric table updated periodically.
  - `agg_monthly_revenue`: Pre-aggregated monthly summary table for executive dashboards.

### Mandatory Audit Columns in Aggregated Tables
1. **`updated_at` / `created_at`**: Timestamp recording when the aggregation batch was computed. Alerts consumers if data is stale.
2. **`row_count`**: Count of raw rows aggregated into each summary row (used for audit validation).
3. **`aggregation_date` / Grain Column**: Clear temporal grain of summary (daily, hourly, or monthly).

---

## 3. Architecture Benefits

- **Eliminates Metric Drift**: Dashboards and scripts query `vw_active_customers` instead of inventing custom SQL logic. Updating the view updates all consumers automatically.
- **Instant Dashboard Performance**: Queries against `agg_daily_metrics` load in under 5 milliseconds regardless of underlying raw table sizes.
- **Zero Ambiguity**: Prefix conventions (`vw_` vs `agg_` vs raw tables) clarify data lineage instantly for any developer.
