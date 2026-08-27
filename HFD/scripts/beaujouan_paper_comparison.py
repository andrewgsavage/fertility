"""Overlay HFD-derived expected-children-by-age-of-first-birth curves
(same cft.txt recursion as births_per_mother_region_grid.py, one line per
birth cohort) against Beaujouan, Zeman & Nathan (2023, Demographic
Research) -- "mothers' completed fertility conditional on age at first
birth" (their CFMx), for the seven of their ten countries HFD has cohort
parity-progression data for (France, Italy and Switzerland aren't in
HFD's cft.txt at all).

Unlike the Roustaei et al. Finland comparison, these values are exact,
not digitized by eye: the paper supplies an Excel supplement (one sheet
per country) with the CFMx figures underlying its own Figure 3, grouped
into 1940-49/1950-59/1960-69 birth-cohort decades and 5-year age-at-
first-birth bins (15-19 .. 35-39; 40-44 dropped here as the paper's own
Figure 3 does, since CFMx there is mostly at its definitional floor of 1
child and adds noise rather than signal). Age bins are plotted at their
midpoint (17, 22, 27, 32, 37).
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

from births_per_mother_region_grid import X_LIM, Y_LIM, load_data
from country_names import COUNTRY_NAMES

# GBR isn't an HFD code (paper's own label, compared against UK_ONS below).
COUNTRY_TITLES = {**COUNTRY_NAMES, "GBR": "Great Britain"}

# Paper's own age bins, plotted at their midpoint.
BIN_MIDPOINTS = [17, 22, 27, 32, 37]

# Extracted from the paper's supplementary Excel file (48-15_supplement.xlsx,
# one sheet per country, "CFMx" block), not digitized from the figure.
PAPER_CFMX = {
    "AUT": {
        "1940-49": [2.551, 2.294, 2.016, 1.608, 1.422],
        "1950-59": [2.443, 2.254, 1.984, 1.649, 1.424],
        "1960-69": [2.488, 2.198, 1.953, 1.780, 1.402],
    },
    "NLD": {
        "1940-49": [3.018, 2.389, 2.103, 1.828, 1.155],
        "1950-59": [2.588, 2.368, 2.332, 2.092, 1.731],
        "1960-69": [2.728, 2.544, 2.295, 2.106, 1.628],
    },
    "NOR": {
        "1940-49": [2.834, 2.619, 2.250, 1.839, 1.442],
        "1950-59": [2.534, 2.428, 2.257, 1.902, 1.622],
        "1960-69": [2.788, 2.576, 2.324, 1.948, 1.542],
    },
    "POL": {
        "1940-49": [3.018, 2.538, 2.163, 1.651, 1.174],
        "1950-59": [2.923, 2.495, 2.035, 1.645, 1.488],
        "1960-69": [2.822, 2.534, 2.043, 1.743, 1.286],
    },
    "SWE": {
        "1940-49": [2.591, 2.366, 2.105, 1.655, 1.593],
        "1950-59": [2.656, 2.407, 2.250, 1.978, 1.625],
        "1960-69": [3.140, 2.594, 2.251, 2.082, 1.793],
    },
    "USA": {
        "1940-49": [3.290, 2.704, 2.201, 1.872, 1.619],
        "1950-59": [2.795, 2.482, 2.177, 1.872, 1.510],
        "1960-69": [3.094, 2.632, 2.312, 1.994, 1.687],
    },
    "GBR": {
        "1940-49": [3.230, 2.560, 2.170, 1.830, 1.440],
        "1950-59": [2.950, 2.530, 2.200, 1.910, 1.500],
        "1960-69": [3.130, 2.570, 2.220, 1.920, 1.520],
    },
}

# Which HFD code each paper country is compared against.
HFD_CODE = {
    "AUT": "AUT",
    "NLD": "NLD",
    "NOR": "NOR",
    "POL": "POL",
    "SWE": "SWE",
    "USA": "USA",
    "GBR": "UK_ONS",
}

DECADE_STYLES = {
    "1940-49": {"linestyle": "-", "color": "black"},
    "1950-59": {"linestyle": "--", "color": "dimgray"},
    "1960-69": {"linestyle": ":", "color": "firebrick"},
}


def plot(df):
    countries = list(PAPER_CFMX.keys())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["cohort"].min(), df["cohort"].max())

    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharex=True, sharey=True)
    axes = axes.ravel()

    for ax, country in zip(axes, countries):
        subset = df[df["code"] == HFD_CODE[country]]
        for cohort, rows in subset.groupby("cohort"):
            rows = rows.sort_values("age")
            ax.plot(rows["age"], rows["expected_children"], color=cmap(norm(cohort)), alpha=0.4, linewidth=0.8)

        for decade, values in PAPER_CFMX[country].items():
            ax.plot(BIN_MIDPOINTS, values, linewidth=2, label=decade, **DECADE_STYLES[decade])

        ax.set_xlim(*X_LIM)
        ax.set_xticks(list(range(20, X_LIM[1], 10)) + [X_LIM[1]])
        ax.set_ylim(*Y_LIM)
        ax.grid(True, linewidth=0.4)
        ax.set_title(COUNTRY_TITLES.get(country, country), fontsize=10)

    for ax in axes[len(countries):]:
        ax.axis("off")

    axes[0].legend(fontsize=8, loc="upper right", title="Beaujouan et al.\nbirth cohort")
    fig.supxlabel("Age at first birth")
    fig.supylabel("Expected / completed children")
    fig.suptitle("HFD birth cohorts vs Beaujouan, Zeman & Nathan 2023 (1940-49 / 1950-59 / 1960-69 cohorts)")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=axes.tolist(), label="HFD birth cohort", shrink=0.7)
    cbar.ax.yaxis.set_major_locator(MultipleLocator(10))
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))

    return fig


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)
    path = "outputs/beaujouan_paper_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
