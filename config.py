"""
All parameters of the project in one place.

main.py and the experiment runner both read these values, so every
run uses the same documented settings.
"""

# Randomness
DEFAULT_SEED = 42        # seed of the first run
DEFAULT_RUNS = 10        # number of runs behind the comparison table in main.py

# Hill Climbing
HC_MAX_ITERATIONS = 1000

# Simulated Annealing
SA_INITIAL_TEMPERATURE = 100.0
SA_COOLING_RATE = 0.999
SA_MINIMUM_TEMPERATURE = 0.001
SA_MAX_ITERATIONS = 20000

# Genetic Algorithm
GA_POPULATION_SIZE = 50
GA_GENERATIONS = 200
GA_TOURNAMENT_SIZE = 3
GA_MUTATION_RATE = 0.2

# Experiments
EXPERIMENT_SIZES = [5, 10, 20, 30]   # number of customers in each dataset
EXPERIMENT_RUNS = 30                 # runs of every algorithm on every dataset
EXPERIMENT_DATASET_SEED = 42         # seed used to generate the datasets
