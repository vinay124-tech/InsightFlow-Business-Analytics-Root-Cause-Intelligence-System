from src.database import create_database
from src.queries import *

create_database()

print(get_kpis())
print(get_monthly_sales().head())
print(get_country_sales())
print(get_top_products())
print(get_sales_by_hour())
print(get_sales_by_weekday())
print(get_monthly_orders())
print(get_top_customers())