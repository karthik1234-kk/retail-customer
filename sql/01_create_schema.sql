-- ============================================================================
-- Project: Retail Customer 360 Performance Dashboard
-- File: 01_create_schema.sql
-- Description: MySQL DDL Schema Definition for retail_360 database
-- Author: Senior Data Engineer & Analyst
-- ============================================================================

-- 1. Create Database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS retail_360
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE retail_360;

-- 2. Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ----------------------------------------------------------------------------
-- Table 1: customers
-- Stores customer demographic and geographic profile attributes
-- ----------------------------------------------------------------------------
CREATE TABLE customers (
    customer_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT NULL,
    gender VARCHAR(20) NOT NULL,
    location VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add index on location for geographic query acceleration
CREATE INDEX idx_customers_location ON customers(location);


-- ----------------------------------------------------------------------------
-- Table 2: products
-- Master catalog containing retail items, categories, selling prices, and unit costs
-- ----------------------------------------------------------------------------
CREATE TABLE products (
    product_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT chk_price_positive CHECK (price >= 0),
    CONSTRAINT chk_cost_positive CHECK (cost >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add index on category for category-level rollups
CREATE INDEX idx_products_category ON products(category);


-- ----------------------------------------------------------------------------
-- Table 3: orders
-- Transactional fact table tracking customer purchases with foreign keys
-- ----------------------------------------------------------------------------
CREATE TABLE orders (
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    order_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id) 
        ON UPDATE CASCADE 
        ON DELETE CASCADE,
    CONSTRAINT chk_quantity_positive CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Composite & lookup indexes for high-performance aggregations
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_product_id ON orders(product_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_date_cust ON orders(order_date, customer_id);

-- Display created schema verification
SHOW TABLES;
