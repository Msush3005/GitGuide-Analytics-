import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_business_metrics_dataset(num_days=90, filepath="data/raw/daily_business_metrics.csv"):
    """
    Generates synthetic daily business metrics dataset spanning 90 days with:
    - Normal daily revenue distribution (mean ~$10,000, std ~$1,500)
    - Normal transaction count (mean ~500, std ~50)
    - Normal signup rate (mean ~150, std ~20)
    - Injected specific anomalies (e.g. $2,000 drop on day 45, $48,000 spike on day 75)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic daily business metrics dataset ({num_days} days)...")
        np.random.seed(42)
        dates = pd.date_range(start="2025-01-01", periods=num_days, freq="D")

        revenue = np.random.normal(10000, 1500, num_days)
        tx_count = np.random.normal(500, 50, num_days)
        signups = np.random.normal(150, 20, num_days)

        # Inject specific anomalies into dataset
        revenue[44] = 2000.0   # Severe drop on Day 45 (2025-02-14) -> CRITICAL
        tx_count[44] = 45.0
        signups[44] = 8.0

        revenue[74] = 48000.0  # Massive spike on Day 75 (2025-03-16) -> CRITICAL
        tx_count[74] = 2200.0
        signups[74] = 680.0

        revenue[20] = 4500.0   # Moderate dip on Day 21 (2025-01-21) -> HIGH
        revenue[60] = 16500.0  # Moderate surge on Day 61 (2025-03-02) -> HIGH

        df_raw = pd.DataFrame({
            "date": dates,
            "amount": np.round(revenue, 2),
            "transaction_count": np.round(tx_count).astype(int),
            "signup_rate": np.round(signups).astype(int)
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset created successfully at {filepath}.")
    else:
        print(f"Loading existing daily business metrics from {filepath}...")
        df_raw = pd.read_csv(filepath)
        df_raw["date"] = pd.to_datetime(df_raw["date"])

    return df_raw


def task1_check_thresholds(metrics, alert_rules):
    """
    Task 1: Threshold-Based Anomaly Detection.
    Checks metrics against predefined min/max business rules.
    """
    print("\n--- Task 1: Threshold-Based Anomaly Detection ---")
    alerts = []
    for metric_name, rule in alert_rules.items():
        value = metrics[metric_name]
        if value < rule['min']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['min'],
                'direction': 'BELOW_MIN',
                'severity': 'HIGH'
            })
        elif value > rule['max']:
            alerts.append({
                'metric': metric_name,
                'value': value,
                'threshold': rule['max'],
                'direction': 'ABOVE_MAX',
                'severity': 'MEDIUM'
            })

    for alert in alerts:
        print(f"  [ALERT] {alert['metric']} {alert['direction']}: Actual={alert['value']} (Threshold={alert['threshold']}) -> Severity: {alert['severity']}")

    return alerts


def task2_detect_anomalies_zscore(series, threshold=2):
    """
    Task 2: Statistical Anomaly Detection with Z-Score.
    Identifies values beyond N standard deviations from the mean across a lookback window.
    """
    print(f"\n--- Task 2: Statistical Anomaly Detection (Z-Score > {threshold}) ---")
    mean = series.mean()
    std = series.std()
    z_scores = np.abs((series - mean) / std)
    anomalies = series[z_scores > threshold]

    print(f"Lookback Window Size : {len(series)} days")
    print(f"Series Mean          : ${mean:,.2f}")
    print(f"Series Std Dev       : ${std:,.2f}")
    print(f"Anomalies Detected   : {len(anomalies)} out of {len(series)} days\n")

    for date, value in anomalies.items():
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        print(f"  - {date_str}: ${value:,.2f} (Z-Score: {z_scores[date]:.2f})")

    return anomalies, z_scores, mean, std


def classify_severity(value, mean, std):
    """
    Task 3 Helper: Classifies anomaly severity based on z-score deviation.
    """
    z_score = abs((value - mean) / std)
    if z_score > 3.0:
        return 'CRITICAL'
    elif z_score > 2.0:
        return 'HIGH'
    elif z_score > 1.5:
        return 'MEDIUM'
    else:
        return 'LOW'


def task3_severity_classification(anomalies, z_scores, mean, std):
    """
    Task 3: Severity Classification and Filtering.
    """
    print("\n--- Task 3: Severity Classification & Critical Alerting ---")
    anomaly_severity = []
    for date, value in anomalies.items():
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        severity = classify_severity(value, mean, std)
        anomaly_severity.append({
            'date': date_str,
            'value': value,
            'z_score': round(z_scores[date], 2),
            'severity': severity
        })

    severity_df = pd.DataFrame(anomaly_severity)
    print(severity_df)

    critical_and_high = severity_df[severity_df['severity'].isin(['CRITICAL', 'HIGH'])]
    print(f"\n[ALERT]: {len(critical_and_high)} CRITICAL / HIGH severity anomalies require immediate investigation!")

    return severity_df, critical_and_high


def task4_anomaly_logging_audit_trail(anomalies, z_scores, daily_revenue, mean, std):
    """
    Task 4: Persistent Anomaly Audit Trail Logging.
    Exports to anomalies_log.csv and output/anomalies_log.csv.
    """
    print("\n--- Task 4: Anomaly Logging & Persistent Audit Trail ---")
    anomaly_log = []
    now_ts = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    for date, value in anomalies.items():
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
        severity = classify_severity(value, mean, std)
        expected_min = mean - 2 * std
        expected_max = mean + 2 * std

        anomaly_log.append({
            'timestamp': now_ts,
            'anomaly_date': date_str,
            'metric': 'daily_revenue',
            'value': round(value, 2),
            'expected_range': f"${expected_min:,.0f} - ${expected_max:,.0f}",
            'z_score': round(z_scores[date], 2),
            'severity': severity,
            'status': 'OPEN'  # OPEN, INVESTIGATED, RESOLVED
        })

    anomalies_df = pd.DataFrame(anomaly_log)

    # Save to root and output directory as required
    anomalies_df.to_csv('anomalies_log.csv', index=False)

    os.makedirs("output", exist_ok=True)
    anomalies_df.to_csv('output/anomalies_log.csv', index=False)

    print(f"Logged {len(anomalies_df)} anomalies to anomalies_log.csv and output/anomalies_log.csv")
    return anomalies_df


def task5_visualization_with_flagged_points(daily_revenue, anomalies, mean, std):
    """
    Task 5: Time-Series Visualization with Rolling MA, Expected Range, and Flagged Anomaly Points.
    Saves to anomaly_detection.png and output/anomaly_detection.png.
    """
    print("\n--- Task 5: Time-Series Visualization with Flagged Points ---")
    fig, ax = plt.subplots(figsize=(14, 6))

    # 1. Plot raw daily values
    ax.plot(daily_revenue.index, daily_revenue.values, marker='o', markersize=4, label='Daily Revenue ($)', color='#2563eb', linewidth=1.8)

    # 2. Plot 7-day rolling average
    rolling_avg = daily_revenue.rolling(window=7).mean()
    ax.plot(rolling_avg.index, rolling_avg.values, label='7-Day Moving Average', color='#16a34a', linewidth=2.2, linestyle='--')

    # 3. Highlight anomaly points with red 'X' markers and annotations
    for date, value in anomalies.items():
        ax.scatter(date, value, color='#dc2626', s=180, marker='X', zorder=5, label='Anomaly Flagged' if date == anomalies.index[0] else "")
        ax.annotate(
            f"ANOMALY\n${value:,.0f}",
            (date, value),
            xytext=(0, 14),
            textcoords='offset points',
            ha='center',
            fontweight='bold',
            fontsize=8,
            color='#dc2626'
        )

    # 4. Shade expected range (mean +- 2 std)
    ax.fill_between(daily_revenue.index, mean - 2 * std, mean + 2 * std, alpha=0.15, color='#3b82f6', label=r'Expected Range ($\mu \pm 2\sigma$)')

    ax.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
    ax.set_title('Daily Revenue Time-Series with Flagged Statistical Anomalies', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save to root and output directory as required
    plt.savefig('anomaly_detection.png', dpi=150)
    
    os.makedirs("output", exist_ok=True)
    plot_path = "output/anomaly_detection.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()

    print(f"Saved visualization to anomaly_detection.png and {plot_path}")


def main():
    print("=" * 60)
    print("  Anomaly Detection & Risk Identification Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_business_metrics_dataset()
    df_ts = df.set_index("date")

    # Task 1: Threshold Alerts Test
    alert_rules = {
        'daily_revenue': {'min': 5000, 'max': 50000},
        'transaction_count': {'min': 100, 'max': 10000},
        'signup_rate': {'min': 10, 'max': 500}
    }
    today_metrics = {'daily_revenue': 2500, 'transaction_count': 50, 'signup_rate': 5}
    task1_check_thresholds(today_metrics, alert_rules)

    # Task 2: Statistical Z-Score Detection over 30-day lookback window
    daily_revenue = df_ts['amount'].tail(30)
    anomalies, z_scores, mean, std = task2_detect_anomalies_zscore(daily_revenue, threshold=2)

    # Task 3: Severity Classification
    severity_df, critical_df = task3_severity_classification(anomalies, z_scores, mean, std)

    # Task 4: Audit Trail Logging
    anomalies_df = task4_anomaly_logging_audit_trail(anomalies, z_scores, daily_revenue, mean, std)

    # Task 5: Visualization
    task5_visualization_with_flagged_points(daily_revenue, anomalies, mean, std)

    anomalies_df.to_csv("data/processed/anomalies_summary.csv", index=False)
    print("\n[SUCCESS] Anomaly Detection & Risk Identification Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
