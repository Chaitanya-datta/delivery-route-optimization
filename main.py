"""
Comparative Delivery Route Optimization
Hill Climbing, Simulated Annealing and Genetic Algorithm

Usage:
    python3 main.py
    python3 main.py --input data/input.csv --seed 42

Phase 1: loads the input, builds a random initial route, validates it
and prints its distance. The three algorithms are added in later phases.
"""

import argparse
import os
import random
import sys

from utils.data_loader import WAREHOUSE_ID, load_locations
from utils.distance import route_distance
from utils.route import (
    build_complete_route,
    format_route,
    random_route,
    validate_complete_route,
)

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")
DEFAULT_SEED = 42


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

    # One random generator, created from the seed, so runs are reproducible.
    rng = random.Random(args.seed)

    initial_route = random_route(customer_ids, rng)
    validate_complete_route(build_complete_route(initial_route), customer_ids)

    print_heading("RANDOM INITIAL ROUTE (no optimization yet)")
    print(f"Seed:\n{args.seed}\n")
    print(f"Route:\n{format_route(initial_route)}\n")
    print(f"Total distance:\n{route_distance(initial_route, locations):.2f}")


if __name__ == "__main__":
    main()
