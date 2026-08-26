"""Overlay HFD-derived expected-children-by-age-of-first-birth curves for
Finland (same cft.txt recursion as births_per_mother_region_grid.py, one
line per birth cohort) against Figure 2B of Roustaei et al. (2019, BMJ
Open) -- "completed fertility rate by age at first birth" for Finnish
women whose first birth occurred in 1987-91 or 1992-96, digitized by eye
from the published figure (https://bmjopen.bmj.com/content/9/1/e026336,
Finnish Medical Birth Register data). Two independent methods (HFD's
own parity-progression tables vs the paper's direct register tabulation)
and two different cohort definitions (mother's birth year vs her first-
birth calendar year) landing on the same curve shape is the comparison
being made here -- not a claim that the two datasets are identical.
"""

import matplotlib.pyplot as plt

from births_per_mother_region_grid import X_LIM, Y_LIM, load_data

# Digitized from Figure 2B (zoomed screenshot, gridlines at every 2 years /
# 0.5 children), reading the age-15-45 x-axis at each labelled tick.
PAPER_AGES = [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45]
PAPER_CURVES = {
    "Roustaei et al. 1987-91": [3.15, 3.15, 3.20, 2.80, 2.65, 2.40, 2.20, 2.00,
                                 1.90, 1.75, 1.60, 1.45, 1.30, 1.20, 1.05, 1.00],
    "Roustaei et al. 1992-96": [3.30, 3.35, 3.35, 2.85, 2.70, 2.45, 2.25, 2.05,
                                 1.95, 1.80, 1.65, 1.50, 1.35, 1.25, 1.10, 1.25],
}
PAPER_COLORS = {"Roustaei et al. 1987-91": "black", "Roustaei et al. 1992-96": "dimgray"}


def plot(df):
    subset = df[df["code"] == "FIN"]
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(subset["cohort"].min(), subset["cohort"].max())

    fig, ax = plt.subplots(figsize=(6, 5))
    for cohort, rows in subset.groupby("cohort"):
        rows = rows.sort_values("age")
        ax.plot(rows["age"], rows["expected_children"], color=cmap(norm(cohort)), alpha=0.5, linewidth=0.8)

    for label, values in PAPER_CURVES.items():
        ax.plot(PAPER_AGES, values, color=PAPER_COLORS[label], linewidth=2, linestyle="--", label=label)

    ax.set_xlim(*X_LIM)
    ax.set_ylim(*Y_LIM)
    ax.set_xticks(list(range(20, X_LIM[1], 10)) + [X_LIM[1]])
    ax.grid(True, linewidth=0.4)
    ax.set_xlabel("Age at first birth")
    ax.set_ylabel("Expected / completed children")
    ax.set_title(f"Finland ({int(subset['cohort'].min())}–{int(subset['cohort'].max())} birth cohorts)\nvs Roustaei et al. 2019 (women whose first birth was 1987-96)")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=ax, label="HFD birth cohort", shrink=0.8)
    ax.legend(fontsize=8, loc="upper right")

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)
    path = "outputs/finland_paper_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
