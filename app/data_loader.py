import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "processed" / "enrollment.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_enrollment_data():
    """Retrieves headcount data joined with institution and region metadata."""
    query = """
    SELECT 
        h.fiscal_year,
        i.institution_name,
        r.region_name,
        h.student_type,
        h.headcount
    FROM fact_student_headcount h
    JOIN dim_institution i ON h.institution_id = i.institution_id
    JOIN dim_region r ON h.region_id = r.region_id;
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)

def load_financial_fte_data():
    """Retrieves FTE target/actuals and operating grants joined with institutions."""
    query = """
    SELECT 
        f.fiscal_year,
        i.institution_name,
        f.fte_actual,
        f.fte_target,
        f.operating_grant
    FROM fact_institution_financials_fte f
    JOIN dim_institution i ON f.institution_id = i.institution_id;
    """
    with get_connection() as conn:
        return pd.read_sql(query, conn)