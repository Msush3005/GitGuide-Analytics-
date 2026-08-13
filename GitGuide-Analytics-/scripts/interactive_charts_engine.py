import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine


def ensure_plotly_database(database_path="analytics.db"):
    """Ensures database has synthetic data for Plotly charts."""
    engine = create_engine(f"sqlite:///{database_path}")
    np.random.seed(42)

    # Daily Revenue & Orders (90 days)
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
    revenues = np.round(np.random.normal(loc=15000, scale=3500, size=90) + np.linspace(2000, 8000, 90), 2)
    order_counts = np.random.randint(40, 120, size=90)

    df_daily = pd.DataFrame({
        'order_date': dates.strftime('%Y-%m-%d'),
        'amount': revenues,
        'order_count': order_counts
    })
    df_daily.to_sql('daily_sales', engine, if_exists='replace', index=False)

    # Product Performance (10 products)
    products = [f"Product {chr(65+i)}" for i in range(10)]
    prod_rev = [120000, 95000, 88000, 75000, 62000, 55000, 48000, 41000, 35000, 28000]
    prod_profit = [val * np.random.uniform(0.25, 0.40) for val in prod_rev]
    prod_orders = [2500, 2100, 1800, 1500, 1300, 1100, 950, 800, 700, 550]
    prod_aov = [r / o for r, o in zip(prod_rev, prod_orders)]

    df_products = pd.DataFrame({
        'product_name': products,
        'revenue': prod_rev,
        'profit': prod_profit,
        'order_count': prod_orders,
        'aov': prod_aov
    })
    df_products.to_sql('product_metrics', engine, if_exists='replace', index=False)

    print(f"[SUCCESS] Prepared Plotly database '{database_path}'.")
    return engine, df_daily, df_products


def task1_create_hover_charts(df_daily, df_products, output_dir="interactive_charts"):
    """Task 1: Create Two Plotly Charts with Custom & Multi-Column Hover Tooltips."""
    print("\n--- Task 1: Create Plotly Charts with Hover Tooltips ---")

    # Chart 1: Revenue Trend with Custom Hover
    fig1 = go.Figure(data=go.Scatter(
        x=df_daily['order_date'],
        y=df_daily['amount'],
        mode='lines+markers',
        hovertemplate='<b>Date: %{x|%Y-%m-%d}</b><br>' +
                      'Daily Revenue: $%{y:,.2f}<br>' +
                      '<extra></extra>',
        line=dict(color='#1f77b4', width=2.5),
        marker=dict(size=6, color='#1f77b4')
    ))
    fig1.update_layout(
        title='Daily Revenue Trend (Custom Hover Tooltip)',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    # Chart 2: Product Performance with Multi-Column Hover
    hover_text = [
        f"<b>{p}</b><br>" +
        f"Revenue: ${r:,.2f}<br>" +
        f"Order Count: {o:,}<br>" +
        f"Average Order Value: ${a:,.2f}<extra></extra>"
        for p, r, o, a in zip(df_products['product_name'], df_products['revenue'], df_products['order_count'], df_products['aov'])
    ]

    fig2 = go.Figure(data=go.Bar(
        x=df_products['product_name'],
        y=df_products['revenue'],
        hovertemplate=hover_text,
        marker=dict(color='#ff7f0e')
    ))
    fig2.update_layout(
        title='Product Performance (Multi-Column Hover Tooltip)',
        xaxis_title='Product Name',
        yaxis_title='Total Revenue ($)',
        height=500,
        template='plotly_white'
    )

    file1 = os.path.join(output_dir, 'chart1_revenue_trend.html')
    file2 = os.path.join(output_dir, 'chart2_product_performance.html')
    fig1.write_html(file1)
    fig2.write_html(file2)

    os.makedirs("output", exist_ok=True)
    fig1.write_html('output/chart1_revenue_trend.html')
    fig2.write_html('output/chart2_product_performance.html')

    print(f"  [SUCCESS] Saved {file1}")
    print(f"  [SUCCESS] Saved {file2}")


def task2_create_dropdown_chart(df_products, output_dir="interactive_charts"):
    """Task 2: Create Dropdown Filter to Toggle Views (updatemenus)."""
    print("\n--- Task 2: Create Dropdown Filter Chart (updatemenus) ---")

    fig3 = go.Figure()

    # Trace 0: Revenue (Visible initially)
    fig3.add_trace(go.Bar(
        x=df_products['product_name'],
        y=df_products['revenue'],
        name='Revenue',
        marker=dict(color='#1f77b4'),
        visible=True,
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))

    # Trace 1: Profit (Hidden)
    fig3.add_trace(go.Bar(
        x=df_products['product_name'],
        y=df_products['profit'],
        name='Profit',
        marker=dict(color='#ff7f0e'),
        visible=False,
        hovertemplate='<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>'
    ))

    # Trace 2: Order Count (Hidden)
    fig3.add_trace(go.Bar(
        x=df_products['product_name'],
        y=df_products['order_count'],
        name='Order Count',
        marker=dict(color='#2ca02c'),
        visible=False,
        hovertemplate='<b>%{x}</b><br>Orders: %{y:,}<extra></extra>'
    ))

    fig3.update_layout(
        updatemenus=[dict(
            active=0,
            x=0.0,
            xanchor='left',
            y=1.15,
            yanchor='top',
            buttons=[
                dict(label='Revenue', method='update', args=[{'visible': [True, False, False]}, {'title': 'Product Performance: Revenue ($)'}]),
                dict(label='Profit', method='update', args=[{'visible': [False, True, False]}, {'title': 'Product Performance: Profit ($)'}]),
                dict(label='Order Count', method='update', args=[{'visible': [False, False, True]}, {'title': 'Product Performance: Order Count'}])
            ]
        )],
        title='Product Performance Metric Selector',
        xaxis_title='Product Name',
        height=500,
        template='plotly_white'
    )

    file3 = os.path.join(output_dir, 'chart3_metric_selector.html')
    fig3.write_html(file3)
    fig3.write_html('output/chart3_metric_selector.html')
    print(f"  [SUCCESS] Saved {file3}")


def task3_create_interactive_zoom_chart(df_daily, output_dir="interactive_charts"):
    """Task 3: Enable Native Zoom, Pan, Reset & Selection Interactions."""
    print("\n--- Task 3: Enable Zoom, Pan, and Reset Interactions ---")

    fig4 = go.Figure(data=go.Scatter(
        x=df_daily['order_date'],
        y=df_daily['amount'],
        mode='lines+markers',
        marker=dict(size=8, color='#9467bd'),
        line=dict(color='#9467bd', width=2),
        hovertemplate='<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>'
    ))

    fig4.update_layout(
        title='Interactive Exploration Chart (Zoom, Pan, Box Select, Reset)',
        xaxis_title='Date',
        yaxis_title='Revenue ($)',
        dragmode='zoom',
        hovermode='closest',
        height=550,
        template='plotly_white'
    )

    # Task 5: Add Date Range Selector Buttons & Range Slider
    fig4.update_xaxes(
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

    file4 = os.path.join(output_dir, 'chart4_interactive.html')
    fig4.write_html(file4)
    fig4.write_html('output/chart4_interactive.html')
    print(f"  [SUCCESS] Saved {file4}")


def main():
    print("=" * 60)
    print("  Interactive Plotly Chart Design Engine")
    print("=" * 60)

    output_dir = "interactive_charts"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("output", exist_ok=True)

    engine, df_daily, df_products = ensure_plotly_database("analytics.db")

    task1_create_hover_charts(df_daily, df_products, output_dir)
    task2_create_dropdown_chart(df_products, output_dir)
    task3_create_interactive_zoom_chart(df_daily, output_dir)

    print("\n[SUCCESS] Interactive Plotly Charts Generated Successfully!")


if __name__ == "__main__":
    main()
