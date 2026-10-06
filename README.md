# Comparative Delivery Route Optimization Using Hill Climbing, Simulated Annealing and Genetic Algorithm

> **Status:** Phases 1–2 of 7 are complete (input loading, distance, route
> representation, route validation, Hill Climbing). Simulated Annealing, the
> Genetic Algorithm, the experiments and the plots are added in later phases,
> and this README is updated as each one is finished.

## 1. Problem statement

A delivery company has **one warehouse**, **one vehicle** and **several
customers**. Every location has an ID and X/Y coordinates. The vehicle must:

1. start at the warehouse,
2. visit every customer exactly once,
3. return to the warehouse.

The objective is to **minimize the total travel distance**.

Example route: `W -> C1 -> C4 -> C2 -> C5 -> C3 -> W`

## 2. Motivation

The number of possible routes grows very quickly: with `n` customers there
are `n!` possible orderings (30 customers give about 2.65 x 10^32). Checking
every route is not practical, so we use local search methods that look for a
good route without trying all of them. The project compares how three such
methods behave on the same problem.

## 3. Module

Module 3 – Local Search

- Hill Climbing
- Simulated Annealing
- Genetic Algorithm

## 4. AI formulation

| Part | Definition |
|---|---|
| **State** | A complete ordering (permutation) of all customers, e.g. `[C1, C4, C2, C5, C3]`. The warehouse is fixed at the start and end, so this means `W -> C1 -> C4 -> C2 -> C5 -> C3 -> W`. |
| **Initial state** | A random valid ordering of all customers. |
| **Action** | Swap two customer positions. |
| **Transition model** | A swap gives another ordering that still contains every customer exactly once, so it is another valid route. |
| **Goal test** | Find a route with the minimum possible total distance. These are search methods that try to find high-quality routes; they do **not** guarantee the mathematically best route. |
| **Cost function** | Total route distance, including warehouse -> first customer and last customer -> warehouse. |

Distance between two locations is the Euclidean distance:

```
distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
```

## 5. Hill Climbing

Code: `algorithms/hill_climbing.py`

Hill Climbing keeps **one** current route and repeatedly tries to improve it.

1. Start from a random route and calculate its distance.
2. Build the **neighbourhood**: every route that can be made by swapping two
   customer positions. For `n` customers there are `n(n-1)/2` neighbours.
3. Calculate the distance of every neighbour and remember the shortest one.
4. **Decision:** if that best neighbour is shorter than the current route,
   move to it. Otherwise stop.
5. Repeat from step 2 until no neighbour is shorter, or the iteration limit
   is reached.

This is the *steepest-descent* form of Hill Climbing: it looks at all
neighbours and takes the best one. The decision in the code is:

```python
# AI DECISION: move to the improving neighbouring route.
if best_neighbour_cost < current_cost:
    current_route = best_neighbour
    current_cost = best_neighbour_cost
```

**Why it works:** every move makes the route strictly shorter, so the
distance can only go down and the search must eventually stop.

**Its weakness:** it stops at the first route that no single swap can
improve. This is a **local optimum**. A shorter route may exist, but reaching
it would need a move that first makes the route longer, and Hill Climbing
never accepts a worse route. Which local optimum it reaches depends on the
random starting route.

Randomness is used only for the starting route. After that the search is
deterministic.

## 6. Simulated Annealing

*To be implemented in Phase 3.*

## 7. Genetic Algorithm

*To be implemented in Phase 4.*

## 8. Input format

A CSV file (default: `data/input.csv`):

```
ID,X,Y
W,50,50
C1,20,30
C2,70,20
C3,80,70
C4,30,80
C5,60,10
```

- The row with ID `W` is the warehouse.
- Every other row is a customer.
- The file is read when the program runs. No coordinates are written inside
  the code, so any CSV in this format can be used.

The loader reports a clear error for: missing file, empty file, wrong header,
missing ID, missing coordinate, non-numeric coordinate, duplicate ID, no
warehouse, and no customers.

## 9. Output format

For each algorithm the program prints the best route, best distance,
execution time and number of iterations. This is the actual output of
`python3 main.py` for Hill Climbing (the input data listing printed before
it is left out here; the execution time differs slightly on every run):

```
Random seed: 42

==================================================
HILL CLIMBING
==================================================

Initial route:
W -> C4 -> C2 -> C3 -> C5 -> C1 -> W

Initial distance:
303.18

Best route:
W -> C4 -> C3 -> C2 -> C5 -> C1 -> W

Best distance:
232.95

Execution time:
0.0001 seconds

Iterations:
2

Stopped because:
local optimum (no improving neighbour)
```

One iteration means one full look at the neighbourhood. The last iteration
is the one that finds no improving neighbour, which is how the algorithm
knows it has reached a local optimum.

Results for Simulated Annealing and the Genetic Algorithm are added in
Phases 3–4.

## 10. Installation

Python 3.10 or newer is required. The algorithms use only the Python
standard library. Matplotlib is needed only for the plots (Phase 6):

```
pip install -r requirements.txt
```

## 11. How to run

```
python3 main.py
python3 main.py --input data/input.csv --seed 42
```

| Option | Meaning | Default |
|---|---|---|
| `--input` | path to the input CSV file | `data/input.csv` |
| `--seed` | random seed, for reproducible runs | `42` |

Run the tests:

```
python3 -m unittest discover -s tests -v
```

## 12. How to generate datasets

*To be added in Phase 5.*

## 13. How to run experiments

*To be added in Phase 5.*

## 14. Parameters

Parameters are set at the top of `main.py`.

**Hill Climbing**

| Parameter | Value | Meaning |
|---|---|---|
| `HC_MAX_ITERATIONS` | 1000 | Safety limit on iterations. Normally the search stops earlier, at a local optimum. |

*Parameters for the other algorithms are added with them.*

## 15. Project structure

```
delivery-route-optimization/
├── data/
│   └── input.csv            sample input
├── algorithms/
│   └── hill_climbing.py     Hill Climbing (others added in Phases 3–4)
├── utils/
│   ├── data_loader.py       reads and checks the CSV
│   ├── distance.py          Euclidean distance and the route cost function
│   └── route.py             route representation and validation
├── experiments/             experiment runner (Phase 5)
├── results/                 saved plots and result files (Phases 5–6)
├── tests/
│   ├── test_phase1.py
│   └── test_hill_climbing.py
├── main.py
├── requirements.txt
└── README.md
```

## 16. Limitations

- One warehouse and one vehicle only.
- Straight-line (Euclidean) distances, not real roads.
- No vehicle capacity, time windows or traffic.
- The algorithms are heuristic: they look for a good route and do not
  guarantee the shortest possible one.

## 17. External AI tool declaration

Claude was used as a supporting programming assistant for code drafting,
debugging, documentation and test-data generation. The AI algorithms and
their decision-making logic were implemented in the project code and
verified by the project members.
