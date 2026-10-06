"""
Phase 6 tests: the plots.

Run from the project folder:
    python3 -m unittest discover -s tests -v

These tests are skipped if Matplotlib is not installed.
"""

import copy
import os
import shutil
import sys
import tempfile
import unittest

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

try:
    from utils.visualization import (
        ALGORITHM_COLORS,
        plot_comparison,
        plot_convergence,
        plot_routes,
    )
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from utils.comparison import ALGORITHM_NAMES, run_algorithm
from utils.data_loader import load_locations

SAMPLE_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@unittest.skipUnless(MATPLOTLIB_AVAILABLE, "Matplotlib is not installed")
class TestVisualization(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp()
        self.locations, self.customer_ids = load_locations(SAMPLE_INPUT)
        self.results = [
            run_algorithm(name, self.locations, self.customer_ids, seed=1)
            for name in ALGORITHM_NAMES
        ]

    def tearDown(self):
        shutil.rmtree(self.folder)

    def assert_is_png(self, path):
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 5000)
        with open(path, "rb") as image_file:
            self.assertEqual(image_file.read(8), PNG_SIGNATURE)

    def test_every_algorithm_has_a_colour(self):
        for name in ALGORITHM_NAMES:
            self.assertIn(name, ALGORITHM_COLORS)
        self.assertEqual(len(set(ALGORITHM_COLORS.values())), len(ALGORITHM_NAMES))

    def test_route_plot(self):
        path = os.path.join(self.folder, "routes.png")
        plot_routes(self.locations, self.results, path, title="Test")
        self.assert_is_png(path)

    def test_convergence_plot(self):
        path = os.path.join(self.folder, "convergence.png")
        plot_convergence(self.results, path, title="Test")
        self.assert_is_png(path)

    def test_comparison_chart(self):
        summary_rows = []
        for size in [5, 10]:
            for number, name in enumerate(ALGORITHM_NAMES):
                summary_rows.append({
                    "customers": size,
                    "algorithm": name,
                    "average_distance": 100.0 * size + number,
                    "std_dev": 5.0,
                })
        path = os.path.join(self.folder, "comparison.png")
        plot_comparison(summary_rows, path, title="Test")
        self.assert_is_png(path)

    def test_plotting_does_not_change_the_results(self):
        results_before = copy.deepcopy(self.results)
        locations_before = dict(self.locations)
        plot_routes(self.locations, self.results, os.path.join(self.folder, "a.png"))
        plot_convergence(self.results, os.path.join(self.folder, "b.png"))
        self.assertEqual(self.results, results_before)
        self.assertEqual(self.locations, locations_before)

    def test_single_algorithm_and_one_customer(self):
        locations = {"W": (0.0, 0.0), "A": (3.0, 4.0)}
        result = run_algorithm("Hill Climbing", locations, ["A"], seed=1)
        routes_path = os.path.join(self.folder, "one_route.png")
        convergence_path = os.path.join(self.folder, "one_convergence.png")
        plot_routes(locations, [result], routes_path)
        plot_convergence([result], convergence_path)
        self.assert_is_png(routes_path)
        self.assert_is_png(convergence_path)


if __name__ == "__main__":
    unittest.main()
