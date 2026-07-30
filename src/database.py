from pathlib import Path
import duckdb

DB_PATH = Path("data/database/retail.duckdb")
CSV_PATH = Path("data/processed/retail_clean.csv")


def create_database():
    """
    Creates the database from the cleaned CSV.
    Safe to run multiple times.
    """
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with duckdb.connect(DB_PATH) as con:

        con.execute("""
            CREATE OR REPLACE TABLE retail AS
            SELECT *
            FROM read_csv_auto(?, sample_size = -1, types={
        'Invoice':'VARCHAR',
        'StockCode':'VARCHAR',
        'Description':'VARCHAR',
        'Quantity':'INTEGER',
        'InvoiceDate':'TIMESTAMP',
        'Price':'DOUBLE',
        'Customer ID':'DOUBLE',
        'Country':'VARCHAR',
        'Revenue':'DOUBLE',
        'Year':'INTEGER',
        'Month':'INTEGER',
        'MonthName':'VARCHAR',
        'Quarter':'INTEGER',
        'Day':'INTEGER',
        'DayName':'VARCHAR',
        'Hour':'INTEGER',
        'Weekday':'INTEGER'} 
        )
        """, [str(CSV_PATH)])

        rows = con.execute("""
            SELECT COUNT(*)
            FROM retail
        """).fetchone()[0]

        print(f"Database created successfully.")
        print(f"Rows imported: {rows:,}")
        


def get_connection():
    """
    Returns a DuckDB connection.
    """

    return duckdb.connect(DB_PATH)