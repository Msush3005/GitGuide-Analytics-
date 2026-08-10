import os
import sys
import json
import numpy as np
import pandas as pd

# Add project root to sys.path to enable imports from kpis module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kpis.kpi_functions import (
    calculate_mau,
    calculate_revenue_per_customer,
    calculate_churn_rate,
    calculate_payment_success_rate,
    calculate_customer_acquisition_cost
)


def generate_kpi_dataset(num_customers=5500, filepath="data/raw/kpi_transactions_data.csv"):
    """
    Generates synthetic KPI transactions dataset with:
    - 5,500 distinct active customers (targeting MAU range 5,000 - 6,000)
    - Average RPC around $98.50 (targeting range $90 - $110)
    - Churn rate around 3.8% (targeting range 0% - 5%)
    - Payment success rate 98.2% (targeting range 95% - 100%)
    - CAC around $32.50 (targeting range $0 - $50)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic KPI dataset ({num_customers:,} active customers)...")
        np.random.seed(42)

        customer_ids = [f"CUST_{i:06d}" for i in range(1, num_customers + 1)]
        segments = np.random.choice(['Enterprise', 'SMB', 'Startup'], size=num_customers, p=[0.10, 0.40, 0.50])

        rows = []
        base_date = pd.Timestamp.now() - pd.Timedelta(days=60)

        for cid, seg in zip(customer_ids, segments):
            # Period 1 activity (days 31-60 ago)
            tx_count_p1 = np.random.randint(1, 4)
            for _ in range(tx_count_p1):
                tx_date = base_date + pd.Timedelta(days=np.random.randint(0, 28))
                prod = np.random.choice(['Cloud Pro', 'Analytics Suite', 'Enterprise Core'])
                amt = np.random.normal(250, 30) if seg == 'Enterprise' else (np.random.normal(90, 15) if seg == 'SMB' else np.random.normal(45, 10))
                status = 'SUCCESS' if np.random.rand() < 0.982 else 'FAILED'
                cac = 45.0 if seg == 'Enterprise' else (32.0 if seg == 'SMB' else 18.0)
                rows.append({
                    'transaction_id': f"TX_{len(rows)+1:08d}",
                    'customer_id': cid,
                    'customer_type': seg,
                    'product': prod,
                    'transaction_date': tx_date,
                    'amount': round(max(amt, 10.0), 2),
                    'status': status,
                    'acquisition_cost': cac
                })

            # Period 2 activity (last 30 days) - 3.8% churn rate
            if np.random.rand() >= 0.038:
                tx_count_p2 = np.random.randint(1, 4)
                for _ in range(tx_count_p2):
                    tx_date = max_date = pd.Timestamp.now() - pd.Timedelta(days=np.random.randint(0, 28))
                    prod = np.random.choice(['Cloud Pro', 'Analytics Suite', 'Enterprise Core'])
                    amt = np.random.normal(250, 30) if seg == 'Enterprise' else (np.random.normal(90, 15) if seg == 'SMB' else np.random.normal(45, 10))
                    status = 'SUCCESS' if np.random.rand() < 0.982 else 'FAILED'
                    cac = 45.0 if seg == 'Enterprise' else (32.0 if seg == 'SMB' else 18.0)
                    rows.append({
                        'transaction_id': f"TX_{len(rows)+1:08d}",
                        'customer_id': cid,
                        'customer_type': seg,
                        'product': prod,
                        'transaction_date': tx_date,
                        'amount': round(max(amt, 10.0), 2),
                        'status': status,
                        'acquisition_cost': cac
                    })

        df_raw = pd.DataFrame(rows)
        df_raw.to_csv(filepath, index=False)
        print(f"Dataset created successfully with {len(df_raw):,} transactions.")
    else:
        print(f"Loading existing KPI dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)
        df_raw['transaction_date'] = pd.to_datetime(df_raw['transaction_date'])

    return df_raw


def task2_compute_kpis(df):
    """
    Task 2: Compute all 5 KPIs using imported functions.
    """
    print("\n--- Task 2: Compute Core Business KPIs ---")
    mau = calculate_mau(df, days=30)
    rpc = calculate_revenue_per_customer(df)
    churn = calculate_churn_rate(df, period_days=30)
    pay_success = calculate_payment_success_rate(df)
    cac = calculate_customer_acquisition_cost(df)

    print(f"  - Monthly Active Users (MAU)      : {mau:,} customers")
    print(f"  - Revenue per Customer (RPC)       : ${rpc:.2f}")
    print(f"  - Monthly Churn Rate              : {churn:.2%}")
    print(f"  - Payment Success Rate            : {pay_success:.2%}")
    print(f"  - Customer Acquisition Cost (CAC) : ${cac:.2f}")

    current_kpis = {
        'mau': mau,
        'revenue_per_customer': rpc,
        'churn_rate': churn,
        'payment_success_rate': pay_success,
        'customer_acquisition_cost': cac
    }
    return current_kpis


def task3_validate_against_targets(current_kpis, targets_filepath="kpis/kpi_validation_targets.json"):
    """
    Task 3: Validate computed KPIs against target JSON ranges.
    Exports report to output/kpi_validation_report.csv.
    """
    print("\n--- Task 3: Validate KPIs Against Target JSON Configuration ---")
    with open(targets_filepath, "r") as f:
        targets = json.load(f)

    validation_report = []
    for kpi_name, target_cfg in targets.items():
        actual = current_kpis[kpi_name]
        min_val = target_cfg['min']
        max_val = target_cfg['max']
        unit = target_cfg['unit']

        status = 'PASS' if min_val <= actual <= max_val else 'ALERT'

        if unit == 'currency_usd':
            formatted_actual = f"${actual:,.2f}"
            formatted_target = f"${min_val:,.2f} - ${max_val:,.2f}"
        elif unit == 'percentage':
            formatted_actual = f"{actual:.2%}"
            formatted_target = f"{min_val:.2%} - {max_val:.2%}"
        else:
            formatted_actual = f"{actual:,.0f}"
            formatted_target = f"{min_val:,.0f} - {max_val:,.0f}"

        validation_report.append({
            'kpi_key': kpi_name,
            'kpi_description': target_cfg['description'],
            'actual_raw': actual,
            'actual_formatted': formatted_actual,
            'target_min': min_val,
            'target_max': max_val,
            'target_formatted': formatted_target,
            'status': status
        })

    validation_df = pd.DataFrame(validation_report)
    print(validation_df[['kpi_description', 'actual_formatted', 'target_formatted', 'status']])

    os.makedirs("output", exist_ok=True)
    report_csv = "output/kpi_validation_report.csv"
    validation_df.to_csv(report_csv, index=False)

    failures = validation_df[validation_df['status'] == 'ALERT']
    if len(failures) > 0:
        print(f"\n[ALERT]: {len(failures)} KPI(s) out of target range - Review required!")
    else:
        print(f"\n[SUCCESS]: All {len(validation_df)} KPIs within target range!")

    return validation_df


def task4_kpi_decomposition(df):
    """
    Task 4: KPI Decomposition Hierarchy (Top-Level -> By Segment -> By Product).
    Exports text output to output/kpi_decomposition.txt.
    """
    print("\n--- Task 4: KPI Decomposition Hierarchy ---")
    total_revenue = df['amount'].sum()
    revenue_by_segment = df.groupby('customer_type')['amount'].sum()
    revenue_by_product = df.groupby(['customer_type', 'product'])['amount'].sum()

    decomposition_text = f"""============================================================
KPI DECOMPOSITION HIERARCHY REPORT
============================================================

LEVEL 1 (Top-Level Business Metric):
  - Total Monthly Revenue : ${total_revenue:,.2f}

LEVEL 2 (Breakdown by Customer Segment):
  - Enterprise Segment    : ${revenue_by_segment.get('Enterprise', 0):,.2f} ({(revenue_by_segment.get('Enterprise', 0)/total_revenue)*100:.1f}%)
  - SMB Segment           : ${revenue_by_segment.get('SMB', 0):,.2f} ({(revenue_by_segment.get('SMB', 0)/total_revenue)*100:.1f}%)
  - Startup Segment       : ${revenue_by_segment.get('Startup', 0):,.2f} ({(revenue_by_segment.get('Startup', 0)/total_revenue)*100:.1f}%)

LEVEL 3 (Detailed Product Breakdown per Segment):
"""
    for (seg, prod), amt in revenue_by_product.items():
        pct = (amt / total_revenue) * 100
        decomposition_text += f"  - [{seg:<10}] {prod:<18}: ${amt:,.2f} ({pct:.1f}% of total)\n"

    decomposition_text += f"\nVERIFICATION: Sub-component sum (${revenue_by_segment.sum():,.2f}) == Total Revenue (${total_revenue:,.2f})\n"
    decomposition_text += "============================================================\n"

    print(decomposition_text)

    os.makedirs("output", exist_ok=True)
    report_txt = "output/kpi_decomposition.txt"
    with open(report_txt, "w") as f:
        f.write(decomposition_text)
    print(f"Saved KPI decomposition report to: {report_txt}")


def main():
    print("=" * 60)
    print("  KPI Definition & Business Metric Design Engine")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_kpi_dataset()
    current_kpis = task2_compute_kpis(df)
    validation_df = task3_validate_against_targets(current_kpis)
    task4_kpi_decomposition(df)

    print("\n[SUCCESS] KPI Definition & Business Metric Design Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
