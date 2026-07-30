from src.database import get_connection


def get_kpis():
    with get_connection() as con:

        total_revenue = con.execute("""
            SELECT SUM(Revenue)
            FROM retail
        """).fetchone()[0]

        total_orders = con.execute("""
            SELECT COUNT(DISTINCT Invoice)
            FROM retail
        """).fetchone()[0]

        total_customers = con.execute("""
            SELECT COUNT(DISTINCT "Customer ID")
            FROM retail
            WHERE "Customer ID" IS NOT NULL
        """).fetchone()[0]

        total_products = con.execute("""
            SELECT COUNT(DISTINCT StockCode)
            FROM retail
        """).fetchone()[0]

        average_order_value = con.execute("""
            SELECT AVG(order_total)
            FROM (
                SELECT Invoice,
                       SUM(Revenue) AS order_total
                FROM retail
                GROUP BY Invoice
            )
        """).fetchone()[0]

        return {
            "Total Revenue": total_revenue,
            "Total Orders": total_orders,
            "Total Customers": total_customers,
            "Total Products": total_products,
            "Average Order Value": average_order_value,
        }


# Total Monthly sales     
def get_monthly_sales():
    query = """
    SELECT
        Year,
        Month,
        MonthName,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    GROUP BY Year, Month, MonthName
    ORDER BY Year, Month;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
# sales by country
def get_country_sales(limit=10):
    query = f"""
    SELECT
        Country,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    GROUP BY Country
    ORDER BY TotalRevenue DESC
    LIMIT {limit};
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#  top selling products   
def get_top_products(limit=10):
    query = f"""
    SELECT
        Description,
        SUM(Quantity) AS UnitsSold,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    WHERE Description IS NOT NULL
    GROUP BY Description
    ORDER BY TotalRevenue DESC
    LIMIT {limit};
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
 
#sales by hr   
def get_sales_by_hour():
    query = """
    SELECT
        Hour,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    GROUP BY Hour
    ORDER BY Hour;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()


#sales by weekday
def get_sales_by_weekday():
    query = """
    SELECT
        DayName,
        Weekday,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    GROUP BY DayName, Weekday
    ORDER BY Weekday;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#montly orders
def get_monthly_orders():
    query = """
    SELECT
        Year,
        Month,
        MonthName,
        COUNT(DISTINCT Invoice) AS TotalOrders
    FROM retail
    GROUP BY Year, Month, MonthName
    ORDER BY Year, Month;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#Top customers by revenue
def get_top_customers(limit=10):
    query = f"""
    SELECT
        "Customer ID" AS CustomerID,
        SUM(Revenue) AS TotalRevenue
    FROM retail
    WHERE "Customer ID" IS NOT NULL
    GROUP BY "Customer ID"
    ORDER BY TotalRevenue DESC
    LIMIT {limit};
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    


## Advanced metrics 

# Month over month revenue growth 
def get_month_over_month_growth():
    query = """
    WITH monthly_sales AS (
        SELECT
            MAKE_DATE(Year, Month, 1) AS MonthDate,
            Year,
            Month,
            MonthName,
            SUM(Revenue) AS TotalRevenue
        FROM retail
        GROUP BY Year, Month, MonthName
    )

    SELECT
        MAKE_DATE(Year, Month, 1) AS MonthDate,
        Year,
        Month,
        MonthName,
        TotalRevenue,

        LAG(TotalRevenue) OVER (
            ORDER BY Year, Month
        ) AS PreviousMonthRevenue,

        ROUND(
            (
                (TotalRevenue - LAG(TotalRevenue) OVER (ORDER BY Year, Month))
                /
                LAG(TotalRevenue) OVER (ORDER BY Year, Month)
            ) * 100,
            2
        ) AS GrowthPercent

    FROM monthly_sales
    ORDER BY Year, Month;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#country performance
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

        ROUND(AVG(OrderValue),2) AS AverageOrderValue

    FROM order_totals

    GROUP BY Country

    ORDER BY TotalRevenue DESC;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#customer segmentation
def get_customer_segments():
    query = """
    WITH customer_sales AS (

        SELECT

            "Customer ID" AS CustomerID,

            SUM(Revenue) AS TotalSpent

        FROM retail

        WHERE "Customer ID" IS NOT NULL

        GROUP BY "Customer ID"

    )

    SELECT

        CASE

            WHEN TotalSpent >= 10000 THEN 'High Value'

            WHEN TotalSpent >= 3000 THEN 'Medium Value'

            ELSE 'Low Value'

        END AS CustomerSegment,

        COUNT(*) AS Customers,

        ROUND(AVG(TotalSpent),2) AS AverageSpend

    FROM customer_sales

    GROUP BY CustomerSegment

    ORDER BY AverageSpend DESC;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#Declining products
def get_top_declining_products(limit=10):
    query = f"""
    WITH monthly_product_sales AS (

        SELECT

            Description,

            Year,

            Month,

            SUM(Revenue) AS Revenue

        FROM retail

        WHERE Description IS NOT NULL

        GROUP BY Description, Year, Month

    ),

    product_growth AS (

        SELECT

            Description,

            Year,

            Month,

            Revenue,

            Revenue
            -
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

    LIMIT {limit};
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()
    
#country revenue contribution
def get_sales_contribution():
    query = """
    SELECT

        Country,

        SUM(Revenue) AS Revenue,

        ROUND(
            SUM(Revenue) * 100.0 /
            (SELECT SUM(Revenue) FROM retail),
            2
        ) AS ContributionPercent

    FROM retail

    GROUP BY Country

    ORDER BY Revenue DESC;
    """

    with get_connection() as con:
        return con.execute(query).fetchdf()

































