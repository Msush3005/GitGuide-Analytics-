import pandas as pd
import json
import os
from datetime import datetime


def detect_exact_duplicates(df):
    exact_dups = df.duplicated().sum()

    dup_rows = df[df.duplicated(keep=False)]

    print("\nEXACT DUPLICATES")
    print(f"Duplicates Found: {exact_dups}")

    return exact_dups, dup_rows


def detect_near_duplicates(df, key_columns):
    duplicate_keys = df[df.duplicated(subset=key_columns, keep=False)]

    print("\nNEAR DUPLICATES")
    print(duplicate_keys)

    return duplicate_keys


def remove_exact_duplicates(df, keep="first"):

    rows_before = len(df)

    df_dedup = df.drop_duplicates(keep=keep)

    rows_after = len(df_dedup)

    print(f"Rows Removed: {rows_before-rows_after}")

    return df_dedup


def remove_near_duplicates(df, key_columns, keep_strategy="most_complete"):

    if keep_strategy == "last":
        df = df.drop_duplicates(subset=key_columns, keep="last")

    elif keep_strategy == "first":
        df = df.drop_duplicates(subset=key_columns, keep="first")

    else:

        def keep_best(group):
            idx = group.isnull().sum(axis=1).idxmin()
            return group.loc[[idx]]

        df = (
            df.groupby(key_columns, group_keys=False)
            .apply(keep_best)
            .reset_index(drop=True)
        )

    return df


def log_removed_duplicates(original_df, dedup_df):

    os.makedirs("output", exist_ok=True)

    removed = original_df.loc[~original_df.index.isin(dedup_df.index)]

    removed.to_csv("output/removed_duplicates_audit.csv", index=False)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "removed_records": int(len(removed)),
        "reason": "Duplicate Removal"
    }

    with open("output/dedup_audit_summary.json", "w") as f:
        json.dump(summary, f, indent=4)

    return removed


def compare_before_after(original_df, dedup_df):

    summary = {
        "rows_before": len(original_df),
        "rows_after": len(dedup_df),
        "rows_removed": len(original_df)-len(dedup_df),
        "removal_percentage": round(
            ((len(original_df)-len(dedup_df))/len(original_df))*100,2),
        "nulls_before": int(original_df.isnull().sum().sum()),
        "nulls_after": int(dedup_df.isnull().sum().sum()),
        "timestamp": datetime.now().isoformat()
    }

    with open("output/dedup_summary.json","w") as f:
        json.dump(summary,f,indent=4)

    print(summary)

    return summary


if __name__ == "__main__":

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df_original = pd.read_csv("data/raw/data_with_dupes.csv")

    print("Starting Deduplication...")

    detect_exact_duplicates(df_original)

    detect_near_duplicates(
        df_original,
        ["customer_id","transaction_date"]
    )

    df = remove_exact_duplicates(df_original)

    df = remove_near_duplicates(
        df,
        ["customer_id","transaction_date"],
        "most_complete"
    )

    log_removed_duplicates(df_original, df)

    compare_before_after(df_original, df)

    df.to_csv(
        "data/processed/deduplicated_data.csv",
        index=False
    )

    print("Done!")