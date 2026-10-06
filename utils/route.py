"""
Route representation and validation.

STATE (customer route):
    A list holding every customer ID exactly once, for example
    [C1, C4, C2, C5, C3]. The algorithms only change this list.

Complete route:
    The customer route with the warehouse fixed at both ends:
    [W, C1, C4, C2, C5, C3, W]
"""

from utils.data_loader import WAREHOUSE_ID


def random_route(customer_ids, rng):
    """
    INITIAL STATE: a random ordering of all customers.

    rng is a random.Random object, so the result is reproducible
    when the same seed is used.
    """
    route = list(customer_ids)  # copy, so the original list is not changed
    rng.shuffle(route)
    return route


def build_complete_route(customer_route):
    """Add the warehouse at the beginning and at the end."""
    return [WAREHOUSE_ID] + list(customer_route) + [WAREHOUSE_ID]


def format_route(customer_route):
    """Text form of the complete route, e.g. 'W -> C1 -> C2 -> W'."""
    return " -> ".join(build_complete_route(customer_route))


def validate_customer_route(customer_route, customer_ids):
    """
    Check that a customer route is a valid permutation of the customers.

    Returns True if valid. Raises ValueError explaining the problem if not.
    """
    if WAREHOUSE_ID in customer_route:
        raise ValueError(
            "Invalid route: the warehouse must not appear among the customers."
        )

    duplicates = []
    seen = set()
    for customer_id in customer_route:
        if customer_id in seen and customer_id not in duplicates:
            duplicates.append(customer_id)
        seen.add(customer_id)
    if duplicates:
        raise ValueError(f"Invalid route: duplicate customers {duplicates}.")

    missing = [c for c in customer_ids if c not in seen]
    if missing:
        raise ValueError(f"Invalid route: missing customers {missing}.")

    unknown = [c for c in customer_route if c not in customer_ids]
    if unknown:
        raise ValueError(f"Invalid route: unknown customers {unknown}.")

    return True


def validate_complete_route(complete_route, customer_ids):
    """
    Check a complete route such as [W, C1, C2, W]:
    the warehouse must be first and last, and the part in between
    must be a valid customer route.
    """
    if len(complete_route) < 3:
        raise ValueError(
            "Invalid route: a complete route needs the warehouse, "
            "at least one customer, and the warehouse again."
        )

    if complete_route[0] != WAREHOUSE_ID:
        raise ValueError("Invalid route: it must start at the warehouse.")

    if complete_route[-1] != WAREHOUSE_ID:
        raise ValueError("Invalid route: it must end at the warehouse.")

    return validate_customer_route(complete_route[1:-1], customer_ids)
