from __future__ import annotations

import numpy as np
import pandas as pd


def generate_data(size: int = 100, seed: int = 42, start_date: str = "2025-01-01") -> pd.DataFrame:
    """Generate synthetic sales data."""
    np.random.seed(seed)

    data = {
        "date": pd.date_range(start=start_date, periods=size, freq="D"),
        "product_id": np.random.randint(100, 105, size=size),
        "quantity": np.random.randint(1, 15, size=size),
        "unit_price": np.random.uniform(100.0, 500.0, size=size),
        "rating": np.random.choice([1, 2, 3, 4, 5, np.nan], size=size),
    }
    return pd.DataFrame(data)


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Fill missing ratings and compute total revenue."""
    cleaned = df.copy()
    cleaned["rating"] = cleaned["rating"].fillna(cleaned["rating"].mean())
    cleaned["total_revenue"] = cleaned["quantity"] * cleaned["unit_price"]
    return cleaned


def compute_product_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product level metrics."""
    return (
        df.groupby("product_id", as_index=False)
        .agg(
            total_revenue=("total_revenue", "sum"),
            rating=("rating", "mean"),
            quantity=("quantity", "count"),
        )
        .sort_values("product_id")
        .reset_index(drop=True)
    )


def compute_revenue_metrics(df: pd.DataFrame) -> tuple[float, float]:
    """Return average and standard deviation of revenue."""
    revenue_array = df["total_revenue"].to_numpy()
    avg_revenue = float(np.mean(revenue_array))
    std_dev = float(np.std(revenue_array))
    return avg_revenue, std_dev


def detect_high_value_sales(df: pd.DataFrame, avg: float, std: float) -> pd.DataFrame:
    """Return rows above avg + std threshold."""
    threshold = avg + std
    return df[df["total_revenue"] > threshold].copy()
