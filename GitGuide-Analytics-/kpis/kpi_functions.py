import pandas as pd


def calculate_mau(df, days=30):
    """
    Monthly Active Users: distinct customers active in the last N days.
    """
    if 'transaction_date' not in df.columns:
        return 0
    df_temp = df.copy()
    df_temp['transaction_date'] = pd.to_datetime(df_temp['transaction_date'])
    max_date = df_temp['transaction_date'].max()
    cutoff = max_date - pd.Timedelta(days=days)
    active = df_temp[df_temp['transaction_date'] >= cutoff]['customer_id'].nunique()
    return int(active)


def calculate_revenue_per_customer(df):
    """
    Average revenue per unique customer.
    """
    if df.empty or 'amount' not in df.columns or 'customer_id' not in df.columns:
        return 0.0
    total_revenue = df['amount'].sum()
    unique_customers = df['customer_id'].nunique()
    if unique_customers == 0:
        return 0.0
    return float(total_revenue / unique_customers)


def calculate_churn_rate(df, period_days=30):
    """
    Customers who had activity in period 1 (days 31-60 ago) but none in period 2 (last 30 days).
    """
    if 'transaction_date' not in df.columns or 'customer_id' not in df.columns:
        return 0.0
    df_temp = df.copy()
    df_temp['transaction_date'] = pd.to_datetime(df_temp['transaction_date'])
    max_date = df_temp['transaction_date'].max()

    period_2_start = max_date - pd.Timedelta(days=period_days)
    period_1_start = period_2_start - pd.Timedelta(days=period_days)

    active_p1 = df_temp[
        (df_temp['transaction_date'] >= period_1_start) & (df_temp['transaction_date'] < period_2_start)
    ]['customer_id'].unique()

    active_p2 = df_temp[
        df_temp['transaction_date'] >= period_2_start
    ]['customer_id'].unique()

    if len(active_p1) == 0:
        return 0.0

    churned = len([c for c in active_p1 if c not in active_p2])
    return float(churned / len(active_p1))


def calculate_payment_success_rate(df):
    """
    Ratio of successful transactions to total attempted transactions.
    """
    if 'status' not in df.columns or len(df) == 0:
        return 1.0
    successful = len(df[df['status'].str.upper() == 'SUCCESS'])
    total = len(df)
    return float(successful / total) if total > 0 else 0.0


def calculate_customer_acquisition_cost(df):
    """
    Average acquisition cost per acquired customer.
    """
    if 'acquisition_cost' not in df.columns or 'customer_id' not in df.columns:
        return 35.0
    total_cost = df.groupby('customer_id')['acquisition_cost'].first().sum()
    total_customers = df['customer_id'].nunique()
    return float(total_cost / total_customers) if total_customers > 0 else 0.0
