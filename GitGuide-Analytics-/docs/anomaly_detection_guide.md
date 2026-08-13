# Technical Guide: Anomaly Detection & Risk Identification

This guide details statistical anomaly detection methods, threshold alerting engines, severity classification taxonomies, audit trail logging, and false-positive reduction strategies.

---

## 1. What is an Anomaly? (Business Definition)

An anomaly is any data point or pattern that deviates significantly from expected operational behavior.

### Business Impact Categories
- **Operational Failures**: Revenue dropping 50% due to silent payment gateway outages.
- **Fraud & Security Risks**: Signup rates spiking 10x normal levels due to bot attacks.
- **Data Errors**: Revenue reporting $0 or duplicate transactions inflating revenue 4x.

---

## 2. Threshold-Based vs. Statistical Detection

| Feature | Threshold-Based Detection | Statistical (Z-Score) Detection |
| :--- | :--- | :--- |
| **Mechanism** | Hardcoded min/max boundaries (e.g. Min Revenue < $5,000) | Standard deviation distance from rolling mean ($z = \frac{\|x - \mu\|}{\sigma}$) |
| **Best Used For** | Known physical/contractual bounds (SLA limits, minimum balance) | Dynamic time-series with seasonality and shifting baselines |
| **Adaptability** | Static (requires manual tuning when business scales) | Adaptive (automatically adjusts as rolling average scales) |
| **Failure Mode** | High false positives if business grows past fixed max | Sensitive to extreme outliers inflating standard deviation ($\sigma$) |

---

## 3. Z-Score Mathematical Derivation & Severity Taxonomy

### Formula
$$z = \frac{|x - \mu|}{\sigma}$$

Where:
- $x$ = Current observed value
- $\mu$ = Rolling mean over lookback window (e.g. 30 days)
- $\sigma$ = Rolling standard deviation

### Severity Levels
- **CRITICAL** ($z > 3.0$): Extreme outlier (> 99.7% confidence), immediate page to on-call engineer.
- **HIGH** ($z > 2.0$): Significant anomaly (> 95% confidence), high-priority audit log entry.
- **MEDIUM** ($z > 1.5$): Moderate deviation, recorded for trend monitoring.
- **LOW** ($z \le 1.5$): Normal operational variance.

---

## 4. Flagged Anomaly Investigation Workflow

When an anomaly is flagged:
1. **Audit Log Record**: Write entry to `anomalies_log.csv` with status `OPEN`.
2. **Alert Notification**: Dispatch alert containing metric name, actual value, expected range ($\mu \pm 2\sigma$), and z-score.
3. **Root Cause Analysis**: Execute dimensional breakdown (`customer_type`, `payment_method`, error logs).
4. **Resolution Tracking**: Update status to `INVESTIGATED` and finally `RESOLVED` once remediated.

---

## 5. Reducing False Positives & Tuning Sensitivity

To prevent alert fatigue:
1. **Use Rolling Windows**: Compute $\mu$ and $\sigma$ over a rolling 30-day window rather than all-time global statistics.
2. **Combine Methods**: Require BOTH a threshold violation AND a statistical $z > 2.0$ breach for page-level alerts.
3. **Minimum Sample Size**: Enforce a minimum sample threshold before evaluating z-scores to prevent noisy alerts during low-volume hours.
