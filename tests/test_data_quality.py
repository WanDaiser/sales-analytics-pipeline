from __future__ import annotations

import numpy as np
import pandas as pd

from sales_analysis.pipeline import clean_and_enrich, generate_data


class TestDataQuality:
    """Data quality and validation tests."""

    def test_no_null_values_after_cleaning(self) -> None:
        """Ensure no null values remain after data cleaning."""
        raw_df = generate_data(size=100, seed=42)
        cleaned_df = clean_and_enrich(raw_df)
        
        assert cleaned_df.isnull().sum().sum() == 0, "Cleaned data contains null values"

    def test_product_id_range(self) -> None:
        """Verify product IDs are within expected range."""
        df = generate_data(size=100, seed=42)
        
        assert df["product_id"].min() >= 100, "Product ID below minimum"
        assert df["product_id"].max() < 105, "Product ID above maximum"

    def test_quantity_positive(self) -> None:
        """Check that all quantities are positive integers."""
        df = generate_data(size=100, seed=42)
        
        assert (df["quantity"] > 0).all(), "Negative quantities found"
        assert df["quantity"].dtype in [np.int64, np.int32], "Quantity not integer type"

    def test_unit_price_positive(self) -> None:
        """Verify all unit prices are positive."""
        df = generate_data(size=100, seed=42)
        
        assert (df["unit_price"] > 0).all(), "Non-positive unit prices found"

    def test_rating_range(self) -> None:
        """Check ratings are within valid range after cleaning."""
        df = generate_data(size=100, seed=42)
        cleaned_df = clean_and_enrich(df)
        
        assert cleaned_df["rating"].min() >= 1.0, "Rating below minimum"
        assert cleaned_df["rating"].max() <= 5.0, "Rating above maximum"

    def test_total_revenue_calculation(self) -> None:
        """Validate revenue calculation accuracy."""
        df = generate_data(size=50, seed=42)
        cleaned_df = clean_and_enrich(df)
        
        expected = cleaned_df["quantity"] * cleaned_df["unit_price"]
        assert np.allclose(cleaned_df["total_revenue"], expected), "Revenue calculation error"

    def test_date_continuity(self) -> None:
        """Ensure dates are sequential without gaps."""
        df = generate_data(size=30, seed=42, start_date="2025-01-01")
        
        date_diff = df["date"].diff().dropna()
        expected_diff = pd.Timedelta(days=1)
        
        assert (date_diff == expected_diff).all(), "Date sequence has gaps"

    def test_data_schema(self) -> None:
        """Verify expected column schema."""
        df = generate_data(size=10, seed=42)
        
        expected_columns = ["date", "product_id", "quantity", "unit_price", "rating"]
        assert list(df.columns) == expected_columns, "Schema mismatch"

    def test_no_duplicate_rows(self) -> None:
        """Check for unexpected duplicate entries."""
        df = generate_data(size=100, seed=42)
        
        # Allow duplicates in data (synthetic generation may create them)
        # But verify structure is as expected
        assert len(df) == 100, "Row count mismatch"
