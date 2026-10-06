# Comparative Delivery Route Optimization Using Hill Climbing, Simulated Annealing and Genetic Algorithm

> **Status:** Phase 1 of 7 is complete (input loading, distance, route
> representation, route validation). The three algorithms, the experiments
> and the plots are added in later phases, and this README is updated as
> each one is finished.

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

*To be implemented in Phase 2.*

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

At this phase the program prints the input data and one random initial
route with its distance. This is the actual output of `python3 main.py`:

```
==================================================
INPUT DATA
==================================================
Warehouse W: (50, 50)
Customers: 5
  C1: (20, 30)
  C2: (70, 20)
  C3: (80, 70)
  C4: (30, 80)
  C5: (60, 10)

==================================================
RANDOM INITIAL ROUTE (no optimization yet)
==================================================
Seed:
42

Route:
W -> C4 -> C2 -> C3 -> C5 -> C1 -> W

Total distance:
303.18
```

Per-algorithm results (best route, best distance, execution time,
iterations/generations) are added in Phases 2–4.

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

*Algorithm parameters are documented here as each algorithm is added.*

## 15. Project structure

```
delivery-route-optimization/
├── data/
│   └── input.csv            sample input
├── algorithms/              the three algorithms (Phases 2–4)
├── utils/
│   ├── data_loader.py       reads and checks the CSV
│   ├── distance.py          Euclidean distance and the route cost function
│   └── route.py             route representation and validation
├── experiments/             experiment runner (Phase 5)
├── results/                 saved plots and result files (Phases 5–6)
├── tests/
│   └── test_phase1.py
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
