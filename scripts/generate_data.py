"""
retail-customer-360: Synthetic Dataset Generator
Generates realistic retail customer, product, and order records (1500+ records).
Exports data as raw CSV files and creates MySQL INSERT statements.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
from config import RAW_DATA_DIR, SQL_DIR, NUM_CUSTOMERS, NUM_PRODUCTS, NUM_ORDERS

# Fixed seed for reproducibility
random.seed(42)

# --- Reference Lists for Realistic Data ---
FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Ananya", "Rahul", "Sneha",
    "Arjun", "Kavya", "James", "Emma", "Liam", "Olivia", "Noah", "Sophia",
    "Lucas", "Mia", "Ethan", "Isabella", "Alexander", "Charlotte", "Daniel", "Amelia",
    "Mateo", "Camila", "Mohammed", "Fatima", "Carlos", "Elena", "Chen", "Mei",
    "Takeshi", "Yuki", "David", "Sarah", "Michael", "Emily", "Rajesh", "Pooja"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Mehta", "Iyer", "Nair", "Reddy", "Gupta",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young"
]

LOCATIONS = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad",
    "New York", "Los Angeles", "Chicago", "San Francisco", "London", "Toronto", "Sydney", "Singapore"
]

PRODUCT_CATALOG = [
    # Electronics
    ("Wireless Noise-Canceling Headphones", "Electronics", 149.99, 65.00),
    ("Smartwatch Series 8", "Electronics", 299.99, 130.00),
    ("Bluetooth Portable Speaker", "Electronics", 59.99, 24.00),
    ("Ultra HD 4K Webcam", "Electronics", 89.99, 38.00),
    ("Mechanical Gaming Keyboard", "Electronics", 119.99, 50.00),
    ("Wireless Ergonomic Mouse", "Electronics", 45.99, 18.00),
    ("Fast Charging Power Bank 20000mAh", "Electronics", 39.99, 15.00),
    ("USB-C Multiport Adapter Hub", "Electronics", 34.99, 12.00),
    # Fashion & Apparel
    ("Classic Slim-Fit Denim Jeans", "Fashion", 54.99, 20.00),
    ("Organic Cotton Crewneck T-Shirt", "Fashion", 24.99, 8.00),
    ("Water-Resistant Windbreaker Jacket", "Fashion", 89.99, 35.00),
    ("Breathable Running Shoes", "Fashion", 95.00, 38.00),
    ("Polarized Aviator Sunglasses", "Fashion", 69.99, 22.00),
    ("Leather Bifold Minimalist Wallet", "Fashion", 39.99, 14.00),
    ("Cashmere Blend Winter Scarf", "Fashion", 49.99, 18.00),
    ("Canvas Everyday Backpack", "Fashion", 59.99, 22.00),
    # Home & Kitchen
    ("Stainless Steel Electric Kettle", "Home & Kitchen", 44.99, 18.00),
    ("Non-Stick Ceramic Frying Pan", "Home & Kitchen", 39.99, 16.00),
    ("Espresso & Cappuccino Maker", "Home & Kitchen", 189.99, 85.00),
    ("Digital Air Fryer 5.8 Quart", "Home & Kitchen", 119.99, 52.00),
    ("Aromatherapy Essential Oil Diffuser", "Home & Kitchen", 29.99, 11.00),
    ("Memory Foam Ergonomic Pillow", "Home & Kitchen", 49.99, 19.00),
    ("Reusable Glass Food Containers (5-Pack)", "Home & Kitchen", 34.99, 13.00),
    ("Robot Vacuum Cleaner", "Home & Kitchen", 249.99, 110.00),
    # Beauty & Health
    ("Vitamin C Brightening Facial Serum", "Beauty & Health", 28.99, 9.00),
    ("Hydrating Daily Face Moisturizer", "Beauty & Health", 22.99, 7.50),
    ("Ionic Hair Dryer with Diffuser", "Beauty & Health", 79.99, 32.00),
    ("Electric Sonic Toothbrush", "Beauty & Health", 59.99, 23.00),
    ("Organic Argan Hair Repair Oil", "Beauty & Health", 24.99, 8.00),
    ("Mineral Sunscreen SPF 50", "Beauty & Health", 19.99, 6.00),
    ("Deep Tissue Percussion Massage Gun", "Beauty & Health", 99.99, 42.00),
    ("Aroma Bath Salts & Spa Gift Set", "Beauty & Health", 32.99, 11.00),
    # Sports & Outdoors
    ("High-Density Eco-Friendly Yoga Mat", "Sports & Outdoors", 38.99, 14.00),
    ("Insulated Stainless Steel Water Bottle 32oz", "Sports & Outdoors", 29.99, 10.00),
    ("Adjustable Dumbbells Set (pair)", "Sports & Outdoors", 159.99, 70.00),
    ("Resistance Exercise Bands (Set of 5)", "Sports & Outdoors", 19.99, 6.00),
    ("Camping Hammock with Tree Straps", "Sports & Outdoors", 35.99, 13.00),
    ("Trekking Backpack 40L Waterproof", "Sports & Outdoors", 79.99, 31.00),
    ("Bicycle LED Headlight and Taillight Set", "Sports & Outdoors", 27.99, 9.50),
    ("Fitness Jump Rope with Ball Bearings", "Sports & Outdoors", 14.99, 4.50),
]


def generate_customers(num_customers=NUM_CUSTOMERS):
    """Generate realistic customer records."""
    customers = []
    genders = ["Male", "Female", "Other"]
    gender_weights = [0.48, 0.48, 0.04]

    for i in range(1, num_customers + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        
        # Realistic age distribution (peaks between 22 and 55)
        age = int(random.triangular(18, 70, 32))
        gender = random.choices(genders, weights=gender_weights)[0]
        location = random.choice(LOCATIONS)
        
        customers.append({
            "customer_id": i,
            "name": name,
            "age": age,
            "gender": gender,
            "location": location
        })
    
    df = pd.DataFrame(customers)
    
    # Introduce 3 controlled null values to simulate real-world raw dirty data
    # (e.g., missing age or missing location)
    df.loc[random.randint(10, 20), "location"] = None
    df.loc[random.randint(25, 35), "age"] = None
    
    return df


def generate_products():
    """Generate realistic product catalog."""
    products = []
    for i, (prod_name, category, price, cost) in enumerate(PRODUCT_CATALOG, start=1):
        products.append({
            "product_id": i,
            "product_name": prod_name,
            "category": category,
            "price": round(price, 2),
            "cost": round(cost, 2)
        })
    return pd.DataFrame(products)


def generate_orders(customers_df, products_df, num_orders=NUM_ORDERS):
    """Generate realistic retail orders spanning the last 15 months."""
    orders = []
    
    # Customer IDs & Product IDs
    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    
    # Bias towards repeat purchases (Pareto principle: ~20% customers generate ~60% orders)
    loyal_customers = customer_ids[: int(len(customer_ids) * 0.25)]
    casual_customers = customer_ids[int(len(customer_ids) * 0.25):]
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 3, 31)
    date_range_days = (end_date - start_date).days
    
    order_id = 1001
    for _ in range(num_orders):
        # 60% chance an order belongs to loyal customers
        if random.random() < 0.60:
            cust_id = random.choice(loyal_customers)
        else:
            cust_id = random.choice(casual_customers)
            
        prod_id = random.choice(product_ids)
        
        # Quantity follows right-skewed distribution (mostly 1 or 2, rarely 3 to 5)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
        
        # Random date with month weights to simulate seasonal peaks (Nov/Dec holiday spikes)
        random_days = random.randint(0, date_range_days)
        order_date = start_date + timedelta(days=random_days)
        
        orders.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product_id": prod_id,
            "quantity": quantity,
            "order_date": order_date.strftime("%Y-%m-%d")
        })
        order_id += 1
        
    df = pd.DataFrame(orders)
    
    # Inject 5 duplicate order entries to simulate dirty raw transactional data
    duplicates = df.sample(5, random_state=42)
    df = pd.concat([df, duplicates], ignore_index=True)
    
    return df


def export_sql_insert_script(customers_df, products_df, orders_df):
    """Generates MySQL insert statements script (sql/02_insert_data.sql)."""
    sql_file = SQL_DIR / "02_insert_data.sql"
    
    # Clean temporary copies for SQL inserts so foreign keys are satisfied
    c_clean = customers_df.copy()
    c_clean["age"] = c_clean["age"].fillna(30).astype(int)
    c_clean["location"] = c_clean["location"].fillna("Unknown")
    
    o_clean = orders_df.drop_duplicates(subset=["order_id"]).copy()
    
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("-- =========================================================\n")
        f.write("-- 02_insert_data.sql: Retail 360 Dataset Population\n")
        f.write("-- =========================================================\n")
        f.write("USE retail_360;\n\n")
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        f.write("TRUNCATE TABLE orders;\n")
        f.write("TRUNCATE TABLE products;\n")
        f.write("TRUNCATE TABLE customers;\n")
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
        
        # Customers Insert
        f.write("-- Inserting Customers\n")
        f.write("INSERT INTO customers (customer_id, name, age, gender, location) VALUES\n")
        cust_lines = []
        for _, row in c_clean.iterrows():
            name_esc = str(row['name']).replace("'", "''")
            cust_lines.append(f"({row['customer_id']}, '{name_esc}', {row['age']}, '{row['gender']}', '{row['location']}')")
        f.write(",\n".join(cust_lines) + ";\n\n")
        
        # Products Insert
        f.write("-- Inserting Products\n")
        f.write("INSERT INTO products (product_id, product_name, category, price, cost) VALUES\n")
        prod_lines = []
        for _, row in products_df.iterrows():
            pname_esc = str(row['product_name']).replace("'", "''")
            prod_lines.append(f"({row['product_id']}, '{pname_esc}', '{row['category']}', {row['price']}, {row['cost']})")
        f.write(",\n".join(prod_lines) + ";\n\n")
        
        # Orders Insert in batches of 200
        f.write("-- Inserting Orders\n")
        batch_size = 200
        for i in range(0, len(o_clean), batch_size):
            batch = o_clean.iloc[i : i + batch_size]
            f.write("INSERT INTO orders (order_id, customer_id, product_id, quantity, order_date) VALUES\n")
            ord_lines = []
            for _, row in batch.iterrows():
                ord_lines.append(f"({row['order_id']}, {row['customer_id']}, {row['product_id']}, {row['quantity']}, '{row['order_date']}')")
            f.write(",\n".join(ord_lines) + ";\n\n")
            
    print(f"[SUCCESS] Generated SQL insert script: {sql_file}")


import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    print("[INFO] Starting synthetic dataset generation for Retail Customer 360...")
    
    customers_df = generate_customers()
    products_df = generate_products()
    orders_df = generate_orders(customers_df, products_df)
    
    # Save raw CSVs
    cust_path = RAW_DATA_DIR / "customers.csv"
    prod_path = RAW_DATA_DIR / "products.csv"
    ord_path = RAW_DATA_DIR / "orders.csv"
    
    customers_df.to_csv(cust_path, index=False)
    products_df.to_csv(prod_path, index=False)
    orders_df.to_csv(ord_path, index=False)
    
    print(f"[SUCCESS] Generated {len(customers_df)} customer records -> {cust_path}")
    print(f"[SUCCESS] Generated {len(products_df)} product records -> {prod_path}")
    print(f"[SUCCESS] Generated {len(orders_df)} order records -> {ord_path}")
    
    # Generate SQL seed file
    export_sql_insert_script(customers_df, products_df, orders_df)
    print("[SUCCESS] Step 1 Data Generation completed successfully!\n")



if __name__ == "__main__":
    main()
