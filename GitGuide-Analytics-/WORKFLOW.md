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
- `feature/` - New analytical tasks or data pipeline capabilities (e.g., `feature/data-ingestion`, `feature/github-workflow-setup`, `feature/python-workflow-script`)
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

## 5. Production Python Data Pipeline Script (`scripts/data_workflow.py`)

Notebook-based exploration is converted into a modular, production-ready Python script to ensure automated execution, CI/CD compatibility, and clear maintainability.

### How to Execute the Script
Run the pipeline from the command line from the project root or from inside the `scripts/` directory:

```bash
# Execute from project root
python scripts/data_workflow.py

# Alternatively, execute from scripts directory
cd scripts
python data_workflow.py

# Save execution output log
python scripts/data_workflow.py > output/sample_run.txt
```

### Function Breakdown & Responsibilities
- **`ingest_data(filepath)`**: Reads raw CSV or JSON datasets into a Pandas DataFrame. Verifies file existence and logs record counts.
- **`process_data(df)`**: Applies transformations:
  - Deduplication (`drop_duplicates()`).
  - Numerical median imputation for null values.
  - Categorical fallback string imputation.
  - Feature engineering (`total_contributions = commits_count + pull_requests_opened`).
- **`output_results(df, output_path)`**: Exports the cleaned DataFrame to CSV format, automatically creates parent directories if missing, and prints execution checkmark confirmations (`✓ Data successfully processed`).

### How to Modify for New Datasets
1. **Change Input File Path**: Update `input_file` in the `if __name__ == "__main__":` block to point to your new dataset (e.g., `data/raw/new_transactions.csv`).
2. **Update Required Columns**: Modify column checks or feature engineering logic inside `process_data(df)` to match the target schema.
3. **Change Output Location**: Update `output_file` (e.g., `output/transformed_metrics.csv`).

---

## 6. Dataset Intake Validation (`scripts/validate_intake.py`)

Before transforming any dataset, we run an intake validation check. This acts as a quality firewall, preventing corrupted or malformed data from entering our analytics pipeline and causing downstream failures.

### Why Intake Validation Matters
- **Quality Gatekeeper**: Catches schema changes, file formatting issues, empty files, or encoding anomalies early.
- **Fail-Fast Design**: Stops execution immediately if foundational properties (e.g., file existence, extension) are missing.
- **Audit Trail**: Generates a structured JSON validation report (`output/intake_report.json`) detailing pass/fail status and baseline statistics.

### How to Execute the Script
Run the validation script from the project root:

```bash
python scripts/validate_intake.py
```

This will read the raw dataset from `data/raw/sample.csv`, run the checks, and save the report to `output/intake_report.json`.

### Function Breakdown & Responsibilities
- **`validate_file_exists(filepath)`**: Verifies that the file exists and is not 0 bytes.
- **`validate_file_format(filepath, allowed_formats)`**: Validates file extension against allowed formats (default: `csv`, `json`, `xlsx`).
- **`validate_schema(df, expected_columns)`**: Checks if the file contains all expected columns, and flags any missing or extra columns.
- **`detect_encoding(filepath)`**: Automatically detects file encoding with confidence using `chardet` to avoid decoding errors during file reads.
- **`capture_dataset_stats(filepath, df)`**: Captures baseline dimensions like row count, column count, and file size in MB and bytes.
- **`generate_intake_report(filepath, expected_columns)`**: Aggregates all validation steps and stats into a structured JSON report.

### How to Adapt for New Datasets
1. **Change Expected Columns**: Update the `EXPECTED_COLUMNS` list at the top of `scripts/validate_intake.py` to match the schema of your new raw data.
2. **Configure Paths**: Update `sample_file` in the main execution block to point to the new raw data source path.

---

## 7. Multi-Format Data Ingestion (`scripts/ingest_data.py`)

This module enables robust ingestion of raw business datasets in multiple formats (CSVs with varying delimiters/encodings, structured JSON, flattened/nested files) into Pandas DataFrames.

### How to Execute the Ingestion Script
Run the ingestion script from the project root:

```bash
python scripts/ingest_data.py
```

This loads raw files from `data/raw/customers.csv` and `data/raw/transactions.json`, processes them, and saves the cleaned tabular results into the `data/processed/` folder.

### Function Breakdown & Responsibilities
- **`ingest_csv(filepath, delimiter, encoding, dtype_dict)`**: Loads a CSV file using explicit, documented parsing arguments. Handles FileNotFoundError and logs dimensions.
- **`ingest_json(filepath, is_nested)`**: Loads a JSON file. If `is_nested=True`, it uses `pd.json_normalize()` to flatten nested structures (e.g., `{'info': {'name': 'Alice'}}` becomes column `info.name`).
- **`ingest_csv_with_fallback(filepath, delimiters, fallback_encodings)`**: Sequentially attempts combinations of separators (e.g. `,`, `;`, `\t`) and character sets (e.g. `utf-8`, `latin-1`, `cp1252`) if default decoding fails.
- **`document_ingestion(df, source_file)`**: Prints an audit log report for the team, documenting rows, columns, column data types, missing/null counts, and a 3-row preview.

### How to Modify for New Datasets
1. **Add Ingestion Steps**: Add new calls to `ingest_csv` or `ingest_json` in the script's `__main__` execution block.
2. **Configure File Paths**: Set the raw input paths and processed output target folders.
3. **Specify Data Types**: Create a `dtype_dict` mapping column names to target pandas datatypes (e.g. `{'customer_id': 'int64'}`) to ensure consistent database keys.

---

## 8. Missing Value Imputation Strategy (`scripts/handle_missing.py`)

This module manages missing data by analyzing null distributions and applying domain-appropriate imputation strategies. It guarantees that downstream mathematical calculations and model training run on complete datasets.

### How to Execute the Imputation Script
Run the imputation script from the project root:

```bash
python scripts/handle_missing.py
```

This reads the raw dataset from `data/raw/missing_data.csv`, treats missing values, generates a decision log at `output/imputation_decisions.json`, and exports the final cleaned dataset to `data/processed/cleaned_data.csv`.

### Imputation Rules & Selection Criteria
- **Row Dropping (`drop_rows_with_nulls`)**: Applied to critical key identifier columns (e.g. `customer_id`, `email`). Imputing identifiers introduces fake records and corrupts joins.
- **Median/Mean Imputation (`impute_mean_median`)**: Applied to numerical columns (e.g. `amount`, `quantity`). Median is preferred for highly skewed distributions to prevent outlier bias.
- **Mode Imputation (`impute_mode`)**: Applied to categorical columns (e.g. `category`, `region`), filling nulls with the most frequent value.
- **Forward-Fill (`impute_forward_fill`)**: Applied to sequential/time-series data (e.g. `last_updated`), propagating the last known state forward.

### Auditing & Validation
- **Imputation Decisions Log (`output/imputation_decisions.json`)**: Tracks every column, strategy used, value imputed, and business reasoning for auditing.
- **Comparison Validation Report**: Prints a terminal report detailing total rows before/after, rows removed, and final null percentages.

### How to Customize for New Columns
1. **Update Pipeline Calls**: Modify column parameters in the main execution block of `scripts/handle_missing.py`.
2. **Update Imputation Decisions**: Add entries in the `document_imputation_decisions` function mapping columns to their business justification.

---

## 9. Data Type Standardization (`scripts/enforce_types.py`)

This module enforces strict data types on raw datasets. Standardizing unstructured strings into clean datatypes prevents database join misalignments, numeric calculation errors, and parsing ambiguities.

### How to Execute the Type Enforcement Script
Run the script from the project root:

```bash
python scripts/enforce_types.py
```

This reads the untyped data from `data/raw/untyped_data.csv`, converts dates, currency formats, and boolean indicators, and saves the cleaned dataset to `data/processed/typed_data.csv`. It also writes a before/after audit report to `output/dtype_conversion_report.csv`.

### Type Standardisation Rules & Functions
- **Datetime Casting (`convert_string_dates_to_datetime`)**: Converts string representations to proper pandas datetimes. Always specify `date_format` to prevent date-parsing ambiguities (e.g. interpreting `01-02-2025` differently in US vs UK regions).
- **Currency Cleaning (`convert_currency_to_float`)**: Strips formatting symbols like `$` and `,` from currency columns and casts variables to `float64`, enabling downstream mathematical aggregations.
- **Boolean Flag Mapping (`convert_integers_to_boolean`)**: Maps integer binary flags (`0` and `1`) and text labels (`yes`, `no`, `true`, `false`) to native pandas booleans.
- **Conversion Audit (`compare_dtypes`)**: Evaluates columns before/after, generating `output/dtype_conversion_report.csv` listing column changes.

### How to Configure for New Columns
1. **Define Target Dtypes**: Modify parameters in the `__main__` execution block of `scripts/enforce_types.py`.
2. **Add Custom Mapping**: Extend `convert_integers_to_boolean` if your new dataset introduces non-standard binary flags (e.g. `active`/`inactive`).

---

## 10. Data Dictionary Mapping & Maintenance Strategy

This component establishes a single source of truth mapping technical data columns to stakeholder business definitions, KPI calculations, and structural relationships.

### Documentation Files
- **Data Dictionary CSV (`docs/data_dictionary.csv`)**: Tabular schema map listing technical formats, stakeholder descriptions, KPI contexts, and notes.
- **Data Dictionary Guide (`docs/DATA_DICTIONARY.md`)**: Comprehensive Markdown guide documenting details, KPI formulas, ambiguous renaming justifications, and column relationship equations.

### Maintenance Workflow for Future Updates
When new columns or datasets are introduced in future releases:
1. **Initiate Schema Review**: The product analyst or engineer proposes the new schema additions during design reviews.
2. **Standardize Naming**: Resolve and document naming ambiguities using clear business labels instead of generic abbreviations.
3. **Update Data Dictionary CSV**: Append new rows to `docs/data_dictionary.csv` defining types, descriptions, business meaning, and KPIs.
4. **Update Data Dictionary Guide**: Add sections to `docs/DATA_DICTIONARY.md` describing update frequencies, null-handling strategies, and mathematical column relationships.
5. **Periodic Audits**: Conduct quarterly reviews of the dictionary to ensure descriptions stay aligned with evolving CRM metrics.

---

## 11. String Cleaning Pipeline (`scripts/string_cleaning_pipeline.py`)

This module builds a reusable text standardization pipeline to clean, normalize, and consolidate text fields before analytical calculations. Standardizing strings prevents grouping and aggregation errors caused by trailing spaces or case differences.

### How to Execute the String Cleaning Pipeline
Run the script from the project root:

```bash
python scripts/string_cleaning_pipeline.py
```

This generates a synthetic dataset representing messy input entries (spaces, case variances, special characters), processes the data, displays a before/after value counts audit, runs edge-case tests, and saves the cleaned results to `data/processed/cleaned_strings.csv`.

### Key Cleaning Techniques
- **Whitespace Trimming (`strip_all_strings`)**: Trims leading and trailing spaces from all string columns to resolve spacing-based duplication.
- **Casing Normalization (`normalize_casing`)**: Normalizes categorical columns to lowercase or uppercase so that entries like `John` and `JOHN` merge into a single unique value.
- **Special Characters Strip (`remove_special_characters`)**: Applies regex filter `[^a-zA-Z0-9 ]` to remove non-alphanumeric noise (e.g. converting `São Paulo` to `So Paulo` and `Montréal` to `Montral`).
- **Category Map Consolidation**: Translates spelling variances and abbreviations (e.g., `sme`, `smb`, `small medium enterprise`) into canonical labels (`SMB`) using mapping dictionaries.
- **Null Safety (`clean_text_column`)**: Integrates NaN/null detection and warning messages while preserving missing records during cleaning.

### Customizing for New Columns
1. **Define New Mapping Keys**: Add entry groups in the configuration dictionary in `scripts/string_cleaning_pipeline.py`.
2. **Toggle Parameters**: Adjust `lowercase`, `strip`, `remove_special`, or `mapping` flags in `clean_text_column` to configure the cleaning level per column.

---

## 12. Datetime Feature Engineering (`scripts/datetime_feature_engineering.py`)

This module processes raw transaction dates into proper Pandas datetime64 values and extracts multiple temporal dimensions to enable time-series aggregations, trend analysis, and recency-based churn modeling.

### How to Execute the Datetime Feature Engineering Script
Run the script from the project root:

```bash
python scripts/datetime_feature_engineering.py
```

This generates a 130-week synthetic transaction dataset, parses date strings using explicit formatting patterns, extracts temporal features, resamples weekly sales metrics, calculates customer recency, generates day-of-week x hour aggregation pivot tables, and exports an additive seasonal decomposition plot to `output/datetime_decomposition.png`.

### Core Engineering Operations
- **Explicit Datetime Parsing (`parse_timestamp_explicit`)**: Standardizes date strings to datetime64 structures using explicit format variables (e.g. `%Y-%m-%d %H:%M:%S`). This prevents regional date-parsing ambiguities.
- **Feature Extraction (`extract_temporal_features`)**: Extracts the day of the week, hour of the day (0-23), and ISO week numbers to evaluate transaction volumes and identify busy times.
- **Weekly Resampling**: Groups and sums transaction amounts into weekly buckets (`resample('W')`) to identify long-term business performance trends.
- **Customer Recency calculation (`compute_recency_metric`)**: Evaluates the number of days since each customer's last purchase. Recency metrics are vital indicators for churn-prediction systems.
- **Multi-dimensional Heatmap Aggregation (`build_time_indexed_aggregation`)**: Summarizes transaction counts and values grouped by day of the week and hour, identifying peak activity windows.
- **Seasonal Decomposition**: Decomposes weekly revenue into Trend, Seasonal, and Residual components using statsmodels to help identify repeating business patterns.

### How to Configure for New Datasets
1. **Change Input Timestamp columns**: Update target column parameters in the main execution block of `scripts/datetime_feature_engineering.py`.
2. **Configure Parsing Formats**: Adjust the format string to match your input dates (e.g., `%d/%m/%Y %H:%M:%S` for European formats).
3. **Change Resampling Frequency**: Modify the resampling argument (e.g., `'D'` for daily, `'M'` for monthly) depending on reporting needs.

---

## 13. Outlier Detection and Handling Strategy (`scripts/handle_outliers.py`)

This module manages extreme numerical anomalies and unfeasible inputs (e.g., revenue of $50,000 when typical is $500, or age values of 155) using statistical detection thresholds, capping/Winsorization bounds, binary anomaly flags, and an audit trail.

### How to Execute the Outlier Handling Script
Run the script from the project root:

```bash
python scripts/handle_outliers.py
```

This reads raw numerical inputs from `data/raw/outlier_data.csv`, evaluates anomalies, caps boundary values, appends a combined binary anomaly flag `is_outlier`, exports cleaned results to `data/processed/outliers_treated.csv`, and logs transformation decisions in `output/cleaning_log.csv`.

### Statistical Outlier Methods & Selection Criteria
- **Z-Score Detection (`detect_outliers_zscore`)**: Measures how many standard deviations ($\sigma$) a value lies from the mean ($\mu$). Effective for normally distributed data ($\text{Threshold} = \pm 3.0$).
- **IQR Detection (`detect_outliers_iqr`)**: Calculates the Interquartile Range ($\text{IQR} = Q_3 - Q_1$) and flags values below $Q_1 - 1.5 \times \text{IQR}$ or above $Q_3 + 1.5 \times \text{IQR}$. Highly robust for right-skewed or heavy-tailed distributions.
- **Capping / Winsorization (`cap_outliers`)**: Replaces values outside boundary limits with upper and lower thresholds (`.clip()`), preserving data records without distorting statistical metrics.
- **Binary Flagging (`flag_combined_outliers`)**: Creates an `is_outlier` boolean column combining Z-score and IQR flags, enabling downstream analytics to filter or weight records dynamically.
- **Transformation Audit (`create_cleaning_log`)**: Saves transformation logs to `output/cleaning_log.csv` detailing target columns, methods used, threshold limits, and affected row counts.

### How to Configure for New Columns
1. **Add Target Columns**: Include new columns in the processing pipeline of `scripts/handle_outliers.py`.
2. **Select Detection Method**: Choose IQR for skewed metrics (e.g., spend, transaction size) or Z-score for symmetric normal metrics.
3. **Adjust Multiplier**: Increase the IQR multiplier (e.g., to $3.0 \times \text{IQR}$) to isolate extreme outliers while keeping mild anomalies intact.

---

## 14. Data Quality and Business Rule Validation (`scripts/validate_rules.py`)

This module enforces domain-specific validation constraints across incoming data records prior to downstream pipeline execution. It validates numerical ranges, null constraints, string formats, and multi-column temporal business rules, isolating failure records for investigation.

### Validation vs. Data Cleaning
- **Data Validation**: Evaluates data against strict logical rules, generating boolean assertions. Invalid records are quarantined to prevent corrupted assumptions from entering the pipeline.
- **Data Cleaning**: Modifies or imputes values (e.g. capping outliers, stripping whitespace) to transform malformed records into valid formats.

### How to Execute the Validation Script
Run the script from the project root:

```bash
python scripts/validate_rules.py
```

This reads test inputs from `data/raw/quality_test.csv`, evaluates validation rules, exports isolated failure records to `output/validation_failures.csv`, and outputs clean records to `data/processed/validated_clean_data.csv`.

### Rule Categories & Functions
- **Range Checks (`validate_range_checks`)**: Verifies numerical boundaries (e.g., $0 \le \text{age} \le 150$, $\text{price} \ge 0$, and $\text{birth\_date} \le \text{today}$).
- **Null Constraints (`validate_null_constraints`)**: Enforces mandatory entity keys (e.g., non-null `customer_id` and `email`).
- **Format Pattern Matching (`validate_format_patterns`)**: Validates regex formatting (e.g., presence of `@` in email and exact 10-digit phone strings `^\d{10}$`).
- **Business Rule Validation (`validate_business_rules`)**: Verifies multi-column relational logic (e.g. $\text{end\_date} \ge \text{start\_date}$).
- **Failure Isolation (`generate_validation_report`)**: Aggregates boolean checks (`passes_all_checks`), quarantines failed rows into `output/validation_failures.csv`, and outputs clean records.

### How to Add New Validation Rules
1. **Define Validation Function**: Add a new function in `scripts/validate_rules.py` returning a boolean Series column (e.g., `valid_discount`).
2. **Register in Summary List**: Add the new boolean column to the `validation_cols` list in `generate_validation_report`.

---

## 15. Relational Data Merging and Join Validation (`scripts/merge_datasets.py`)

This module executes relational merges across entity datasets (e.g. combining 1,000 customer records with 5,000 transaction orders on `customer_id`), validates row count deltas, detects unmatched keys, evaluates join strategies, prevents column name collisions, and exports structured join decision logs.

### How to Execute the Merging Script
Run the script from the project root:

```bash
python scripts/merge_datasets.py
```

This reads/generates input files `data/raw/customers_merge.csv` and `data/raw/orders_merge.csv`, performs explicit Left Join merging, isolates unmatched customer keys and orphaned orders into `output/unmatched_customers.csv` and `output/unmatched_orders.csv`, writes an audit report to `output/join_report.json`, and exports the clean merged dataset to `data/processed/merged_customer_orders.csv`.

### Key Join Concepts & Functions
- **Explicit Join & Row Count Validation (`execute_explicit_join`)**: Merges tables explicitly on key parameters (`pd.merge(df_left, df_right, on='customer_id', how='left')`). Calculates and logs row count deltas ($\text{Result Rows} - \text{Left Rows}$) to detect unintended record duplication or unexpected loss.
- **Unmatched Key Diagnostics (`detect_unmatched_keys`)**: Identifies records present in one table but missing in the other using `.isin()` filters. Exports unmatched left entities (customers with zero orders) and orphaned right entities (orders with unmapped customer IDs).
- **Join Strategy Comparison (`compare_join_types`)**: Evaluates record counts across the 4 fundamental join types:
  - **Inner Join**: Returns only matching keys present in both tables.
  - **Left Join**: Preserves all left table records regardless of matches.
  - **Right Join**: Preserves all right table records regardless of matches.
  - **Outer Join**: Preserves all records from both tables, filling missing fields with NaN.
- **Duplication & Suffix Collision Prevention (`validate_column_duplication`)**: Inspects merged column headers for `_x` and `_y` suffix collisions caused by non-key duplicate column names and calculates key cardinality (`value_counts()`).
- **Join Audit Logging (`document_join_decision`)**: Exports a structured JSON audit report (`output/join_report.json`) recording table names, join types, row counts, unmatched counts, and business reasoning.

### How to Configure for New Datasets
1. **Change Input Files**: Update raw data paths in `scripts/merge_datasets.py`.
2. **Set Target Join Keys**: Modify `join_key` (or pass multi-key lists `on=['customer_id', 'region']`).
3. **Configure Join Strategy**: Change the `how` parameter (`left`, `inner`, `outer`) depending on whether missing matches must be retained or dropped.

---

## 16. Business Feature Engineering & Customer Segmentation (`scripts/engineer_features.py`)

This module transforms raw operational variables (counts, days, totals) into contextual business features through time/volume ratio normalization, fixed & quantile binning (`pd.cut` & `pd.qcut`), and composite RFM health scoring.

### How to Execute the Feature Engineering Script
Run the script from the project root:

```bash
python scripts/engineer_features.py
```

This reads/generates input metrics from `data/raw/customer_activity.csv`, computes ratio features, segments customers into categorical tiers, aggregates RFM scores, exports processed records to `data/processed/engineered_features.csv`, and writes an audit summary to `output/feature_engineering_report.json`.

### Feature Types & Engineering Principles
- **Ratio Features (`create_ratio_features`)**: Normalizes raw counts against time or volume dimensions to extract true behavioral signals:
  - `transactions_per_month` = `total_transactions / (days_as_customer / 30.0)`
  - `avg_spend_per_transaction` = `total_spent / total_transactions`
  - `lifetime_value_per_month` = `total_spent / (days_as_customer / 30.0)`
- **Equal-Width Binning (`pd.cut`)**: Categorizes continuous metrics into predefined business thresholds (e.g. `engagement_bin_equal`: `low` [0-2], `medium` [2-10], `high` [>10]).
- **Equal-Frequency Quantile Binning (`pd.qcut`)**: Segments continuous metrics into balanced quantile groups (e.g. `spend_tier_quantile`: 4 equal-sized quartiles `tier_1` to `tier_4`).
- **Composite RFM Scoring (`compute_rfm_composite_score`)**: Constructs an integrated customer health score by combining 5-quantile Recency, Frequency, and Monetary scores (`rfm_score = recency_score + frequency_score + monetary_score`).
- **Feature Audit Logging (`export_feature_report`)**: Writes a structured JSON summary report (`output/feature_engineering_report.json`) recording ratio feature statistics, tier distributions, and RFM score metrics.

### How to Configure for New Datasets
1. **Change Input Features**: Update column references in `scripts/engineer_features.py` to target your dataset's activity metrics.
2. **Adjust Bin Boundaries**: Modify threshold lists in `pd.cut()` to match domain business rules (e.g., custom engagement thresholds).
3. **Customize Quantiles**: Change `q` parameter in `pd.qcut()` (e.g. `q=5` for quintiles or `q=10` for deciles).

---

## 17. High-Performance Vectorized Operations & Benchmarking (`scripts/vectorized_performance.py`)

This module replaces slow Python iterative loops (`for` loops and `.apply()`) with C-compiled NumPy array vectorization. It executes Min-Max and Z-Score normalizations across 100,000+ records, measures timing benchmarks, computes speedup multipliers, and integrates optimized arrays back into Pandas DataFrames.

### How to Execute the Performance Optimization Script
Run the script from the project root:

```bash
python scripts/vectorized_performance.py
```

This reads/generates input metrics from `data/raw/large_revenue_dataset.csv` (100,000 records), compares Python loop execution vs. NumPy array vectorization, exports optimized features to `data/processed/vectorized_optimized_features.csv`, and logs performance metrics in `output/performance_benchmark_report.json`.

### Core Vectorization Principles & Functions
- **Interpreter Overhead Elimination**: Python loops call the interpreter for every row, compounding execution latency. NumPy operates on contiguous C-memory blocks in a single parallelized operation.
- **Vectorized Min-Max Normalization (`min_max_normalize_vectorized`)**: Normalizes numerical metrics to $[0, 1]$ using element-wise array math: `(revenue_array - revenue_array.min()) / (revenue_array.max() - revenue_array.min())`.
- **Vectorized Z-Score Normalization (`z_score_normalize_vectorized`)**: Standardizes numerical metrics to mean 0 and standard deviation 1: `(revenue_array - revenue_array.mean()) / revenue_array.std()`.
- **Performance Benchmarking (`benchmark_performance`)**: Uses `time.time()` to measure execution duration across 100,000 records, calculating the speedup factor ($\text{Loop Time} / \text{Vectorized Time}$, achieving 20x+ speedups).
- **Benchmark Audit Reporting (`export_benchmark_report`)**: Writes a structured JSON summary (`output/performance_benchmark_report.json`) detailing record counts, execution times in seconds, and speedup ratios.

### How to Configure for New Columns
1. **Change Numerical Target Columns**: Update `column` parameters in `scripts/vectorized_performance.py` (e.g., `transaction_count`).
2. **Apply Custom Vectorized Formulas**: Use NumPy mathematical functions (e.g. `np.log1p()`, `np.where()`) for element-wise array operations.

---

## 18. Distribution Analysis & Statistical Profiling (`scripts/analyze_distributions.py`)

This module evaluates the statistical distribution shape of customer revenue and activity metrics. It calculates skewness and kurtosis parameters, determines when medians are superior to means, exports Histogram & KDE density plots, and compares High-Value vs. Low-Value customer spend distributions.

### How to Execute the Distribution Analysis Script
Run the script from the project root:

```bash
python scripts/analyze_distributions.py
```

This reads/generates bimodal revenue inputs from `data/raw/bimodal_revenue_dataset.csv` (5,000 records), calculates statistical moments, exports distribution plots to `output/distribution_plots.png` and segment comparisons to `output/segment_distribution_comparison.png`, writes clean data to `data/processed/distribution_analyzed_data.csv`, and outputs an audit report to `output/distribution_analysis_report.json`.

### Statistical Concepts & Visual Methods
- **Skewness & Central Tendency (`compute_distribution_statistics`)**: Measures asymmetry using `scipy.stats.skew`. Positive skew ($> +1.0$) indicates that a small cluster of high-value enterprise accounts pulls up the mean (e.g. Mean $\$5,315.87$ vs Median $\$393.13$). In skewed distributions, the median represents true typical customer spend.
- **Kurtosis & Tail Risk**: Measures tail weight using `scipy.stats.kurtosis`. High excess kurtosis ($> 3.0$) indicates leptokurtic distributions where extreme financial outliers are prevalent.
- **Histogram & KDE Density Plotting (`plot_distribution_shape`)**: Renders combined equal-width histograms and Kernel Density Estimates (`sns.histplot(..., kde=True)`), adding mean/median benchmark lines to visually demonstrate distribution pull.
- **Segment Distribution Comparisons (`plot_segment_comparison`)**: Partitions customers into High-Value ($\ge Q_3$) and Low-Value ($\le Q_1$) tiers and plots overlapping KDE density curves to evaluate cohort differences.
- **Statistical Audit Logging (`export_distribution_report`)**: Saves a structured JSON report (`output/distribution_analysis_report.json`) recording statistical moments, skewness/kurtosis interpretations, and segment distributions.

### How to Configure for New Columns
1. **Target Feature Columns**: Update `column` parameters in `scripts/analyze_distributions.py` (e.g. `total_transactions`).
2. **Adjust Segment Percentiles**: Modify quantile thresholds for segment comparisons (e.g. 90th percentile for top enterprise tiers).

---

## 19. Feature Correlation Analysis & Feature Selection (`scripts/analyze_correlations.py`)

This module evaluates relationships across numerical features and target labels (e.g. customer churn). It calculates Pearson (linear) and Spearman (rank monotonic) correlation matrices, renders annotated heatmaps, isolates collinear feature pairs ($|r| > 0.7$), performs business causation analysis to avoid spurious conclusions, and drops redundant features.

### How to Execute the Correlation Script
Run the script from the project root:

```bash
python scripts/analyze_correlations.py
```

This reads/generates churn customer inputs from `data/raw/churn_customer_data.csv` (1,000 records), calculates Pearson and Spearman correlation matrices, renders a correlation heatmap to `output/correlation_heatmap.png`, performs causation analysis, drops redundant collinear variables (`engagement` when $r=0.92$ with `transactions_per_month`), exports clean feature sets to `data/processed/selected_uncorrelated_features.csv`, and writes an audit summary to `output/correlation_analysis_report.json`.

### Correlation Principles & Causation vs. Correlation
- **Pearson vs. Spearman (`compute_pearson_spearman`)**:
  - **Pearson ($r$)**: Measures linear relationships between continuous variables.
  - **Spearman ($\rho$)**: Measures monotonic relationships using rank order, making it robust against non-linear trends and extreme outliers.
- **Correlation Heatmap Matrix (`plot_correlation_heatmap`)**: Uses `seaborn` (`sns.heatmap(..., annot=True, cmap='coolwarm', center=0)`) to render visual color gradients highlighting positive and negative feature associations.
- **Collinearity & Redundancy Isolation (`find_strong_correlations`)**: Isolates feature pairs where $|r| > 0.7$. Highly correlated features (e.g. `engagement` vs `transactions_per_month` at $r=0.92$) introduce multi-collinearity issues in predictive models.
- **Causation Confounder Analysis (`perform_causation_analysis`)**: Distinguishes correlation from causation. For example, `support_tickets` correlates $r=0.8$ with `churn`, but tickets do not cause churn—underlying `customer_pain` causes both support tickets and churn.
- **Feature Selection (`select_uncorrelated_features`)**: Drops redundant collinear variables while preserving the most interpretable metrics, exporting clean datasets to `data/processed/selected_uncorrelated_features.csv`.

### How to Configure for New Columns
1. **Target Label Selection**: Modify `target_col` in `scripts/analyze_correlations.py` (e.g., `churn` or `lifetime_value`).
2. **Adjust Collinearity Threshold**: Change `threshold` parameter in `find_strong_correlations()` (e.g., set to $0.8$ or $0.85$).

---

## 20. Python Streamlit Interactive Analytics Dashboard (`app.py`)

The `app.py` module is the main Streamlit web dashboard for GitGuide Analytics. It provides four interactive pages:

- **🏠 Home / Upload Page**: Dataset overview, contributor KPI metrics, activity chart.
- **📊 Dashboard Analytics**: PR review timeline histogram, commit distribution, contributor role pie chart.
- **🔍 Data Explorer**: Interactive filterable data table with CSV export capability.
- **💡 Business Insights**: Key findings—churn risk profiles, top contributors, reviewer bottlenecks.

### How to Start the Dashboard
```bash
streamlit run app.py
```

### Dataset Loading Priority
1. **Live GitHub URL** → fetched and cached at `data/raw/fetched_github_repo_data.csv`
2. **Manual CSV Upload** → via Streamlit sidebar file uploader
3. **Default project dataset** → from `output/processed.csv` or `data/raw/sample.csv`

---

## 21. Live GitHub Repository URL Ingestion & CSV Auto-Creation (`scripts/github_repo_ingestion.py`)

This module enables GitGuide Analytics to accept any public GitHub repository URL or `owner/repo` slug, fetch live contributor activity, PR review timelines, and commit history using the GitHub REST API, and generate a fully structured CSV dataset that feeds directly into the analytics dashboard.

### Architecture

```
GitHub REST API  →  github_repo_ingestion.py  →  data/raw/fetched_github_repo_data.csv
                                                →  data/processed/fetched_github_repo_processed.csv
                                                →  output/github_ingestion_report.json
```

### Fetched Data Categories

| Category | GitHub API Endpoint | Fields Captured |
|---|---|---|
| Commits | `/repos/{owner}/{repo}/commits` | sha, author login, message, timestamp |
| Pull Requests | `/repos/{owner}/{repo}/pulls` | PR number, title, state, review days, lines changed |
| Contributors | `/repos/{owner}/{repo}/contributors` | login, contributions count, role estimate |
| Repo Metadata | `/repos/{owner}/{repo}` | stars, forks, full name |

### Authentication & Rate Limits
- **Without token**: 60 requests/hour (public IP rate limit)
- **With token** (recommended): 5,000 requests/hour

Set your GitHub Personal Access Token via the `GITHUB_TOKEN` environment variable:
```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "ghp_your_token_here"
python scripts/github_repo_ingestion.py Msush3005/GitGuide-Analytics-
```

### Supported Input Formats
```bash
# Full URL
python scripts/github_repo_ingestion.py https://github.com/facebook/react

# Owner/repo slug
python scripts/github_repo_ingestion.py Msush3005/GitGuide-Analytics-
```

### Streamlit Dashboard Integration
The Streamlit sidebar includes a **"🔗 Live GitHub Repository"** text input and **"🚀 Fetch Live GitHub Data"** button. When clicked:
1. `generate_csv_from_github_api()` is called with the provided URL.
2. Data is saved to `data/raw/fetched_github_repo_data.csv`.
3. The dashboard refreshes automatically with the live data.
4. On subsequent visits, the previously fetched CSV is auto-loaded.

### Generated Outputs

| File | Description |
|---|---|
| `data/raw/fetched_github_repo_data.csv` | Raw merged contributor + PR dataset |
| `data/processed/fetched_github_repo_processed.csv` | Processed, cleaned copy for pipeline |
| `output/github_ingestion_report.json` | Audit report: timestamps, record counts, API stats |

### How to Configure for New Repositories
1. **Change max items**: Set `max_items` parameter in `generate_csv_from_github_api()` (default: 100 per category).
2. **Add new API fields**: Extend the dictionaries in `fetch_github_repo_metrics()` with any additional GitHub REST API response fields.
3. **Set authentication**: Always set `GITHUB_TOKEN` for private repos or high-volume ingestion.













