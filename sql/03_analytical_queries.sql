-- ============================================================================
-- Project: Retail Customer 360 Performance Dashboard
-- File: 03_analytical_queries.sql
-- Description: Core Analytical SQL Queries for Business Insights
-- Author: Senior Data Engineer & Analyst
-- ============================================================================

USE retail_360;

-- ----------------------------------------------------------------------------
-- QUERY 1: Executive KPI Summary (Total Revenue, Total Profit, Orders, AOV)
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_active_customers,
    SUM(o.quantity) AS total_units_sold,
    ROUND(SUM(o.quantity * p.price), 2) AS total_revenue,
    ROUND(SUM(o.quantity * p.cost), 2) AS total_cost,
    ROUND(SUM(o.quantity * (p.price - p.cost)), 2) AS total_profit,
    ROUND((SUM(o.quantity * (p.price - p.cost)) / SUM(o.quantity * p.price)) * 100, 2) AS gross_profit_margin_pct,
    ROUND(SUM(o.quantity * p.price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value_aov
FROM orders o
JOIN products p ON o.product_id = p.product_id;


-- ----------------------------------------------------------------------------
-- QUERY 2: Top 10 Customers by Revenue Contribution
-- ----------------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.name AS customer_name,
    c.location,
    c.gender,
    c.age,
    COUNT(DISTINCT o.order_id) AS total_orders_placed,
    SUM(o.quantity) AS total_items_purchased,
    ROUND(SUM(o.quantity * p.price), 2) AS total_spend,
    ROUND(SUM(o.quantity * (p.price - p.cost)), 2) AS total_profit_generated,
    ROUND(SUM(o.quantity * p.price) / COUNT(DISTINCT o.order_id), 2) AS customer_aov,
    MAX(o.order_date) AS most_recent_order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name, c.location, c.gender, c.age
ORDER BY total_spend DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- QUERY 3: Sales Performance & Profitability by Product Category
-- ----------------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) AS unique_products_in_catalog,
    COUNT(o.order_id) AS total_orders_count,
    SUM(o.quantity) AS total_units_sold,
    ROUND(SUM(o.quantity * p.price), 2) AS category_revenue,
    ROUND(SUM(o.quantity * p.cost), 2) AS category_cost,
    ROUND(SUM(o.quantity * (p.price - p.cost)), 2) AS category_profit,
    ROUND((SUM(o.quantity * (p.price - p.cost)) / SUM(o.quantity * p.price)) * 100, 2) AS profit_margin_pct,
    ROUND(
        (SUM(o.quantity * p.price) / 
            (SELECT SUM(ord.quantity * prd.price) FROM orders ord JOIN products prd ON ord.product_id = prd.product_id)
        ) * 100, 2
    ) AS revenue_contribution_pct
FROM products p
JOIN orders o ON p.product_id = o.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- ----------------------------------------------------------------------------
-- QUERY 4: Monthly Sales, Revenue & Profit Growth Trends
-- ----------------------------------------------------------------------------
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') AS order_year_month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS monthly_active_customers,
    SUM(o.quantity) AS total_quantity_sold,
    ROUND(SUM(o.quantity * p.price), 2) AS monthly_revenue,
    ROUND(SUM(o.quantity * (p.price - p.cost)), 2) AS monthly_profit,
    ROUND((SUM(o.quantity * (p.price - p.cost)) / SUM(o.quantity * p.price)) * 100, 2) AS monthly_profit_margin_pct,
    ROUND(SUM(o.quantity * p.price) / COUNT(DISTINCT o.order_id), 2) AS monthly_aov
FROM orders o
JOIN products p ON o.product_id = p.product_id
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY order_year_month ASC;


-- ----------------------------------------------------------------------------
-- QUERY 5: Customer Order Frequency Distribution (Repeat vs One-Time Buyers)
-- ----------------------------------------------------------------------------
WITH CustomerOrderCounts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN '1 Order (One-Time)'
        WHEN order_count BETWEEN 2 AND 4 THEN '2 - 4 Orders (Occasional)'
        WHEN order_count BETWEEN 5 AND 9 THEN '5 - 9 Orders (Regular)'
        ELSE '10+ Orders (Power Buyer)'
    END AS purchase_frequency_tier,
    COUNT(customer_id) AS customer_count,
    ROUND((COUNT(customer_id) / (SELECT COUNT(*) FROM CustomerOrderCounts)) * 100, 2) AS pct_of_customer_base
FROM CustomerOrderCounts
GROUP BY purchase_frequency_tier
ORDER BY customer_count DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Customer Recency & Churn Risk Overview
-- ----------------------------------------------------------------------------
WITH CustomerRecency AS (
    SELECT 
        c.customer_id,
        c.name,
        MAX(o.order_date) AS last_order_date,
        DATEDIFF('2025-04-01', MAX(o.order_date)) AS days_since_last_purchase,
        COUNT(o.order_id) AS order_frequency,
        ROUND(SUM(o.quantity * p.price), 2) AS monetary_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN products p ON o.product_id = p.product_id
    GROUP BY c.customer_id, c.name
)
SELECT 
    CASE 
        WHEN days_since_last_purchase <= 60 THEN 'Active (<= 60 days)'
        WHEN days_since_last_purchase BETWEEN 61 AND 150 THEN 'Warm (61 - 150 days)'
        WHEN days_since_last_purchase BETWEEN 151 AND 270 THEN 'Cooling Off (151 - 270 days)'
        ELSE 'At Risk / Inactive (> 270 days)'
    END AS customer_recency_status,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(monetary_value), 2) AS total_spend_in_tier,
    ROUND(AVG(monetary_value), 2) AS avg_spend_per_customer
FROM CustomerRecency
GROUP BY customer_recency_status
ORDER BY customer_count DESC;
