"""
Runs all three algorithms on datasets of different sizes and compares them.

Usage:
    python3 experiments/run_experiments.py
    python3 experiments/run_experiments.py --runs 10 --sizes 5 10

For every dataset size:
    1. a dataset is generated (same dataset seed -> same dataset every time)
    2. every algorithm is run `runs` times, with seeds 1, 2, 3, ...
    3. the results are summarized in a comparison table

All algorithms get the same datasets and the same seeds. The numbers are
also saved in the results folder:
    experiment_summary.csv - one row per dataset size and algorithm
    experiment_runs.csv    - one row per single run
"""

import argparse
import csv
import os
import sys

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

import config
from data.generate_data import generate_dataset
from utils.comparison import ALGORITHM_NAMES, print_comparison_table, run_many, summarize
from utils.data_loader import load_locations
from utils.route import format_route

DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
RESULTS_FOLDER = os.path.join(PROJECT_FOLDER, "results")


def run_experiments(sizes, runs, dataset_seed, data_folder, results_folder):
    """
    Run the experiments and return (summary_rows, run_rows).
    Both are lists of dictionaries, ready to be written to CSV files.
    """
    seeds = list(range(1, runs + 1))
    summary_rows = []
    run_rows = []

    for size in sizes:
        dataset_path = os.path.join(data_folder, f"customers_{size}.csv")
        generate_dataset(size, dataset_seed, dataset_path)
        locations, customer_ids = load_locations(dataset_path)

        print("=" * 126)
        print(f"{size} CUSTOMERS   ({runs} runs per algorithm, dataset: {dataset_path})")
        print("=" * 126)

        summaries = []
        for name in ALGORITHM_NAMES:
            results = run_many(name, locations, customer_ids, seeds)
            summary = summarize(results)
            summaries.append(summary)

            summary_rows.append({
                "customers": size,
                "algorithm": name,
                "runs": summary["runs"],
                "best_distance": round(summary["best_distance"], 4),
                "average_distance": round(summary["average_distance"], 4),
                "std_dev": round(summary["std_dev"], 4),
                "worst_distance": round(summary["worst_distance"], 4),
                "average_time_seconds": round(summary["average_time"], 6),
                "average_iterations_or_generations": round(summary["average_iterations"], 2),
                "average_route_evaluations": round(summary["average_evaluations"], 2),
                "best_route": format_route(summary["best_route"]),
            })

            for result in results:
                run_rows.append({
                    "customers": size,
                    "algorithm": name,
                    "seed": result["seed"],
                    "best_distance": round(result["best_distance"], 4),
                    "execution_time_seconds": round(result["execution_time"], 6),
                    "iterations_or_generations": result["iterations"],
                    "route_evaluations": result["evaluations"],
                    "best_route": format_route(result["best_route"]),
                })

        print_comparison_table(summaries)
        print()

    os.makedirs(results_folder, exist_ok=True)
    write_csv(os.path.join(results_folder, "experiment_summary.csv"), summary_rows)
    write_csv(os.path.join(results_folder, "experiment_runs.csv"), run_rows)

    return summary_rows, run_rows


def write_csv(path, rows):
    with open(path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Compare the three algorithms on several dataset sizes")
    parser.add_argument("--sizes", type=int, nargs="+", default=config.EXPERIMENT_SIZES,
                        help="numbers of customers to test")
    parser.add_argument("--runs", type=int, default=config.EXPERIMENT_RUNS,
                        help="runs of every algorithm on every dataset")
    parser.add_argument("--dataset-seed", type=int, default=config.EXPERIMENT_DATASET_SEED,
                        help="seed used to generate the datasets")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")
    if min(args.sizes) < 1:
        parser.error("every size must be at least 1")

    run_experiments(args.sizes, args.runs, args.dataset_seed, DATA_FOLDER, RESULTS_FOLDER)

    print(f"Results saved in {RESULTS_FOLDER}")
    print("  experiment_summary.csv")
    print("  experiment_runs.csv")
    print()
    print("Std Dev is the standard deviation of the best distance over the runs.")
    print("Execution Time, Iterations/Generations and Route Evaluations are averages per run.")


if __name__ == "__main__":
    main()
