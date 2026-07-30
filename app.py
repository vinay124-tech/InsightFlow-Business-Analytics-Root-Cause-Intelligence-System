import streamlit as st
import plotly.express as px
from src.queries import *

# Page setup
st.set_page_config(
    page_title="InsightFlow",
    page_icon="📊",
    layout="wide"
)

st.title("📊 InsightFlow")
st.subheader("Business Analytics & Root Cause Intelligence System")

# KPI Cards for all metrics 

kpis = get_kpis()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Revenue",
    f"₹{kpis['Total Revenue']:,.0f}"
)

col2.metric(
    "Orders",
    f"{kpis['Total Orders']:,}"
)

col3.metric(
    "Customers",
    f"{kpis['Total Customers']:,}"
)

col4.metric(
    "Products",
    f"{kpis['Total Products']:,}"
)

col5.metric(
    "Avg Order",
    f"₹{kpis['Average Order Value']:,.2f}"
)

# Monthly revenue chart 

monthly = get_monthly_sales()

fig = px.line(monthly, x="MonthName", y="TotalRevenue", color="Year", markers=True, title="Monthly Revenue Trend")

st.plotly_chart(fig, use_container_width=True)


# 2 coulmn layout for next coming charts

left,right = st.columns(2)


# country revenue

country = get_country_sales()

fig = px.bar(
    country,
    x="Country",
    y="TotalRevenue",
    title="Revenue by Country"
)

left.plotly_chart(fig,use_container_width=True)

# Top products

products = get_top_products()

fig = px.bar(
    products,
    x="TotalRevenue",
    y="Description",
    orientation="h",
    title="Top Products"
)

right.plotly_chart(fig,use_container_width=True)

# sales by hour

left,right = st.columns(2)

hour = get_sales_by_hour()

fig = px.line(
    hour,
    x="Hour",
    y="TotalRevenue",
    markers=True,
    title="Sales by Hour"
)

left.plotly_chart(fig,use_container_width=True)

# weekday sales chart

weekday = get_sales_by_weekday()

fig = px.bar(
    weekday,
    x="DayName",
    y="TotalRevenue",
    title="Sales by Weekday"
)

right.plotly_chart(fig,use_container_width=True)

# cutomer segments 

left,right = st.columns(2)

segment = get_customer_segments()

fig = px.pie(
    segment,
    values="Customers",
    names="CustomerSegment",
    title="Customer Segments"
)

left.plotly_chart(fig,use_container_width=True)


# Month over month growth 

growth = get_month_over_month_growth()

fig = px.bar(
    growth,
    x="MonthDate",
    y="GrowthPercent",
    title="Month-over-Month Growth"
)

right.plotly_chart(fig,use_container_width=True)

# Top customers of the firm 

customers = get_top_customers()

fig = px.bar(
    customers,
    x="CustomerID",
    y="TotalRevenue",
    title="Top Customers"
)

st.plotly_chart(fig,use_container_width=True)

# Revenue Table

st.subheader("Monthly Revenue Table")

st.dataframe(
    monthly,
    use_container_width=True
)
