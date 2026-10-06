"""
Phase 2 tests: Hill Climbing.

Run from the project folder:
    python3 -m unittest discover -s tests -v
"""

import itertools
import os
import random
import sys
import unittest

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

from algorithms.hill_climbing import generate_neighbours, hill_climbing
from utils.data_loader import load_locations
from utils.distance import route_distance
from utils.route import swap_positions, validate_customer_route

SAMPLE_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")


def make_random_problem(number_of_customers, seed):
    """Create random test locations (not used by the project itself)."""
    rng = random.Random(seed)
    locations = {"W": (50.0, 50.0)}
    customer_ids = []
    for number in range(1, number_of_customers + 1):
        customer_id = f"C{number}"
        locations[customer_id] = (rng.uniform(0, 100), rng.uniform(0, 100))
        customer_ids.append(customer_id)
    return locations, customer_ids


class TestSwapAndNeighbours(unittest.TestCase):

    def test_swap_positions(self):
        route = ["C1", "C2", "C3", "C4", "C5"]
        self.assertEqual(swap_positions(route, 1, 4), ["C1", "C5", "C3", "C4", "C2"])
        # The original route is not changed.
        self.assertEqual(route, ["C1", "C2", "C3", "C4", "C5"])

    def test_neighbours_of_three_customers(self):
        neighbours = generate_neighbours(["C1", "C2", "C3"])
        self.assertEqual(
            neighbours,
            [["C2", "C1", "C3"], ["C3", "C2", "C1"], ["C1", "C3", "C2"]],
        )

    def test_neighbour_count_and_validity(self):
        for n in [1, 2, 5, 10]:
            route = [f"C{k}" for k in range(1, n + 1)]
            neighbours = generate_neighbours(route)
            self.assertEqual(len(neighbours), n * (n - 1) // 2)
            for neighbour in neighbours:
                self.assertTrue(validate_customer_route(neighbour, route))
                self.assertNotEqual(neighbour, route)
            # All neighbours are different from each other.
            self.assertEqual(len(set(map(tuple, neighbours))), len(neighbours))


class TestHillClimbing(unittest.TestCase):

    def test_result_is_valid_for_many_sizes_and_seeds(self):
        for n in [1, 2, 3, 5, 10, 20]:
            locations, customer_ids = make_random_problem(n, seed=n)
            for seed in range(5):
                result = hill_climbing(locations, customer_ids, random.Random(seed))

                self.assertTrue(validate_customer_route(result["best_route"], customer_ids))
                self.assertTrue(validate_customer_route(result["initial_route"], customer_ids))

                # The reported distance is the real distance of the reported route.
                self.assertAlmostEqual(
                    result["best_distance"],
                    route_distance(result["best_route"], locations),
                )
                self.assertAlmostEqual(
                    result["initial_distance"],
                    route_distance(result["initial_route"], locations),
                )
                self.assertLessEqual(result["best_distance"], result["initial_distance"])
                self.assertGreaterEqual(result["execution_time"], 0)

    def test_convergence_history(self):
        locations, customer_ids = make_random_problem(15, seed=3)
        result = hill_climbing(locations, customer_ids, random.Random(1))
        history = result["history"]

        # One entry for the start plus one per iteration.
        self.assertEqual(len(history), result["iterations"] + 1)
        self.assertEqual([step for step, cost in history], list(range(len(history))))
        self.assertAlmostEqual(history[0][1], result["initial_distance"])
        self.assertAlmostEqual(history[-1][1], result["best_distance"])

        # Hill Climbing never accepts a worse route.
        costs = [cost for step, cost in history]
        for earlier, later in zip(costs, costs[1:]):
            self.assertLessEqual(later, earlier)

    def test_stops_at_a_local_optimum(self):
        for seed in range(10):
            locations, customer_ids = make_random_problem(12, seed=seed)
            result = hill_climbing(locations, customer_ids, random.Random(seed))
            self.assertIn("local optimum", result["stop_reason"])

            # No single swap makes the final route shorter.
            for neighbour in generate_neighbours(result["best_route"]):
                self.assertGreaterEqual(
                    route_distance(neighbour, locations), result["best_distance"]
                )

    def test_iteration_limit(self):
        locations, customer_ids = make_random_problem(20, seed=5)
        result = hill_climbing(locations, customer_ids, random.Random(0), max_iterations=2)
        self.assertEqual(result["iterations"], 2)
        self.assertIn("iteration limit", result["stop_reason"])
        self.assertTrue(validate_customer_route(result["best_route"], customer_ids))

    def test_evaluation_count(self):
        n = 8
        locations, customer_ids = make_random_problem(n, seed=2)
        result = hill_climbing(locations, customer_ids, random.Random(0))
        neighbours_per_iteration = n * (n - 1) // 2
        self.assertEqual(
            result["evaluations"], 1 + result["iterations"] * neighbours_per_iteration
        )

    def test_same_seed_gives_same_result(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        first = hill_climbing(locations, customer_ids, random.Random(42))
        second = hill_climbing(locations, customer_ids, random.Random(42))
        self.assertEqual(first["best_route"], second["best_route"])
        self.assertEqual(first["history"], second["history"])

    def test_different_seeds_start_from_different_routes(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        starts = set()
        for seed in range(10):
            result = hill_climbing(locations, customer_ids, random.Random(seed))
            starts.add(tuple(result["initial_route"]))
        self.assertGreater(len(starts), 1)

    def test_one_customer(self):
        locations = {"W": (0.0, 0.0), "A": (3.0, 4.0)}
        result = hill_climbing(locations, ["A"], random.Random(0))
        self.assertEqual(result["best_route"], ["A"])
        self.assertAlmostEqual(result["best_distance"], 10.0)

    def test_inputs_are_not_changed(self):
        locations, customer_ids = make_random_problem(10, seed=4)
        ids_before = list(customer_ids)
        locations_before = dict(locations)
        hill_climbing(locations, customer_ids, random.Random(0))
        self.assertEqual(customer_ids, ids_before)
        self.assertEqual(locations, locations_before)

    def test_never_better_than_the_true_optimum(self):
        # With 5 customers all 120 routes can be checked directly.
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        optimum = min(
            route_distance(list(order), locations)
            for order in itertools.permutations(customer_ids)
        )
        for seed in range(30):
            result = hill_climbing(locations, customer_ids, random.Random(seed))
            self.assertGreaterEqual(result["best_distance"], optimum - 1e-9)


if __name__ == "__main__":
    unittest.main()
