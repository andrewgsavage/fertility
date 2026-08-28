"""Same expected-children-given-first-birth-age recursion as
births_per_mother_region_grid.py, run on HFD's period fertility tables
(pft.txt) instead of cohort tables (cft.txt) -- one line per calendar year
instead of one line per birth cohort -- for every country in
COUNTRY_REGIONS. A period-basis cross-check of the same estimation method
against the main (cohort-based) chart, covering every country rather than
just the handful with register-measured parity data.

UK_ONS is skipped: it has no HFD period table to run this on (the main
chart's UK column comes from ONS Table 3 instead, which is inherently
cohort-based).
"""

import pathlib

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator
from PIL import Image

from births_per_mother_region_grid import X_LIM, Y_LIM
from births_per_mother_region_grid import _expected_children_curve as expected_children_curve
from country_names import COUNTRY_REGIONS, country_title

COLS = ["code", "year", "x", "w0x", "m1x", "q1x", "l0x", "b1x", "L0x", "Sb1x",
        "w1x", "m2x", "q2x", "l1x", "b2x", "L1x", "Sb2x",
        "w2x", "m3x", "q3x", "l2x", "b3x", "L2x", "Sb3x",
        "w3x", "m4x", "q4x", "l3x", "b4x", "L3x", "Sb4x",
        "w4x", "m5px", "q5px", "l4x", "b5px", "L4x", "Sb5px"]


def load_data():
    df = pd.read_csv("data/HFD/pft.txt", sep=r"\s+", skiprows=3, names=COLS, na_values=".")
    df = df[pd.to_numeric(df["x"], errors="coerce").notna()].copy()
    df["x"] = df["x"].astype(int)

    rows = []
    for (code, year), sub in df.groupby(["code", "year"]):
        for age, value in expected_children_curve(sub).items():
            rows.append({"code": code, "year": year, "age": age, "expected_children": value})
    return pd.DataFrame(rows)


def slug(name):
    return name.lower().replace(" & ", "_").replace(" / ", "_").replace(" ", "_")


def make_region_grid(df, countries):
    cmap = plt.colormaps["turbo"]
    norm = plt.Normalize(df["year"].min(), df["year"].max())

    ncols = len(countries)
    fig, axes = plt.subplots(
        1, ncols, figsize=(3 * ncols, 3), sharex=True, sharey=True,
        gridspec_kw={"wspace": 0}, squeeze=False,
    )

    for col, country in enumerate(countries):
        subset = df[df["code"] == country]
        ax = axes[0, col]
        for year, rows in subset.groupby("year"):
            rows = rows.sort_values("age")
            ax.plot(rows["age"], rows["expected_children"], color=cmap(norm(year)), alpha=0.6, linewidth=0.8)
        ax.set_xlim(*X_LIM)
        ax.set_xticks(list(range(20, X_LIM[1], 10)) + [X_LIM[1]])
        ax.set_ylim(*Y_LIM)
        ax.grid(True, linewidth=0.4)
        ax.set_title(country_title(country, subset["year"].min(), subset["year"].max()), fontsize=9)
        if col == 0:
            ax.set_ylabel("Expected children")

    # wspace=0 means each interior panel's rightmost *visible* x-tick label
    # sits right next to the next panel's leftmost one, overlapping. Hiding
    # it on every panel but the last leaves one label per boundary instead
    # of two colliding ones. get_xticklabels() includes off-range ticks
    # just outside xlim (e.g. "50" when xlim tops out at 45), so the
    # rightmost *visible* one has to be picked by position, not by index.
    for ax in axes[0, :-1]:
        xlim = ax.get_xlim()
        positions = ax.get_xticks()
        labels = ax.get_xticklabels()
        visible = [i for i, p in enumerate(positions) if xlim[0] <= p <= xlim[1]]
        if visible:
            labels[visible[-1]].set_visible(False)

    fig.subplots_adjust(bottom=0.22)
    fig.supxlabel("Age at first birth")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist(), label="Year", shrink=0.6)
    cbar.ax.yaxis.set_major_locator(MultipleLocator(10))
    cbar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f}"))

    buf_path = pathlib.Path("outputs") / "_tmp_region_grid.png"
    fig.savefig(buf_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    image = Image.open(buf_path).convert("RGB")
    buf_path.unlink()
    return image


if __name__ == "__main__":
    df = load_data()

    images = {
        region: make_region_grid(df, [c for c in countries if c != "UK_ONS"])
        for region, countries in COUNTRY_REGIONS.items()
    }

    canvas_width = max(im.width for im in images.values())
    canvas_height = max(im.height for im in images.values())

    for region, im in images.items():
        canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
        canvas.paste(im, (0, 0))
        path = f"outputs/births_per_mother_estimated_region_{slug(region)}.png"
        canvas.save(path)
        print(f"Saved {path}")
