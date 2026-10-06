"""
Plots of the results, saved as PNG files.

Nothing in this file makes a search decision or changes a result. Every
value that is drawn comes from the dictionaries returned by the
algorithms or from the experiment summary.

    plot_routes      - the best route of each algorithm on the map
    plot_convergence - best distance after each iteration / generation
    plot_comparison  - average distance of each algorithm per dataset size
"""

import matplotlib

matplotlib.use("Agg")  # draw straight to files; no window is opened

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from utils.data_loader import WAREHOUSE_ID
from utils.route import build_complete_route

# One fixed colour per algorithm, used in every plot.
ALGORITHM_COLORS = {
    "Hill Climbing": "#2a78d6",        # blue
    "Simulated Annealing": "#eb6834",  # orange
    "Genetic Algorithm": "#1baf7a",    # green
}

BACKGROUND = "#fcfcfb"
TEXT_COLOR = "#0b0b0b"
SECONDARY_TEXT_COLOR = "#52514e"
GRID_COLOR = "#e6e5e0"


def style_axes(ax):
    """Shared look: light background, no box, quiet axis text."""
    ax.set_facecolor(BACKGROUND)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.tick_params(colors=SECONDARY_TEXT_COLOR, labelsize=9, length=0)


def save_figure(fig, output_path):
    fig.savefig(output_path, dpi=150, facecolor=BACKGROUND)
    plt.close(fig)
    return output_path


def square_map_limits(locations):
    """
    Return (x_min, x_max, y_min, y_max) for a square map area that
    contains every location, with some empty space around the edge.
    """
    xs = [x for x, y in locations.values()]
    ys = [y for x, y in locations.values()]

    centre_x = (min(xs) + max(xs)) / 2
    centre_y = (min(ys) + max(ys)) / 2

    # Half of the longer side, plus 15% so labels fit inside.
    half_side = max(max(xs) - min(xs), max(ys) - min(ys), 1) / 2 * 1.15

    return (centre_x - half_side, centre_x + half_side,
            centre_y - half_side, centre_y + half_side)


def draw_route(ax, locations, result):
    """Draw one route on the given axes."""
    complete_route = build_complete_route(result["best_route"])
    color = ALGORITHM_COLORS[result["algorithm"]]

    # Route lines: W -> first customer -> ... -> last customer -> W.
    xs = [locations[location_id][0] for location_id in complete_route]
    ys = [locations[location_id][1] for location_id in complete_route]
    ax.plot(xs, ys, color=color, linewidth=2, solid_joinstyle="round", zorder=1)

    # Customers.
    customer_xs = [locations[customer_id][0] for customer_id in result["best_route"]]
    customer_ys = [locations[customer_id][1] for customer_id in result["best_route"]]
    ax.scatter(customer_xs, customer_ys, s=45, color=TEXT_COLOR,
               edgecolors=BACKGROUND, linewidths=1.5, zorder=2)

    # Warehouse: a larger square.
    warehouse_x, warehouse_y = locations[WAREHOUSE_ID]
    ax.scatter([warehouse_x], [warehouse_y], s=170, marker="s", color=TEXT_COLOR,
               edgecolors=BACKGROUND, linewidths=1.5, zorder=3)

    # Labels next to every location.
    for location_id in complete_route[:-1]:
        x, y = locations[location_id]
        ax.annotate(location_id, (x, y), xytext=(6, 6), textcoords="offset points",
                    fontsize=8, color=TEXT_COLOR, zorder=4)

    style_axes(ax)
    ax.grid(color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    # Same scale on both axes, so distances on the map are not distorted.
    x_min, x_max, y_min, y_max = square_map_limits(locations)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X", color=SECONDARY_TEXT_COLOR, fontsize=9)
    ax.set_title(f"{result['algorithm']}\ndistance {result['best_distance']:.2f}",
                 fontsize=11, color=TEXT_COLOR)


def plot_routes(locations, results, output_path, title=""):
    """
    ROUTE VISUALIZATION: one map per algorithm, showing the warehouse
    (square), the customers (dots), their IDs and the best route found.
    """
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 6.2),
                             squeeze=False, layout="constrained")
    fig.patch.set_facecolor(BACKGROUND)

    for ax, result in zip(axes[0], results):
        draw_route(ax, locations, result)
    axes[0][0].set_ylabel("Y", color=SECONDARY_TEXT_COLOR, fontsize=9)

    if title:
        fig.suptitle(title, fontsize=13, color=TEXT_COLOR)
    return save_figure(fig, output_path)


def plot_convergence(results, output_path, title=""):
    """
    CONVERGENCE PLOT: best route distance (y) after each iteration or
    generation (x), one panel per algorithm.

    The panels share the y-axis so the distances can be compared. They do
    not share the x-axis, because one step means something different for
    each algorithm (see the README).
    """
    fig, axes = plt.subplots(1, len(results), figsize=(5 * len(results), 4.4),
                             squeeze=False, sharey=True, layout="constrained")
    fig.patch.set_facecolor(BACKGROUND)

    for ax, result in zip(axes[0], results):
        steps = [step for step, distance in result["history"]]
        distances = [distance for step, distance in result["history"]]
        color = ALGORITHM_COLORS[result["algorithm"]]

        # The best distance stays the same until a better route is found,
        # so it is drawn as steps.
        ax.plot(steps, distances, color=color, linewidth=2, drawstyle="steps-post")

        # Mark the final value (its number is in the panel title).
        ax.scatter([steps[-1]], [distances[-1]], s=45, color=color,
                   edgecolors=BACKGROUND, linewidths=1.5, zorder=3)

        style_axes(ax)
        ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.margins(x=0.06)
        # Iterations and generations are whole numbers.
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title(f"{result['algorithm']}\nfinal best distance {distances[-1]:.2f}",
                     fontsize=11, color=TEXT_COLOR)

        if result["algorithm"] == "Genetic Algorithm":
            ax.set_xlabel("Generation", color=SECONDARY_TEXT_COLOR, fontsize=9)
        else:
            ax.set_xlabel("Iteration", color=SECONDARY_TEXT_COLOR, fontsize=9)

    axes[0][0].set_ylabel("Best route distance", color=SECONDARY_TEXT_COLOR, fontsize=9)

    if title:
        fig.suptitle(title, fontsize=13, color=TEXT_COLOR)
    return save_figure(fig, output_path)


def plot_comparison(summary_rows, output_path, title=""):
    """
    COMPARISON CHART: average best distance of every algorithm for every
    dataset size. The thin vertical line on each bar shows plus/minus one
    standard deviation over the runs.

    summary_rows - list of dictionaries with the keys
                   customers, algorithm, average_distance, std_dev
    """
    sizes = []
    algorithms = []
    for row in summary_rows:
        if row["customers"] not in sizes:
            sizes.append(row["customers"])
        if row["algorithm"] not in algorithms:
            algorithms.append(row["algorithm"])

    fig, ax = plt.subplots(figsize=(9, 5), layout="constrained")
    fig.patch.set_facecolor(BACKGROUND)

    bar_width = 0.22
    bar_step = 0.25  # a little wider than a bar, so neighbours do not touch

    for algorithm_number, algorithm in enumerate(algorithms):
        positions = []
        averages = []
        deviations = []
        for size_number, size in enumerate(sizes):
            for row in summary_rows:
                if row["customers"] == size and row["algorithm"] == algorithm:
                    offset = (algorithm_number - (len(algorithms) - 1) / 2) * bar_step
                    positions.append(size_number + offset)
                    averages.append(float(row["average_distance"]))
                    deviations.append(float(row["std_dev"]))

        ax.bar(positions, averages, width=bar_width, color=ALGORITHM_COLORS[algorithm],
               label=algorithm, yerr=deviations,
               error_kw={"ecolor": SECONDARY_TEXT_COLOR, "elinewidth": 1, "capsize": 3})

    style_axes(ax)
    ax.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(range(len(sizes)))
    ax.set_xticklabels([f"{size} customers" for size in sizes])
    ax.set_ylabel("Average best distance (lower is better)",
                  color=SECONDARY_TEXT_COLOR, fontsize=9)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=9, labelcolor=TEXT_COLOR, loc="upper left")

    if title:
        ax.set_title(title, fontsize=12, color=TEXT_COLOR)
    return save_figure(fig, output_path)
