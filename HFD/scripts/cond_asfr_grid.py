import math

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, NullLocator, PercentFormatter

from country_names import asfr1_value, country_title, cpfr1_value, order_by_asfr1_20

ORDER_CONFIG = {
    1: {"label": "first", "ylim": (0, 0.18)},
    2: {"label": "second", "ylim": (0, 0.25)},
}
DEVIATION_BASE_YEARS = range(2023, 2027)
DEVIATION_BASE_LABEL = f"{DEVIATION_BASE_YEARS[0]}-{DEVIATION_BASE_YEARS[-1]} average"
RELATIVE_BASE_YEARS = range(2014, 2017)
RELATIVE_BASE_LABEL = f"{RELATIVE_BASE_YEARS[0]}-{RELATIVE_BASE_YEARS[-1]} average"
GLOBAL_BASE_LABEL = "all-country, all-year average"


def load_data():
    df = pd.read_csv(
        "data/HFD/mi.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"],
        na_values=".",
    )
    df["age"] = df["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
    df = df[df["year"] >= 2005]
    df = df[df["code"] != "UKR"]
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


def make_grid(df, order):
    column = f"m{order}x"
    config = ORDER_CONFIG[order]
    countries = order_by_asfr1_20(df["code"].unique())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        for year, row in subset.groupby("year"):
            row = row.sort_values("age")
            ax.plot(row["age"], row[column], color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.set_title(
            country_title(
                country, subset["year"].min(), subset["year"].max(),
                cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
            ),
            fontsize=9,
        )
        ax.set_xlim(15, 45)
        ax.set_ylim(*config["ylim"])
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Conditional ASFR ({config['label']} birth)")
    fig.suptitle(f"Conditional age-specific fertility rates for {config['label']} births, by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)

    save(fig, f"outputs/cond_asfr{order}_grid.png")


def make_deviation_grid(df, order):
    column = f"m{order}x"
    label = ORDER_CONFIG[order]["label"]
    countries = order_by_asfr1_20(df["code"].unique())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        title = country_title(
            country, subset["year"].min(), subset["year"].max(),
            cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
        )
        baseline = subset[subset["year"].isin(DEVIATION_BASE_YEARS)].groupby("age")[column].mean()
        if baseline.empty:
            ax.set_title(f"{title}\n(no {DEVIATION_BASE_LABEL})", fontsize=9)
            ax.set_xlim(15, 45)
            ax.grid(True, linewidth=0.4)
            continue
        for year, row in subset.groupby("year"):
            row = row.sort_values("age").set_index("age")[column]
            deviation = row - baseline
            ax.plot(deviation.index, deviation.values, color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(15, 45)
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Deviation from {DEVIATION_BASE_LABEL} conditional ASFR ({label} birth)")
    fig.suptitle(f"Conditional ASFR for {label} births, deviation from {DEVIATION_BASE_LABEL}, by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)

    save(fig, f"outputs/cond_asfr{order}_deviation_grid.png")


def make_relative_deviation_grid(df, order):
    column = f"m{order}x"
    label = ORDER_CONFIG[order]["label"]
    countries = order_by_asfr1_20(df["code"].unique())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        title = country_title(
            country, subset["year"].min(), subset["year"].max(),
            cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
        )
        baseline = subset[subset["year"].isin(RELATIVE_BASE_YEARS)].groupby("age")[column].mean()
        if baseline.empty:
            ax.set_title(f"{title}\n(no {RELATIVE_BASE_LABEL})", fontsize=9)
            ax.set_xlim(15, 45)
            ax.grid(True, linewidth=0.4)
            continue
        for year, row in subset.groupby("year"):
            row = row.sort_values("age").set_index("age")[column]
            relative_deviation = (row - baseline) / baseline
            ax.plot(relative_deviation.index, relative_deviation.values, color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(15, 45)
        ax.set_ylim(-1, 2)
        ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Deviation from {RELATIVE_BASE_LABEL} conditional ASFR ({label} birth), as proportion of base")
    fig.suptitle(f"Conditional ASFR for {label} births, relative deviation from {RELATIVE_BASE_LABEL}, by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)

    save(fig, f"outputs/cond_asfr{order}_relative_deviation_grid.png")


def make_relative_deviation_log_grid(df, order):
    column = f"m{order}x"
    label = ORDER_CONFIG[order]["label"]
    countries = order_by_asfr1_20(df["code"].unique())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        title = country_title(
            country, subset["year"].min(), subset["year"].max(),
            cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
        )
        baseline = subset[subset["year"].isin(RELATIVE_BASE_YEARS)].groupby("age")[column].mean()
        if baseline.empty:
            ax.set_title(f"{title}\n(no {RELATIVE_BASE_LABEL})", fontsize=9)
            ax.set_xlim(15, 45)
            ax.grid(True, linewidth=0.4)
            continue
        for year, row in subset.groupby("year"):
            row = row.sort_values("age").set_index("age")[column]
            ratio = row / baseline
            ax.plot(ratio.index, ratio.values, color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.axhline(1, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(15, 45)
        ax.set_yscale("log")
        ax.set_ylim(0.5, 2.0)
        ax.set_yticks([0.5, 0.75, 1.0, 1.5, 2.0])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x * 100:.0f}%"))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Conditional ASFR ({label} birth) as % of {RELATIVE_BASE_LABEL}, log scale")
    fig.suptitle(f"Conditional ASFR for {label} births, as % of {RELATIVE_BASE_LABEL} (log scale), by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)

    save(fig, f"outputs/cond_asfr{order}_relative_deviation_log_grid.png")


def make_relative_deviation_log_global_grid(df, order):
    column = f"m{order}x"
    label = ORDER_CONFIG[order]["label"]
    countries = order_by_asfr1_20(df["code"].unique())
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    baseline = df.groupby("age")[column].mean()

    fig, axes, n = new_grid(countries)
    for ax, country in zip(axes, countries):
        subset = df[df["code"] == country]
        title = country_title(
            country, subset["year"].min(), subset["year"].max(),
            cpfr1=cpfr1_value(country), asfr1_20=asfr1_value(country),
        )
        for year, row in subset.groupby("year"):
            row = row.sort_values("age").set_index("age")[column]
            ratio = row / baseline.reindex(row.index)
            ax.plot(ratio.index, ratio.values, color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.axhline(1, color="black", linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=9)
        ax.set_xlim(15, 45)
        ax.set_yscale("log")
        ax.set_ylim(0.125, 4.0)
        ax.set_yticks([0.125, 0.25, 0.5, 1.0, 2.0, 4.0])
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x * 100:.0f}%"))
        ax.yaxis.set_minor_locator(NullLocator())
        ax.grid(True, linewidth=0.4)

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.supxlabel("Age")
    fig.supylabel(f"Conditional ASFR ({label} birth) as % of {GLOBAL_BASE_LABEL}, log scale")
    fig.suptitle(f"Conditional ASFR for {label} births, as % of {GLOBAL_BASE_LABEL} (log scale), by country")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=axes.tolist(), label="Year", shrink=0.6)

    save(fig, f"outputs/cond_asfr{order}_relative_deviation_log_global_grid.png")


if __name__ == "__main__":
    df = load_data()
    for order in (1, 2):
        make_grid(df, order)
        make_deviation_grid(df, order)
        make_relative_deviation_grid(df, order)
        make_relative_deviation_log_grid(df, order)
        make_relative_deviation_log_global_grid(df, order)
