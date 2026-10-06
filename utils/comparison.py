"""
Running the algorithms several times and comparing the results.

Nothing in this file makes a search decision. It only calls the three
algorithms with the parameters from config.py and summarizes what they
returned.
"""

import random
import statistics

import config
from algorithms.genetic_algorithm import genetic_algorithm
from algorithms.hill_climbing import hill_climbing
from algorithms.simulated_annealing import simulated_annealing
from utils.route import build_complete_route, validate_complete_route

ALGORITHM_NAMES = ["Hill Climbing", "Simulated Annealing", "Genetic Algorithm"]


def run_algorithm(name, locations, customer_ids, seed):
    """
    Run one algorithm once, with the parameters from config.py.

    Every run gets its own random generator created from `seed`, so a
    run can be repeated exactly by using the same seed again.
    """
    rng = random.Random(seed)

    if name == "Hill Climbing":
        result = hill_climbing(
            locations,
            customer_ids,
            rng,
            max_iterations=config.HC_MAX_ITERATIONS,
        )
    elif name == "Simulated Annealing":
        result = simulated_annealing(
            locations,
            customer_ids,
            rng,
            initial_temperature=config.SA_INITIAL_TEMPERATURE,
            cooling_rate=config.SA_COOLING_RATE,
            minimum_temperature=config.SA_MINIMUM_TEMPERATURE,
            max_iterations=config.SA_MAX_ITERATIONS,
        )
    elif name == "Genetic Algorithm":
        result = genetic_algorithm(
            locations,
            customer_ids,
            rng,
            population_size=config.GA_POPULATION_SIZE,
            generations=config.GA_GENERATIONS,
            tournament_size=config.GA_TOURNAMENT_SIZE,
            mutation_rate=config.GA_MUTATION_RATE,
        )
    else:
        raise ValueError(f"Unknown algorithm: {name}")

    # Check that the algorithm returned a valid route.
    validate_complete_route(build_complete_route(result["best_route"]), customer_ids)

    result["seed"] = seed
    return result


def run_many(name, locations, customer_ids, seeds):
    """Run one algorithm once for every seed and return the list of results."""
    results = []
    for seed in seeds:
        results.append(run_algorithm(name, locations, customer_ids, seed))
    return results


def summarize(results):
    """Summarize several runs of the same algorithm."""
    distances = [result["best_distance"] for result in results]
    times = [result["execution_time"] for result in results]
    iterations = [result["iterations"] for result in results]
    evaluations = [result["evaluations"] for result in results]

    # The run with the shortest route.
    best_run = results[0]
    for result in results:
        if result["best_distance"] < best_run["best_distance"]:
            best_run = result

    # Standard deviation needs at least two runs.
    if len(distances) > 1:
        std_dev = statistics.stdev(distances)
    else:
        std_dev = 0.0

    return {
        "algorithm": results[0]["algorithm"],
        "runs": len(results),
        "best_distance": min(distances),
        "average_distance": statistics.mean(distances),
        "std_dev": std_dev,
        "worst_distance": max(distances),
        "average_time": statistics.mean(times),
        "average_iterations": statistics.mean(iterations),
        "average_evaluations": statistics.mean(evaluations),
        "best_route": best_run["best_route"],
    }


def print_comparison_table(summaries):
    """Print one row per algorithm."""
    header = (
        f"{'Algorithm':<20}"
        f"{'Best Distance':>15}"
        f"{'Average Distance':>18}"
        f"{'Std Dev':>10}"
        f"{'Execution Time (s)':>20}"
        f"{'Iterations/Generations':>24}"
        f"{'Route Evaluations':>19}"
    )
    print(header)
    print("-" * len(header))

    for summary in summaries:
        print(
            f"{summary['algorithm']:<20}"
            f"{summary['best_distance']:>15.2f}"
            f"{summary['average_distance']:>18.2f}"
            f"{summary['std_dev']:>10.2f}"
            f"{summary['average_time']:>20.4f}"
            f"{summary['average_iterations']:>24.1f}"
            f"{summary['average_evaluations']:>19.1f}"
        )
