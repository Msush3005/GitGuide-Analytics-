# GitGuide Analytics – GitHub Contributor Analytics

## Project Description

GitGuide Analytics is a data analytics platform that helps open-source maintainers understand contributor onboarding and retention. It collects GitHub repository data such as pull requests, issues, contributors, and review timelines, processes the data, and presents meaningful insights through an interactive dashboard. The goal is to identify onboarding patterns that encourage or discourage first-time contributors from returning.

---

# Setup

## 1. Clone the repository

### macOS / Linux

```bash
git clone <repository-url>
cd GitGuide-Analytics
```

### Windows

```powershell
git clone <repository-url>
cd GitGuide-Analytics
```

---

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv .venv
```

### Windows

```powershell
python -m venv .venv
```

---

## 3. Activate the Virtual Environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 4. Install Dependencies

### macOS / Linux

```bash
pip install -r requirements.txt
```

### Windows

```powershell
pip install -r requirements.txt
```

---

## Project Structure

```
GitGuide-Analytics/
│
├── data/
│   Raw and processed datasets used for analysis.
│
├── notebooks/
│   Jupyter notebooks for exploration and experimentation.
│
├── src/
│   Core application source code.
│
│   ├── ingestion/
│   │   Fetches data from GitHub API or CSV files.
│   │
│   ├── preprocessing/
│   │   Cleans, validates, and transforms datasets.
│   │
│   ├── analytics/
│   │   Calculates KPIs and contributor analytics.
│   │
│   ├── database/
│   │   SQLite database connection and queries.
│   │
│   └── dashboard/
│       Streamlit dashboard application.
│
├── tests/
│   Unit tests for project modules.
│
├── requirements.txt
│   Python dependencies.
│
├── .env.example
│   Example environment variables.
│
├── README.md
│   Project documentation.
│
└── .gitignore
    Git ignore rules.
```

---

# Notes

This project requires environment variables to access the GitHub API and configure the database.

1. Copy the example environment file:

```bash
cp .env.example .env
```

Windows (PowerShell):

```powershell
copy .env.example .env
```

2. Open the newly created `.env` file.

3. Replace the placeholder values with your own credentials.

Required environment variables include:

- GitHub Personal Access Token
- GitHub API Base URL
- SQLite Database Path
- Streamlit Server Port
- Debug Mode

> **Important:** Never commit your `.env` file to GitHub. Only commit `.env.example`.
