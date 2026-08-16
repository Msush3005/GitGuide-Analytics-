# Analysis Export & Multi-Format Reporting Guide

> **System**: GitGuide Analytics Automated Reporting Subsystem  
> **Source Code**: `export_functions.py` | `streamlit_export_integration.py`  
> **Output Directory**: `output/YYYY-MM-DD_HHMM_analysis/`  

---

## 1. What's Included in Every Export Package

Each automated export package is generated into a timestamped directory (e.g., `output/2026-08-16_2015_analysis/`) containing four standardized artifacts:

```
output/2026-08-16_2015_analysis/
├── cleaned_data.csv         ← Excel-ready raw dataset
├── summary_report.pdf       ← Executive summary for leadership
├── interactive_report.html  ← Interactive browser report with Plotly charts
└── README.md                ← Export metadata & audit trail
```

---

### 📊 `cleaned_data.csv`
* **Purpose**: Raw, fully sanitized analysis dataset for further exploration in Excel or BI tools (PowerBI, Tableau).
* **Rows & Columns**: Ingested contributor rows (e.g., 50,000 records or active GitHub repo cohort) across columns `contributor_login`, `commits_count`, `contributor_role`, `pull_requests_opened`, `avg_pr_review_days`, `avg_lines_changed`, `repository_name`.
* **Use Case**: Stakeholders can filter, sort, build custom pivot tables, and conduct ad-hoc calculations.
* **Refresh Schedule**: Updated daily at 5:00 PM via automated daemon and on-demand via Streamlit dashboard.

---

### 📄 `summary_report.pdf`
* **Purpose**: Clean, printable executive summary designed for leadership meetings, board decks, and email distribution.
* **Content**: Executive Problem Statement, Key Findings, Risk Analysis, Quantified Recommendations, and Action Timelines.
* **Length & Format**: 1–2 pages, professional typography, brand-aligned purple/cyan palette, standalone readability without code.
* **Use Case**: Share directly with C-suite executives, attach to weekly status emails, or print for physical meetings.

---

### 🌐 `interactive_report.html`
* **Purpose**: Complete standalone interactive report featuring embedded Plotly visualizations.
* **Content**: Full executive narrative combined with interactive charts (Area commit trends, grouped bar charts, bubble scatter plots, donut charts, histograms, violin plots).
* **Size & Dependencies**: Single lightweight HTML file (~15–20 KB). Uses Plotly CDN — requires zero local Python or server setup to view.
* **Use Case**: Open in any browser (Chrome, Edge, Safari). Stakeholders can hover over data points for tooltips, zoom into specific date ranges, and toggle legend items.
* **Sharing**: Email as a standalone attachment — opens instantly on desktop or mobile browsers.

---

### 📝 `README.md` (Metadata File)
* **Purpose**: Auditable execution log and data provenance metadata.
* **Fields Captured**: Timestamp of generation, total record count, column schema list, and date range covered.

---

## 2. How Stakeholders Use These Files

| Stakeholder Role | Recommended File | Action |
|---|---|---|
| **VP / Executive** | `summary_report.pdf` | Read the 2-page PDF for high-level findings, financial ROI, and budget decision points. |
| **Data Analyst / Ops** | `cleaned_data.csv` | Open in Excel, build pivot tables, run ad-hoc filters, or load into PowerBI. |
| **Engineering Lead** | `interactive_report.html` | Open in browser, zoom into PR review cycle time distributions, and inspect contributor bottlenecks. |
| **Auditor / Devops** | `README.md` | Verify pipeline execution timestamp, dataset row counts, and schema validation flags. |

---

## 3. Refresh & Execution Options

### A. On-Demand Streamlit Export (One-Click)
1. Open the Streamlit dashboard (`streamlit run app.py`).
2. Navigate to the **📥 Automated Export** section in the left sidebar.
3. Click **🚀 Trigger Full Export (CSV + PDF + HTML)**.
4. Use the one-click download buttons to save `cleaned_data.csv`, `interactive_report.html`, or `summary_report.pdf` directly to your local computer.

### B. Scheduled Automation Daemon (Python `schedule`)
Run the background scheduler runner script:
```bash
python streamlit_export_integration.py
```
This registers a daily job scheduled at `17:00` (5:00 PM) that executes `export_analysis()`, generates fresh multi-format outputs, and logs verification metrics automatically.

### C. Linux/Mac Cron Integration
Add to crontab (`crontab -e`) to run every day at 5:00 PM:
```bash
0 17 * * * /usr/bin/python3 /path/to/GitGuide-Analytics-/streamlit_export_integration.py >> /path/to/export.log 2>&1
```

### D. Windows Task Scheduler Setup
Create a daily scheduled task running at 5:00 PM:
```powershell
schtasks /create /tn "GitGuide_Daily_Export" /tr "C:\Users\prasa\OneDrive\Desktop\GitGuide-Analytics-\venv\Scripts\python.exe C:\Users\prasa\OneDrive\Desktop\GitGuide-Analytics-\streamlit_export_integration.py" /sc daily /st 17:00
```

---

## 🎥 Video Demonstration Script (3-5 Minutes)

For video walkthrough submissions, follow this step-by-step demonstration outline:

1. **[0:00 - 0:45] Calling `export_analysis()` in Python**
   - Open terminal and run `python export_functions.py`.
   - Highlight the console output displaying `[OK]` checks for CSV, PDF, HTML, and README.md generation.
2. **[0:45 - 1:30] File Verification & Excel Inspection**
   - Open the generated `output/YYYY-MM-DD_HHMM_analysis/` folder.
   - Show file sizes and open `cleaned_data.csv` in Excel/VS Code to demonstrate clean columns and rows.
3. **[1:30 - 2:30] Interactive HTML & PDF Report Review**
   - Open `interactive_report.html` in Chrome/Edge. Demonstrate hovering over Plotly charts, zooming, and scrolling through the executive summary.
   - Open `summary_report.pdf` to show the printable PDF layout.
4. **[2:30 - 3:30] Streamlit One-Click Downloads**
   - Open the live Streamlit dashboard (`localhost:8501`).
   - Click **🚀 Trigger Full Export** in the sidebar.
   - Click **📊 Download Data (CSV)** and **🌐 Download Report (HTML)** to demonstrate browser download functionality.
5. **[3:30 - 5:00] Scheduled Job & Email Automation Concept**
   - Explain how `schedule.every().day.at("17:00")` runs `run_scheduled_export()` in the background.
   - Explain email automation enhancement (`smtplib` / SendGrid API): attaching `summary_report.pdf` and emailing it automatically to executive stakeholders every Friday at 5 PM.
