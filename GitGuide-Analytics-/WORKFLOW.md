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

## 9. NumPy Vectorised Computation Workflow (`scripts/vectorized_ops.py`)

This module replaces slow, iterative Python loops with high-performance NumPy vectorized computations for numerical transformations (normalization, scoring, ranking).

### Why Vectorization Over Python Loops
- **C-Level Performance**: NumPy operations run pre-compiled C loops without Python interpreter overhead per element.
- **Contiguous Memory Arrays**: Operates on contiguous memory blocks, leveraging CPU cache locality and SIMD (Single Instruction Multiple Data) hardware instructions.
- **Production Scalability**: Computes million-row datasets in milliseconds (20x to 3000x faster than standard Python loops).

### How to Execute the Script
Run the script from the project root:

```bash
python scripts/vectorized_ops.py
```

### Function Breakdown & Responsibilities
- **`generate_benchmark_dataset(num_rows, filepath)`**: Generates or loads a synthetic dataset of 100,000 revenue records.
- **`task1_min_max_normalization(df)`**: Applies `(arr - arr.min()) / (arr.max() - arr.min())` to scale revenue into the `[0, 1]` range.
- **`task2_z_score_normalization(df)`**: Applies `(arr - arr.mean()) / arr.std()` for standard score normal distribution (mean=0, std=1).
- **`task3_bulk_ranking(df)`**: Uses `np.argsort(-revenue_array)` to rank all records in descending revenue order in $O(N \log N)$ vector time.
- **`task4_time_performance_comparison(df)`**: Benchmarks Python loop execution vs NumPy vectorization using `time.time()` and reports speedup metrics.
- **`task5_integrate_back_to_dataframe(df, ...)`**: Assigns calculated NumPy arrays back to the Pandas DataFrame as new columns (`revenue_normalized`, `revenue_zscore`, `revenue_rank`) and verifies shapes and dtypes.

