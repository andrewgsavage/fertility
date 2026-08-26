import io
import pathlib
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator
from PIL import Image

from country_names import COUNTRY_REGIONS, country_title

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from births_per_mother_uk_ons import load_expected_children_curves as load_uk_curves  # noqa: E402

# HFD's cft.txt caps its birth-order breakdown at "5th or higher order" (a
# woman who reaches it is folded into a single q5px hazard with no further
# split). This approximates that terminal state as exactly 5 children — a
# small undercount for the shrinking few who go on to a 6th+, negligible in
# these mostly-modern, mostly-low-fertility cohorts.
VALUE_5PLUS = 5.0

# The backward recursion treats "no data past this age" as "assume she has
# no more children past this age" — a safe assumption near the end of the
# fertile window, but a severe *under*-estimate for a cohort that's simply
# too young for the data to have caught up with yet (e.g. a cohort tracked
# only to age 25 would have every one of its curves collapse to ~1 by 25,
# as if every woman stopped at her first child). So only cohorts whose
# tracked data reaches this age are used at all — this is why some
# countries with only recently-started HFD coverage (Belgium, Croatia,
# South Korea) show no lines: none of their tracked cohorts are old enough
# yet for this page's terminal-age assumption to be safe.
MIN_COMPLETE_AGE = 45
X_LIM = (18, 45)
Y_LIM = (1.0, 4.0)


def load_data():
    cft = pd.read_csv(
        "data/HFD/cft.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "cohort", "x", "b1x", "l0x", "m1x", "q1x", "Sb1x",
               "b2x", "l1x", "m2x", "q2x", "Sb2x",
               "b3x", "l2x", "m3x", "q3x", "Sb3x",
               "b4x", "l3x", "m4x", "q4x", "Sb4x",
               "b5px", "l4x", "m5px", "q5px", "Sb5px", "chix"],
        na_values=".",
    )
    cft = cft[pd.to_numeric(cft["x"], errors="coerce").notna()].copy()
    cft["x"] = cft["x"].astype(int)

    max_tracked_age = cft.dropna(subset=["q2x"]).groupby(["code", "cohort"])["x"].max()
    complete_cohorts = max_tracked_age[max_tracked_age >= MIN_COMPLETE_AGE].index

    rows = []
    for (code, cohort), sub in cft.groupby(["code", "cohort"]):
        if (code, cohort) not in complete_cohorts:
            continue
        for age, value in _expected_children_curve(sub).items():
            rows.append({"code": code, "cohort": cohort, "age": age, "expected_children": value})

    uk_rows = [
        {"code": "UK_ONS", "cohort": cohort, "age": age, "expected_children": value}
        for cohort, curve in load_uk_curves().items()
        for age, value in curve.items()
    ]
    return pd.DataFrame(rows + uk_rows)


def _expected_children_curve(sub):
    """{age: E[total children | first birth at exactly this age]} for one
    (code, cohort) group of cft.txt — a backward recursion over age using
    that cohort's own parity-progression hazards (q2x..q5px): starting from
    the oldest tracked age and working down, at each step folding in that
    age's chance of moving up one more parity. A woman still short of the
    next parity past the oldest tracked age is assumed done having
    children (terminal value = her current parity)."""
    sub = sub.sort_values("x")
    ages = sub["x"].to_numpy()
    q2 = sub["q2x"].fillna(0).to_numpy()
    q3 = sub["q3x"].fillna(0).to_numpy()
    q4 = sub["q4x"].fillna(0).to_numpy()
    q5p = sub["q5px"].fillna(0).to_numpy()

    e1_next, e2_next, e3_next, e4_next = 1.0, 2.0, 3.0, 4.0
    curve = {}
    for i in range(len(ages) - 1, -1, -1):
        e4 = q5p[i] * VALUE_5PLUS + (1 - q5p[i]) * e4_next
        e3 = q4[i] * e4_next + (1 - q4[i]) * e3_next
        e2 = q3[i] * e3_next + (1 - q3[i]) * e2_next
        e1 = q2[i] * e2_next + (1 - q2[i]) * e1_next
        curve[ages[i]] = e1
        e1_next, e2_next, e3_next, e4_next = e1, e2, e3, e4
    return curve


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
    norm = plt.Normalize(df["cohort"].min(), df["cohort"].max())

    ncols = len(countries)
    fig, axes = plt.subplots(
        1, ncols, figsize=(3 * ncols, 3), sharex=True, sharey=True,
        gridspec_kw={"wspace": 0},
        squeeze=False,
    )

    for col, country in enumerate(countries):
        subset = df[df["code"] == country]
        ax = axes[0, col]
        for cohort, cohort_rows in subset.groupby("cohort"):
            cohort_rows = cohort_rows.sort_values("age")
            ax.plot(
                cohort_rows["age"], cohort_rows["expected_children"],
                color=cmap(norm(cohort)), alpha=0.6, linewidth=0.8,
            )
        ax.set_xlim(*X_LIM)
        ax.set_ylim(*Y_LIM)
        ax.grid(True, linewidth=0.4)
        ax.set_title(
            country_title(country, subset["cohort"].min(), subset["cohort"].max()),
            fontsize=9,
        )
        if col == 0:
            ax.set_ylabel("Expected children")

    fig.supxlabel("Age at first birth")

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = fig.colorbar(sm, ax=axes.ravel().tolist(), label="Birth cohort", shrink=0.6)
    cbar.ax.yaxis.set_major_locator(MultipleLocator(10))
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
        path = f"outputs/births_per_mother_region_{slug(region)}.png"
        canvas.save(path)
        print(f"Saved {path}")
