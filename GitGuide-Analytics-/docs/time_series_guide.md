# Technical Guide: Time-Series Trend & Rolling Metrics

This guide details temporal data aggregation, moving average smoothing, percentage change calculations, and time-series data cleaning strategies.

---

## 1. Resampling Definition vs. GroupBy Split-Apply-Combine

- **Resampling (`.resample()`)**:
  - Requires a DatetimeIndex.
  - Frequency-aware temporal aggregation (e.g. Daily `'D'`, Weekly `'W'`, Monthly `'ME'`).
  - Understands chronological continuity and auto-fills missing time intervals.
- **GroupBy (`.groupby()`)**:
  - Groups by discrete categorical values or explicit keys.
  - Unaware of temporal intervals or calendar gaps.

---

## 2. Rolling Window Mechanics & Window Size Selection

Moving averages calculate metrics across a sliding window of historical rows:

$$\text{MA}_K(t) = \frac{1}{K} \sum_{i=0}^{K-1} x(t-i)$$

- **Small Window (e.g. 7 days)**: Responsive to short-term shifts and weekly seasonality; retains some high-frequency noise.
- **Large Window (e.g. 30 days / 90 days)**: Smooths out daily/weekly noise completely to isolate structural long-term business trends.
- **Trade-off**: Larger windows introduce execution lag at sharp trend turning points.

---

## 3. Month-over-Month Percentage Change (`.pct_change()`)

Percentage change measures period-over-period momentum:

$$\text{PctChange}(t) = \frac{x(t) - x(t-1)}{x(t-1)} \times 100$$

- **Positive Values ($> 0$)**: Indicates period-over-period growth/acceleration.
- **Negative Values ($< 0$)**: Indicates period-over-period contraction/decline.
- **Zero ($0$)**: Indicates flat/stable performance.

---

## 4. Handling Missing Data & Gaps in Time-Series Data

When time-series records contain missing dates or null values:

1. **Reindexing Frequency (`.asfreq('D')`)**: Exposes missing dates in the time range by inserting `NaN` rows.
2. **Forward Fill (`.ffill()`)**: Propagates the last valid observation forward (ideal for stable prices/inventory levels).
3. **Backward Fill (`.bfill()`)**: Uses the next valid observation to fill preceding missing slots.
4. **Linear Interpolation (`.interpolate(method='time')`)**: Computes mathematically estimated values along a linear trajectory between surrounding known timestamps.
