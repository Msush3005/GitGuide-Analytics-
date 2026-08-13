# GitGuide Analytics - Team GitHub Workflow & Collaboration Guide

This document outlines the engineering practices and GitHub workflows established for the **GitGuide Analytics** data product team. Following these guidelines ensures code quality, predictable releases, transparent issue tracking, and a clean git history.

---

## 1. Branching Strategy

Our team utilizes a structured feature-branch workflow to keep the production codebase stable and reliable.

- **`main` Branch**: Holds releasable, production-ready code only. Direct commits to `main` are strictly prohibited.
- **Feature & Task Branches**: All development work occurs in short-lived branches created off `main`. Branch names must adhere to the standard naming convention:

```bash
# Branch Naming Pattern
[type]/[short-description]
```

### Supported Branch Types
- `feature/` - New analytical tasks or data pipeline capabilities (e.g., `feature/data-ingestion`, `feature/github-workflow-setup`)
- `fix/` - Bug fixes and pipeline corrections (e.g., `fix/validation-logic`)
- `docs/` - Documentation updates and user guides (e.g., `docs/data-dictionary`)
- `refactor/` - Code restructures without functionality changes (e.g., `refactor/transformer-module`)
- `chore/` - Maintenance, dependency updates, and config (e.g., `chore/requirements-update`)

### Branch Lifecycle
1. Branch off updated `main`: `git checkout main && git pull origin main && git checkout -b feature/data-ingestion`
2. Commit changes using Conventional Commits.
3. Open a Pull Request (PR) to `main`.
4. After code review approval and merge, **delete the feature branch** to prevent repository clutter.

---

## 2. Commit Message Conventions

We adhere strictly to the **Conventional Commits** standard to ensure readable history and automated changelog generation.

### Commit Format
```text
[type]: [short summary in present tense]

[optional description body explaining WHY the change was made]
```

### Types Allowed
| Type | Purpose | Example |
| :--- | :--- | :--- |
| `feat` | New feature or user capability | `feat: add data validation pipeline module` |
| `fix` | Bug fix in code or pipeline | `fix: resolve null value handling in contributor parser` |
| `docs` | Documentation changes only | `docs: document team github workflow and conventions` |
| `refactor` | Code change that neither fixes a bug nor adds a feature | `refactor: optimize database connection pooling` |
| `test` | Adding or updating tests | `test: add unit tests for CSV schema validator` |
| `chore` | Build process, tool updates, dependencies | `chore: update requirements.txt with pandas` |

### Why Conventional Commits?
- **Context Clarity**: Teammates can immediately understand the scope and impact of changes from git logs.
- **Automated Tooling**: Enables automatic semver versioning and changelog generation.
- **Bi-directional Traceability**: Connects commits directly to analytical deliverables and code reviews.

---

## 3. Pull Request (PR) & Code Review Process

Pull Requests serve as the gateway for integrating code into `main`.

### PR Requirements
1. **Clear Title**: Action-oriented description of the change (e.g., `Add data validation workflow and team branching guidelines`).
2. **Detailed Context**: Explain *what* changed, *why* it changed, and how it was tested.
3. **Issue Linking**: Link relevant GitHub issues using standard closing keywords (e.g., `Closes #2`, `Fixes #3`).
4. **Commit Summary**: Include a summary of included commits.

### Review Criteria
- **Mandatory Approval**: PRs require at least one peer approval prior to merging.
- **Focus Areas**:
  - **Correctness & Logic**: Code fulfills the acceptance criteria without side effects.
  - **Data Integrity & Schema**: Ingested and transformed data maintains expected schemas.
  - **Code Clarity**: Readable code with appropriate inline comments and type annotations.
  - **Commit Hygiene**: Clean, properly formatted commit messages following team conventions.

---

## 4. GitHub Issue Tracking Approach

Sprint deliverables and bugs are tracked using GitHub Issues.

- **Pre-requisite**: Every feature or fix begins with a trackable GitHub issue before coding starts.
- **Issue Requirements**:
  - **Action-oriented Title**: Specific title (e.g., `Implement GitHub Data Ingestion Pipeline`).
  - **Context & Definition of Done**: Body detailing business value, requirements, and concrete acceptance criteria.
  - **Label(s)**: Categorized with relevant tags (e.g., `enhancement`, `data-pipeline`, `feature`, `documentation`).
  - **Assignee**: Explicitly assigned to the team member responsible for execution.
- **Lifecycle Closure**: Issues are automatically closed when their linked PR is merged into `main` (via `Closes #X`).

---

## 10. GroupBy Aggregation & Segment Insights Workflow (`scripts/segment_analysis.py`)

This module executes multi-dimensional segment aggregations, 2D pivot tables, segment ranking, and actionable insight matrix generation for customer churn and revenue analytics.

### Why GroupBy Segmentation Matters
- **Exposes Hidden Variances**: Overall dataset averages can mask critical segment issues (e.g. an overall 5% churn average masking a 12% churn rate in SMB customers).
- **Split-Apply-Combine Pattern**: Splitting data by keys, applying aggregation functions (`mean`, `sum`, `count`), and combining results into actionable matrices.

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/segment_analysis.py
```

### Function Breakdown & Responsibilities
- **`generate_segment_dataset(num_rows, filepath)`**: Generates synthetic customer churn dataset across Enterprise, SMB, and Startup segments.
- **`task1_single_level_groupby(df)`**: Aggregates churn rate, total revenue, customer count, and support tickets per `customer_type`.
- **`task2_multi_level_groupby(df)`**: Performs multi-index aggregation across `['customer_type', 'product']` and unstacks results.
- **`task3_pivot_table(df)`**: Creates 2D cross-tabulation of revenue by customer type and product using `pd.pivot_table()`.
- **`task4_rank_and_identify_performers(segment_metrics)`**: Ranks segments by churn rate and computes revenue contribution percentage share.
- **`task5_surface_actionable_insights(segment_metrics)`**: Evaluates business thresholds (>10% churn = High Priority intervention) and exports report to `output/segment_insights.csv`.

---

## 11. Time-Series Trend & Rolling Metrics Workflow (`scripts/rolling_metrics.py`)

This module executes temporal data analytics, smoothing daily volatility with rolling moving averages, resampling frequency periods, tracking cumulative sums, and evaluating growth momentum.

### Why Time-Series Analysis Matters
- **Filters Daily Volatility**: Raw daily revenue data contains noise and weekly seasonality; 7-day and 30-day rolling averages isolate true underlying business momentum.
- **Prevents Reactive Decision-Making**: Evaluates trends rather than reacting to isolated single-day revenue drops.

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/rolling_metrics.py
```

### Function Breakdown & Responsibilities
- **`generate_timeseries_dataset(num_days, filepath)`**: Generates 365 days of synthetic daily revenue and order data containing trend, weekly seasonality, and noise.
- **`task1_resample_data(df)`**: Aggregates daily date-indexed data into weekly (`W`) and monthly (`ME`) frequency buckets using `sum()`, `count()`, and `mean()`.
- **`task2_compute_rolling_averages(df)`**: Computes 7-day and 30-day moving averages and saves visual trend comparison to `output/rolling_avg.png`.
- **`task3_calculate_mom_change(monthly_revenue)`**: Calculates Month-over-Month growth rates using `.pct_change() * 100`.
- **`task4_compute_cumulative_sum(df)`**: Computes `.cumsum()` cumulative total revenue and exports plot to `output/cumulative.png`.
- **`task5_identify_trend_and_implications(df, ...)`**: Evaluates recent 30-day rolling window direction (UP/DOWN/FLAT), calculates volatility, and exports structured business interpretation to `output/trend_analysis.txt`.

---

## 16. Anomaly Detection & Risk Identification Workflow (`scripts/anomaly_detection.py`)

This module executes automated threshold checking and statistical z-score anomaly monitoring, categorizing severity levels, maintaining persistent audit logs, and generating time-series charts with flagged anomaly markers.

### Why Anomaly Detection Matters
- **Early Warning System**: Catches silent payment failures or fraud bot spikes within minutes before financial loss multiplies.
- **Audit Trail & Governance**: Persists all detected anomalies into `anomalies_log.csv` with status tracking (`OPEN`, `INVESTIGATED`, `RESOLVED`).

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/anomaly_detection.py
```

### Function Breakdown & Responsibilities
- **`generate_business_metrics_dataset(num_days, filepath)`**: Generates 90 days of daily metrics with injected high/low anomalies.
- **`task1_check_thresholds(metrics, alert_rules)`**: Checks metrics against static min/max business rule boundaries.
- **`task2_detect_anomalies_zscore(series, threshold)`**: Computes rolling z-scores over a 30-day lookback window ($z > 2.0$).
- **`task3_severity_classification(anomalies, ...)`**: Classifies anomalies into `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW` levels.
- **`task4_anomaly_logging_audit_trail(...)`**: Persists audit log records into `anomalies_log.csv` and `output/anomalies_log.csv`.
- **`task5_visualization_with_flagged_points(...)`**: Renders raw revenue line, 7-day rolling average, shaded $\pm 2\sigma$ range, and red 'X' anomaly markers, saving to `anomaly_detection.png` and `output/anomaly_detection.png`.

---

## 17. SQL Environment & Database Integration Workflow (`scripts/database_integration.py`)

This module executes Python-to-SQL database integration, configuring SQLAlchemy engines, writing DataFrames to database tables, inspecting schemas, running analytical queries, and packaging reusable loading functions.

### Why Database Integration Matters
- **Single Source of Truth**: Replaces scattered local CSV files and notebooks with a centralized, queryable database table.
- **Repeatable & Auditable Pipelines**: Encapsulates data persistence and schema validation inside reusable module functions.

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/database_integration.py
```

### Function Breakdown & Responsibilities
- **`generate_sample_cleaned_data(num_records)`**: Generates 1,000 synthetic cleaned customer records for database persistence.
- **`task1_setup_database_connection(database_path)`**: Initializes SQLAlchemy engine `sqlite:///analytics.db` and verifies connection.
- **`task2_load_cleaned_dataframe(df_clean, engine, table_name)`**: Writes DataFrame to SQL table (`if_exists='replace'`) and verifies row count.
- **`task5_validate_metrics(mau_df, revenue_df, funnel_df)`**: Asserts metric integrity (zero nulls, valid ranges, logical order/revenue consistency).

---

## 19. SQL Filtering, Grouping & Aggregation Workflow (`scripts/sql_filtering_engine.py`)

This module demonstrates advanced SQL filtering and reporting clauses (`WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, window functions) stored in version-controlled `.sql` files under `/queries/`.

### Why Clause Distinction Matters
- **WHERE vs HAVING**: `WHERE` filters raw rows before grouping (improving performance by reducing input size); `HAVING` filters aggregate group metrics after grouping.
- **Data Quality & Reporting**: Prevents common analytics errors by separating raw data quality checks from business threshold filtering.

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/sql_filtering_engine.py
```

### Function Breakdown & Responsibilities
- **`ensure_filtering_database(database_path)`**: Ensures `customers` (with `industry`) and `transactions` (with `status`) tables exist in `analytics.db`.
- **`load_query(query_name, queries_dir)`**: Loads raw SQL query text from `/queries/` files.
- **`execute_and_export(query_name, engine, output_dir)`**: Executes queries via `pd.read_sql` and exports results to CSV.
- Executed Query Files: `where_filtering.sql`, `group_by_aggregation.sql`, `having_filtering.sql`, `where_having_combined.sql`, `order_by_ranking.sql`, `percentage_share.sql`.
- **`task3_validate_schema(engine, table_name)`**: Inspects table columns, data types, and nullability, saving report to `output/sql_schema_validation.txt`.
- **`task4_query_and_return_results(engine, table_name)`**: Executes SELECT filters and SQL aggregations (`GROUP BY customer_type`), returning results to Pandas DataFrames and `output/sql_query_summary.csv`.
- **`load_cleaned_data_to_database(df, table_name, database_path)`**: Reusable production pipeline function for automated data loading and validation.
