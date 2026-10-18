"""
retail-customer-360: Export Dashboard Datasets Module
Exports processed, cleaned, and enriched datasets to outputs/ directory
formatted specifically for Power BI reporting and visualization.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from pathlib import Path
import pandas as pd
from config import OUTPUT_DIR
from data_processing import RetailDataPipeline


def export_all_datasets(pipeline=None):
    """
    Executes pipeline and exports the 4 core Power BI dashboard datasets:
    1. customers_cleaned.csv
    2. sales_summary.csv
    3. customer_segments.csv
    4. monthly_trends.csv
    """
    if pipeline is None:
        pipeline = RetailDataPipeline()
        sales_master, customer_segments, monthly_trends = pipeline.run_pipeline()
    else:
        sales_master = pipeline.sales_master
        customer_segments = pipeline.customer_segments_df
        monthly_trends = pipeline.monthly_trends_df

    print("[INFO] Exporting cleaned and aggregated datasets to outputs/ folder...")

    # 1. customers_cleaned.csv
    customers_cleaned = pipeline.get_cleaned_customers()
    cust_file = OUTPUT_DIR / "customers_cleaned.csv"
    customers_cleaned.to_csv(cust_file, index=False)
    print(f"[EXPORT] Created: {cust_file} ({len(customers_cleaned)} rows)")

    # 2. sales_summary.csv
    # Select cleanest analytical columns for the Star-Schema Fact table in Power BI
    sales_cols = [
        "order_id", "customer_id", "product_id", "order_date", "order_year_month",
        "order_year", "order_quarter", "day_of_week",
        "product_name", "category", "price", "cost", "quantity",
        "total_amount", "total_cost", "profit", "profit_margin_pct",
        "name", "age", "age_group", "gender", "location"
    ]
    sales_summary = sales_master[sales_cols].copy()
    sales_file = OUTPUT_DIR / "sales_summary.csv"
    sales_summary.to_csv(sales_file, index=False)
    print(f"[EXPORT] Created: {sales_file} ({len(sales_summary)} rows)")

    # 3. customer_segments.csv
    # RFM, CLV, and behavioral attributes
    segment_cols = [
        "customer_id", "name", "age", "age_group", "gender", "location",
        "recency_days", "frequency", "monetary_value", "monetary_profit",
        "r_score", "f_score", "m_score", "rfm_code", "rfm_weighted_score",
        "customer_segment", "rfm_persona", "average_order_value", "clv"
    ]
    customer_segments_export = customer_segments[segment_cols].copy()
    seg_file = OUTPUT_DIR / "customer_segments.csv"
    customer_segments_export.to_csv(seg_file, index=False)
    print(f"[EXPORT] Created: {seg_file} ({len(customer_segments_export)} rows)")

    # 4. monthly_trends.csv
    trend_file = OUTPUT_DIR / "monthly_trends.csv"
    monthly_trends.to_csv(trend_file, index=False)
    print(f"[EXPORT] Created: {trend_file} ({len(monthly_trends)} rows)")

    print("[SUCCESS] All 4 Power BI datasets exported successfully!\n")
    return {
        "customers_cleaned": cust_file,
        "sales_summary": sales_file,
        "customer_segments": seg_file,
        "monthly_trends": trend_file
    }


if __name__ == "__main__":
    export_all_datasets()
