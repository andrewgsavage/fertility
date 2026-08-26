"""Overlay HFD-derived expected-children-by-age-of-first-birth curves for
Finland (same cft.txt recursion as births_per_mother_region_grid.py, one
line per birth cohort) against Roustaei et al. (2019, BMJ Open)
-- "completed fertility rate by age at first birth" for Finnish women
whose first birth occurred in one of four 5-year periods from 1987-2006,
digitized by eye from the paper's online supplementary figure (panel B of
https://pmc.ncbi.nlm.nih.gov/articles/instance/6340426/bin/bmjopen-2018-026336supp001.pdf),
which extends the main text's Figure 2B (1987-91 and 1992-96 only) with
two further periods. The supplementary PDF has no caption identifying
what its three panels (A/B/C) each represent; panel B was picked because
its 1.0-3.5 children-per-woman scale and 1987-91/1992-96 curves match
Figure 2B exactly, so it's presumed to be the same measure extended to
later periods rather than a different subgroup.

These are two different kinds of measurement, not two samples of the same
thing. HFD's curve is a modeled expected value: it chains each cohort's
own age-specific parity-progression hazards together, assuming a woman's
chance of a 2nd, 3rd, etc. birth can be treated as an independent
probability at each age. The paper's curve, from Finland's individually-
linked Medical Birth Register, is presumably a direct empirical average --
the actual completed number of children real women had, tracked via
personal identifiers, with no chaining of rates required. The two also
group cohorts differently (mother's birth year vs her first-birth
calendar year). That a rate-chained model and a direct headcount land on
the same curve shape is itself a check on the independence assumption the
recursion relies on -- not a claim that the two datasets are identical.
"""

import matplotlib.pyplot as plt

from births_per_mother_region_grid import X_LIM, Y_LIM, load_data

# Digitized at gridline resolution (every 2 years / 0.5 children) from
# panel B of the supplementary PDF, which plots four curves: 1987-91,
# 1992-96, 1997-01, 2002-06. The first two match Figure 2B in the main
# text; the latter two are new here.
PAPER_AGES = [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45]
PAPER_CURVES = {
    "Roustaei et al. 1987-91": [3.15, 3.15, 3.20, 2.80, 2.65, 2.40, 2.20, 2.00,
                                 1.90, 1.75, 1.60, 1.45, 1.30, 1.20, 1.05, 1.00],
    "Roustaei et al. 1992-96": [3.30, 3.35, 3.35, 2.85, 2.70, 2.45, 2.25, 2.05,
                                 1.95, 1.80, 1.65, 1.50, 1.35, 1.25, 1.10, 1.25],
    "Roustaei et al. 1997-01": [3.30, 3.40, 3.45, 2.90, 2.72, 2.47, 2.27, 2.07,
                                 1.97, 1.82, 1.67, 1.52, 1.37, 1.27, 1.12, 1.20],
    "Roustaei et al. 2002-06": [3.30, 3.40, 3.45, 2.90, 2.72, 2.47, 2.27, 2.07,
                                 1.97, 1.82, 1.67, 1.52, 1.37, 1.27, 1.12, 1.35],
}
PAPER_COLORS = {
    "Roustaei et al. 1987-91": "black",
    "Roustaei et al. 1992-96": "dimgray",
    "Roustaei et al. 1997-01": "darkred",
    "Roustaei et al. 2002-06": "firebrick",
}


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
    ax.set_title(f"Finland ({int(subset['cohort'].min())}–{int(subset['cohort'].max())} birth cohorts)\nvs Roustaei et al. 2019 (women whose first birth was 1987-2006)")

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
