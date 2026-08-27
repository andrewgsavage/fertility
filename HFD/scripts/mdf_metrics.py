"""Microdemographic Framework (Shaw 2025) metrics for docs/hfd/mdf.md: TMR,
CPM and TFR for every country in HFD's tfrRRbo.txt, rendered as matplotlib
small multiples -- one region grid per tab, one panel per country, with all
three metrics overlaid on a dual y-axis (TMR left, CPM/TFR right) -- the
same pairing as the paper's own Fig. 1, extended with TFR on the right
axis. TCR is skipped (it's just 1 - TMR, so redundant alongside TMR here).

TFR = TMR x CPM. TMR (Total Maternal Rate) is HFD's TFR1 (period first-birth
TFR) -- the share of women who become mothers under current age-specific
rates. CPM (Children per Mother) is TFR / TFR1 -- average family size among
those who become mothers.
"""

import datetime
import io
import pathlib
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from PIL import Image

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from country_names import COUNTRY_REGIONS, country_title  # noqa: E402
from mdf_uk_ons import load_period_metrics as load_uk_ons_metrics  # noqa: E402

INPUT = _SCRIPT_DIR.parent / "data" / "HFD" / "tfrRRbo.txt"
XLIM = (1950, datetime.date.today().year)

# Same regions/countries as docs/hfd/first-vs-second-birth.md
# (country_names.COUNTRY_REGIONS) -- its UK_ONS placeholder (an ONS
# reconstruction, since that page's conditional-ASFR source (mi.txt) has no
# UK data) sits alongside GBR_NP here rather than replacing it, since
# tfrRRbo.txt *does* have real UK data -- just only from 2013, so UK_ONS
# still adds real value by reaching back to 1965 (see mdf_uk_ons.py).
MDF_REGIONS = {
    region: [c for code in codes for c in (["GBR_NP", "UK_ONS"] if code == "UK_ONS" else [code])]
    for region, codes in COUNTRY_REGIONS.items()
}

TMR_COLOR = "#2a78d6"
CPM_COLOR = "#2a9d5c"
TFR_COLOR = "#8a8a8a"
TMR_YLIM = (0, 120)
COUNT_YLIM = (0, 6)
PERCENT_FORMATTER = FuncFormatter(lambda value, _: f"{value:.0f}%")
LEGEND_HANDLES = [
    Line2D([], [], color=TMR_COLOR, linewidth=1.5, label="TMR"),
    Line2D([], [], color=CPM_COLOR, linewidth=1.5, label="CPM"),
    Line2D([], [], color=TFR_COLOR, linewidth=1.5, linestyle="--", label="TFR"),
]


def load_data():
    df = pd.read_csv(
        INPUT,
        sep=r"\s+",
        engine="python",
        skiprows=3,
        names=[
            "code", "year", "TFR", "TFR1", "TFR2", "TFR3", "TFR4", "TFR5p",
            "TFR40", "TFR40_1", "TFR40_2", "TFR40_3", "TFR40_4", "TFR40_5p",
        ],
        na_values=".",
    )
    df = df.dropna(subset=["TFR", "TFR1"])
    df["TMR"] = df["TFR1"]
    df["CPM"] = df["TFR"] / df["TFR1"]
    df = df[["code", "year", "TFR", "TMR", "CPM"]]

    uk_ons = load_uk_ons_metrics()
    uk_ons_df = pd.DataFrame(
        [{"code": "UK_ONS", "year": year, "TMR": tmr, "CPM": cpm, "TFR": tfr} for year, (tmr, cpm, tfr) in uk_ons.items()],
    )

    return pd.concat([df, uk_ons_df], ignore_index=True).sort_values(["code", "year"])


def make_region_grid(df, countries):
    """Render one region's grid, sized to its own country count, all
    columns sharing one fixed XLIM so countries are directly comparable by
    calendar year (data before/after a country's own coverage just leaves
    that stretch of its panel blank). wspace=0 butts columns together with
    no gap, matching cond_asfr_region_grid.py's convention. Returns a PIL
    image; final canvas-size equalization across regions happens in the
    caller."""
    ncols = len(countries)
    fig, axes = plt.subplots(
        1, ncols, figsize=(2.6 * ncols, 3.4), sharey=True,
        gridspec_kw={"wspace": 0}, squeeze=False,
    )
    axes = axes[0]

    for col, code in enumerate(countries):
        subset = df[df["code"] == code]
        year_min, year_max = subset["year"].min(), subset["year"].max()
        ax = axes[col]
        ax2 = ax.twinx()

        ax.plot(subset["year"], subset["TMR"] * 100, color=TMR_COLOR, linewidth=1.4)
        ax2.plot(subset["year"], subset["CPM"], color=CPM_COLOR, linewidth=1.4)
        ax2.plot(subset["year"], subset["TFR"], color=TFR_COLOR, linewidth=1.4, linestyle="--")

        ax.set_xlim(*XLIM)
        ax.set_ylim(*TMR_YLIM)
        ax2.set_ylim(*COUNT_YLIM)
        ax.grid(True, linewidth=0.4)
        ax.yaxis.set_major_formatter(PERCENT_FORMATTER)
        ax.set_title(country_title(code, year_min, year_max), fontsize=9)
        # Right-axis tick labels only on the last column, to avoid every
        # panel repeating them -- the left axis's tick labels are already
        # deduped to the first column by sharey=True.
        ax2.tick_params(labelright=col == ncols - 1)
        if col == 0:
            ax.set_ylabel("TMR (%)", color=TMR_COLOR)
        if col == ncols - 1:
            ax2.set_ylabel("CPM / TFR (children)")

    fig.supxlabel("Year")
    fig.legend(handles=LEGEND_HANDLES, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.06), frameon=False)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def slug(name):
    return name.lower().replace(" & ", "_").replace(" / ", "_").replace(" ", "_")


if __name__ == "__main__":
    df = load_data()

    images = {region: make_region_grid(df, countries) for region, countries in MDF_REGIONS.items()}

    # Regions have different country counts, so their tightly-cropped images
    # are different sizes. Pad each onto a common white canvas (the largest
    # image's size) so every saved PNG has identical dimensions.
    canvas_width = max(im.width for im in images.values())
    canvas_height = max(im.height for im in images.values())

    for region, im in images.items():
        canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
        canvas.paste(im, (0, 0))
        path = f"outputs/mdf_region_{slug(region)}.png"
        canvas.save(path)
        print(f"Saved {path}")
