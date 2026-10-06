"""
Generates synthetic delivery datasets.

Usage:
    python3 data/generate_data.py
        creates data/customers_5.csv, customers_10.csv, customers_20.csv
        and customers_30.csv

    python3 data/generate_data.py --customers 15 --seed 7 --output data/my_data.csv
        creates one dataset with 15 customers

The warehouse W is placed at the centre of a 100 x 100 map. Each customer
gets random whole-number coordinates between 0 and 100. The same seed
always produces the same dataset.
"""

import argparse
import csv
import os
import random

DATA_FOLDER = os.path.dirname(os.path.abspath(__file__))

MAP_SIZE = 100
WAREHOUSE_POSITION = (50, 50)
DEFAULT_SIZES = [5, 10, 20, 30]
DEFAULT_SEED = 42


def generate_dataset(number_of_customers, seed, output_path):
    """Write a CSV with the warehouse and `number_of_customers` customers."""
    if number_of_customers < 1:
        raise ValueError("The number of customers must be at least 1.")
    if number_of_customers > 5000:
        raise ValueError("The number of customers must not be more than 5000.")

    rng = random.Random(seed)

    rows = [("W", WAREHOUSE_POSITION[0], WAREHOUSE_POSITION[1])]
    used_positions = {WAREHOUSE_POSITION}

    for number in range(1, number_of_customers + 1):
        # Pick a position that no other location is using.
        position = WAREHOUSE_POSITION
        while position in used_positions:
            position = (rng.randint(0, MAP_SIZE), rng.randint(0, MAP_SIZE))
        used_positions.add(position)

        rows.append((f"C{number}", position[0], position[1]))

    with open(output_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["ID", "X", "Y"])
        writer.writerows(rows)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic delivery datasets")
    parser.add_argument("--customers", type=int, help="number of customers (default: 5, 10, 20 and 30)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="random seed")
    parser.add_argument("--output", help="output file (only with --customers)")
    args = parser.parse_args()

    if args.output and args.customers is None:
        parser.error("--output can only be used together with --customers")

    if args.customers is None:
        sizes = DEFAULT_SIZES
    else:
        sizes = [args.customers]

    for size in sizes:
        output_path = args.output or os.path.join(DATA_FOLDER, f"customers_{size}.csv")
        try:
            generate_dataset(size, args.seed, output_path)
        except ValueError as error:
            parser.error(str(error))
        print(f"Created {output_path} ({size} customers, seed {args.seed})")


if __name__ == "__main__":
    main()
