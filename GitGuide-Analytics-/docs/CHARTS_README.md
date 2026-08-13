# Analysis Visualizations & Design Principles

This directory contains five high-resolution 300dpi chart visualizations adhering to core business visualization design principles: matching chart type to data relationship, complete labeling, consistent color palette, and insight annotations.

---

## Chart 1: Revenue by Product Line
- **File**: `chart1_revenue_by_product.png`
- **Type**: Horizontal Bar Chart (Category Comparison)
- **Business Question**: Which product line generates the highest gross revenue?
- **Key Insight**: Cloud Hosting dominates revenue generation at $5.20M, followed by Analytics Suite at $3.80M.
- **Labelling & Formatting**: Revenue formatted in Millions (`$M`), sorted descending.
- **Annotation**: Highlighted Cloud Hosting as market leader (`$5.2M`).

---

## Chart 2: Revenue Trend
- **File**: `chart2_revenue_trend.png`
- **Type**: Line Chart with Multiple Series (Trend Over Time)
- **Business Question**: How has revenue trended over the last 12 months across top product lines?
- **Key Insight**: Consistent growth trajectory for Cloud Hosting, reaching $640K in Dec 2024.
- **Labelling & Formatting**: Currency in Thousands (`$K`), dates formatted as `MMM YYYY`.
- **Annotation**: Marked August seasonal slowdown dip and added dashed green target reference line ($500K/month).

---

## Chart 3: Order Value Distribution
- **File**: `chart3_order_value_distribution.png`
- **Type**: Binned Histogram (Distribution of Values)
- **Business Question**: What is the typical distribution of customer order values?
- **Key Insight**: Bimodal distribution revealing two distinct customer purchasing behaviors (Starter Tier ~$65 vs Enterprise Bundles ~$480).
- **Labelling & Formatting**: X-axis order values in `$`, Y-axis frequency count.
- **Annotation**: Annotated both distribution peaks (Starter Tier vs Enterprise Bundles).

---

## Chart 4: Revenue Composition
- **File**: `chart4_revenue_composition.png`
- **Type**: Stacked Bar Chart (Composition & Part-to-Whole)
- **Business Question**: How does total quarterly revenue break down by product line composition?
- **Key Insight**: Cloud Hosting and Analytics Suite drive over 60% of total quarterly volume, peaking at $5.1M total in Q4.
- **Labelling & Formatting**: Stacked segments color-coded to company palette, revenue in Millions (`$M`).
- **Annotation**: Arrow marking Q4 peak revenue surge (+$5.1M total).

---

## Chart 5: Marketing Spend vs Revenue
- **File**: `chart5_marketing_vs_revenue.png`
- **Type**: Scatter Plot with Trend Line (Correlation & Outlier Detection)
- **Business Question**: Does marketing campaign spend correlate with generated revenue?
- **Key Insight**: Strong positive correlation ($r = 0.88$) between spend and revenue, with one significant campaign outlier requiring audit.
- **Labelling & Formatting**: Both axes in Thousands (`$K`), includes linear regression trend line.
- **Annotation**: Highlighted campaign outlier (High Spend $145K, Low Revenue $210K).

---

## Design System & Accessibility

- **Color Palette**: Palette uses muted, colorblind-safe hex values (`#1f77b4`, `#ff7f0e`, `#2ca02c`, `#d62728`, `#9467bd`).
- **Accessibility**: High contrast ratios against white backgrounds; labels and distinct markers ensure legibility in grayscale or for colorblind viewers.
