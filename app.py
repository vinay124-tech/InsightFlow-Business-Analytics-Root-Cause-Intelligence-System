import streamlit as st
import plotly.express as px
from src.queries import *

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="InsightFlow",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def format_currency(value):
    if value is None:
        return "₹0"

    if value >= 1_000_000:
        return f"₹{value/1_000_000:.2f}M"

    if value >= 1_000:
        return f"₹{value/1_000:.2f}K"

    return f"₹{value:.2f}"


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📊 InsightFlow")

st.caption(
    "Business Analytics & Root Cause Intelligence System"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("📊 InsightFlow")

    st.markdown("---")

    st.header("Dashboard Filters")

    selected_country = st.selectbox(
        "Country",
        ["All"] + sorted(get_country_sales()["Country"].tolist())
    )

    st.markdown("---")

    st.info(
        """
### InsightFlow

Business Analytics Dashboard

Version 1.0

Python • DuckDB • SQL • Streamlit
"""
    )

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

kpis = get_kpis(selected_country)

monthly = get_monthly_sales(selected_country)

country = get_country_sales()

products = get_top_products(selected_country)

hour = get_sales_by_hour(selected_country)

weekday = get_sales_by_weekday(selected_country)

segments = get_customer_segments(selected_country)

growth = get_month_over_month_growth(selected_country)

customers = get_top_customers(selected_country)

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.markdown("## 📌 Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "💰 Revenue",
    format_currency(kpis["Total Revenue"])
)

c2.metric(
    "🛒 Orders",
    f"{kpis['Total Orders']:,}"
)

c3.metric(
    "👥 Customers",
    f"{kpis['Total Customers']:,}"
)

c4.metric(
    "📦 Products",
    f"{kpis['Total Products']:,}"
)

c5.metric(
    "💳 Avg Order",
    format_currency(kpis["Average Order Value"])
)

# --------------------------------------------------
# SALES ANALYSIS
# --------------------------------------------------

st.markdown("---")

st.markdown("## 📈 Sales Analysis")

fig = px.line(
    monthly,
    x="MonthDate",
    y="TotalRevenue",
    markers=True,
    title="Monthly Revenue Trend",
    template="plotly_white"
)

fig.update_traces(fill="tozeroy")

fig.update_layout(height=450)

st.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# COUNTRY + PRODUCT
# --------------------------------------------------

left, right = st.columns(2)

fig = px.bar(
    country,
    x="Country",
    y="TotalRevenue",
    title="Revenue by Country",
    color="TotalRevenue",
    color_continuous_scale="Blues",
    template="plotly_white"
)

fig.update_layout(height=450)

left.plotly_chart(
    fig,
    width="stretch"
)

fig = px.bar(
    products,
    x="TotalRevenue",
    y="Description",
    orientation="h",
    title="Top Products",
    color="TotalRevenue",
    color_continuous_scale="Greens",
    template="plotly_white"
)

fig.update_layout(
    height=450,
    yaxis=dict(autorange="reversed")
)

right.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# TIME ANALYSIS
# --------------------------------------------------

st.markdown("---")
st.markdown("## ⏰ Time Analysis")

left, right = st.columns(2)

fig = px.line(
    hour,
    x="Hour",
    y="TotalRevenue",
    markers=True,
    title="Sales by Hour",
    template="plotly_white"
)

fig.update_layout(height=420)

left.plotly_chart(
    fig,
    width="stretch"
)

days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

weekday["DayName"] = weekday["DayName"].astype(str)

weekday["DayName"] = (
    weekday["DayName"]
    .str.strip()
    .str.title()
)

weekday["DayName"] = weekday["DayName"].astype(
    "category"
)

weekday["DayName"] = weekday["DayName"].cat.set_categories(
    days,
    ordered=True
)

weekday = weekday.sort_values("DayName")

fig = px.bar(
    weekday,
    x="DayName",
    y="TotalRevenue",
    title="Sales by Weekday",
    color="TotalRevenue",
    color_continuous_scale="Oranges",
    template="plotly_white"
)

fig.update_layout(height=420)

right.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# CUSTOMER ANALYSIS
# --------------------------------------------------

st.markdown("---")
st.markdown("## 👥 Customer Analysis")

left, right = st.columns(2)

fig = px.pie(
    segments,
    values="Customers",
    names="CustomerSegment",
    title="Customer Segments",
    hole=0.45
)

left.plotly_chart(
    fig,
    width="stretch"
)

fig = px.bar(
    customers,
    x="CustomerID",
    y="TotalRevenue",
    title="Top Customers",
    color="TotalRevenue",
    color_continuous_scale="Purples",
    template="plotly_white"
)

fig.update_layout(height=420)

right.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# BUSINESS GROWTH
# --------------------------------------------------

st.markdown("---")
st.markdown("## 📊 Business Growth")

growth = growth.dropna(subset=["GrowthPercent"])

fig = px.bar(
    growth,
    x="MonthDate",
    y="GrowthPercent",
    title="Month-over-Month Revenue Growth",
    color="GrowthPercent",
    color_continuous_scale="RdYlGn",
    template="plotly_white"
)

fig.update_layout(height=450)

st.plotly_chart(
    fig,
    width="stretch"
)

# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------

st.markdown("---")
st.markdown("## 📋 Executive Summary")

highest_month = monthly.loc[
    monthly["TotalRevenue"].idxmax()
]

top_country = country.iloc[0]

top_product = products.iloc[0]

peak_hour = hour.loc[
    hour["TotalRevenue"].idxmax()
]

st.success(
    f"""
### Key Business Insights

💰 **Total Revenue:** {format_currency(kpis["Total Revenue"])}

📈 **Highest Revenue Month:** {highest_month["MonthName"]} {highest_month["Year"]}

🌍 **Top Market:** {top_country["Country"]}

🏆 **Best Selling Product:** {top_product["Description"]}

⏰ **Peak Sales Hour:** {int(peak_hour["Hour"])}:00

👥 **Active Customers:** {kpis["Total Customers"]:,}
"""
)

st.info(
    """
### Business Recommendations

• Increase inventory before peak sales months.

• Prioritize marketing in the highest revenue markets.

• Promote top-selling products more aggressively.

• Schedule campaigns around peak purchasing hours.

• Develop loyalty offers for high-value customers.
"""
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")
