"""Reproduce the completed-fertility-by-age-at-first-birth curves for
Swedish women born 1935-39 and 1950-54, from Andersson (2008: 49, Table
12d), as reprinted in Schmidt, Sobotka, Bentzen & Nyboe Andersen (2012,
Hum Reprod Update 18(1):29-43, Fig. 4) -- digitized by eye from that
figure.

No HFD overlay here: HFD's own Swedish parity-progression data (cft.txt)
only starts at the 1955 birth cohort, so there's no cohort in common with
this figure's much older 1935-39/1950-54 cohorts to compare against. Kept
as a standalone historical data point instead -- the same measure as the
rest of this page's "Comparison to published research" section, just
predating HFD's own coverage.
"""

import matplotlib.pyplot as plt

# Digitized by eye, one point per age year, from Fig. 4 of Schmidt et al.
# 2012 (originally Andersson 2008, Table 12d).
AGES = list(range(15, 45))
COHORT_1935_39 = [
    3.65, 3.22, 3.08, 2.92, 2.76, 2.62, 2.55, 2.44, 2.38, 2.32,
    2.20, 2.15, 2.06, 2.00, 1.92, 1.86, 1.78, 1.70, 1.62, 1.58,
    1.49, 1.46, 1.33, 1.28, 1.22, 1.16, 1.13, 1.11, 1.08, 1.00,
]
COHORT_1950_54 = [
    2.80, 2.78, 2.67, 2.64, 2.58, 2.47, 2.45, 2.39, 2.36, 2.33,
    2.30, 2.26, 2.20, 2.17, 2.12, 2.06, 2.02, 1.95, 1.89, 1.80,
    1.75, 1.60, 1.56, 1.47, 1.35, 1.28, 1.20, 1.15, 1.12, 1.02,
]


def plot():
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(AGES, COHORT_1935_39, color="navy", linewidth=1.5, marker="D", markersize=3, label="Cohorts 1935-39")
    ax.plot(AGES, COHORT_1950_54, color="black", linewidth=1.5, marker="s", markersize=3, label="Cohorts 1950-54")

    ax.set_xlim(15, 44)
    ax.set_ylim(1.0, 4.0)
    ax.grid(True, linewidth=0.4)
    ax.set_xlabel("Age at first birth")
    ax.set_ylabel("Completed fertility rate")
    ax.set_title("Sweden: Andersson (2008) via Schmidt et al. 2012")
    ax.legend(fontsize=9)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    fig = plot()
    path = "outputs/andersson_sweden_paper_comparison.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
