"""
Phase 3 tests: Simulated Annealing.

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

from algorithms.simulated_annealing import (
    acceptance_probability,
    random_neighbour,
    simulated_annealing,
)
from utils.data_loader import load_locations
from utils.distance import route_distance
from utils.route import validate_customer_route

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


class TestRandomNeighbour(unittest.TestCase):

    def test_neighbour_is_one_swap_away(self):
        route = ["C1", "C2", "C3", "C4", "C5"]
        rng = random.Random(0)
        for _ in range(200):
            neighbour = random_neighbour(route, rng)
            self.assertTrue(validate_customer_route(neighbour, route))
            changed = [k for k in range(len(route)) if route[k] != neighbour[k]]
            self.assertEqual(len(changed), 2)
        # The original route is not changed.
        self.assertEqual(route, ["C1", "C2", "C3", "C4", "C5"])

    def test_two_customers(self):
        self.assertEqual(random_neighbour(["C1", "C2"], random.Random(0)), ["C2", "C1"])


class TestAcceptanceProbability(unittest.TestCase):

    def test_formula(self):
        # exp(-10 / 10) = exp(-1)
        self.assertAlmostEqual(acceptance_probability(10, 10), 0.36787944117)
        self.assertAlmostEqual(acceptance_probability(0, 5), 1.0)

    def test_higher_temperature_accepts_more(self):
        self.assertGreater(acceptance_probability(20, 100), acceptance_probability(20, 10))
        self.assertGreater(acceptance_probability(20, 10), acceptance_probability(20, 1))

    def test_bigger_increase_is_accepted_less(self):
        self.assertGreater(acceptance_probability(5, 10), acceptance_probability(50, 10))

    def test_always_between_zero_and_one(self):
        for delta in [0, 0.001, 1, 50, 1000, 1e9]:
            for temperature in [1e-9, 0.001, 1, 100, 1e6]:
                probability = acceptance_probability(delta, temperature)
                self.assertGreaterEqual(probability, 0.0)
                self.assertLessEqual(probability, 1.0)

    def test_zero_temperature_does_not_divide_by_zero(self):
        self.assertEqual(acceptance_probability(10, 0), 0.0)
        self.assertEqual(acceptance_probability(10, -1), 0.0)


class TestSimulatedAnnealing(unittest.TestCase):

    def test_result_is_valid_for_many_sizes_and_seeds(self):
        for n in [1, 2, 3, 5, 10, 20]:
            locations, customer_ids = make_random_problem(n, seed=n)
            for seed in range(5):
                result = simulated_annealing(locations, customer_ids, random.Random(seed))

                self.assertTrue(validate_customer_route(result["best_route"], customer_ids))
                self.assertTrue(validate_customer_route(result["initial_route"], customer_ids))

                # The reported distance is the real distance of the reported route.
                self.assertAlmostEqual(
                    result["best_distance"],
                    route_distance(result["best_route"], locations),
                )
                self.assertLessEqual(result["best_distance"], result["initial_distance"])
                self.assertGreaterEqual(result["execution_time"], 0)

    def test_convergence_history(self):
        locations, customer_ids = make_random_problem(15, seed=3)
        result = simulated_annealing(locations, customer_ids, random.Random(1))
        history = result["history"]

        # One entry for the start plus one per iteration.
        self.assertEqual(len(history), result["iterations"] + 1)
        self.assertEqual([step for step, cost in history], list(range(len(history))))
        self.assertAlmostEqual(history[0][1], result["initial_distance"])
        self.assertAlmostEqual(history[-1][1], result["best_distance"])
        self.assertEqual(result["evaluations"], result["iterations"] + 1)

        # The BEST distance so far can never get worse.
        costs = [cost for step, cost in history]
        for earlier, later in zip(costs, costs[1:]):
            self.assertLessEqual(later, earlier)

    def test_worse_routes_are_sometimes_accepted(self):
        locations, customer_ids = make_random_problem(15, seed=3)
        result = simulated_annealing(locations, customer_ids, random.Random(1))
        self.assertGreater(result["worse_moves_accepted"], 0)

    def test_very_low_temperature_accepts_almost_no_worse_routes(self):
        locations, customer_ids = make_random_problem(15, seed=3)
        result = simulated_annealing(
            locations,
            customer_ids,
            random.Random(1),
            initial_temperature=1e-6,
            minimum_temperature=1e-12,
            max_iterations=3000,
        )
        self.assertEqual(result["worse_moves_accepted"], 0)

    def test_stops_at_minimum_temperature(self):
        locations, customer_ids = make_random_problem(10, seed=1)
        result = simulated_annealing(
            locations,
            customer_ids,
            random.Random(0),
            initial_temperature=100,
            cooling_rate=0.9,
            minimum_temperature=1,
            max_iterations=100000,
        )
        self.assertIn("minimum temperature", result["stop_reason"])
        self.assertLess(result["final_temperature"], 1)
        # 100 * 0.9^k drops below 1 after 44 coolings.
        self.assertEqual(result["iterations"], 44)

    def test_stops_at_iteration_limit(self):
        locations, customer_ids = make_random_problem(10, seed=1)
        result = simulated_annealing(
            locations, customer_ids, random.Random(0), max_iterations=50
        )
        self.assertEqual(result["iterations"], 50)
        self.assertIn("iteration limit", result["stop_reason"])
        self.assertTrue(validate_customer_route(result["best_route"], customer_ids))

    def test_invalid_parameters_are_rejected(self):
        locations, customer_ids = make_random_problem(5, seed=1)
        rng = random.Random(0)
        with self.assertRaisesRegex(ValueError, "initial_temperature"):
            simulated_annealing(locations, customer_ids, rng, initial_temperature=0)
        with self.assertRaisesRegex(ValueError, "minimum_temperature"):
            simulated_annealing(locations, customer_ids, rng, minimum_temperature=0)
        with self.assertRaisesRegex(ValueError, "cooling_rate"):
            simulated_annealing(locations, customer_ids, rng, cooling_rate=1.0)
        with self.assertRaisesRegex(ValueError, "cooling_rate"):
            simulated_annealing(locations, customer_ids, rng, cooling_rate=0)

    def test_same_seed_gives_same_result(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        first = simulated_annealing(locations, customer_ids, random.Random(42))
        second = simulated_annealing(locations, customer_ids, random.Random(42))
        self.assertEqual(first["best_route"], second["best_route"])
        self.assertEqual(first["history"], second["history"])

    def test_different_seeds_give_different_searches(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        histories = set()
        for seed in range(5):
            result = simulated_annealing(locations, customer_ids, random.Random(seed))
            histories.add(tuple(result["history"]))
        self.assertGreater(len(histories), 1)

    def test_one_customer(self):
        locations = {"W": (0.0, 0.0), "A": (3.0, 4.0)}
        result = simulated_annealing(locations, ["A"], random.Random(0))
        self.assertEqual(result["best_route"], ["A"])
        self.assertAlmostEqual(result["best_distance"], 10.0)
        self.assertEqual(result["iterations"], 0)

    def test_inputs_are_not_changed(self):
        locations, customer_ids = make_random_problem(10, seed=4)
        ids_before = list(customer_ids)
        locations_before = dict(locations)
        simulated_annealing(locations, customer_ids, random.Random(0))
        self.assertEqual(customer_ids, ids_before)
        self.assertEqual(locations, locations_before)

    def test_never_better_than_the_true_optimum(self):
        # With 5 customers all 120 routes can be checked directly.
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        optimum = min(
            route_distance(list(order), locations)
            for order in itertools.permutations(customer_ids)
        )
        for seed in range(10):
            result = simulated_annealing(locations, customer_ids, random.Random(seed))
            self.assertGreaterEqual(result["best_distance"], optimum - 1e-9)


if __name__ == "__main__":
    unittest.main()
