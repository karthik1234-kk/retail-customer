"""
retail-customer-360: Configuration Module
Contains centralized paths, database credentials, and analytics parameters.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "outputs"
SQL_DIR = BASE_DIR / "sql"
DASHBOARD_DIR = BASE_DIR / "dashboard"

# Ensure directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, OUTPUT_DIR, SQL_DIR, DASHBOARD_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Database Configuration (MySQL defaults)
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",  # Set your MySQL root password here or pass via env var
    "database": "retail_360",
}

# SQLite fallback database path for standalone execution
SQLITE_DB_PATH = DATA_DIR / "retail_360.db"

# Data Generation Parameters
NUM_CUSTOMERS = 300
NUM_PRODUCTS = 40
NUM_ORDERS = 1500

# Age Group Bins & Labels
AGE_BINS = [17, 25, 35, 45, 55, 100]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-55", "56+"]

# Segmentation Cutoffs (RFM percentile thresholds)
SEGMENT_HIGH_VALUE_THRESHOLD = 0.80  # Top 20%
SEGMENT_MEDIUM_VALUE_THRESHOLD = 0.40  # Next 40%
# Remaining 40% -> Low Value
