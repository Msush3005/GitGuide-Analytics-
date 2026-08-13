# Dashboard Design Documentation

## Information Hierarchy Applied

The Executive Business Performance Dashboard is structured using a **Four-Level Information Hierarchy** to align with human visual scanning and cognitive processing:

- **Level 1 (Status - Top Row)**: 5 KPI Summary Cards designed for 5-second scanning to answer *"Are we on track?"*:
  1. **Monthly Revenue ($5.2M, +12.5% MoM)**: Measures overall top-line financial performance against company growth goals.
  2. **Active Customers (2,500, +5.2% MoM)**: Tracks user base health and product adoption breadth.
  3. **Avg Order Value ($145, +3.1% MoM)**: Evaluates monetization depth and pricing expansion.
  4. **Churn Rate (4.8%, -1.2% MoM)**: Monitors customer loss and retention health (inverse delta coloring: green for decrease).
  5. **NPS Score (72, +4 pts)**: Measures customer satisfaction and brand loyalty.

- **Level 2 (Trends - Middle Section)**: 3 Time-Series Trend Charts answering *"Is performance getting better or worse?"*:
  - **Monthly Revenue Trend vs. Target ($5.0M)**: Line chart with a green dashed target reference line.
  - **Active vs. Churned Customers Trend**: Dual-axis line chart illustrating customer acquisition vs. attrition dynamics.
  - **Average Order Value (AOV) Trend**: Line chart tracking monetization stability against a $140 benchmark.

- **Level 3 (Segments - Breakdown Section)**: Horizontal Bar Chart answering *"Which customer segments drive revenue?"*:
  - **Revenue by Customer Segment**: Breaks down revenue into Enterprise ($2.1M), Mid-Market ($1.5M), SMB ($1.0M), and Starter ($0.6M) with data labels.

- **Level 4 (Detail - Bottom Section & Sidebar Filters)**: Data Explorer answering *"Show me individual record-level data for deeper investigation"*:
  - Interactive sidebar filters for **Customer Segment** and **Date Range**, dynamic record count, and an instant **CSV Data Export** button.

---

## Design Principles Applied

1. **Progressive Disclosure**: High-level status KPIs are displayed immediately; granular record-level data is hidden behind sidebar filters and expandable table views to reduce cognitive overload.
2. **Spatial Organization**: The most critical top-line revenue KPI is positioned at the top-left (following Western left-to-right, top-to-bottom reading patterns).
3. **Consistent Metaphor**: Visual semantics are unified across the dashboard — Blue (`#1f77b4`) represents core metrics, Green (`#2ca02c`) signifies positive targets/trends, Red (`#d62728`) flags churn/risk, and Orange (`#ff7f0e`) highlights secondary comparisons.
4. **Context Over Numbers**: Raw numbers are paired with period-over-period delta percentages (`+12.5% MoM`), target reference lines (`$5.0M Target`), and benchmark comparisons.

---

## Color Palette Tokens

- **Primary Accent**: `#1f77b4` (Blue) — Core revenue and customer trend lines.
- **Secondary Accent**: `#ff7f0e` (Orange) — AOV trend and Mid-Market segment.
- **Success / Target**: `#2ca02c` (Green) — Positive deltas, revenue target line, and SMB segment.
- **Danger / Warning**: `#d62728` (Red) — Churn rate metrics, churned customer trends, and Starter segment.

---

## Target Audience Personas

1. **CEO (Primary Glance User)**: Focuses on Level 1 KPI cards during 5-second weekly check-ins to verify company health.
2. **VP of Sales & Marketing (Operational User)**: Evaluates Level 2 trends and Level 3 segment breakdowns daily to optimize acquisition channels.
3. **Data Analysts & Finance Managers (Power Users)**: Leverages Level 4 sidebar filters and CSV exports to investigate segment anomalies.

---

## Data Sources & SQL Engine Views

- **KPI Values**: Computed from `vw_monthly_revenue` and `vw_active_customers` views.
- **Trend Data**: Queried from `agg_daily_revenue` aggregated monthly metrics table.
- **Segment Breakdown**: Computed from `vw_customer_segments` relational view in `analytics.db`.
