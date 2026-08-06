import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_timeseries_dataset(num_days=365, filepath="data/raw/daily_revenue_timeseries.csv"):
    """
    Generates a 1-year daily revenue time-series dataset featuring:
    - Overall upward growth trend
    - Weekly seasonality (higher sales on weekends)
    - Random daily noise (volatility)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic 1-year time-series dataset ({num_days} days)...")
        np.random.seed(42)
        dates = pd.date_range(start="2025-01-01", periods=num_days, freq="D")
        
        # Base trend + Weekly seasonality + Gaussian noise
        base_trend = np.linspace(5000, 15000, num_days)
        day_of_week_effect = np.array([1.2 if d.weekday() in [4, 5] else 0.9 for d in dates])
        noise = np.random.normal(0, 1500, num_days)

        revenue = base_trend * day_of_week_effect + noise
        revenue = np.maximum(revenue, 1000.0)  # Floor revenue at $1,000

        orders = (revenue / np.random.uniform(45, 65, num_days)).astype(int)

        df_raw = pd.DataFrame({
            "date": dates,
            "revenue": np.round(revenue, 2),
            "orders": orders
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset created successfully at {filepath}.")
    else:
        print(f"Loading existing time-series dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)
        df_raw["date"] = pd.to_datetime(df_raw["date"])

    return df_raw


def task1_resample_data(df):
    """
    Task 1: Resample Data by Time Period (Weekly & Monthly).
    Uses sum, count, and mean aggregations.
    """
    print("\n--- Task 1: Resample Data by Time Period ---")
    df_ts = df.set_index("date")

    # Resample to Weekly
    weekly_revenue = df_ts["revenue"].resample("W").sum()
    weekly_count = df_ts["orders"].resample("W").count()
    weekly_avg = df_ts["revenue"].resample("W").mean()

    # Resample to Monthly
    try:
        monthly_revenue = df_ts["revenue"].resample("ME").sum()
        monthly_count = df_ts["orders"].resample("ME").count()
        monthly_avg = df_ts["revenue"].resample("ME").mean()
    except ValueError:
        monthly_revenue = df_ts["revenue"].resample("M").sum()
        monthly_count = df_ts["orders"].resample("M").count()
        monthly_avg = df_ts["revenue"].resample("M").mean()

    peak_week = weekly_revenue.idxmax().strftime("%Y-%m-%d")
    peak_week_val = weekly_revenue.max()
    peak_month = monthly_revenue.idxmax().strftime("%Y-%m")
    peak_month_val = monthly_revenue.max()

    print(f"Weekly Aggregation Summary ({len(weekly_revenue)} weeks):")
    print(f"  - Peak Week  : {peak_week} (${peak_week_val:,.2f})")
    print(f"Monthly Aggregation Summary ({len(monthly_revenue)} months):")
    print(f"  - Peak Month : {peak_month} (${peak_month_val:,.2f})")

    resampled_monthly = pd.DataFrame({
        "total_revenue": monthly_revenue,
        "order_days": monthly_count,
        "avg_daily_revenue": monthly_avg
    })
    resampled_monthly.to_csv("data/processed/resampled_monthly_revenue.csv")

    return df_ts, weekly_revenue, monthly_revenue


def task2_compute_rolling_averages(df):
    """
    Task 2: Compute 7-day and 30-day Rolling Averages and plot alongside raw daily noise.
    """
    print("\n--- Task 2: Compute Rolling Window Averages ---")
    df["revenue_ma7"] = df["revenue"].rolling(window=7).mean()
    df["revenue_ma30"] = df["revenue"].rolling(window=30).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["revenue"], label="Raw Daily Revenue", alpha=0.3, color="gray")
    plt.plot(df["date"], df["revenue_ma7"], label="7-Day Moving Average", color="blue", linewidth=1.5)
    plt.plot(df["date"], df["revenue_ma30"], label="30-Day Moving Average", color="red", linewidth=2.0)
    plt.title("Daily Revenue vs. 7-Day & 30-Day Rolling Averages", fontsize=14, fontweight="bold")
    plt.xlabel("Date")
    plt.ylabel("Revenue ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    os.makedirs("output", exist_ok=True)
    plot_path = "output/rolling_avg.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved rolling average visualization to: {plot_path}")

    return df


def task3_calculate_mom_change(monthly_revenue):
    """
    Task 3: Calculate Month-over-Month Percentage Change.
    """
    print("\n--- Task 3: Month-over-Month Percentage Change ---")
    mom_change = monthly_revenue.pct_change() * 100

    growth_months = mom_change[mom_change > 0]
    decline_months = mom_change[mom_change < 0]

    print("Month-over-Month Growth Rates (%):")
    for idx, val in mom_change.items():
        month_str = idx.strftime("%Y-%m")
        if pd.isna(val):
            print(f"  - {month_str}: Baseline Month")
        else:
            status = "GROWTH" if val > 0 else "DECLINE"
            print(f"  - {month_str}: {val:+.2f}% ({status})")

    print(f"\nTotal Growth Months: {len(growth_months)}")
    print(f"Total Decline Months: {len(decline_months)}")

    return mom_change, growth_months, decline_months


def task4_compute_cumulative_sum(df):
    """
    Task 4: Compute Cumulative Revenue Sum and save plot.
    """
    print("\n--- Task 4: Compute Cumulative Sum ---")
    df["cumulative_revenue"] = df["revenue"].cumsum()
    total_accumulated = df["cumulative_revenue"].iloc[-1]

    plt.figure(figsize=(10, 5))
    plt.plot(df["date"], df["cumulative_revenue"], color="green", linewidth=2.0)
    plt.title("Cumulative Accumulated Revenue Over Time", fontsize=14, fontweight="bold")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Revenue ($)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    plot_path = "output/cumulative.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()

    print(f"Total Accumulated Revenue by End of Period: ${total_accumulated:,.2f}")
    print(f"Saved cumulative revenue visualization to: {plot_path}")

    return df, total_accumulated


def task5_identify_trend_and_implications(df, mom_change, total_accumulated):
    """
    Task 5: Identify Trend Pattern and Business Implications.
    Saves report to output/trend_analysis.txt.
    """
    print("\n--- Task 5: Identify Trend Pattern & Business Implications ---")
    recent_ma30 = df["revenue_ma30"].dropna().iloc[-30:]
    first_ma30 = recent_ma30.iloc[0]
    last_ma30 = recent_ma30.iloc[-1]

    trend_direction = "UPTREND (Accelerating)" if last_ma30 > first_ma30 else ("DOWNTREND (Declining)" if last_ma30 < first_ma30 else "FLAT (Stable)")
    trend_magnitude = ((last_ma30 - first_ma30) / first_ma30) * 100
    daily_volatility = df["revenue"].std()
    latest_mom = mom_change.dropna().iloc[-1]

    analysis = f"""============================================================
TIME-SERIES TREND & ROLLING METRICS - BUSINESS REPORT
============================================================
Analysis Window: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}

1. STATISTICAL METRICS SUMMARY:
   - Trend Direction (30-Day Moving Average) : {trend_direction}
   - 30-Day MA Growth Magnitude               : {trend_magnitude:+.2f}%
   - Latest Month-over-Month Growth           : {latest_mom:+.2f}%
   - Daily Revenue Volatility (Std Dev)       : ${daily_volatility:,.2f}
   - Total Accumulated Revenue                : ${total_accumulated:,.2f}

2. BUSINESS IMPLICATIONS:
   - The 30-day moving average filters out daily volatility (${daily_volatility:,.2f}) to demonstrate sustainable revenue acceleration.
   - Month-over-month trends confirm robust demand expansion over the evaluated 1-year period.
   - Day-to-day fluctuations (e.g. weekend spikes vs weekday drops) represent operational noise rather than structural business decline.

3. RECOMMENDED STRATEGIC ACTIONS:
   - Maintain core marketing acquisition campaigns; do not execute panicky discounting based on single-day dips.
   - Leverage weekly seasonality patterns to optimize weekend staffing and inventory allocation.
   - Plan budget expansions based on the 30-day rolling baseline rather than volatile daily peaks.
============================================================
"""
    print(analysis)

    txt_path = "output/trend_analysis.txt"
    with open(txt_path, "w") as f:
        f.write(analysis)
    print(f"Saved trend analysis report to: {txt_path}")

    return analysis


def main():
    print("=" * 60)
    print("  Time-Series Trend & Rolling Metrics Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_timeseries_dataset()
    df_ts, weekly_revenue, monthly_revenue = task1_resample_data(df)
    df = task2_compute_rolling_averages(df)
    mom_change, growth_months, decline_months = task3_calculate_mom_change(monthly_revenue)
    df, total_accumulated = task4_compute_cumulative_sum(df)
    task5_identify_trend_and_implications(df, mom_change, total_accumulated)

    print("\n[SUCCESS] Time-Series Trend & Rolling Metrics Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
