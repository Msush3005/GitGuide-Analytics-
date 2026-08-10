# Technical Guide: Root Cause Investigation Workflow

This guide details systematic anomaly investigation methodology, dimension filtering, statistical correlation analysis, and external hypothesis validation.

---

## 1. What is Root Cause Investigation & What It Produces

Root cause investigation is a diagnostic workflow that traces performance anomalies back to their underlying structural failure point.

### Primary Outputs Produced
1. **Time Window & Scope Isolation**: Exact start/end timestamps and affected cohort boundary.
2. **Single Primary Pattern**: The specific dimension value exhibiting 100% specificity with the failure.
3. **High-Confidence Hypothesis**: Grounded in empirical log evidence and verified against external data.
4. **Financial Action Plan**: Corrective engineering steps with estimated annual ROI.

---

## 2. Investigation Structure: What Was Checked First & Why

A systematic investigation follows a 4-step elimination funnel:

1. **Step 1: Narrow Time First**: Isolate the anomaly date and hour. Narrowing time first reduces noise by filtering out 99% of normal operational data.
2. **Step 2: Narrow Segment**: Evaluate metrics across dimensions (`customer_type`, `payment_method`, `region`, `device_type`).
3. **Step 3: Pattern & Error Log Inspection**: Inspect error messages within the isolated time/segment window.
4. **Step 4: Formulate & Validate Hypothesis**: Cross-reference internal patterns against external infrastructure status logs.

---

## 3. Filtering Dimensions & Pattern Qualification

### Why Payment Method Qualified as Root Cause
- **Customer Type**: Enterprise (34.6%), SMB (47.0%), Startup (44.2%) all experienced failures $\rightarrow$ Not segment-specific.
- **Region**: US-East (50%), US-West (40.9%), EU-Central (37.8%) all experienced failures $\rightarrow$ Not region-specific.
- **Payment Method**: Credit Card ($0.0\%$ success / $100\%$ failure) vs. Debit ($100\%$ success) vs. Crypto ($96.6\%$ success) $\rightarrow$ **100% Specific Pattern Match**.

---

## 4. Distinguishing Correlation vs. Causation

To prove true **causation** rather than mere correlation:

1. **Control Groups**: Debit and Crypto transactions processed during the exact same hour experienced 0% failure, proving internal database and web servers were healthy.
2. **Dominant Error Specificity**: Over 95% of failed credit card attempts explicitly logged `"Stripe API timeout"`.
3. **External Timeline Match**: Public Stripe status logs confirmed a global gateway outage from `14:15` to `14:45 UTC`, confirming external causality.
