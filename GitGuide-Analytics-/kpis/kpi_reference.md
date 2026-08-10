# Formal KPI Reference Document

This reference document outlines the single source of truth for all business Key Performance Indicators (KPIs) used across Finance, Sales, Product, and Marketing teams.

---

## 1. Monthly Active Users (MAU)
- **Definition**: Distinct customers with at least one completed transaction in the last 30 days.
- **Formula**: `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
- **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`, `status`)
- **Target Range**: 5,000 - 6,000 customers
- **Owner**: Product Manager
- **Update Frequency**: Daily
- **Notes**: Core indicator of active customer engagement; seasonal dips occur during Q4 holidays.

---

## 2. Revenue per Customer (RPC)
- **Definition**: Average total revenue generated per unique customer over the evaluation period.
- **Formula**: `SUM(amount) / COUNT(DISTINCT customer_id)`
- **Data Source**: `transactions` table (columns: `amount`, `customer_id`)
- **Target Range**: $90.00 - $110.00
- **Owner**: Revenue / Finance Lead
- **Update Frequency**: Weekly
- **Notes**: Measures monetization efficiency per customer account across all products.

---

## 3. Churn Rate
- **Definition**: Percentage of active customers in period 1 who performed zero transactions in period 2.
- **Formula**: `(Active Customers P1 - Retained Customers P2) / Active Customers P1`
- **Data Source**: `transactions` table (columns: `customer_id`, `transaction_date`)
- **Target Range**: 0.00% - 5.00% (0.00 - 0.05)
- **Owner**: Customer Success Lead
- **Update Frequency**: Monthly
- **Notes**: Measures customer attrition momentum; values above 5.0% trigger high-priority intervention.

---

## 4. Payment Success Rate
- **Definition**: Ratio of successful payment transactions to total attempted transactions.
- **Formula**: `COUNT(transaction_id WHERE status = 'SUCCESS') / COUNT(transaction_id)`
- **Data Source**: `transactions` table (columns: `transaction_id`, `status`)
- **Target Range**: 95.0% - 100.0% (0.95 - 1.00)
- **Owner**: Engineering / Infrastructure Lead
- **Update Frequency**: Real-time / Daily
- **Notes**: Monitors payment gateway health and checkout friction.

---

## 5. Customer Acquisition Cost (CAC)
- **Definition**: Average sales and marketing spend required to acquire a single active customer.
- **Formula**: `SUM(marketing_spend + sales_cost) / COUNT(DISTINCT new_customer_id)`
- **Data Source**: `acquisition_costs` table (columns: `acquisition_cost`, `customer_id`)
- **Target Range**: $0.00 - $50.00
- **Owner**: Growth Marketing Lead
- **Update Frequency**: Monthly
- **Notes**: Ensures acquisition economics remain sustainable relative to customer LTV.
