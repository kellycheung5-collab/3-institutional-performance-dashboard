import os
import shutil
import sqlite3
from pathlib import Path

# Set up paths relative to the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Source database location
source_db = RAW_DIR / "enrollment.db"
target_db = PROCESSED_DIR / "enrollment.db"

def setup_database():
    # Ensure processed directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not source_db.exists():
        raise FileNotFoundError(f"Source database not found at {source_db}")

    # Copy raw database into data/processed/
    shutil.copy(source_db, target_db)
    print(f"Copied database from {source_db} to {target_db}")

    # Standardize fiscal_year format in data/processed/enrollment.db
    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE fact_institution_financials_fte
        SET fiscal_year = SUBSTR(fiscal_year, 4, 4) || '/20' || SUBSTR(fiscal_year, 9, 2)
        WHERE fiscal_year LIKE 'FY %';
    """)

    conn.commit()
    conn.close()
    print("Successfully updated fiscal_year formats in data/processed/enrollment.db!")

if __name__ == "__main__":
    setup_database()