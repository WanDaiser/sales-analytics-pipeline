from __future__ import annotations

import numpy as np
import pandas.testing as pdt

from sales_analysis.pipeline import (
    clean_and_enrich,
    compute_product_stats,
    compute_revenue_metrics,
    detect_high_value_sales,
    generate_data,
)


def test_generate_data_shape_and_columns() -> None:
    df = generate_data(size=100, seed=42, start_date="2025-01-01")
    expected_columns = {"date", "product_id", "quantity", "unit_price", "rating"}

    assert len(df) == 100
    assert set(df.columns) == expected_columns


def test_clean_and_enrich_imputes_rating_and_computes_total_revenue() -> None:
    df = generate_data(size=50, seed=42)
    cleaned = clean_and_enrich(df)

    assert cleaned["rating"].isna().sum() == 0
    assert "total_revenue" in cleaned.columns

    first_expected = cleaned.loc[0, "quantity"] * cleaned.loc[0, "unit_price"]
    assert np.isclose(cleaned.loc[0, "total_revenue"], first_expected)


def test_compute_product_stats_deterministic_with_fixed_seed() -> None:
    df1 = clean_and_enrich(generate_data(size=120, seed=99))
    df2 = clean_and_enrich(generate_data(size=120, seed=99))

    stats1 = compute_product_stats(df1)
    stats2 = compute_product_stats(df2)

    assert list(stats1.columns) == ["product_id", "total_revenue", "rating", "quantity"]
    pdt.assert_frame_equal(stats1, stats2)


def test_high_value_filter_matches_manual_threshold() -> None:
    df = clean_and_enrich(generate_data(size=100, seed=7))
    avg, std = compute_revenue_metrics(df)

    high_value = detect_high_value_sales(df, avg=avg, std=std)
    threshold = avg + std
    manual = df[df["total_revenue"] > threshold]

    pdt.assert_frame_equal(
        high_value.reset_index(drop=True),
        manual.reset_index(drop=True),
    )
