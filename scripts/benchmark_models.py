#!/usr/bin/env python3
"""CLI utility to execute the IEEE Offline Evaluation & Benchmark Suite.

Generates comparative performance tables across Popularity, Collaborative
Filtering, SVD Matrix Factorization, Content-Based, and Hybrid recommendation models.
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.evaluation import benchmark_all_models


def main():
    parser = argparse.ArgumentParser(
        description="Run offline evaluation benchmark for AI recommendation models."
    )
    parser.add_argument(
        "--k", type=int, default=5, help="Cutoff rank for Top-K metrics (default: 5)"
    )
    parser.add_argument(
        "--users",
        type=int,
        default=50,
        help="Number of held-out test users to sample (default: 50)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="",
        help="Optional path to export benchmark results as CSV",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="",
        help="Optional path to export benchmark results as Markdown table",
    )
    args = parser.parse_args()

    print("================================================================================")
    print(f"IEEE OFFLINE EVALUATION BENCHMARK: Top-{args.k} Metrics (Test Users: {args.users})")
    print("================================================================================")
    print("Evaluating models against stratified train-test splits...")

    results_df = benchmark_all_models(k=args.k, max_test_users=args.users)

    formatted = results_df.round(4)
    print("\n" + formatted.to_string())
    print("================================================================================")

    if args.output_csv:
        formatted.to_csv(args.output_csv)
        print(f"Results successfully saved to CSV: {args.output_csv}")

    if args.output_md:
        with open(args.output_md, "w", encoding="utf-8") as f:
            f.write(formatted.to_markdown())
        print(f"Results successfully saved to Markdown: {args.output_md}")


if __name__ == "__main__":
    main()
