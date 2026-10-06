"""
Comparative Delivery Route Optimization
Hill Climbing, Simulated Annealing and Genetic Algorithm

Usage:
    python3 main.py
    python3 main.py --input data/input.csv --seed 42 --runs 10

Loads the input, runs all three algorithms on it, prints the result of
each one and then a comparison table over several runs.
The algorithm parameters are in config.py.
"""

import argparse
import os
import sys

import config
from utils.comparison import ALGORITHM_NAMES, print_comparison_table, run_many, summarize
from utils.data_loader import WAREHOUSE_ID, load_locations
from utils.route import format_route

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")


def print_heading(title):
    print("=" * 50)
    print(title)
    print("=" * 50)


def print_locations(locations, customer_ids):
    print_heading("INPUT DATA")
    x, y = locations[WAREHOUSE_ID]
    print(f"Warehouse {WAREHOUSE_ID}: ({x:g}, {y:g})")
    print(f"Customers: {len(customer_ids)}")
    for customer_id in customer_ids:
        x, y = locations[customer_id]
        print(f"  {customer_id}: ({x:g}, {y:g})")
    print()


def print_result(result):
    """Print the result of one run of one algorithm."""
    if result["algorithm"] == "Genetic Algorithm":
        count_name = "Generations"
        start_name = "Best route in the initial population"
    else:
        count_name = "Iterations"
        start_name = "Initial route"

    print_heading(result["algorithm"].upper())
    print()
    print(f"{start_name}:\n{format_route(result['initial_route'])}\n")
    print(f"Distance of that route:\n{result['initial_distance']:.2f}\n")
    print(f"Best route:\n{format_route(result['best_route'])}\n")
    print(f"Best distance:\n{result['best_distance']:.2f}\n")
    print(f"Execution time:\n{result['execution_time']:.4f} seconds\n")
    print(f"{count_name}:\n{result['iterations']}\n")
    print(f"Stopped because:\n{result['stop_reason']}\n")


def main():
    parser = argparse.ArgumentParser(description="Delivery route optimization")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="path to the input CSV file")
    parser.add_argument("--seed", type=int, default=config.DEFAULT_SEED, help="random seed of the first run")
    parser.add_argument("--runs", type=int, default=config.DEFAULT_RUNS,
                        help="number of runs used for the comparison table")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")

    try:
        locations, customer_ids = load_locations(args.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"INPUT ERROR: {error}")
        sys.exit(1)

    print_locations(locations, customer_ids)

    # Every algorithm is run once for each of these seeds. All algorithms
    # get the same seeds, so Hill Climbing and Simulated Annealing start
    # from the same random initial routes.
    seeds = list(range(args.seed, args.seed + args.runs))

    all_results = []
    for name in ALGORITHM_NAMES:
        all_results.append(run_many(name, locations, customer_ids, seeds))

    # Detailed output: the first run (the one that used --seed).
    print(f"Random seed: {args.seed}\n")
    for results in all_results:
        print_result(results[0])

    # Comparison over all runs.
    print("=" * 126)
    print(f"COMPARISON OVER {args.runs} RUNS (seeds {seeds[0]} to {seeds[-1]})")
    print("=" * 126)
    print_comparison_table([summarize(results) for results in all_results])
    print()
    print("Std Dev is the standard deviation of the best distance over the runs.")
    print("Execution Time, Iterations/Generations and Route Evaluations are averages per run.")


if __name__ == "__main__":
    main()
