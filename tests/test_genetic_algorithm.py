"""
Phase 4 tests: Genetic Algorithm.

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

from algorithms.genetic_algorithm import (
    create_population,
    evaluate_population,
    genetic_algorithm,
    order_crossover,
    swap_mutation,
    tournament_selection,
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


class FixedCutPoints:
    """Stands in for the random generator so a crossover example can be checked by hand."""

    def __init__(self, start, end):
        self.cut_points = [start, end]

    def sample(self, population, k):
        return list(self.cut_points)


class TestPopulation(unittest.TestCase):

    def test_population_is_valid(self):
        customer_ids = ["C1", "C2", "C3", "C4", "C5"]
        population = create_population(customer_ids, 30, random.Random(0))
        self.assertEqual(len(population), 30)
        for chromosome in population:
            self.assertTrue(validate_customer_route(chromosome, customer_ids))
            self.assertNotIn("W", chromosome)
        # The population is not 30 copies of the same route.
        self.assertGreater(len(set(map(tuple, population))), 1)

    def test_evaluate_population(self):
        locations, customer_ids = make_random_problem(6, seed=1)
        population = create_population(customer_ids, 10, random.Random(0))
        costs = evaluate_population(population, locations)
        self.assertEqual(len(costs), 10)
        for chromosome, cost in zip(population, costs):
            self.assertAlmostEqual(cost, route_distance(chromosome, locations))


class TestTournamentSelection(unittest.TestCase):

    population = [["A"], ["B"], ["C"], ["D"]]
    costs = [40.0, 10.0, 30.0, 20.0]

    def test_whole_population_tournament_returns_the_best(self):
        for seed in range(20):
            winner = tournament_selection(self.population, self.costs, 4, random.Random(seed))
            self.assertEqual(winner, ["B"])

    def test_tournament_larger_than_population(self):
        winner = tournament_selection(self.population, self.costs, 10, random.Random(0))
        self.assertEqual(winner, ["B"])

    def test_shorter_routes_are_selected_more_often(self):
        rng = random.Random(0)
        wins = {"A": 0, "B": 0, "C": 0, "D": 0}
        for _ in range(2000):
            winner = tournament_selection(self.population, self.costs, 2, rng)
            wins[winner[0]] += 1
        self.assertGreater(wins["B"], wins["D"])
        self.assertGreater(wins["D"], wins["C"])
        self.assertGreater(wins["C"], wins["A"])
        # The worst route can never win a tournament of two different routes.
        self.assertEqual(wins["A"], 0)

    def test_tournament_of_one_is_a_random_pick(self):
        rng = random.Random(0)
        winners = set()
        for _ in range(200):
            winners.add(tournament_selection(self.population, self.costs, 1, rng)[0])
        self.assertEqual(winners, {"A", "B", "C", "D"})


class TestOrderCrossover(unittest.TestCase):

    def test_worked_example(self):
        parent1 = ["C1", "C2", "C3", "C4", "C5"]
        parent2 = ["C3", "C5", "C1", "C2", "C4"]
        child = order_crossover(parent1, parent2, FixedCutPoints(1, 2))
        self.assertEqual(child, ["C5", "C2", "C3", "C1", "C4"])

    def test_whole_parent_slice(self):
        parent1 = ["C1", "C2", "C3"]
        parent2 = ["C3", "C2", "C1"]
        self.assertEqual(order_crossover(parent1, parent2, FixedCutPoints(0, 2)), parent1)

    def test_child_is_always_a_valid_permutation(self):
        rng = random.Random(0)
        for n in [1, 2, 3, 5, 10, 30]:
            customer_ids = [f"C{k}" for k in range(1, n + 1)]
            for _ in range(300):
                parent1 = list(customer_ids)
                parent2 = list(customer_ids)
                rng.shuffle(parent1)
                rng.shuffle(parent2)
                parent1_before = list(parent1)
                parent2_before = list(parent2)

                child = order_crossover(parent1, parent2, rng)

                self.assertTrue(validate_customer_route(child, customer_ids))
                self.assertEqual(len(child), n)
                # The parents are not changed.
                self.assertEqual(parent1, parent1_before)
                self.assertEqual(parent2, parent2_before)

    def test_identical_parents_give_the_same_child(self):
        parent = ["C4", "C1", "C3", "C2"]
        for seed in range(20):
            self.assertEqual(order_crossover(parent, parent, random.Random(seed)), parent)

    def test_child_is_a_new_list(self):
        parent = ["C1"]
        child = order_crossover(parent, parent, random.Random(0))
        self.assertEqual(child, parent)
        self.assertIsNot(child, parent)


class TestSwapMutation(unittest.TestCase):

    def test_rate_zero_never_mutates(self):
        route = ["C1", "C2", "C3", "C4", "C5"]
        for seed in range(20):
            self.assertEqual(swap_mutation(route, 0.0, random.Random(seed)), route)

    def test_rate_one_always_swaps_two_customers(self):
        route = ["C1", "C2", "C3", "C4", "C5"]
        for seed in range(50):
            mutated = swap_mutation(route, 1.0, random.Random(seed))
            self.assertTrue(validate_customer_route(mutated, route))
            changed = [k for k in range(len(route)) if route[k] != mutated[k]]
            self.assertEqual(len(changed), 2)
        # The original is not changed.
        self.assertEqual(route, ["C1", "C2", "C3", "C4", "C5"])

    def test_rate_is_respected(self):
        route = ["C1", "C2", "C3", "C4", "C5"]
        rng = random.Random(0)
        mutated_count = 0
        for _ in range(5000):
            if swap_mutation(route, 0.2, rng) != route:
                mutated_count += 1
        self.assertGreater(mutated_count, 850)
        self.assertLess(mutated_count, 1150)

    def test_one_customer(self):
        self.assertEqual(swap_mutation(["C1"], 1.0, random.Random(0)), ["C1"])


class TestGeneticAlgorithm(unittest.TestCase):

    def test_result_is_valid_for_many_sizes_and_seeds(self):
        for n in [1, 2, 3, 5, 10, 20]:
            locations, customer_ids = make_random_problem(n, seed=n)
            for seed in range(3):
                result = genetic_algorithm(locations, customer_ids, random.Random(seed))

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
        result = genetic_algorithm(
            locations, customer_ids, random.Random(1), population_size=30, generations=80
        )
        history = result["history"]

        # One entry for the initial population plus one per generation.
        self.assertEqual(result["iterations"], 80)
        self.assertEqual(len(history), 81)
        self.assertEqual([step for step, cost in history], list(range(81)))
        self.assertAlmostEqual(history[0][1], result["initial_distance"])
        self.assertAlmostEqual(history[-1][1], result["best_distance"])
        self.assertEqual(result["evaluations"], 30 * 81)

        # The best distance of the whole run can never get worse.
        costs = [cost for step, cost in history]
        for earlier, later in zip(costs, costs[1:]):
            self.assertLessEqual(later, earlier)
        self.assertAlmostEqual(result["best_distance"], min(costs))

    def test_improves_on_the_initial_population(self):
        locations, customer_ids = make_random_problem(20, seed=7)
        result = genetic_algorithm(locations, customer_ids, random.Random(0))
        self.assertLess(result["best_distance"], result["initial_distance"])

    def test_small_population(self):
        # Population of 2 with a tournament size larger than the population.
        locations, customer_ids = make_random_problem(8, seed=2)
        result = genetic_algorithm(
            locations,
            customer_ids,
            random.Random(0),
            population_size=2,
            generations=20,
            tournament_size=5,
        )
        self.assertTrue(validate_customer_route(result["best_route"], customer_ids))
        self.assertEqual(len(result["history"]), 21)

    def test_invalid_parameters_are_rejected(self):
        locations, customer_ids = make_random_problem(5, seed=1)
        rng = random.Random(0)
        with self.assertRaisesRegex(ValueError, "population_size"):
            genetic_algorithm(locations, customer_ids, rng, population_size=1)
        with self.assertRaisesRegex(ValueError, "generations"):
            genetic_algorithm(locations, customer_ids, rng, generations=0)
        with self.assertRaisesRegex(ValueError, "tournament_size"):
            genetic_algorithm(locations, customer_ids, rng, tournament_size=0)
        with self.assertRaisesRegex(ValueError, "mutation_rate"):
            genetic_algorithm(locations, customer_ids, rng, mutation_rate=1.5)

    def test_same_seed_gives_same_result(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        first = genetic_algorithm(locations, customer_ids, random.Random(42))
        second = genetic_algorithm(locations, customer_ids, random.Random(42))
        self.assertEqual(first["best_route"], second["best_route"])
        self.assertEqual(first["history"], second["history"])

    def test_different_seeds_give_different_searches(self):
        locations, customer_ids = make_random_problem(15, seed=9)
        histories = set()
        for seed in range(5):
            result = genetic_algorithm(locations, customer_ids, random.Random(seed))
            histories.add(tuple(result["history"]))
        self.assertGreater(len(histories), 1)

    def test_one_customer(self):
        locations = {"W": (0.0, 0.0), "A": (3.0, 4.0)}
        result = genetic_algorithm(locations, ["A"], random.Random(0))
        self.assertEqual(result["best_route"], ["A"])
        self.assertAlmostEqual(result["best_distance"], 10.0)

    def test_inputs_are_not_changed(self):
        locations, customer_ids = make_random_problem(10, seed=4)
        ids_before = list(customer_ids)
        locations_before = dict(locations)
        genetic_algorithm(locations, customer_ids, random.Random(0))
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
            result = genetic_algorithm(locations, customer_ids, random.Random(seed))
            self.assertGreaterEqual(result["best_distance"], optimum - 1e-9)


if __name__ == "__main__":
    unittest.main()
