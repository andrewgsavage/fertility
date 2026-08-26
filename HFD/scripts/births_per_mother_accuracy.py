"""How well does births_per_mother_region_grid.py's backward-recursion
estimate match reality?

cft.txt (used by that page) only has HFD's *estimated* parity-progression
hazards -- there's no census/register-measured cohort equivalent to check
it against. But HFD's *period* fertility tables come in both flavours:
pft.txt (same estimation method as cft.txt) and pftc.txt (measured
directly from register/census parity data, i.e. the processed output of
XXXparity.txt). Both have the same q2x-q5px hazard columns cft.txt does,
so the exact same recursion can run on either -- just per calendar year
instead of per birth cohort -- giving an apples-to-apples check of the
estimation method wherever register data exists.

Restricted to the handful of countries with continuous multi-decade
register coverage in pftc.txt (Denmark, Finland, Hungary, Norway, Sweden;
>=30 years each) -- everywhere else pftc.txt only has isolated census
years, too sparse for a year-by-year comparison.

See births_per_mother_period_grid.py for the same period-basis recursion
applied (estimated only, no register comparison) to every country.
"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator

from births_per_mother_region_grid import _expected_children_curve as expected_children_curve
from country_names import country_title

REGISTER_COUNTRIES = ["DNK", "FIN", "HUN", "NOR", "SWE"]
X_LIM = (18, 45)

COLS = ["code", "year", "x", "w0x", "m1x", "q1x", "l0x", "b1x", "L0x", "Sb1x",
        "w1x", "m2x", "q2x", "l1x", "b2x", "L1x", "Sb2x",
        "w2x", "m3x", "q3x", "l2x", "b3x", "L2x", "Sb3x",
        "w3x", "m4x", "q4x", "l3x", "b4x", "L3x", "Sb4x",
        "w4x", "m5px", "q5px", "l4x", "b5px", "L4x", "Sb5px"]


def load_period_table(path):
    df = pd.read_csv(path, sep=r"\s+", skiprows=3, names=COLS, na_values=".")
    df = df[pd.to_numeric(df["x"], errors="coerce").notna()].copy()
    df["x"] = df["x"].astype(int)
    return df


def curves_by_year(df, code):
    """{year: {age: expected_children}} for one country, every year present."""
    subset = df[df["code"] == code]
    return {year: expected_children_curve(rows) for year, rows in subset.groupby("year")}


def error_summary(estimated, actual):
    """One row per (year, age) cell present in both curves, for ages in
    X_LIM -- the same cells the sample-year plot below draws from."""
    rows = []
    for year, est_curve in estimated.items():
        act_curve = actual.get(year, {})
        for age in range(*X_LIM):
            if age in est_curve and age in act_curve:
                rows.append({"year": year, "age": age,
                             "diff": est_curve[age] - act_curve[age]})
    return pd.DataFrame(rows)


def make_plot(estimated_by_country, actual_by_country):
    fig, axes = plt.subplots(
        1, len(REGISTER_COUNTRIES), figsize=(3.2 * len(REGISTER_COUNTRIES), 3.4),
        sharex=True, sharey=True,
    )
    all_years = sorted(set().union(*(estimated_by_country[c].keys() for c in REGISTER_COUNTRIES)))
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(min(all_years), max(all_years))

    for ax, code in zip(axes, REGISTER_COUNTRIES):
        estimated = estimated_by_country[code]
        actual = actual_by_country[code]
        sample_years = sorted(set(estimated) & set(actual))[::10]  # every ~10th year, evenly spread
        for year in sample_years:
            ages = [a for a in range(*X_LIM) if a in estimated[year] and a in actual[year]]
            color = cmap(norm(year))
            ax.plot(ages, [estimated[year][a] for a in ages], color=color, linestyle="--", linewidth=1)
            ax.plot(ages, [actual[year][a] for a in ages], color=color, linestyle="-", linewidth=1)
        ax.set_xlim(*X_LIM)
        ax.set_xticks(list(range(20, X_LIM[1], 10)) + [X_LIM[1]])
        ax.grid(True, linewidth=0.4)
        ax.set_title(country_title(code), fontsize=9)
        ax.set_xlabel("Age at first birth")
    axes[0].set_ylabel("Expected total children")
    axes[0].plot([], [], color="grey", linestyle="--", label="Estimated (pft.txt)")
    axes[0].plot([], [], color="grey", linestyle="-", label="Register-based (pftc.txt)")
    axes[0].legend(fontsize=7, loc="lower left")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)
    cbar.ax.yaxis.set_major_locator(MultipleLocator(10))
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))
    return fig


if __name__ == "__main__":
    pft = load_period_table("data/HFD/pft.txt")
    pftc = load_period_table("data/HFD/pftc.txt")

    estimated_by_country = {code: curves_by_year(pft, code) for code in REGISTER_COUNTRIES}
    actual_by_country = {code: curves_by_year(pftc, code) for code in REGISTER_COUNTRIES}

    all_errors = pd.concat([
        error_summary(estimated_by_country[code], actual_by_country[code]).assign(code=code)
        for code in REGISTER_COUNTRIES
    ])
    print(all_errors.groupby("code")["diff"].agg(
        mean="mean", mae=lambda s: s.abs().mean(), max_abs=lambda s: s.abs().max(),
    ))
    print("Overall MAE:", all_errors["diff"].abs().mean())

    fig = make_plot(estimated_by_country, actual_by_country)
    path = "outputs/births_per_mother_accuracy.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"Saved {path}")
