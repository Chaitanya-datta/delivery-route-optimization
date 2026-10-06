"""
Phase 1 tests: CSV loading, distance, route representation and validation.

Run from the project folder:
    python3 -m unittest discover -s tests -v
"""

import math
import os
import random
import sys
import tempfile
import unittest

PROJECT_FOLDER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_FOLDER)

from utils.data_loader import load_locations
from utils.distance import euclidean_distance, route_distance
from utils.route import (
    build_complete_route,
    format_route,
    random_route,
    validate_complete_route,
    validate_customer_route,
)

SAMPLE_INPUT = os.path.join(PROJECT_FOLDER, "data", "input.csv")


def write_temp_csv(text):
    """Write text to a temporary CSV file and return its path."""
    handle, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(handle, "w", encoding="utf-8", newline="") as csv_file:
        csv_file.write(text)
    return path


class TestDataLoader(unittest.TestCase):

    def load_text(self, text):
        path = write_temp_csv(text)
        try:
            return load_locations(path)
        finally:
            os.remove(path)

    def test_sample_input(self):
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        self.assertEqual(customer_ids, ["C1", "C2", "C3", "C4", "C5"])
        self.assertEqual(locations["W"], (50.0, 50.0))
        self.assertEqual(locations["C5"], (60.0, 10.0))
        self.assertEqual(len(locations), 6)

    def test_different_csv_is_read_dynamically(self):
        locations, customer_ids = self.load_text("ID,X,Y\nC9,1.5,2\nW,0,0\nA,-3,4\n")
        self.assertEqual(customer_ids, ["C9", "A"])
        self.assertEqual(locations["C9"], (1.5, 2.0))
        self.assertEqual(locations["A"], (-3.0, 4.0))

    def test_blank_lines_and_spaces_are_tolerated(self):
        locations, customer_ids = self.load_text("id, x, y\n\nW, 0, 0\n C1 , 3 , 4 \n\n")
        self.assertEqual(customer_ids, ["C1"])
        self.assertEqual(locations["C1"], (3.0, 4.0))

    def test_file_saved_by_excel_with_byte_order_mark(self):
        locations, customer_ids = self.load_text("\ufeffID,X,Y\nW,0,0\nC1,3,4\n")
        self.assertEqual(customer_ids, ["C1"])
        self.assertEqual(locations["W"], (0.0, 0.0))

    def test_windows_line_endings(self):
        locations, customer_ids = self.load_text("ID,X,Y\r\nW,0,0\r\nC1,3,4\r\n")
        self.assertEqual(customer_ids, ["C1"])
        self.assertEqual(locations["C1"], (3.0, 4.0))

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_locations("this_file_does_not_exist.csv")

    def test_empty_file(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            self.load_text("")

    def test_wrong_header(self):
        with self.assertRaisesRegex(ValueError, "header"):
            self.load_text("Name,Lat,Lon\nW,0,0\nC1,1,1\n")

    def test_missing_coordinate(self):
        with self.assertRaisesRegex(ValueError, "missing coordinate"):
            self.load_text("ID,X,Y\nW,0,0\nC1,5,\n")

    def test_missing_column(self):
        with self.assertRaisesRegex(ValueError, "expected 3 values"):
            self.load_text("ID,X,Y\nW,0,0\nC1,5\n")

    def test_invalid_coordinate(self):
        with self.assertRaisesRegex(ValueError, "invalid coordinate"):
            self.load_text("ID,X,Y\nW,0,0\nC1,abc,5\n")

    def test_nan_coordinate(self):
        with self.assertRaisesRegex(ValueError, "invalid coordinate"):
            self.load_text("ID,X,Y\nW,0,0\nC1,nan,5\n")

    def test_duplicate_id(self):
        with self.assertRaisesRegex(ValueError, "duplicate ID 'C1'"):
            self.load_text("ID,X,Y\nW,0,0\nC1,1,1\nC1,2,2\n")

    def test_duplicate_warehouse(self):
        with self.assertRaisesRegex(ValueError, "duplicate ID 'W'"):
            self.load_text("ID,X,Y\nW,0,0\nC1,1,1\nW,2,2\n")

    def test_missing_id(self):
        with self.assertRaisesRegex(ValueError, "ID is missing"):
            self.load_text("ID,X,Y\nW,0,0\n,1,1\n")

    def test_no_warehouse(self):
        with self.assertRaisesRegex(ValueError, "No warehouse"):
            self.load_text("ID,X,Y\nC1,1,1\nC2,2,2\n")

    def test_no_customers(self):
        with self.assertRaisesRegex(ValueError, "No customers"):
            self.load_text("ID,X,Y\nW,0,0\n")


class TestDistance(unittest.TestCase):

    def test_euclidean_distance(self):
        self.assertAlmostEqual(euclidean_distance((0, 0), (3, 4)), 5.0)
        self.assertAlmostEqual(euclidean_distance((2, 2), (2, 2)), 0.0)
        # Direction does not matter.
        self.assertAlmostEqual(
            euclidean_distance((1, 7), (4, 3)), euclidean_distance((4, 3), (1, 7))
        )

    def test_route_distance_includes_both_warehouse_legs(self):
        # W(0,0) -> A(3,4) -> W(0,0) = 5 out + 5 back
        locations = {"W": (0.0, 0.0), "A": (3.0, 4.0)}
        self.assertAlmostEqual(route_distance(["A"], locations), 10.0)

    def test_route_distance_square(self):
        # Driving around a 10 x 10 square = 40.
        locations = {"W": (0, 0), "A": (10, 0), "B": (10, 10), "C": (0, 10)}
        self.assertAlmostEqual(route_distance(["A", "B", "C"], locations), 40.0)
        # Crossing the diagonals is longer: 10 + 10 + two diagonals.
        self.assertAlmostEqual(
            route_distance(["B", "A", "C"], locations), 20 + 2 * math.sqrt(200)
        )

    def test_route_distance_on_sample_input(self):
        # Worked out by hand for W -> C1 -> C2 -> C3 -> C4 -> C5 -> W.
        locations, customer_ids = load_locations(SAMPLE_INPUT)
        expected = (
            math.sqrt(1300)        # W  -> C1
            + 3 * math.sqrt(2600)  # C1 -> C2, C2 -> C3, C3 -> C4
            + math.sqrt(5800)      # C4 -> C5
            + math.sqrt(1700)      # C5 -> W
        )
        self.assertAlmostEqual(route_distance(customer_ids, locations), expected)
        # 36.0555 + 3 * 50.9902 + 76.1577 + 41.2311
        self.assertAlmostEqual(expected, 306.4149, places=3)


class TestRoute(unittest.TestCase):

    customer_ids = ["C1", "C2", "C3", "C4", "C5"]

    def test_complete_route_has_warehouse_at_both_ends(self):
        self.assertEqual(build_complete_route(["C2", "C1"]), ["W", "C2", "C1", "W"])
        self.assertEqual(format_route(["C2", "C1"]), "W -> C2 -> C1 -> W")

    def test_random_route_is_valid_and_does_not_change_input(self):
        original = list(self.customer_ids)
        for seed in range(50):
            route = random_route(self.customer_ids, random.Random(seed))
            self.assertTrue(validate_customer_route(route, self.customer_ids))
        self.assertEqual(self.customer_ids, original)

    def test_same_seed_gives_same_route(self):
        first = random_route(self.customer_ids, random.Random(42))
        second = random_route(self.customer_ids, random.Random(42))
        self.assertEqual(first, second)

    def test_different_seeds_give_different_routes(self):
        routes = set()
        for seed in range(20):
            routes.add(tuple(random_route(self.customer_ids, random.Random(seed))))
        self.assertGreater(len(routes), 1)

    def test_one_customer(self):
        route = random_route(["C1"], random.Random(1))
        self.assertEqual(route, ["C1"])
        self.assertTrue(validate_complete_route(build_complete_route(route), ["C1"]))

    def test_duplicate_customer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_customer_route(["C1", "C2", "C2", "C4", "C5"], self.customer_ids)

    def test_missing_customer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_customer_route(["C1", "C2", "C3", "C4"], self.customer_ids)

    def test_unknown_customer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown"):
            validate_customer_route(
                ["C1", "C2", "C3", "C4", "C5", "C99"], self.customer_ids
            )

    def test_warehouse_inside_customer_route_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "warehouse"):
            validate_customer_route(["C1", "W", "C3", "C4", "C5"], self.customer_ids)

    def test_complete_route_must_start_at_warehouse(self):
        with self.assertRaisesRegex(ValueError, "start"):
            validate_complete_route(
                ["C1", "C2", "C3", "C4", "C5", "W"], self.customer_ids
            )

    def test_complete_route_must_end_at_warehouse(self):
        with self.assertRaisesRegex(ValueError, "end"):
            validate_complete_route(
                ["W", "C1", "C2", "C3", "C4", "C5"], self.customer_ids
            )

    def test_valid_complete_route(self):
        self.assertTrue(
            validate_complete_route(
                ["W", "C3", "C1", "C5", "C2", "C4", "W"], self.customer_ids
            )
        )


if __name__ == "__main__":
    unittest.main()
