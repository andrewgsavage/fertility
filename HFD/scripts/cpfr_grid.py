import math

import matplotlib.pyplot as plt
import pandas as pd

from country_names import asfr1_value, country_title, cpfr1_value, order_by_asfr1_20

ORDER_LABELS = {1: "first", 2: "second"}
BASE_COHORTS = range(1982, 1988)


def load_data(order):
    column = f"cpfr{order}"
    df = pd.read_csv(
        "data/HFD/cpfrVVbo.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "cohort", "cpfr", "cpfr1", "cpfr2", "cpfr3", "cpfr4", "cpfr5p"],
        na_values=".",
    )
    df["age"] = df["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
    df = df[df["code"] != "UKR"]
    df = df.rename(columns={"cohort": "birth_year", column: "value"})[["code", "birth_year", "age", "value"]]
    return df


def new_grid(countries):
    n = len(countries)
    ncols = 6
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(3 * ncols, 2.7 * nrows), sharex=True, sharey=True,
        gridspec_kw={"wspace": 0.35, "hspace": 0.45},
    )
    return fig, axes.flatten(), n


def save(fig, path):
    plt.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def make_grid(order):
    label = ORDER_LABELS[order]
    df = load_data(order)
    df = df[df["birth_year"] >= 1970]
    countries = order_by_asfr1_20(df["code"].unique())

    cmap = plt.colormaps["viridis"]
    norm = plt.Normalize(df["birth_year"].min(), df["birth_year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        for cohort, row in subset.groupby("birth_year"):
            row = row.sort_values("age")
            ax.plot(row["age"], row["value"], color=cmap(norm(cohort)), alpha=0.5, linewidth=0.8)
        ax.set_title(
            country_title(
                country, subset["birth_year"].min(), subset["birth_year"].max(),
                cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
            ),
            fontsize=9,
        )
        ax.set_xlim(15, 45)
        ax.set_ylim(0, 1)
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Cumulative {label}-birth rate")
    fig.suptitle(f"Cumulative {label}-birth rate by age, per birth cohort, by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Birth year", shrink=0.6)

    save(fig, f"outputs/cpfr{order}_cohort_grid.png")


def make_deviation_grid(order):
    label = ORDER_LABELS[order]
    df = load_data(order)
    countries = order_by_asfr1_20(df["code"].unique())

    display = df[df["birth_year"] >= 1970]
    cmap = plt.colormaps["viridis"]
    norm = plt.Normalize(display["birth_year"].min(), display["birth_year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        country_all = df[df["code"] == country]
        baseline = country_all[country_all["birth_year"].isin(BASE_COHORTS)].groupby("age")["value"].mean()
        subset = display[display["code"] == country]
        title = country_title(
            country, subset["birth_year"].min(), subset["birth_year"].max(),
            cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
        )
        if baseline.empty:
            ax.set_title(f"{title}\n(no base cohort)", fontsize=9)
            ax.set_xlim(15, 45)
            ax.grid(True, linewidth=0.4)
            continue
        for cohort, row in subset.groupby("birth_year"):
            row = row.sort_values("age").set_index("age")["value"]
            deviation = row - baseline
            ax.plot(deviation.index, deviation.values, color=cmap(norm(cohort)), alpha=0.5, linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(15, 45)
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Deviation from 1982-1987 average cumulative {label}-birth rate")
    fig.suptitle(f"Cumulative {label}-birth rate, deviation from 1982-1987 cohort average, by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Birth year", shrink=0.6)

    save(fig, f"outputs/cpfr{order}_cohort_deviation_grid.png")


if __name__ == "__main__":
    for order in (1, 2):
        make_grid(order)
        make_deviation_grid(order)
