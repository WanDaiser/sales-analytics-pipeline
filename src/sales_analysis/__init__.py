"""Sales analysis package."""

from .pipeline import (
    clean_and_enrich,
    compute_product_stats,
    compute_revenue_metrics,
    detect_high_value_sales,
    generate_data,
)

__all__ = [
    "generate_data",
    "clean_and_enrich",
    "compute_product_stats",
    "compute_revenue_metrics",
    "detect_high_value_sales",
]
