# Technical Guide: Behavioural Analysis & User Segmentation

This guide provides deep technical concepts on user segmentation, sample size confidence intervals, visual metric normalization, and operational actionability thresholds.

---

## 1. Segment Definition & Why Segmentation Matters

Aggregate reporting (e.g. "average churn is 7%") compresses diverse customer populations into a single misleading average. 

Grouping by `customer_type` reveals three distinct operational profiles:
- **Enterprise**: High LTV ($\sim \$150k$), low churn ($1.0\%$), high retention ($\sim 1,250$ days).
- **SMB**: Middle LTV ($\sim \$8k$), high churn ($11.8\%$), high support ticket volume ($4.4$ tickets/cust).
- **Startup**: High volume, lower LTV ($\sim \$2k$), moderate churn ($8.7\%$).

---

## 2. Sample Size Caution & Confidence Intervals

When comparing segments of varying sample sizes (e.g. Enterprise $N=54$ vs. Startup $N=539$):

1. **Standard Error of Mean**:
   $$\text{SE} = \frac{\sigma}{\sqrt{N}}$$
   Smaller sample sizes ($N=54$) exhibit wider confidence intervals around metric estimates than larger samples ($N=539$).
2. **Business Caution**:
   Single-customer events in small segments cause larger percentage swings. Always evaluate sample counts alongside percentages before making major capital commitments.

---

## 3. Visualization Mechanics: Heatmap Color Scaling

Plotting raw metrics side-by-side (e.g. LTV $\$150,000$ vs Churn Rate $0.01$) creates extreme scale imbalance:
- **Min-Max Color Normalization**:
  $$x_{\text{scaled}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$
  Scales color mapping across $[0, 1]$ while displaying raw metric numbers as text annotations inside each cell (`annot=True`).

---

## 4. Actionability Thresholds: When to Shift Business Strategy

A metric variance justifies a dedicated segment strategy only when it meets three criteria:

1. **Statistical Significance**: The difference exceeds noise bounds ($\ge 2\times \text{SE}$).
2. **Economic Impact**: The revenue delta justifies dedicated resource allocation.
3. **Operational Feasibility**: The team can execute tailored interventions (e.g., dedicated CSMs vs self-service documentation).
