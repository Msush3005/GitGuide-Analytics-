"""
Live GitHub Repository URL Ingestion & CSV Auto-Creation Pipeline
GitGuide-Analytics

Accepts any public GitHub repository URL or slug (e.g. https://github.com/facebook/react or owner/repo).
Fetches live commits, pull requests, contributors, and review timeline data from the GitHub REST API.
Generates a standardized structured CSV dataset compatible with the GitGuide Analytics dashboard.

Usage:
    python scripts/github_repo_ingestion.py Msush3005/GitGuide-Analytics-
    python scripts/github_repo_ingestion.py https://github.com/facebook/react
"""

import os
import sys
import json
import re
import time
import urllib.request
import urllib.error
import urllib.parse
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# GitHub API base URL
GITHUB_API_BASE = "https://api.github.com"

# Optional: set GITHUB_TOKEN env variable to increase rate limit (5000/hr vs 60/hr)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def parse_github_url(url_or_slug):
    """
    Extract owner and repo name from a GitHub URL or owner/repo slug.

    Accepts:
        - https://github.com/facebook/react
        - https://github.com/facebook/react/tree/main
        - facebook/react

    Returns:
        tuple: (owner, repo)
    """
    url_or_slug = url_or_slug.strip().rstrip("/")

    # Match full GitHub URL
    match = re.search(r"github\.com/([^/]+)/([^/?\s]+)", url_or_slug)
    if match:
        owner = match.group(1)
        repo = match.group(2).split(".git")[0]
        return owner, repo

    # Match owner/repo slug
    if "/" in url_or_slug and not url_or_slug.startswith("http"):
        parts = url_or_slug.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1].split(".git")[0]

    raise ValueError(f"Could not parse GitHub repo from: '{url_or_slug}'")


def _github_request(endpoint, max_items=100):
    """
    Execute paginated GitHub REST API GET request.

    Args:
        endpoint (str): API endpoint path (e.g. /repos/owner/repo/commits).
        max_items (int): Maximum number of items to fetch across pages.

    Returns:
        list: Combined response items from all pages.
    """
    results = []
    per_page = min(max_items, 100)
    page = 1

    while len(results) < max_items:
        url = f"{GITHUB_API_BASE}{endpoint}?per_page={per_page}&page={page}&state=all"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "GitGuide-Analytics/1.0")
        if GITHUB_TOKEN:
            req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")

        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                data = json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print("⚠️  GitHub API rate limit reached. Set GITHUB_TOKEN env variable to increase limit.")
            elif e.code == 404:
                print(f"⚠️  Repository not found or private: {endpoint}")
            return results
        except Exception as e:
            print(f"⚠️  API request failed: {e}")
            return results

        if not data or not isinstance(data, list):
            break

        results.extend(data)

        if len(data) < per_page:
            break

        page += 1
        time.sleep(0.3)  # Respect GitHub rate limits

    return results[:max_items]


def fetch_github_repo_metrics(owner, repo, max_items=100):
    """
    Fetch live contributor commits, pull requests, and repo metadata from GitHub REST API.

    Args:
        owner (str): GitHub repository owner.
        repo (str): GitHub repository name.
        max_items (int): Max items to fetch per category.

    Returns:
        tuple: (commits_df, prs_df, contributors_df, repo_meta)
    """
    print(f"\n📡 Fetching GitHub Repository: {owner}/{repo}")

    # 1. Repo metadata
    try:
        meta_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        req = urllib.request.Request(meta_url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("User-Agent", "GitGuide-Analytics/1.0")
        if GITHUB_TOKEN:
            req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")
        with urllib.request.urlopen(req, timeout=15) as res:
            repo_meta = json.loads(res.read().decode("utf-8"))
        print(f"  ✓ Repository: {repo_meta.get('full_name')} | Stars: {repo_meta.get('stargazers_count', 0):,} | Forks: {repo_meta.get('forks_count', 0):,}")
    except Exception as e:
        print(f"  ⚠️  Could not fetch repo metadata: {e}")
        repo_meta = {"full_name": f"{owner}/{repo}", "stargazers_count": 0, "forks_count": 0}

    # 2. Commits
    print(f"  📥 Fetching commits (up to {max_items})...")
    commits_raw = _github_request(f"/repos/{owner}/{repo}/commits", max_items=max_items)
    commits_rows = []
    for c in commits_raw:
        author = c.get("commit", {}).get("author", {})
        committer = c.get("author") or {}
        commits_rows.append({
            "sha": c.get("sha", "")[:7],
            "contributor_login": committer.get("login", "unknown"),
            "commit_message": c.get("commit", {}).get("message", "")[:60],
            "timestamp": author.get("date", ""),
            "commit_url": c.get("html_url", "")
        })
    commits_df = pd.DataFrame(commits_rows)
    print(f"  ✓ Fetched {len(commits_df)} commits")

    # 3. Pull Requests
    print(f"  📥 Fetching pull requests (up to {max_items})...")
    prs_raw = _github_request(f"/repos/{owner}/{repo}/pulls", max_items=max_items)
    prs_rows = []
    for pr in prs_raw:
        created_at = pr.get("created_at", "")
        closed_at = pr.get("closed_at") or pr.get("merged_at") or ""
        pr_review_days = 0.0
        if created_at and closed_at:
            try:
                t_open = datetime.fromisoformat(created_at.rstrip("Z")).replace(tzinfo=timezone.utc)
                t_close = datetime.fromisoformat(closed_at.rstrip("Z")).replace(tzinfo=timezone.utc)
                pr_review_days = round((t_close - t_open).total_seconds() / 86400, 2)
            except Exception:
                pass

        prs_rows.append({
            "pr_number": pr.get("number", ""),
            "pr_title": str(pr.get("title", ""))[:60],
            "contributor_login": (pr.get("user") or {}).get("login", "unknown"),
            "pr_state": pr.get("state", ""),
            "pr_review_days": pr_review_days,
            "lines_changed": pr.get("additions", 0) + pr.get("deletions", 0),
            "created_at": created_at,
            "merged_at": pr.get("merged_at", ""),
            "pr_url": pr.get("html_url", "")
        })
    prs_df = pd.DataFrame(prs_rows)
    print(f"  ✓ Fetched {len(prs_df)} pull requests")

    # 4. Contributors
    print(f"  📥 Fetching contributors (up to {max_items})...")
    contribs_raw = _github_request(f"/repos/{owner}/{repo}/contributors", max_items=max_items)
    contribs_rows = []
    for i, c in enumerate(contribs_raw):
        role = "Maintainer" if i < 3 else ("Reviewer" if i < 8 else "Contributor")
        contribs_rows.append({
            "contributor_login": c.get("login", "unknown"),
            "commits_count": c.get("contributions", 0),
            "contributor_role": role,
            "profile_url": c.get("html_url", "")
        })
    contributors_df = pd.DataFrame(contribs_rows)
    print(f"  ✓ Fetched {len(contributors_df)} contributors")

    return commits_df, prs_df, contributors_df, repo_meta


def generate_csv_from_github_api(repo_input, output_dir=None):
    """
    Main entry point: Parse a GitHub URL or slug, fetch data, merge into structured CSV.

    Args:
        repo_input (str): GitHub URL or owner/repo slug.
        output_dir (str): Base directory to save outputs.

    Returns:
        tuple: (df_merged, report_dict)
    """
    base_dir = output_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_path = os.path.join(base_dir, "data", "raw", "fetched_github_repo_data.csv")
    processed_path = os.path.join(base_dir, "data", "processed", "fetched_github_repo_processed.csv")
    report_path = os.path.join(base_dir, "output", "github_ingestion_report.json")

    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # Parse URL/slug
    owner, repo = parse_github_url(repo_input)
    print(f"\n{'='*60}")
    print(f"GITHUB REPOSITORY INGESTION: {owner}/{repo}")
    print(f"{'='*60}")

    # Fetch live data
    commits_df, prs_df, contributors_df, repo_meta = fetch_github_repo_metrics(owner, repo, max_items=100)

    # Merge contributor stats with PR stats
    if not contributors_df.empty and not prs_df.empty:
        pr_summary = prs_df.groupby("contributor_login").agg(
            pull_requests_opened=("pr_number", "count"),
            avg_pr_review_days=("pr_review_days", "mean"),
            avg_lines_changed=("lines_changed", "mean")
        ).reset_index()
        df_merged = contributors_df.merge(pr_summary, on="contributor_login", how="left")
    elif not contributors_df.empty:
        df_merged = contributors_df.copy()
        df_merged["pull_requests_opened"] = 0
        df_merged["avg_pr_review_days"] = 0.0
        df_merged["avg_lines_changed"] = 0.0
    else:
        df_merged = pd.DataFrame(columns=["contributor_login", "commits_count", "contributor_role",
                                           "pull_requests_opened", "avg_pr_review_days", "avg_lines_changed"])

    df_merged["repository_name"] = f"{owner}/{repo}"
    df_merged = df_merged.fillna(0)
    df_merged["avg_pr_review_days"] = df_merged["avg_pr_review_days"].round(2)
    df_merged["avg_lines_changed"] = df_merged["avg_lines_changed"].round(0).astype(int)

    # Save raw output
    df_merged.to_csv(raw_path, index=False)
    df_merged.to_csv(processed_path, index=False)
    print(f"\n✓ Saved raw dataset ({len(df_merged)} contributors) to: {raw_path}")
    print(f"✓ Saved processed dataset to: {processed_path}")

    # Build audit report
    report = {
        "repository": f"{owner}/{repo}",
        "stars": repo_meta.get("stargazers_count", 0),
        "forks": repo_meta.get("forks_count", 0),
        "total_contributors": len(contributors_df),
        "total_commits_fetched": len(commits_df),
        "total_prs_fetched": len(prs_df),
        "avg_pr_review_days": round(prs_df["pr_review_days"].mean(), 2) if not prs_df.empty and "pr_review_days" in prs_df else 0,
        "single_commit_contributors": int((df_merged["commits_count"] == 1).sum()),
        "raw_output_path": raw_path,
        "processed_output_path": processed_path,
        "ingested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"✓ Saved ingestion audit report to: {report_path}")
    print(json.dumps(report, indent=2))
    print(f"\n{'='*60}")

    return df_merged, report


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) < 2:
        print("Usage: python scripts/github_repo_ingestion.py <github_url_or_owner/repo>")
        print("Example: python scripts/github_repo_ingestion.py Msush3005/GitGuide-Analytics-")
        sys.exit(1)

    repo_input = sys.argv[1]
    generate_csv_from_github_api(repo_input)
