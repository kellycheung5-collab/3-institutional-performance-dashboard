import pytest
import pandas as pd
from app.data_loader import load_enrollment_data, load_financial_fte_data
from app.app import update_kpi_cards

def test_load_enrollment_data():
    """Verify headcount dataset structure and non-empty return."""
    df = load_enrollment_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"fiscal_year", "institution_name", "region_name", "student_type", "headcount"}
    assert expected_cols.issubset(set(df.columns))

def test_load_financial_fte_data():
    """Verify financial FTE dataset structure and non-empty return."""
    df = load_financial_fte_data()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_cols = {"fiscal_year", "institution_name", "fte_actual", "fte_target", "operating_grant"}
    assert expected_cols.issubset(set(df.columns))

def test_update_kpi_cards():
    """Verify KPI card callback outputs 3 components for a valid institution."""
    df_headcount = load_enrollment_data()
    sample_inst = df_headcount["institution_name"].iloc[0]
    
    cards = update_kpi_cards(sample_inst)
    assert len(cards) == 3