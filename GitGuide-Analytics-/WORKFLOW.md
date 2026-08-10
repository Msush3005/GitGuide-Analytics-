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

## 13. Funnel Analysis & Drop-Off Detection Workflow (`scripts/funnel_analysis.py`)

This module executes sequential conversion funnel tracking across 6 stages, computing drop-off percentages, rendering volume bar charts, quantifying revenue impacts, and formulating A/B test recommendations.

### Why Funnel Analysis Matters
- **Locates Process Friction**: Identifies the exact step where users drop off rather than relying on an overall end-to-end conversion average.
- **Data-Driven Engineering Priorities**: Ranks product bottlenecks by financial revenue impact ($100 per lost user) to direct development resources where ROI is highest.

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/funnel_analysis.py
```

### Function Breakdown & Responsibilities
- **`generate_funnel_dataset(num_users, filepath)`**: Generates synthetic conversion flags for 10,000 users across 6 sequential stages.
- **`task1_define_funnel_stages(df)`**: Counts user volumes across all 6 stages (`Sign Up` through `First Purchase`).
- **`task2_compute_drop_off_rates(stages)`**: Calculates `users_lost`, `completion_rate`, `drop_rate`, and identifies the primary bottleneck.
- **`task3_visualize_funnel(stages)`**: Renders and exports an annotated, color-coded funnel volume bar chart to `output/funnel_chart.png`.
- **`task4_calculate_business_impact(funnel_df)`**: Calculates potential revenue loss (`users_lost * $100`) and ranks bottlenecks by financial priority.
- **`task5_actionable_recommendations(funnel_df)`**: Formulates UX root cause hypotheses, A/B test rollout strategies, and 10% fix revenue impact projections, exporting the report to `output/funnel_analysis.txt`.



