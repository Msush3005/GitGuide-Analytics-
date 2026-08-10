# Technical Guide: Funnel Analysis & Drop-Off Detection

This guide details sequential conversion funnel mechanics, drop-off rate formulas, financial bottleneck prioritization, and multi-cohort funnel comparison techniques.

---

## 1. What is Funnel Analysis & Business Questions Answered

Funnel analysis tracks user progression through a series of mandatory sequential steps leading to a key conversion goal (such as signup, onboarding, or checkout).

### Key Business Questions Answered
1. **Where do we lose the most users?** (Pinpointing friction points).
2. **What is our end-to-end conversion rate?** (Overall pipeline efficiency).
3. **Where should engineering resources focus first?** (Data-driven backlog prioritization).

---

## 2. Stage Definition & Derivation from Event Logs

Funnel stages represent strict, ordered event milestones:
1. `Sign Up` (Top of Funnel - Initial Intent)
2. `Email Entered` (Contact Acquisition)
3. `Password Created` (Credential Setup)
4. `Email Verified` (Identity Confirmation)
5. `Payment Added` (Financial Commitment Setup)
6. `First Purchase` (Bottom of Funnel - Conversion Realization)

**Selection Rule**: Stages must be strictly sequential where a user must complete step $N$ to be eligible for step $N+1$.

---

## 3. Drop-Off & Completion Rate Formulas

For any consecutive stage transition $S_i \rightarrow S_{i+1}$:

1. **Absolute Users Lost**:
   $$\text{Users Lost} = \text{Users}(S_i) - \text{Users}(S_{i+1})$$

2. **Completion Rate (%)**:
   $$\text{Completion Rate} = \frac{\text{Users}(S_{i+1})}{\text{Users}(S_i)} \times 100$$

3. **Drop-Off Rate (%)**:
   $$\text{Drop-Off Rate} = \frac{\text{Users Lost}}{\text{Users}(S_i)} \times 100 = 100\% - \text{Completion Rate}$$

---

## 4. Quantifying Financial Revenue Impact

To translate user drop-off into executive financial language:

$$\text{Revenue Lost} = \text{Users Lost} \times \text{Value per Customer (LTV)}$$

### Bottleneck Ranking Rule
Evaluate bottlenecks by both **percentage drop rate** and **monetary revenue impact**. A $50\%$ drop rate losing $2,000$ users at $100 LTV ($200,000 lost) demands higher priority than a $10\%$ drop rate at top-of-funnel.

---

## 5. Cohort & Segment Funnel Comparison

To compare funnels across time periods or user categories:

1. **Temporal Cohorts (e.g., January vs. February)**: Evaluates whether product UX updates or bug fixes reduced drop-off rates.
2. **Segment Cohorts (e.g., Mobile Web vs. Desktop App)**: Reveals platform-specific bugs or payment gateway friction on specific devices.
