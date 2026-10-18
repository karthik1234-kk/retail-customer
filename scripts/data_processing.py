"""
retail-customer-360: Python Data Processing & Advanced Analytics Module
Performs data cleaning, feature engineering, RFM scoring, Customer Lifetime Value (CLV),
and Customer Segmentation using pandas and numpy.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from datetime import datetime
import numpy as np
import pandas as pd
from config import AGE_BINS, AGE_LABELS
from db_connector import DatabaseManager


class RetailDataPipeline:
    def __init__(self):
        self.db = DatabaseManager()
        self.df_customers = None
        self.df_products = None
        self.df_orders = None
        self.sales_master = None
        self.customer_segments_df = None
        self.monthly_trends_df = None

    def load_data(self):
        """Loads raw tables from database."""
        print(f"[INFO] Ingesting tables from database engine: {self.db.engine_type}...")
        self.df_customers, self.df_products, self.df_orders = self.db.get_tables_dataframes()
        print(f"[SUCCESS] Loaded {len(self.df_customers)} customers, {len(self.df_products)} products, {len(self.df_orders)} orders.")

    def clean_data(self):
        """
        Cleans data:
        - Handles null values
        - Removes duplicate records
        - Enforces correct data types
        """
        print("[INFO] Executing data quality and cleaning routines...")
        
        # 1. Inspect and handle duplicates
        order_dups = self.df_orders.duplicated(subset=["order_id"]).sum()
        if order_dups > 0:
            print(f"[CLEAN] Found {order_dups} duplicate order records. Removing duplicates...")
            self.df_orders = self.df_orders.drop_duplicates(subset=["order_id"]).reset_index(drop=True)
            
        cust_dups = self.df_customers.duplicated(subset=["customer_id"]).sum()
        if cust_dups > 0:
            self.df_customers = self.df_customers.drop_duplicates(subset=["customer_id"]).reset_index(drop=True)
            
        # 2. Inspect and handle null values
        cust_null_age = self.df_customers["age"].isnull().sum()
        if cust_null_age > 0:
            median_age = int(self.df_customers["age"].median())
            print(f"[CLEAN] Imputing {cust_null_age} missing customer ages with median age ({median_age}).")
            self.df_customers["age"] = self.df_customers["age"].fillna(median_age)
            
        cust_null_loc = self.df_customers["location"].isnull().sum()
        if cust_null_loc > 0:
            print(f"[CLEAN] Filling {cust_null_loc} missing customer locations with 'Unknown'.")
            self.df_customers["location"] = self.df_customers["location"].fillna("Unknown")
            
        # 3. Type casting & format checks
        self.df_customers["customer_id"] = self.df_customers["customer_id"].astype(int)
        self.df_customers["age"] = self.df_customers["age"].astype(int)
        
        self.df_products["product_id"] = self.df_products["product_id"].astype(int)
        self.df_products["price"] = self.df_products["price"].astype(float)
        self.df_products["cost"] = self.df_products["cost"].astype(float)
        
        self.df_orders["order_id"] = self.df_orders["order_id"].astype(int)
        self.df_orders["customer_id"] = self.df_orders["customer_id"].astype(int)
        self.df_orders["product_id"] = self.df_orders["product_id"].astype(int)
        self.df_orders["quantity"] = self.df_orders["quantity"].astype(int)
        self.df_orders["order_date"] = pd.to_datetime(self.df_orders["order_date"])
        
        print("[SUCCESS] Data quality checks and cleaning completed.")

    def feature_engineering(self):
        """
        Feature Engineering:
        - Calculates total_amount = quantity * price
        - Calculates unit_profit = price - cost
        - Calculates total_profit = (price - cost) * quantity
        - Calculates profit_margin_pct
        - Creates age_group categorical column
        """
        print("[INFO] Performing feature engineering...")
        
        # Merge orders with products and customers to build master sales dataframe
        merged = self.df_orders.merge(self.df_products, on="product_id", how="inner")
        merged = merged.merge(self.df_customers, on="customer_id", how="inner")
        
        # 1. Total Amount
        merged["total_amount"] = (merged["quantity"] * merged["price"]).round(2)
        
        # 2. Total Cost
        merged["total_cost"] = (merged["quantity"] * merged["cost"]).round(2)
        
        # 3. Unit Profit and Total Profit
        merged["unit_profit"] = (merged["price"] - merged["cost"]).round(2)
        merged["profit"] = (merged["total_amount"] - merged["total_cost"]).round(2)
        
        # 4. Profit Margin Percentage
        merged["profit_margin_pct"] = np.where(
            merged["total_amount"] > 0,
            ((merged["profit"] / merged["total_amount"]) * 100).round(2),
            0.0
        )
        
        # 5. Age Groups
        self.df_customers["age_group"] = pd.cut(
            self.df_customers["age"],
            bins=AGE_BINS,
            labels=AGE_LABELS,
            right=True
        )
        merged["age_group"] = pd.cut(
            merged["age"],
            bins=AGE_BINS,
            labels=AGE_LABELS,
            right=True
        )
        
        # 6. Date Features
        merged["order_year_month"] = merged["order_date"].dt.strftime("%Y-%m")
        merged["order_year"] = merged["order_date"].dt.year
        merged["order_month"] = merged["order_date"].dt.month
        merged["order_quarter"] = "Q" + merged["order_date"].dt.quarter.astype(str)
        merged["day_of_week"] = merged["order_date"].dt.day_name()
        
        self.sales_master = merged
        print(f"[SUCCESS] Master sales dataset enriched with {self.sales_master.shape[1]} engineered features.")

    def perform_analytics(self):
        """
        Performs RFM Analysis, Customer Segmentation, and Customer Lifetime Value (CLV).
        """
        print("[INFO] Computing RFM metrics, Customer Lifetime Value (CLV), and Value Segments...")
        
        # Reference Snapshot Date for Recency calculation: 1 day after the latest order date
        snapshot_date = self.sales_master["order_date"].max() + pd.Timedelta(days=1)
        
        # Aggregate customer-level transactions
        rfm = self.sales_master.groupby("customer_id").agg({
            "order_date": lambda dates: (snapshot_date - dates.max()).days,  # Recency
            "order_id": "nunique",                                           # Frequency
            "total_amount": "sum",                                          # Monetary Value
            "profit": "sum"                                                 # Total Profit
        }).reset_index()
        
        rfm.rename(columns={
            "order_date": "recency_days",
            "order_id": "frequency",
            "total_amount": "monetary_value",
            "profit": "monetary_profit"
        }, inplace=True)
        
        rfm["monetary_value"] = rfm["monetary_value"].round(2)
        rfm["monetary_profit"] = rfm["monetary_profit"].round(2)
        
        # Merge customer demographic details
        rfm = rfm.merge(
            self.df_customers[["customer_id", "name", "age", "age_group", "gender", "location"]],
            on="customer_id",
            how="left"
        )
        
        # --- RFM Scoring (1 to 5) ---
        # Recency: Lower is better -> reverse scoring (5 is most recent)
        rfm["r_score"] = pd.qcut(rfm["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
        
        # Frequency: Higher is better (rank method handles duplicate ties)
        rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Monetary: Higher is better
        rfm["m_score"] = pd.qcut(rfm["monetary_value"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
        
        # Combined RFM Code
        rfm["rfm_code"] = (
            rfm["r_score"].astype(str) + 
            rfm["f_score"].astype(str) + 
            rfm["m_score"].astype(str)
        )
        
        # Weighted RFM Score (Weights: R=0.20, F=0.30, M=0.50)
        rfm["rfm_weighted_score"] = (
            0.20 * rfm["r_score"] + 
            0.30 * rfm["f_score"] + 
            0.50 * rfm["m_score"]
        ).round(2)
        
        # --- Customer Segmentation (High, Medium, Low Value) ---
        # Requirement: High, Medium, Low value tiers
        def assign_tier(row):
            score = row["rfm_weighted_score"]
            if score >= 3.8:
                return "High Value"
            elif score >= 2.4:
                return "Medium Value"
            else:
                return "Low Value"
                
        def assign_detailed_segment(row):
            r = row["r_score"]
            f = row["f_score"]
            m = row["m_score"]
            
            if r >= 4 and f >= 4 and m >= 4:
                return "Champions"
            elif r >= 3 and f >= 3:
                return "Loyal Customers"
            elif r >= 4 and f <= 2:
                return "Recent Shoppers"
            elif r <= 2 and f >= 3:
                return "At Risk"
            elif r <= 2 and f <= 2 and m <= 2:
                return "Hibernating / Lost"
            else:
                return "Potential Loyalists"
                
        rfm["customer_segment"] = rfm.apply(assign_tier, axis=1)
        rfm["rfm_persona"] = rfm.apply(assign_detailed_segment, axis=1)
        
        # --- Customer Lifetime Value (CLV) ---
        # Formula: CLV = (Average Order Value) * (Purchase Frequency per Year) * (Average Customer Lifespan)
        # Assuming an estimated retail industry customer lifespan of 3 years and profit margin weighting:
        rfm["average_order_value"] = (rfm["monetary_value"] / rfm["frequency"]).round(2)
        
        # Time active in years (from first order to last order, or minimum 0.25 years)
        customer_lifespans = self.sales_master.groupby("customer_id").agg(
            first_order=("order_date", "min"),
            last_order=("order_date", "max")
        ).reset_index()
        customer_lifespans["active_days"] = (customer_lifespans["last_order"] - customer_lifespans["first_order"]).dt.days
        rfm = rfm.merge(customer_lifespans[["customer_id", "active_days"]], on="customer_id", how="left")
        
        # Annualized frequency
        annual_frequency = np.maximum(rfm["frequency"], 1.0)
        profit_margin_ratio = np.where(rfm["monetary_value"] > 0, rfm["monetary_profit"] / rfm["monetary_value"], 0.40)
        
        # Standard CLV projection (3-year horizon with margin factor)
        rfm["clv"] = (rfm["average_order_value"] * annual_frequency * profit_margin_ratio * 3.0).round(2)
        
        self.customer_segments_df = rfm
        
        # --- Monthly Trends Aggregation ---
        monthly = self.sales_master.groupby("order_year_month").agg(
            total_orders=("order_id", "nunique"),
            total_units=("quantity", "sum"),
            monthly_revenue=("total_amount", "sum"),
            monthly_cost=("total_cost", "sum"),
            monthly_profit=("profit", "sum"),
            active_customers=("customer_id", "nunique")
        ).reset_index()
        
        monthly["monthly_revenue"] = monthly["monthly_revenue"].round(2)
        monthly["monthly_cost"] = monthly["monthly_cost"].round(2)
        monthly["monthly_profit"] = monthly["monthly_profit"].round(2)
        monthly["profit_margin_pct"] = ((monthly["monthly_profit"] / monthly["monthly_revenue"]) * 100).round(2)
        monthly["average_order_value"] = (monthly["monthly_revenue"] / monthly["total_orders"]).round(2)
        
        self.monthly_trends_df = monthly
        
        print("[SUCCESS] Customer analytics, RFM, CLV, and monthly aggregation completed.")

    def get_cleaned_customers(self):
        """Returns cleaned customers enriched with order summaries."""
        cust_summary = self.customer_segments_df[[
            "customer_id", "name", "age", "age_group", "gender", "location",
            "frequency", "monetary_value", "monetary_profit", "customer_segment"
        ]].copy()
        cust_summary.rename(columns={
            "frequency": "total_orders",
            "monetary_value": "total_spend",
            "monetary_profit": "total_profit"
        }, inplace=True)
        return cust_summary

    def run_pipeline(self):
        """Runs end-to-end data processing workflow."""
        self.load_data()
        self.clean_data()
        self.feature_engineering()
        self.perform_analytics()
        self.db.close()
        return self.sales_master, self.customer_segments_df, self.monthly_trends_df


if __name__ == "__main__":
    pipeline = RetailDataPipeline()
    sales, segments, trends = pipeline.run_pipeline()
    print("\n--- Pipeline Sample Output ---")
    print("\n[Customer Segments Sample]")
    print(segments[["customer_id", "name", "recency_days", "frequency", "monetary_value", "customer_segment", "clv"]].head())
    print("\n[Monthly Trends Sample]")
    print(trends.head())
