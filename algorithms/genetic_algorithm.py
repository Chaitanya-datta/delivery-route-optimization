"""
Genetic Algorithm, written from scratch.

Idea:
    Instead of one current route, keep a POPULATION of routes. In every
    generation a new population is built from the old one:

        selection - better routes are more likely to become parents
        crossover - a child route combines the order of two parents
        mutation  - occasionally two customers of the child are swapped

    Good partial orderings spread through the population over the
    generations, while mutation keeps introducing new variation.

CHROMOSOME:
    One customer ordering, for example [C1, C4, C3, C2, C5].
    The warehouse is not part of the chromosome.

FITNESS:
    This is a minimization problem, so the route distance itself is used:
    the shorter the route, the fitter the chromosome.
"""

import time

from utils.distance import route_distance
from utils.route import random_route, swap_positions


def create_population(customer_ids, population_size, rng):
    """INITIAL POPULATION: random valid customer orderings."""
    population = []
    for _ in range(population_size):
        population.append(random_route(customer_ids, rng))
    return population


def evaluate_population(population, locations):
    """Return the route distance of every chromosome (same order as the population)."""
    costs = []
    for chromosome in population:
        costs.append(route_distance(chromosome, locations))
    return costs


def tournament_selection(population, costs, tournament_size, rng):
    """
    SELECTION: pick a few chromosomes at random and return the best of them.

    Better routes win more tournaments, so they become parents more often,
    but a weaker route can still be chosen if it meets only weaker rivals.
    """
    # A tournament cannot be larger than the population.
    tournament_size = min(tournament_size, len(population))

    competitors = rng.sample(range(len(population)), tournament_size)

    winner = competitors[0]
    for index in competitors[1:]:
        # AI DECISION: the competitor with the shorter route wins.
        if costs[index] < costs[winner]:
            winner = index

    return population[winner]


def order_crossover(parent1, parent2, rng):
    """
    CROSSOVER (Order Crossover): build a child from two parents without
    creating duplicate or missing customers.

    Step 1: copy a random slice of parent1 into the same positions of the child.
    Step 2: fill the empty positions, left to right, with the remaining
            customers in the order they appear in parent2.

    Example with the slice at positions 1 to 2:
        parent1 = [C1, C2, C3, C4, C5]
        parent2 = [C3, C5, C1, C2, C4]
        step 1  = [ _, C2, C3,  _,  _]      slice copied from parent1
        step 2  = [C5, C2, C3, C1, C4]      C5, C1, C4 taken in parent2's order

    A normal one-point crossover could give [C1, C2, C1, C2, C4], which is
    not a valid route. This method always gives a valid permutation.
    """
    size = len(parent1)

    # With fewer than two customers there is nothing to combine.
    if size < 2:
        return list(parent1)

    start, end = sorted(rng.sample(range(size), 2))

    # Step 1: copy the slice from parent1.
    child = [None] * size
    for position in range(start, end + 1):
        child[position] = parent1[position]

    customers_in_slice = set(parent1[start:end + 1])

    # Step 2: the customers still missing, in parent2's order.
    remaining = []
    for customer_id in parent2:
        if customer_id not in customers_in_slice:
            remaining.append(customer_id)

    next_remaining = 0
    for position in range(size):
        if child[position] is None:
            child[position] = remaining[next_remaining]
            next_remaining += 1

    return child


def swap_mutation(chromosome, mutation_rate, rng):
    """
    MUTATION: with probability mutation_rate, swap two random customers.

    Returns a new chromosome. Mutation adds variation that crossover
    alone cannot create, which helps avoid all routes becoming the same.
    """
    if len(chromosome) < 2:
        return list(chromosome)

    if rng.random() < mutation_rate:
        i, j = rng.sample(range(len(chromosome)), 2)
        return swap_positions(chromosome, i, j)

    return list(chromosome)


def index_of_best(costs):
    """Position of the smallest distance in the list."""
    best_index = 0
    for index in range(1, len(costs)):
        if costs[index] < costs[best_index]:
            best_index = index
    return best_index


def genetic_algorithm(
    locations,
    customer_ids,
    rng,
    population_size=50,
    generations=200,
    tournament_size=3,
    mutation_rate=0.2,
):
    """
    Run the Genetic Algorithm and return a dictionary with the results.

    locations       - {location_id: (x, y)} including the warehouse
    customer_ids    - list of all customer IDs
    rng             - random.Random object
    population_size - number of routes in the population
    generations     - number of new populations to create
    tournament_size - number of routes compared in each selection
    mutation_rate   - probability (0 to 1) that a child is mutated
    """
    if population_size < 2:
        raise ValueError("population_size must be at least 2.")
    if generations < 1:
        raise ValueError("generations must be at least 1.")
    if tournament_size < 1:
        raise ValueError("tournament_size must be at least 1.")
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate must be between 0 and 1.")

    start_time = time.perf_counter()

    # Initial population and its distances.
    population = create_population(customer_ids, population_size, rng)
    costs = evaluate_population(population, locations)
    evaluations = len(population)

    # Best solution found over the whole run.
    best_index = index_of_best(costs)
    best_route = list(population[best_index])
    best_cost = costs[best_index]

    initial_best_route = list(best_route)
    initial_best_cost = best_cost

    # Convergence history: (generation, best distance found so far).
    history = [(0, best_cost)]

    for generation in range(1, generations + 1):
        new_population = []

        # ELITISM: the best route of the current population is copied
        # unchanged, so a good route is never lost between generations.
        new_population.append(list(population[index_of_best(costs)]))

        # Fill the rest of the new population with children.
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, costs, tournament_size, rng)
            parent2 = tournament_selection(population, costs, tournament_size, rng)

            child = order_crossover(parent1, parent2, rng)
            child = swap_mutation(child, mutation_rate, rng)

            new_population.append(child)

        # The new generation replaces the old one.
        population = new_population
        costs = evaluate_population(population, locations)
        evaluations += len(population)

        # BEST SOLUTION TRACKING: keep the best route of the whole run.
        generation_best = index_of_best(costs)
        if costs[generation_best] < best_cost:
            best_route = list(population[generation_best])
            best_cost = costs[generation_best]

        history.append((generation, best_cost))

    execution_time = time.perf_counter() - start_time

    return {
        "algorithm": "Genetic Algorithm",
        "best_route": best_route,
        "best_distance": best_cost,
        # For the GA the "initial" route is the best one in the first population.
        "initial_route": initial_best_route,
        "initial_distance": initial_best_cost,
        "iterations": generations,
        "evaluations": evaluations,
        "stop_reason": "generation limit reached",
        "history": history,
        "execution_time": execution_time,
    }
