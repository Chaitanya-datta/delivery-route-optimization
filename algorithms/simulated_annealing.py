"""
Simulated Annealing, written from scratch.

Idea:
    Keep ONE current route, like Hill Climbing. Each iteration tries one
    random swap. A shorter route is always accepted. A longer route is
    SOMETIMES accepted, with a probability that depends on the temperature:

        high temperature -> worse routes are accepted often  (exploration)
        low temperature  -> worse routes are almost never accepted (focused)

    The temperature starts high and is reduced a little every iteration.
    Accepting worse routes early on lets the search leave a local optimum
    that would trap Hill Climbing.
"""

import math
import time

from utils.distance import route_distance
from utils.route import random_route, swap_positions


def random_neighbour(customer_route, rng):
    """
    NEIGHBOUR: swap two randomly chosen, different customer positions.
    This is the same swap action that Hill Climbing uses.
    """
    i, j = rng.sample(range(len(customer_route)), 2)
    return swap_positions(customer_route, i, j)


def acceptance_probability(delta, temperature):
    """
    Probability of accepting a route that is worse by `delta`.

        probability = exp(-delta / temperature)

    A small delta or a high temperature gives a probability close to 1.
    A large delta or a low temperature gives a probability close to 0.
    """
    if temperature <= 0:
        return 0.0  # avoids division by zero: never accept a worse route
    return math.exp(-delta / temperature)


def simulated_annealing(
    locations,
    customer_ids,
    rng,
    initial_temperature=100.0,
    cooling_rate=0.999,
    minimum_temperature=0.001,
    max_iterations=20000,
):
    """
    Run Simulated Annealing and return a dictionary with the results.

    locations           - {location_id: (x, y)} including the warehouse
    customer_ids        - list of all customer IDs
    rng                 - random.Random object
    initial_temperature - starting temperature
    cooling_rate        - temperature is multiplied by this every iteration
    minimum_temperature - the search stops when the temperature falls below this
    max_iterations      - safety limit on the number of iterations
    """
    if initial_temperature <= 0:
        raise ValueError("initial_temperature must be greater than 0.")
    if minimum_temperature <= 0:
        raise ValueError("minimum_temperature must be greater than 0.")
    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate must be between 0 and 1 (for example 0.999).")

    start_time = time.perf_counter()

    # INITIAL STATE: a random ordering of all customers.
    current_route = random_route(customer_ids, rng)
    current_cost = route_distance(current_route, locations)

    initial_route = list(current_route)
    initial_cost = current_cost

    # Best solution found so far. The current route is allowed to get
    # worse, so the best route must be remembered separately.
    best_route = list(current_route)
    best_cost = current_cost

    temperature = initial_temperature
    iterations = 0
    evaluations = 1  # number of routes whose distance was calculated
    worse_moves_accepted = 0
    stop_reason = "iteration limit reached"

    # Convergence history: (iteration, best distance found so far).
    history = [(0, best_cost)]

    # With one customer there is nothing to swap.
    if len(customer_ids) < 2:
        stop_reason = "only one customer (no swap possible)"
        max_iterations = 0

    while iterations < max_iterations:

        if temperature < minimum_temperature:
            stop_reason = "minimum temperature reached"
            break

        iterations += 1

        neighbour = random_neighbour(current_route, rng)
        neighbour_cost = route_distance(neighbour, locations)
        evaluations += 1

        # delta < 0 means the neighbour is shorter (better).
        delta = neighbour_cost - current_cost

        if delta < 0:
            # AI DECISION: always accept a better route.
            accept = True
        else:
            # AI DECISION: probabilistically accept a worse route based on temperature.
            probability = acceptance_probability(delta, temperature)
            random_number = rng.random()
            accept = random_number < probability

            if accept and delta > 0:
                worse_moves_accepted += 1

        if accept:
            current_route = neighbour
            current_cost = neighbour_cost

            if current_cost < best_cost:
                best_route = list(current_route)
                best_cost = current_cost

        history.append((iterations, best_cost))

        # COOLING SCHEDULE: reduce the temperature a little every iteration.
        temperature = temperature * cooling_rate

    execution_time = time.perf_counter() - start_time

    return {
        "algorithm": "Simulated Annealing",
        "best_route": best_route,
        "best_distance": best_cost,
        "initial_route": initial_route,
        "initial_distance": initial_cost,
        "iterations": iterations,
        "evaluations": evaluations,
        "worse_moves_accepted": worse_moves_accepted,
        "final_temperature": temperature,
        "stop_reason": stop_reason,
        "history": history,
        "execution_time": execution_time,
    }
