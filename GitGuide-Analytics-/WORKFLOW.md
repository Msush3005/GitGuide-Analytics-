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








