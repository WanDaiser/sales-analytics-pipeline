from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import (
    clean_and_enrich,
    compute_product_stats,
    compute_revenue_metrics,
    detect_high_value_sales,
    generate_data,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run synthetic sales analysis pipeline.")
    parser.add_argument("--size", type=int, default=100, help="Number of rows to generate.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument("--start-date", type=str, default="2025-01-01", help="Start date for data.")
    parser.add_argument(
        "--report-path",
        type=str,
        default="outputs/report.csv",
        help="Output path for product summary report CSV.",
    )
    parser.add_argument(
        "--transactions-path",
        type=str,
        default="outputs/transactions.csv",
        help="Output path for cleaned transactions CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    raw_df = generate_data(size=args.size, seed=args.seed, start_date=args.start_date)
    cleaned_df = clean_and_enrich(raw_df)

    product_stats = compute_product_stats(cleaned_df)
    avg_revenue, std_dev = compute_revenue_metrics(cleaned_df)
    high_value_sales = detect_high_value_sales(cleaned_df, avg=avg_revenue, std=std_dev)

    report_path = Path(args.report_path)
    transactions_path = Path(args.transactions_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    transactions_path.parent.mkdir(parents=True, exist_ok=True)

    product_stats.to_csv(report_path, index=False)
    cleaned_df.to_csv(transactions_path, index=False)

    print("--- Sales Summary ---")
    print(product_stats.to_string(index=False))
    print(f"\nAvg Revenue: {avg_revenue:.2f} | Std Dev: {std_dev:.2f}")
    print(f"High Value Transactions: {len(high_value_sales)}")


if __name__ == "__main__":
    main()
