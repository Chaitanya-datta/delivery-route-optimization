"""
Hill Climbing (steepest-descent version), written from scratch.

Idea:
    Keep ONE current route. Look at every route that can be reached by
    swapping two customers (the neighbourhood). Move to the best of those
    neighbours, but only if it is shorter than the current route. Repeat
    until no neighbour is shorter. That final route is a LOCAL OPTIMUM:
    no single swap improves it, although a better route may still exist
    somewhere else.
"""

import time

from utils.distance import route_distance
from utils.route import random_route, swap_positions


def generate_neighbours(customer_route):
    """
    NEIGHBOURHOOD: every route obtained by swapping two customer positions.

    For n customers there are n * (n - 1) / 2 neighbours.
    Example for [C1, C2, C3]:
        swap positions 0,1 -> [C2, C1, C3]
        swap positions 0,2 -> [C3, C2, C1]
        swap positions 1,2 -> [C1, C3, C2]
    """
    neighbours = []
    number_of_customers = len(customer_route)

    for i in range(number_of_customers):
        for j in range(i + 1, number_of_customers):
            neighbours.append(swap_positions(customer_route, i, j))

    return neighbours


def hill_climbing(locations, customer_ids, rng, max_iterations=1000):
    """
    Run Hill Climbing and return a dictionary with the results.

    locations      - {location_id: (x, y)} including the warehouse
    customer_ids   - list of all customer IDs
    rng            - random.Random object (used only for the initial route)
    max_iterations - safety limit on the number of iterations
    """
    start_time = time.perf_counter()

    # INITIAL STATE: a random ordering of all customers.
    current_route = random_route(customer_ids, rng)
    current_cost = route_distance(current_route, locations)

    initial_route = list(current_route)
    initial_cost = current_cost

    # Best solution found so far.
    best_route = list(current_route)
    best_cost = current_cost

    iterations = 0
    evaluations = 1  # number of routes whose distance was calculated
    stop_reason = "iteration limit reached"

    # Convergence history: (iteration, distance of the current route).
    history = [(0, current_cost)]

    while iterations < max_iterations:
        iterations += 1

        # Evaluate every neighbour and remember the shortest one.
        best_neighbour = None
        best_neighbour_cost = float("inf")

        for neighbour in generate_neighbours(current_route):
            neighbour_cost = route_distance(neighbour, locations)
            evaluations += 1

            if neighbour_cost < best_neighbour_cost:
                best_neighbour = neighbour
                best_neighbour_cost = neighbour_cost

        # AI DECISION: move to the improving neighbouring route.
        # The move happens only if the best neighbour is strictly shorter
        # than the current route. Hill Climbing never accepts a worse route.
        if best_neighbour_cost < current_cost:
            current_route = best_neighbour
            current_cost = best_neighbour_cost

            best_route = list(current_route)
            best_cost = current_cost

            history.append((iterations, current_cost))
        else:
            # No neighbour is better: we are at a local optimum, so stop.
            history.append((iterations, current_cost))
            stop_reason = "local optimum (no improving neighbour)"
            break

    execution_time = time.perf_counter() - start_time

    return {
        "algorithm": "Hill Climbing",
        "best_route": best_route,
        "best_distance": best_cost,
        "initial_route": initial_route,
        "initial_distance": initial_cost,
        "iterations": iterations,
        "evaluations": evaluations,
        "stop_reason": stop_reason,
        "history": history,
        "execution_time": execution_time,
    }
