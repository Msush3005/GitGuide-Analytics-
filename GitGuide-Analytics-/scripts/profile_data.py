import os
import json
import pandas as pd
import numpy as np


def profile_nulls_and_duplicates(df):
    """
    Compute null percentage and duplicate counts.
    """
    profile = {
        "null_counts": {},
        "null_percentages": {},
        "exact_duplicate_count": 0
    }

    for col in df.columns:
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df)) * 100

        profile["null_counts"][col] = int(null_count)
        profile["null_percentages"][col] = round(null_pct, 2)

    dup_count = df.duplicated().sum()

    profile["exact_duplicate_count"] = int(dup_count)
    profile["duplicate_percentage"] = round((dup_count / len(df)) * 100, 2)

    return profile


def profile_numerical_columns(df):
    """
    Statistical summary of numerical columns.
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns

    stats = {}

    for col in numerical_cols:
        stats[col] = {
            "min": round(df[col].min(), 2),
            "max": round(df[col].max(), 2),
            "mean": round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "std": round(df[col].std(), 2),
            "null_count": int(df[col].isnull().sum())
        }

    return pd.DataFrame(stats).T


def profile_categorical_columns(df, top_n=5):
    """
    Profile categorical columns.
    """
    categorical_cols = df.select_dtypes(include=["object"]).columns

    profile = {}

    for col in categorical_cols:
        profile[col] = {
            "unique_count": int(df[col].nunique()),
            "top_values": df[col].value_counts().head(top_n).to_dict(),
            "null_count": int(df[col].isnull().sum())
        }

    return profile


def identify_quality_issues(df, null_threshold=30, duplicate_threshold=5):
    """
    Detect quality problems.
    """
    issues = []

    null_pcts = (df.isnull().sum() / len(df)) * 100

    for col, pct in null_pcts.items():
        if pct > null_threshold:
            issues.append({
                "type": "High nulls",
                "column": col,
                "severity": "HIGH",
                "value": f"{pct:.1f}% missing",
                "recommendation": "Consider imputation or column exclusion"
            })

    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100

    if dup_pct > duplicate_threshold:
        issues.append({
            "type": "High duplicates",
            "column": "Full row",
            "severity": "HIGH",
            "value": f"{dup_pct:.1f}% duplicated",
            "recommendation": "Deduplication required before analysis"
        })

    for col in df.select_dtypes(include=[np.number]).columns:
        if "amount" in col.lower():
            if (df[col] < 0).any():
                issues.append({
                    "type": "Invalid range",
                    "column": col,
                    "severity": "MEDIUM",
                    "value": "Contains negative values",
                    "recommendation": "Investigate negative entries"
                })

    return issues


def generate_profile_report(df, filepath):
    """
    Generate complete report.
    """
    report = {
        "dataset": filepath,
        "record_count": len(df),
        "column_count": len(df.columns),
        "nulls_and_duplicates": profile_nulls_and_duplicates(df),
        "numerical_stats": profile_numerical_columns(df).to_dict(),
        "categorical_stats": profile_categorical_columns(df),
        "quality_issues": identify_quality_issues(df)
    }

    os.makedirs("output", exist_ok=True)

    with open("output/profile_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print("=" * 60)
    print("DATA QUALITY PROFILE")
    print("=" * 60)
    print("Dataset :", filepath)
    print("Records :", report["record_count"])
    print("Columns :", report["column_count"])

    print("\nQuality Issues Found:", len(report["quality_issues"]))

    for issue in report["quality_issues"]:
        print(
            f"[{issue['severity']}] {issue['type']} "
            f"({issue['column']}) -> {issue['value']}"
        )

    print("=" * 60)

    return report


def main():
    filepath = "data/raw/quality_test.csv"

    df = pd.read_csv(filepath)

    generate_profile_report(df, filepath)


if __name__ == "__main__":
    main()