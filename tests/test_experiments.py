"""
Phase 5 tests: dataset generation, comparison and the experiment runner.

Run from the project folder:
    python3 -m unittest discover -s tests -v
"""

import contextlib
import csv
import io
import os
import shutil
import sys
import tempfile
import unittest

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

from data.generate_data import generate_dataset
from experiments.run_experiments import run_experiments
from utils.comparison import (
    ALGORITHM_NAMES,
    print_comparison_table,
    run_algorithm,
    run_many,
    summarize,
)
from utils.data_loader import load_locations
from utils.distance import route_distance
from utils.route import validate_customer_route

SAMPLE_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")


class TempFolderTest(unittest.TestCase):
    """Gives every test its own temporary folder, removed afterwards."""

    def setUp(self):
        self.folder = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.folder)


class TestGenerateData(TempFolderTest):

    def test_generated_file_can_be_loaded(self):
        for size in [1, 5, 10, 20, 30]:
            path = os.path.join(self.folder, f"customers_{size}.csv")
            generate_dataset(size, 42, path)
            locations, customer_ids = load_locations(path)

            self.assertEqual(customer_ids, [f"C{k}" for k in range(1, size + 1)])
            self.assertEqual(locations["W"], (50.0, 50.0))
            # No two locations share a position.
            self.assertEqual(len(set(locations.values())), size + 1)
            for x, y in locations.values():
                self.assertTrue(0 <= x <= 100)
                self.assertTrue(0 <= y <= 100)

    def test_same_seed_gives_same_dataset(self):
        first = os.path.join(self.folder, "first.csv")
        second = os.path.join(self.folder, "second.csv")
        generate_dataset(20, 7, first)
        generate_dataset(20, 7, second)
        with open(first) as a, open(second) as b:
            self.assertEqual(a.read(), b.read())

    def test_different_seed_gives_different_dataset(self):
        first = os.path.join(self.folder, "first.csv")
        second = os.path.join(self.folder, "second.csv")
        generate_dataset(20, 7, first)
        generate_dataset(20, 8, second)
        with open(first) as a, open(second) as b:
            self.assertNotEqual(a.read(), b.read())

    def test_invalid_size(self):
        with self.assertRaisesRegex(ValueError, "at least 1"):
            generate_dataset(0, 1, os.path.join(self.folder, "bad.csv"))


class TestComparison(unittest.TestCase):

    def test_run_algorithm_for_every_name(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        for name in ALGORITHM_NAMES:
            result = run_algorithm(name, locations, customer_ids, seed=1)
            self.assertEqual(result["algorithm"], name)
            self.assertEqual(result["seed"], 1)
            self.assertTrue(validate_customer_route(result["best_route"], customer_ids))
            self.assertAlmostEqual(
                result["best_distance"], route_distance(result["best_route"], locations)
            )

    def test_unknown_algorithm(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        with self.assertRaisesRegex(ValueError, "Unknown algorithm"):
            run_algorithm("Random Search", locations, customer_ids, seed=1)

    def test_run_many_uses_every_seed(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        results = run_many("Hill Climbing", locations, customer_ids, [3, 4, 5])
        self.assertEqual([result["seed"] for result in results], [3, 4, 5])

    def test_same_seed_is_reproducible(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        for name in ALGORITHM_NAMES:
            first = run_algorithm(name, locations, customer_ids, seed=9)
            second = run_algorithm(name, locations, customer_ids, seed=9)
            self.assertEqual(first["best_route"], second["best_route"])
            self.assertEqual(first["history"], second["history"])

    def test_hill_climbing_and_annealing_share_the_initial_route(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        hc = run_algorithm("Hill Climbing", locations, customer_ids, seed=5)
        sa = run_algorithm("Simulated Annealing", locations, customer_ids, seed=5)
        self.assertEqual(hc["initial_route"], sa["initial_route"])

    def test_summarize_with_known_numbers(self):
        results = [
            {"algorithm": "Test", "best_distance": 10.0, "execution_time": 1.0,
             "iterations": 5, "evaluations": 50, "best_route": ["A", "B"]},
            {"algorithm": "Test", "best_distance": 20.0, "execution_time": 2.0,
             "iterations": 7, "evaluations": 70, "best_route": ["B", "A"]},
            {"algorithm": "Test", "best_distance": 30.0, "execution_time": 3.0,
             "iterations": 9, "evaluations": 90, "best_route": ["B", "A"]},
        ]
        summary = summarize(results)
        self.assertEqual(summary["runs"], 3)
        self.assertAlmostEqual(summary["best_distance"], 10.0)
        self.assertAlmostEqual(summary["average_distance"], 20.0)
        self.assertAlmostEqual(summary["worst_distance"], 30.0)
        self.assertAlmostEqual(summary["std_dev"], 10.0)
        self.assertAlmostEqual(summary["average_time"], 2.0)
        self.assertAlmostEqual(summary["average_iterations"], 7.0)
        self.assertAlmostEqual(summary["average_evaluations"], 70.0)
        self.assertEqual(summary["best_route"], ["A", "B"])

    def test_summarize_single_run(self):
        summary = summarize([
            {"algorithm": "Test", "best_distance": 10.0, "execution_time": 1.0,
             "iterations": 5, "evaluations": 50, "best_route": ["A"]},
        ])
        self.assertEqual(summary["std_dev"], 0.0)
        self.assertAlmostEqual(summary["average_distance"], 10.0)

    def test_table_contains_every_algorithm(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        summaries = [
            summarize(run_many(name, locations, customer_ids, [1, 2]))
            for name in ALGORITHM_NAMES
        ]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_comparison_table(summaries)
        text = output.getvalue()
        for name in ALGORITHM_NAMES:
            self.assertIn(name, text)
        for column in ["Best Distance", "Average Distance", "Execution Time",
                       "Iterations/Generations"]:
            self.assertIn(column, text)


class TestRunExperiments(TempFolderTest):

    def test_small_experiment(self):
        with contextlib.redirect_stdout(io.StringIO()):
            summary_rows, run_rows = run_experiments(
                sizes=[5, 8],
                runs=3,
                dataset_seed=42,
                data_folder=self.folder,
                results_folder=self.folder,
            )

        # 2 sizes x 3 algorithms, and 3 runs of each.
        self.assertEqual(len(summary_rows), 6)
        self.assertEqual(len(run_rows), 18)

        # The saved files hold the same rows.
        with open(os.path.join(self.folder, "experiment_summary.csv")) as csv_file:
            saved_summary = list(csv.DictReader(csv_file))
        with open(os.path.join(self.folder, "experiment_runs.csv")) as csv_file:
            saved_runs = list(csv.DictReader(csv_file))
        self.assertEqual(len(saved_summary), 6)
        self.assertEqual(len(saved_runs), 18)

        # The summary agrees with the single runs it was built from.
        for row in summary_rows:
            distances = [
                run["best_distance"] for run in run_rows
                if run["customers"] == row["customers"] and run["algorithm"] == row["algorithm"]
            ]
            self.assertEqual(len(distances), 3)
            self.assertAlmostEqual(row["best_distance"], min(distances), places=3)
            self.assertAlmostEqual(row["worst_distance"], max(distances), places=3)
            self.assertAlmostEqual(row["average_distance"], sum(distances) / 3, places=3)
            self.assertLessEqual(row["best_distance"], row["average_distance"])

        # Every saved route really has the saved distance.
        for size in [5, 8]:
            locations, customer_ids = load_locations(
                os.path.join(self.folder, f"customers_{size}.csv")
            )
            for run in run_rows:
                if run["customers"] != size:
                    continue
                route = run["best_route"].split(" -> ")[1:-1]
                self.assertTrue(validate_customer_route(route, customer_ids))
                self.assertAlmostEqual(
                    run["best_distance"], route_distance(route, locations), places=3
                )


if __name__ == "__main__":
    unittest.main()
