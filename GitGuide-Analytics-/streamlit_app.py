"""
Assignment 2.46: Interactive Plotly Chart Design
Task 4: Production Streamlit Dashboard Application
"""
import os
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st

# Configure Streamlit Page
st.set_page_config(page_title="Interactive Sales Dashboard", layout="wide")

st.title("📊 Interactive Sales Analytics Dashboard")
st.markdown("This Streamlit application embeds interactive Plotly charts with custom hover tooltips, dropdown metric selectors, zoom/pan controls, and sidebar filters.")

# Database Connection
db_path = 'analytics.db'
if not os.path.exists(db_path):
    db_path = '../analytics.db'

engine = create_engine(f"sqlite:///{db_path}")


@st.cache_data
def load_data():
    try:
        df_daily = pd.read_sql("SELECT * FROM daily_sales", engine)
        df_products = pd.read_sql("SELECT * FROM product_metrics", engine)
    except Exception:
        # Fallback synthetic generation if DB missing
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        df_daily = pd.DataFrame({
            'order_date': dates.strftime('%Y-%m-%d'),
            'amount': [15000 + i * 50 for i in range(90)],
            'order_count': [50 + (i % 30) for i in range(90)]
        })
        df_products = pd.DataFrame({
            'product_name': [f"Product {chr(65+i)}" for i in range(5)],
            'revenue': [100000, 80000, 60000, 40000, 20000],
            'profit': [30000, 24000, 18000, 12000, 6000],
            'order_count': [2000, 1600, 1200, 800, 400],
            'aov': [50.0, 50.0, 50.0, 50.0, 50.0]
        })
    return df_daily, df_products


df_daily, df_products = load_data()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("🔍 Dashboard Filters")
min_amount = st.sidebar.slider("Min Daily Revenue ($)", 0, 30000, 5000, step=1000)

filtered_daily = df_daily[df_daily['amount'] >= min_amount]

st.sidebar.markdown(f"**Filtered Records**: {len(filtered_daily)} / {len(df_daily)} days")

# ---------------------------------------------------------
# Layout: Top Row Metrics
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${filtered_daily['amount'].sum():,.2f}")
with col2:
    st.metric("Avg Daily Revenue", f"${filtered_daily['amount'].mean():,.2f}")
with col3:
    st.metric("Total Days Tracked", len(filtered_daily))

st.markdown("---")

# ---------------------------------------------------------
# Section 1: Plotly Interactive Daily Revenue Trend
# ---------------------------------------------------------
st.subheader("1. Daily Revenue Trend (Custom Hover & Zoom)")

fig_trend = go.Figure(data=go.Scatter(
    x=filtered_daily['order_date'],
    y=filtered_daily['amount'],
    mode='lines+markers',
    hovertemplate='<b>Date: %{x|%Y-%m-%d}</b><br>' +
                  'Revenue: $%{y:,.2f}<br>' +
                  '<extra></extra>',
    line=dict(color='#1f77b4', width=2.5),
    marker=dict(size=7, color='#1f77b4')
))

fig_trend.update_layout(
    title='Daily Revenue Performance',
    xaxis_title='Date',
    yaxis_title='Revenue ($)',
    hovermode='x unified',
    height=450,
    template='plotly_white'
)

fig_trend.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=7, label='1W', step='day', stepmode='backward'),
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(count=3, label='3M', step='month', stepmode='backward'),
            dict(step='all', label='All')
        ])
    ),
    rangeslider=dict(visible=True)
)

st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------
# Section 2: Plotly Metric Selector (Dropdown Filter)
# ---------------------------------------------------------
st.subheader("2. Product Performance (Metric Selector Dropdown)")

fig_selector = go.Figure()

fig_selector.add_trace(go.Bar(
    x=df_products['product_name'],
    y=df_products['revenue'],
    name='Revenue',
    marker=dict(color='#1f77b4'),
    visible=True,
    hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
))

fig_selector.add_trace(go.Bar(
    x=df_products['product_name'],
    y=df_products['profit'],
    name='Profit',
    marker=dict(color='#ff7f0e'),
    visible=False,
    hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>'
))

fig_selector.add_trace(go.Bar(
    x=df_products['product_name'],
    y=df_products['order_count'],
    name='Order Count',
    marker=dict(color='#2ca02c'),
    visible=False,
    hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
))

fig_selector.update_layout(
    updatemenus=[dict(
        active=0,
        x=0.0,
        xanchor='left',
        y=1.15,
        yanchor='top',
        buttons=[
            dict(label='Revenue ($)', method='update', args=[{'visible': [True, False, False]}, {'title': 'Product Performance: Revenue ($)'}]),
            dict(label='Profit ($)', method='update', args=[{'visible': [False, True, False]}, {'title': 'Product Performance: Profit ($)'}]),
            dict(label='Order Count', method='update', args=[{'visible': [False, False, True]}, {'title': 'Product Performance: Order Count'}])
        ]
    )],
    title='Product Metrics Comparison',
    xaxis_title='Product Name',
    height=450,
    template='plotly_white'
)

st.plotly_chart(fig_selector, use_container_width=True)

# Data Table Display
with st.expander("📄 View Raw Data Table"):
    st.dataframe(filtered_daily, use_container_width=True)
