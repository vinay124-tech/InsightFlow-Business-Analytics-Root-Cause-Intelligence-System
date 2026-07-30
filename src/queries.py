from src.database import get_connection


# ==========================
# KPI FUNCTIONS
# ==========================

def get_kpis(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    with get_connection() as con:

        revenue = con.execute(
            f"""
            SELECT SUM(Revenue)
            FROM retail
            {where_clause}
            """,
            params
        ).fetchone()[0]

        orders = con.execute(
            f"""
            SELECT COUNT(DISTINCT Invoice)
            FROM retail
            {where_clause}
            """,
            params
        ).fetchone()[0]

        customers = con.execute(
            f"""
            SELECT COUNT(DISTINCT "Customer ID")
            FROM retail
            {where_clause}
            """,
            params
        ).fetchone()[0]

        products = con.execute(
            f"""
            SELECT COUNT(DISTINCT StockCode)
            FROM retail
            {where_clause}
            """,
            params
        ).fetchone()[0]

        avg_order = con.execute(
            f"""
            SELECT AVG(order_total)
            FROM (
                SELECT Invoice,
                       SUM(Revenue) AS order_total
                FROM retail
                {where_clause}
                GROUP BY Invoice
            )
            """,
            params
        ).fetchone()[0]

        return {
            "Total Revenue": revenue,
            "Total Orders": orders,
            "Total Customers": customers,
            "Total Products": products,
            "Average Order Value": avg_order
        }


# ==========================
# MONTHLY SALES
# ==========================

def get_monthly_sales(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    query = f"""
    SELECT

        MAKE_DATE(Year, Month, 1) AS MonthDate,
        Year,
        Month,
        MonthName,
        SUM(Revenue) AS TotalRevenue

    FROM retail

    {where_clause}

    GROUP BY
        MAKE_DATE(Year, Month, 1),
        Year,
        Month,
        MonthName

    ORDER BY MonthDate
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# COUNTRY SALES
# ==========================

def get_country_sales(limit=10):

    query = f"""
    SELECT
        Country,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    GROUP BY Country
    ORDER BY TotalRevenue DESC
    LIMIT {limit}
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()


# ==========================
# TOP PRODUCTS
# ==========================

def get_top_products(country=None, limit=10):

    params = []

    query = """
    SELECT
        Description,
        SUM(Quantity) AS UnitsSold,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    WHERE Description IS NOT NULL
    """

    if country and country != "All":
        query += " AND Country = ?"
        params.append(country)

    query += f"""
    GROUP BY Description
    ORDER BY TotalRevenue DESC
    LIMIT {limit}
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# SALES BY HOUR
# ==========================

def get_sales_by_hour(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    query = f"""
    SELECT
        Hour,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    {where_clause}
    GROUP BY Hour
    ORDER BY Hour
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# SALES BY WEEKDAY
# ==========================

def get_sales_by_weekday(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    query = f"""
    SELECT
        DayName,
        Weekday,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    {where_clause}
    GROUP BY DayName, Weekday
    ORDER BY Weekday
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# MONTHLY ORDERS
# ==========================

def get_monthly_orders(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    query = f"""
    SELECT

        MAKE_DATE(Year, Month, 1) AS MonthDate,
        Year,
        Month,
        MonthName,
        COUNT(DISTINCT Invoice) AS TotalOrders

    FROM retail

    {where_clause}

    GROUP BY
        MAKE_DATE(Year, Month, 1),
        Year,
        Month,
        MonthName

    ORDER BY MonthDate
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# TOP CUSTOMERS
# ==========================

def get_top_customers(country=None, limit=10):

    params = []

    query = """
    SELECT
        "Customer ID" AS CustomerID,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    WHERE "Customer ID" IS NOT NULL
    """

    if country and country != "All":
        query += " AND Country = ?"
        params.append(country)

    query += f"""
    GROUP BY "Customer ID"
    ORDER BY TotalRevenue DESC
    LIMIT {limit}
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()
    
# ==========================
# MONTH OVER MONTH GROWTH
# ==========================

def get_month_over_month_growth(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "WHERE Country = ?"
        params.append(country)

    query = f"""
    WITH monthly_sales AS (

        SELECT

            MAKE_DATE(Year, Month, 1) AS MonthDate,
            Year,
            Month,
            MonthName,
            SUM(Revenue) AS TotalRevenue

        FROM retail

        {where_clause}

        GROUP BY
            MAKE_DATE(Year, Month, 1),
            Year,
            Month,
            MonthName

    )

    SELECT

        MonthDate,
        Year,
        Month,
        MonthName,
        TotalRevenue,

        LAG(TotalRevenue)
        OVER(
            ORDER BY MonthDate
        ) AS PreviousMonthRevenue,

        ROUND(
            (
                (
                    TotalRevenue -
                    LAG(TotalRevenue)
                    OVER(ORDER BY MonthDate)
                )
                /
                LAG(TotalRevenue)
                OVER(ORDER BY MonthDate)
            ) * 100,
            2
        ) AS GrowthPercent

    FROM monthly_sales

    ORDER BY MonthDate
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# COUNTRY PERFORMANCE
# ==========================

def get_country_performance():

    query = """
    WITH order_totals AS (

        SELECT

            Country,
            Invoice,
            SUM(Revenue) AS OrderValue

        FROM retail

        GROUP BY Country, Invoice

    )

    SELECT

        Country,

        SUM(OrderValue) AS TotalRevenue,

        COUNT(*) AS TotalOrders,

        ROUND(
            AVG(OrderValue),
            2
        ) AS AverageOrderValue

    FROM order_totals

    GROUP BY Country

    ORDER BY TotalRevenue DESC
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()


# ==========================
# CUSTOMER SEGMENTS
# ==========================

def get_customer_segments(country=None):

    where_clause = ""
    params = []

    if country and country != "All":
        where_clause = "AND Country = ?"
        params.append(country)

    query = f"""
    WITH customer_sales AS (

        SELECT

            "Customer ID" AS CustomerID,

            SUM(Revenue) AS TotalSpent

        FROM retail

        WHERE "Customer ID" IS NOT NULL

        {where_clause}

        GROUP BY "Customer ID"

    )

    SELECT

        CASE

            WHEN TotalSpent >= 10000 THEN 'High Value'

            WHEN TotalSpent >= 3000 THEN 'Medium Value'

            ELSE 'Low Value'

        END AS CustomerSegment,

        COUNT(*) AS Customers,

        ROUND(
            AVG(TotalSpent),
            2
        ) AS AverageSpend

    FROM customer_sales

    GROUP BY CustomerSegment

    ORDER BY AverageSpend DESC
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# DECLINING PRODUCTS
# ==========================

def get_top_declining_products(country=None, limit=10):

    params = []

    where_clause = ""

    if country and country != "All":
        where_clause = "AND Country = ?"
        params.append(country)

    query = f"""
    WITH monthly_product_sales AS (

        SELECT

            Description,

            Year,

            Month,

            SUM(Revenue) AS Revenue

        FROM retail

        WHERE Description IS NOT NULL

        {where_clause}

        GROUP BY
            Description,
            Year,
            Month

    ),

    product_growth AS (

        SELECT

            Description,

            Year,

            Month,

            Revenue,

            Revenue -

            LAG(Revenue)

            OVER(

                PARTITION BY Description

                ORDER BY Year, Month

            ) AS RevenueChange

        FROM monthly_product_sales

    )

    SELECT

        Description,

        MIN(RevenueChange) AS LargestDecline

    FROM product_growth

    WHERE RevenueChange IS NOT NULL

    GROUP BY Description

    ORDER BY LargestDecline ASC

    LIMIT {limit}
    """

    with get_connection() as con:
        return con.execute(query, params).fetchdf()


# ==========================
# SALES CONTRIBUTION
# ==========================

def get_sales_contribution():

    query = """
    SELECT

        Country,

        SUM(Revenue) AS Revenue,

        ROUND(

            SUM(Revenue) * 100.0 /

            (

                SELECT SUM(Revenue)

                FROM retail

            ),

            2

        ) AS ContributionPercent

    FROM retail

    GROUP BY Country

    ORDER BY Revenue DESC
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()