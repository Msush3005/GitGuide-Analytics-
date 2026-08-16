"""
Alert Monitoring & Metric Threshold Configuration
GitGuide Analytics Subsystem

Defines threshold-based operational monitoring parameters for business and engineering metrics.
Thresholds are decoupled from dashboard rendering logic to allow continuous configuration updates.
"""

ALERT_THRESHOLDS = {
    "single_commit_dropout": {
        "metric": "Single-Commit Contributor Dropout %",
        "threshold": 30.0,
        "direction": "above",  # alert when value > threshold
        "severity": "critical",
        "message": "First-time contributor drop-off exceeds safe operating limit. Investigate onboarding friction and dev environment setup."
    },
    "avg_pr_review_days": {
        "metric": "Average PR Review Turnaround (Days)",
        "threshold": 3.0,
        "direction": "above",  # alert when value > threshold
        "severity": "warning",
        "message": "PR review turnaround time exceeds the 3-day target. Check maintainer review bandwidth and queue bottleneck."
    },
    "null_percentage": {
        "metric": "Data Quality (Null %)",
        "threshold": 5.0,
        "direction": "above",  # alert when value > threshold
        "severity": "warning",
        "message": "Data null percentage exceeds 5% threshold. Check live ingestion pipeline for missing or unparsed fields."
    },
    "avg_lines_changed": {
        "metric": "Oversized Pull Request Size",
        "threshold": 500.0,
        "direction": "above",
        "severity": "warning",
        "message": "Average lines changed per contribution exceeds 500 lines. Encourage contributors to chunk PRs into smaller units."
    }
}


def check_alerts(current_metrics, thresholds=ALERT_THRESHOLDS):
    """
    Evaluates computed metrics against alert thresholds.

    Args:
        current_metrics (dict): Dict of {metric_key: numeric_value}
        thresholds (dict): Threshold configuration dictionary

    Returns:
        list: List of triggered alert dictionaries containing metric name, value, threshold, severity, and message.
    """
    triggered_alerts = []

    for key, config in thresholds.items():
        if key not in current_metrics or current_metrics[key] is None:
            continue

        value = float(current_metrics[key])
        threshold = float(config["threshold"])
        breached = False

        if config["direction"] == "above" and value > threshold:
            breached = True
        elif config["direction"] == "below" and value < threshold:
            breached = True

        if breached:
            triggered_alerts.append({
                "key": key,
                "metric": config["metric"],
                "value": value,
                "threshold": threshold,
                "severity": config["severity"],
                "message": config["message"]
            })

    return triggered_alerts
