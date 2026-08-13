# Quantitative Supporting Evidence Breakdown

This document provides the specific quantitative evidence, statistical correlations, and chart references supporting each finding in the executive churn analysis narrative.

---

## Finding 1: Support Response Time Correlates Directly With Customer Churn

### Supporting Evidence
1. **Scatter Plot & Correlation Analysis (Chart 1)**:
   - **Visual Evidence**: Scatter plot mapping support response time (X-axis in hours) against annual customer churn rate (Y-axis %). A strong, consistent positive linear relationship is visible.
   - **Correlation Strength**: Correlation coefficient $r = -0.65$ (showing that faster response time is strongly correlated with lower churn rate).
   - **Statistical Power**: Plain-language assessment confirms that the relationship is real, strong, and highly unlikely to be random chance.

2. **Bucketed Churn Rate Breakdown (Chart 2)**:
   - **Sub-2 Hours Response**: 3.0% Annual Churn Rate (Baseline Benchmark)
   - **2 to 4 Hours Response**: 5.0% Annual Churn Rate (+66% increase vs baseline)
   - **4 to 24 Hours Response**: 9.0% Annual Churn Rate (+200% increase vs baseline)
   - **Over 24 Hours Response**: 12.0% Annual Churn Rate (**+300% increase / 4x higher churn rate vs baseline**)

3. **Key Quantified Insight**:
   - Customers waiting over 24 hours for initial support are **4x more likely to cancel their subscriptions** compared to customers served within 2 hours.
   - Support response latency alone accounts for **40% of all customer churn differences** across the company.

### Why This Evidence Matters
This finding is not theoretical — the pattern is strong, statistically robust across all customer cohorts, and directly actionable. It isolates response speed as the single most critical operational lever for reducing customer churn.

---

## Finding 2: High-Value Enterprise Accounts Exhibit Elevated Delays Sensitivity

### Supporting Evidence
1. **Segment Sensitivity Comparison (Chart 3)**:
   - Accounts spending **<$2,000/year**: Churn increases from 4% to 8% when support is delayed >24h (2x increase).
   - Accounts spending **>$10,000/year**: Churn increases from 2% to 7% when support is delayed >24h (**3.5x increase**).

2. **Revenue Loss Concentration**:
   - Accounts spending >$10,000/year represent **15% of total customer count** but **58% of total churned revenue loss** ($1.16M of the $2.0M annual loss).

### Why This Evidence Matters
High-value enterprise accounts have zero tolerance for support delays. Protecting these accounts with dedicated priority routing safeguards over half of our vulnerable revenue with minimal engineering effort.
