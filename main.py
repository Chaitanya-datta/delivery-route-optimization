"""
Comparative Delivery Route Optimization
Hill Climbing, Simulated Annealing and Genetic Algorithm

Usage:
    python3 main.py
    python3 main.py --input data/input.csv --seed 42

Phase 3: loads the input and runs Hill Climbing and Simulated Annealing.
The Genetic Algorithm is added in a later phase.
"""

import argparse
import os
import random
import sys

from algorithms.hill_climbing import hill_climbing
from algorithms.simulated_annealing import simulated_annealing
from utils.data_loader import WAREHOUSE_ID, load_locations
from utils.route import build_complete_route, format_route, validate_complete_route

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")
DEFAULT_SEED = 42

# Hill Climbing parameters
HC_MAX_ITERATIONS = 1000

# Simulated Annealing parameters
SA_INITIAL_TEMPERATURE = 100.0
SA_COOLING_RATE = 0.999
SA_MINIMUM_TEMPERATURE = 0.001
SA_MAX_ITERATIONS = 20000


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


def print_result(result, count_name):
    """Print the result of one algorithm. count_name is 'Iterations' or 'Generations'."""
    print_heading(result["algorithm"].upper())
    print()
    print(f"Initial route:\n{format_route(result['initial_route'])}\n")
    print(f"Initial distance:\n{result['initial_distance']:.2f}\n")
    print(f"Best route:\n{format_route(result['best_route'])}\n")
    print(f"Best distance:\n{result['best_distance']:.2f}\n")
    print(f"Execution time:\n{result['execution_time']:.4f} seconds\n")
    print(f"{count_name}:\n{result['iterations']}\n")
    print(f"Stopped because:\n{result['stop_reason']}\n")


def main():
    parser = argparse.ArgumentParser(description="Delivery route optimization")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="path to the input CSV file")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="random seed")
    args = parser.parse_args()

    try:
        locations, customer_ids = load_locations(args.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"INPUT ERROR: {error}")
        sys.exit(1)

    print_locations(locations, customer_ids)
    print(f"Random seed: {args.seed}\n")

    # Each algorithm gets its own random generator created from the same
    # seed. Runs are reproducible, and both algorithms start from the
    # same random initial route.
    hc_result = hill_climbing(
        locations,
        customer_ids,
        random.Random(args.seed),
        max_iterations=HC_MAX_ITERATIONS,
    )

    sa_result = simulated_annealing(
        locations,
        customer_ids,
        random.Random(args.seed),
        initial_temperature=SA_INITIAL_TEMPERATURE,
        cooling_rate=SA_COOLING_RATE,
        minimum_temperature=SA_MINIMUM_TEMPERATURE,
        max_iterations=SA_MAX_ITERATIONS,
    )

    for result in [hc_result, sa_result]:
        # Check that the algorithm returned a valid route.
        validate_complete_route(build_complete_route(result["best_route"]), customer_ids)
        print_result(result, "Iterations")


if __name__ == "__main__":
    main()
