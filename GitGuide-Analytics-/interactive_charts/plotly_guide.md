# Interactive Plotly Chart Design & Follow-Up Q&A

This directory contains standalone HTML interactive Plotly charts adhering to modern interactive chart design principles: custom hover tooltips, dropdown metric selectors (`updatemenus`), native zoom/pan/reset controls, and date range sliders (`rangeslider`).

---

## Task 5: Technical Follow-Up Q&A

### Question
*You have a time-series Plotly chart showing revenue by week. You want to add a date range slider so users can select which weeks to view (e.g. 'show me only Q1 2024'). How would you implement this in Plotly?*

---

### Implementation Code & Explanation

Plotly provides two complementary mechanisms for time-series date filtering on the X-axis: **`rangeselector` buttons** (predefined time windows) and the **`rangeslider`** (drag-to-select range adjustment).

#### Python Code Example
```python
import plotly.graph_objects as go
import pandas as pd

# 1. Create Time-Series Line Chart
fig = go.Figure(data=go.Scatter(
    x=df_weekly['week_date'],
    y=df_weekly['revenue'],
    mode='lines+markers',
    hovertemplate='<b>Week of %{x|%Y-%m-%d}</b><br>Revenue: $%{y:,.2f}<extra></extra>',
    line=dict(color='#1f77b4', width=2.5)
))

# 2. Add Range Selector Buttons & Range Slider to X-Axis
fig.update_xaxes(
    rangeselector=dict(
        buttons=list([
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(count=3, label='1Q (Q1/Q2)', step='month', stepmode='backward'),
            dict(count=6, label='6M', step='month', stepmode='backward'),
            dict(count=1, label='YTD', step='year', stepmode='todate'),
            dict(step='all', label='All')
        ]),
        bgcolor='#f0f2f6',
        activecolor='#1f77b4'
    ),
    rangeslider=dict(visible=True, thickness=0.1)
)

fig.update_layout(
    title='Weekly Revenue Trend with Date Range Controls',
    xaxis_title='Week',
    yaxis_title='Revenue ($)',
    template='plotly_white'
)

fig.write_html('weekly_revenue_trend.html')
```

---

### Comparative Evaluation: Range Selector Buttons vs. Range Slider

| Feature / Criteria | Range Selector Buttons (`rangeselector`) | Range Slider (`rangeslider`) |
| :--- | :--- | :--- |
| **User Interaction** | Single-click instant period selection (`1M`, `3M`, `YTD`). | Drag-and-drop boundary handles across an inline mini-chart. |
| **Best Used For** | Executive reporting where stakeholders want standard standard business cycles (Last Month, QTD, YTD). | Deep exploratory analysis where analysts want to isolate arbitrary custom date ranges (e.g., Nov 12 to Dec 04). |
| **Screen Space** | Compact horizontal button group placed above chart canvas. | Takes vertical height below X-axis to render mini-overview graph. |
| **Recommended Strategy** | **Combine Both**: Enabling both `rangeselector` and `rangeslider` provides maximum flexibility for both executive & analyst workflows. |

---

## Interactive Chart File Inventory

1. `chart1_revenue_trend.html`: Daily revenue line chart with custom formatted date (`%Y-%m-%d`) and currency (`$%,.0f`) hover tooltips.
2. `chart2_product_performance.html`: Product performance bar chart with multi-column hover tooltips (Revenue, Order Count, AOV).
3. `chart3_metric_selector.html`: Bar chart with `updatemenus` dropdown toggling Revenue, Profit, and Order Count without page reloads.
4. `chart4_interactive.html`: Scatter plot with native zoom, pan, double-click reset, box/lasso select, and date range slider.
