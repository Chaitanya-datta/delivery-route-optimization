"""
Reads the delivery locations from a CSV file.

Expected CSV format:

    ID,X,Y
    W,50,50
    C1,20,30
    C2,70,20

The row with ID "W" is the warehouse. Every other row is a customer.
"""

import csv
import math
import os

WAREHOUSE_ID = "W"


def load_locations(csv_path):
    """
    Load the locations from a CSV file.

    Returns two things:
        locations    - dictionary  {location_id: (x, y)}  including the warehouse
        customer_ids - list of customer IDs in the order they appear in the file

    Raises FileNotFoundError or ValueError with a clear message if the
    input is not usable.
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Input file not found: {csv_path}")

    # "utf-8-sig" also accepts files saved by Excel as "CSV UTF-8", which
    # start with an invisible marker before the first column name.
    with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
        rows = list(csv.reader(csv_file))

    # Ignore completely blank lines.
    rows = [row for row in rows if any(cell.strip() for cell in row)]

    if len(rows) == 0:
        raise ValueError(f"Input file is empty: {csv_path}")

    header = [cell.strip().upper() for cell in rows[0]]
    if header != ["ID", "X", "Y"]:
        raise ValueError(
            f"Invalid header {rows[0]}. The first line must be: ID,X,Y"
        )

    locations = {}
    customer_ids = []

    # Line numbers start at 2 because line 1 is the header.
    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) != 3:
            raise ValueError(
                f"Line {line_number}: expected 3 values (ID,X,Y) but found {len(row)}."
            )

        location_id = row[0].strip()
        x_text = row[1].strip()
        y_text = row[2].strip()

        if location_id == "":
            raise ValueError(f"Line {line_number}: the ID is missing.")

        if x_text == "" or y_text == "":
            raise ValueError(
                f"Line {line_number}: location '{location_id}' has a missing coordinate."
            )

        try:
            x = float(x_text)
            y = float(y_text)
        except ValueError:
            raise ValueError(
                f"Line {line_number}: location '{location_id}' has an invalid "
                f"coordinate ({x_text}, {y_text}). Coordinates must be numbers."
            )

        # float() accepts "nan" and "inf", which are not usable coordinates.
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError(
                f"Line {line_number}: location '{location_id}' has an invalid "
                f"coordinate ({x_text}, {y_text}). Coordinates must be finite numbers."
            )

        if location_id in locations:
            raise ValueError(f"Line {line_number}: duplicate ID '{location_id}'.")

        locations[location_id] = (x, y)
        if location_id != WAREHOUSE_ID:
            customer_ids.append(location_id)

    if WAREHOUSE_ID not in locations:
        raise ValueError(
            f"No warehouse found. One row must have the ID '{WAREHOUSE_ID}'."
        )

    if len(customer_ids) == 0:
        raise ValueError("No customers found. At least one customer is required.")

    return locations, customer_ids
