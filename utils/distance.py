"""
Distance calculations.

route_distance() is the COST FUNCTION of the project. All three
algorithms use this same function, so they are compared fairly.
"""

import math

from utils.data_loader import WAREHOUSE_ID


def euclidean_distance(point_a, point_b):
    """Straight-line distance between two (x, y) points."""
    x1, y1 = point_a
    x2, y2 = point_b
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def route_distance(customer_route, locations):
    """
    COST FUNCTION: total travel distance of a route.

    customer_route is only the order of customers, for example
    [C1, C4, C2]. The vehicle actually drives  W -> C1 -> C4 -> C2 -> W,
    so the trip from the warehouse to the first customer and the trip
    from the last customer back to the warehouse are both included.
    """
    warehouse = locations[WAREHOUSE_ID]
    total = 0.0

    # Start at the warehouse.
    previous_point = warehouse

    for customer_id in customer_route:
        current_point = locations[customer_id]
        total += euclidean_distance(previous_point, current_point)
        previous_point = current_point

    # Return from the last customer to the warehouse.
    total += euclidean_distance(previous_point, warehouse)

    return total
