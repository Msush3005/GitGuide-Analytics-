"""
Assignment 2.47: KPI Card & Summary Metric Design
Task 4: Production Executive Streamlit Dashboard Application
"""
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit Page
st.set_page_config(page_title="Sales Performance KPI Dashboard", layout="wide")

st.title("📈 Executive Sales Performance Dashboard")
st.markdown("Top-row executive KPI cards providing instant status check (Level 1 Status), followed by trends (Level 2) and detailed segment analysis (Level 3).")

# ---------------------------------------------------------
# Task 1 & 4: Five Executive KPI Cards Header Row
# ---------------------------------------------------------
st.markdown("### Executive KPI Summary Header")

col1, col2, col3, col4, col5 = st.columns(5)

kpi_list = [
    {'name': 'Revenue', 'current': '$5.2M', 'change': '+12.5%', 'inverse': False},
    {'name': 'Active Users', 'current': '2,500', 'change': '+5.2%', 'inverse': False},
    {'name': 'Avg Order Value', 'current': '$45', 'change': '+2.1%', 'inverse': False},
    {'name': 'Churn Rate', 'current': '5.2%', 'change': '-2.8%', 'inverse': True},   # Inverted metric: -2.8% is GREEN
    {'name': 'Satisfaction', 'current': '4.2/5', 'change': '+0.3%', 'inverse': False}
]

columns = [col1, col2, col3, col4, col5]

for col, kpi in zip(columns, kpi_list):
    with col:
        if kpi['inverse']:
            st.metric(
                label=kpi['name'],
                value=kpi['current'],
                delta=kpi['change'],
                delta_color='inverse'  # Negative change displays GREEN for Churn!
            )
        else:
            st.metric(
                label=kpi['name'],
                value=kpi['current'],
                delta=kpi['change']
            )

st.divider()

# ---------------------------------------------------------
# Level 2: Trend Analytics Section
# ---------------------------------------------------------
st.subheader("📊 Level 2: Historical Trend Analysis")

col_trend1, col_trend2 = st.columns(2)

# Chart 1: Revenue & Churn Trend
months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
revenue_trend = [4.1, 4.3, 4.5, 4.8, 5.0, 5.2]
churn_trend = [6.2, 5.9, 5.7, 5.5, 5.4, 5.2]

with col_trend1:
    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(x=months, y=revenue_trend, mode='lines+markers', name='Revenue ($M)', line=dict(color='#10b981', width=3)))
    fig_rev.update_layout(title='Monthly Revenue Trajectory ($M)', xaxis_title='Month', yaxis_title='Revenue ($M)', height=350, template='plotly_white')
    st.plotly_chart(fig_rev, use_container_width=True)

with col_trend2:
    fig_churn = go.Figure()
    fig_churn.add_trace(go.Scatter(x=months, y=churn_trend, mode='lines+markers', name='Churn Rate (%)', line=dict(color='#1f77b4', width=3)))
    fig_churn.update_layout(title='Monthly Customer Churn Trajectory (%)', xaxis_title='Month', yaxis_title='Churn Rate (%)', height=350, template='plotly_white')
    st.plotly_chart(fig_churn, use_container_width=True)

# ---------------------------------------------------------
# Level 3: Segment Breakdown & Data Lineage
# ---------------------------------------------------------
st.divider()
st.subheader("📋 Level 3: Segment Breakdown & Data Lineage")

df_segment = pd.DataFrame({
    'Segment': ['SMB', 'Mid-Market', 'Starter', 'Enterprise'],
    'Active Customers': [380, 255, 199, 166],
    'Total Segment Revenue': ['$125,354.43', '$86,550.56', '$69,468.39', '$62,618.07'],
    'Avg Customer Revenue': ['$329.88', '$339.41', '$349.09', '$377.22'],
    'Status': ['On Track', 'On Track', 'On Track', 'On Track']
})

st.dataframe(df_segment, use_container_width=True)
