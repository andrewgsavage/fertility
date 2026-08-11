import io
import pathlib
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter, MultipleLocator, PercentFormatter
from PIL import Image

from country_names import COUNTRY_REGIONS, country_title

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from cond_asfr_uk_ons import load_period_rates  # noqa: E402

SHARED_YLIM = (0, 0.25)
Y_TICKS = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25]

ROWS = [
    (1, "m1x", "First birth", SHARED_YLIM),
    (2, "m2x", "Second birth", SHARED_YLIM),
]


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

    # HFD has no conditional-ASFR tables for the UK — reconstruct it from
    # ONS cohort data and inject as one more "code" so it behaves exactly
    # like an HFD country everywhere else in this script (country_title,
    # per-column plotting, canvas sizing).
    by_period = load_period_rates()
    uk_rows = [
        {"code": "UK_ONS", "year": year, "age": age, "m1x": c1, "m2x": c2}
        for year, ages in by_period.items()
        for age, (c1, c2) in ages.items()
    ]
    df = pd.concat([df, pd.DataFrame(uk_rows)], ignore_index=True)
    return df


def slug(name):
    return (
        name.lower()
        .replace(" & ", "_")
        .replace(" / ", "_")
        .replace(" ", "_")
    )


def make_region_grid(df, countries):
    """Render one region's grid, sized to its own country count (no wasted
    padding columns), cropped tight. Returns a PIL image; final canvas-size
    equalization across regions happens in the caller."""
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    ncols = len(countries)
    fig, axes = plt.subplots(
        2, ncols, figsize=(3 * ncols, 2.7 * 2), sharex=True, sharey=True,
        gridspec_kw={"wspace": 0, "hspace": 0},
        squeeze=False,
    )

    for col, country in enumerate(countries):
        subset = df[df["code"] == country]
        for row, column, label, ylim in ROWS:
            ax = axes[row - 1, col]
            for year, year_rows in subset.groupby("year"):
                year_rows = year_rows.sort_values("age")
                ax.plot(year_rows["age"], year_rows[column], color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
            ax.set_xlim(15, 45)
            ax.set_ylim(*ylim)
            ax.yaxis.set_major_locator(FixedLocator(Y_TICKS))
            ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
            ax.grid(True, linewidth=0.4)
            if row == 1:
                ax.set_title(
                    country_title(country, subset["year"].min(), subset["year"].max()),
                    fontsize=9,
                )
            if col == 0:
                ax.set_ylabel(f"{label}\nConditional ASFR")

    # Rows share a y-axis group (sharey=True), so with hspace=0 the first
    # row's y=0 tick label would sit right on top of the second row's y=0.25
    # label at the shared boundary. Hide just that one label (keep the
    # gridline) rather than the tick's position, since the Locator itself
    # is shared across every axes in the group.
    for value, tick_label in zip(axes[0, 0].get_yticks(), axes[0, 0].get_yticklabels()):
        if value <= SHARED_YLIM[0]:
            tick_label.set_visible(False)

    fig.supxlabel("Age")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist(), label="Year", shrink=0.6)
    cbar.ax.yaxis.set_major_locator(MultipleLocator(5))
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


if __name__ == "__main__":
    df = load_data()

    images = {region: make_region_grid(df, countries) for region, countries in COUNTRY_REGIONS.items()}

    # Regions have different country counts, so their tightly-cropped images
    # are different sizes. Pad each onto a common white canvas (the largest
    # image's size) so every saved PNG has identical dimensions, instead of
    # reserving blank matplotlib subplot columns to achieve that.
    canvas_width = max(im.width for im in images.values())
    canvas_height = max(im.height for im in images.values())

    for region, im in images.items():
        canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
        canvas.paste(im, (0, 0))
        path = f"outputs/cond_asfr_region_{slug(region)}.png"
        canvas.save(path)
        print(f"Saved {path}")
