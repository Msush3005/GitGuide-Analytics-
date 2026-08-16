# 🔭 GitGuide Analytics — Real-Time KPI Dashboard & Pipeline System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![CI/CD Pipeline](https://github.com/Msush3005/GitGuide-Analytics-/actions/workflows/pipeline.yml/badge.svg)](https://github.com/Msush3005/GitGuide-Analytics-/actions)
[![Data Validation](https://github.com/Msush3005/GitGuide-Analytics-/actions/workflows/validate.yml/badge.svg)](https://github.com/Msush3005/GitGuide-Analytics-/actions)

An end-to-end operational analytics platform and interactive Streamlit dashboard designed to monitor open-source developer velocity, pull request turnaround SLA, contributor retention, and code volume. Features automated data pipeline execution, schema contract validation, threshold alert detection, and email report delivery.

---

## 📌 1. Project Overview

**GitGuide Analytics** solves the operational challenge of tracking contributor engagement and pull request latency in software engineering organizations. By transforming raw GitHub repository event streams into actionable KPIs, interactive visualizations, and automated executive reports, leadership and engineering managers can identify onboarding friction, eliminate review bottlenecks, and prevent developer drop-off before productivity suffers.

---

## 📊 2. Dataset Description

- **Data Sources**: Live GitHub API REST endpoints, local CSV/JSON file uploads, or scheduled pipeline runs.
- **Refresh Frequency**: Weekly automated pipeline runs via GitHub Actions cron, plus live interactive file uploads in the Streamlit app.
- **Core Schema**:
  - `contributor_id` (*integer*): Unique identifier for open-source contributors.
  - `contributor_login` (*string*): GitHub username handle.
  - `repository_name` (*string*): Target GitHub repository name.
  - `commits_count` (*integer*): Number of committed commits per contributor.
  - `pull_requests_opened` (*integer*): Count of opened pull requests.
  - `total_contributions` (*integer*): Aggregate sum of commits and pull requests.
  - `lines_changed` (*integer*): Total lines of code added or modified.
  - `contributor_role` (*string*): Role classification (`Maintainer`, `Reviewer`, `Contributor`).
  - `pr_review_days` (*float*): Average pull request review turnaround in days.
  - `timestamp` (*string / YYYY-MM-DD*): Event creation timestamp.

---

## ⚡ 3. Setup & Getting Started

Follow these 5 simple steps to launch the platform locally in under 5 minutes:

### 1. Clone the Repository
```bash
git clone https://github.com/Msush3005/GitGuide-Analytics-.git
cd GitGuide-Analytics-
```

### 2. Create & Activate Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional for Email Delivery)
```bash
cp .env.example .env
# Open .env and add SENDER_EMAIL and SENDER_PASSWORD if sending email reports
```

### 5. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
*Access the live web app in your browser at `http://localhost:8501`.*

---

## ⚙️ 4. Pipeline & System Architecture

### Data Flow Diagram
```
  +-----------------------+
  |  Raw CSV / JSON Data  |
  +-----------------------+
              |
              v
  +-----------------------+
  |  Stage 1: Ingestion   |  <-- Ingest raw records via pipeline.py or st.file_uploader
  +-----------------------+
              |
              v
  +-----------------------+
  |  Stage 2: Cleaning    |  <-- Drop missing IDs, coerce numeric types, validate schema
  +-----------------------+
              |
              v
  +-----------------------+
  | Stage 3: Aggregation  |  <-- Group by role/segment, compute velocity metrics
  +-----------------------+
              |
              v
  +-----------------------+
  |   Stage 4: Output     |  <-- Write cleaned_data.csv & aggregated_metrics.csv
  +-----------------------+
              |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
      +---------------+   +---------------+   +---------------+
      | Streamlit App |   | Alert Engine  |   | Email Delivery|
      |  (Dashboard)  |   | (st.error/warn|   | (smtplib SSL) |
      +---------------+   +---------------+   +---------------+
```

### Stage Explanations
1. **Ingestion (`pipeline.py` / `parse_uploaded_bytes`)**: Loads CSV/JSON inputs into memory cached via `@st.cache_data`.
2. **Data Cleaning (`clean()`)**: Eliminates null records, validates data types, and ensures schema integrity.
3. **Aggregation (`aggregate()`)**: Computes segment summaries (`total_volume`, `avg_volume`, `avg_review_days`).
4. **Export & Storage (`output()`)**: Writes output CSV files to `output/` directory for downstream consumption.
5. **Interactive Dashboard (`app.py`)**: Renders reactive KPI metric cards, time-series line charts, role distribution pie charts, and Plotly histograms.
6. **Threshold Monitoring (`alert_config.py`)**: Evaluates computed metrics against operational limits (`single_commit_dropout > 30%`, `avg_pr_review_days > 3.0d`).
7. **Email Delivery (`report_generator.py` + `email_sender.py`)**: Formats 3-section executive summaries (`KPI SUMMARY`, `KEY FINDINGS`, `RECOMMENDED ACTIONS`) and delivers via SMTP.

---

## 📋 5. Derived Features & Metrics Reference

| Column / Metric Name | Data Type | Formula / Source | Description | Example Value |
|---|---|---|---|---|
| `single_commit_dropout` | `float` | `(count(commits == 1) / total_users) * 100` | Percentage of contributors who drop off after a single commit | `33.3%` |
| `avg_pr_review_days` | `float` | `mean(pr_review_turnaround_days)` | Average turnaround time in days to review and merge PRs | `2.8d` |
| `null_percentage` | `float` | `(null_cells / total_cells) * 100` | Percentage of unparsed or missing values in active dataset | `1.2%` |
| `data_quality_score` | `float` | `100.0 - null_percentage` | Operational data health and completeness score | `98.8%` |
| `avg_lines_changed` | `float` | `mean(lines_changed)` | Average code modification volume per pull request | `420.5` |
| `total_volume` | `integer` | `sum(commits_count)` | Aggregate commits or contributions in selected scope | `1,250` |

---

## ⚠️ 6. Known Limitations & Caveats

1. **Weekly Scheduled Refresh**: Pipeline refreshes automatically every Monday at 6:00 AM UTC via GitHub Actions. Dashboard data reflects the latest pipeline run or manually uploaded file (maximum staleness: 7 days).
2. **Static Alert Thresholds**: Operational thresholds in `alert_config.py` are static limits (e.g., 3.0 days for review turnaround) and do not currently adjust dynamically based on seasonal historical variance.
3. **SMTP Credential Dependency**: Email report delivery requires valid SMTP configuration in `.env`. If credentials are omitted, email sending is safely skipped without crashing the dashboard.
4. **Schema Contract Requirements**: The pipeline and validation script (`validate_data.py`) require primary ID (`contributor_login` / `customer_id`) and numeric volume fields (`commits_count` / `amount`).
5. **Self-Reported Role Classification**: Contributor segment metrics rely on categorical role fields; mid-year role transitions appear under the most recently assigned role.

---

## 🛠️ 7. Automated Testing & CI/CD Workflows

- **Data Validation Workflow** (`.github/workflows/validate.yml`): Executes `python validate_data.py` on every push and PR to verify schema contracts and block bad merges.
- **Weekly Pipeline Refresh Workflow** (`.github/workflows/pipeline.yml`): Runs `python pipeline.py` every Monday at 6:00 AM UTC to refresh data automatically.

---

## 👤 Author & Support
- **Author**: Msush3005
- **Repository**: [GitGuide-Analytics-](https://github.com/Msush3005/GitGuide-Analytics-)
- **License**: MIT