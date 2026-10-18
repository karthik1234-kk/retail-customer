"""
retail-customer-360: Database Connector Module
Provides unified interface for MySQL connection with automatic SQLite staging fallback
so the entire analytics pipeline runs reliably in any environment.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from config import DB_CONFIG, SQLITE_DB_PATH, RAW_DATA_DIR, SQL_DIR


class DatabaseManager:
    def __init__(self, use_mysql_if_available=True):
        self.use_mysql_if_available = use_mysql_if_available
        self.engine_type = "sqlite"  # Default fallback
        self.mysql_conn = None
        self.sqlite_conn = None
        
        if self.use_mysql_if_available:
            self._try_connect_mysql()
            
        if self.engine_type != "mysql":
            self._init_sqlite()

    def _try_connect_mysql(self):
        """Attempts to connect to MySQL server if connector and credentials work."""
        try:
            # Check for pymysql or mysql.connector
            try:
                import pymysql
                self.mysql_conn = pymysql.connect(
                    host=DB_CONFIG["host"],
                    port=DB_CONFIG["port"],
                    user=DB_CONFIG["user"],
                    password=DB_CONFIG["password"],
                    database=DB_CONFIG["database"]
                )
                self.engine_type = "mysql"
                print("[INFO] Connected successfully to MySQL database 'retail_360'.")
            except ImportError:
                try:
                    import mysql.connector
                    self.mysql_conn = mysql.connector.connect(
                        host=DB_CONFIG["host"],
                        port=DB_CONFIG["port"],
                        user=DB_CONFIG["user"],
                        password=DB_CONFIG["password"],
                        database=DB_CONFIG["database"]
                    )
                    self.engine_type = "mysql"
                    print("[INFO] Connected successfully to MySQL database 'retail_360'.")
                except ImportError:
                    # Neither connector installed, use SQLite fallback
                    pass
        except Exception as e:
            print(f"[INFO] MySQL direct connection skipped ({e}). Using embedded SQLite database.")
            self.engine_type = "sqlite"

    def _init_sqlite(self):
        """Initializes SQLite database with schema and raw data for standalone execution."""
        self.sqlite_conn = sqlite3.connect(str(SQLITE_DB_PATH))
        self.engine_type = "sqlite"
        
        # Load raw CSVs into SQLite tables if they exist
        cust_csv = RAW_DATA_DIR / "customers.csv"
        prod_csv = RAW_DATA_DIR / "products.csv"
        ord_csv = RAW_DATA_DIR / "orders.csv"
        
        if cust_csv.exists() and prod_csv.exists() and ord_csv.exists():
            df_cust = pd.read_csv(cust_csv)
            df_prod = pd.read_csv(prod_csv)
            df_ord = pd.read_csv(ord_csv)
            
            df_cust.to_sql("customers", self.sqlite_conn, if_exists="replace", index=False)
            df_prod.to_sql("products", self.sqlite_conn, if_exists="replace", index=False)
            df_ord.to_sql("orders", self.sqlite_conn, if_exists="replace", index=False)

    def get_tables_dataframes(self):
        """Loads customers, products, orders as pandas DataFrames from the active database."""
        conn = self.mysql_conn if self.engine_type == "mysql" else self.sqlite_conn
        
        df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
        df_products = pd.read_sql_query("SELECT * FROM products", conn)
        df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
        
        return df_customers, df_products, df_orders

    def execute_query(self, query):
        """Executes a SQL query and returns result DataFrame."""
        conn = self.mysql_conn if self.engine_type == "mysql" else self.sqlite_conn
        return pd.read_sql_query(query, conn)

    def close(self):
        """Closes active database connections."""
        if self.mysql_conn:
            self.mysql_conn.close()
        if self.sqlite_conn:
            self.sqlite_conn.close()
