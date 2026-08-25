"""Trajectory of each country's peak first-birth conditional ASFR (cond
ASFR1, HFD's m1x): for every (country, year) find the age at which m1x
peaks and the peak value itself, then trace how that (age, value) point
moves year by year.

Country is encoded by color, using colorcet's isoluminant "isolum" map
(constant perceived lightness, so hue alone separates countries with no
brightness cue competing for attention) sampled once per country in
region order, matching the coloring convention used elsewhere in this repo
(e.g. cond_asfr_region_grid.py's per-region grouping). Year is encoded by
opacity — oldest faintest, most recent fully opaque — so each trajectory
reads as moving forward through time without a second color channel.

Reuses the same mi.txt (HFD) + ONS-reconstructed UK data as the region-grid
chart on the HFD > First vs Second Birth page (see cond_asfr_region_grid.py)
so this chart traces the same underlying first-birth curves from a
different angle: where those peaks are, and how they've drifted.
"""

import pathlib
import sys

import colorcet as cc
import pandas as pd
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from cond_asfr_region_grid import load_data  # noqa: E402
from country_names import COUNTRY_NAMES, order_by_region  # noqa: E402

OUTPUT = "outputs/asfr1_peak_trajectory.html"
OUTPUT_PNG = "outputs/asfr1_peak_trajectory.png"

# Oldest year fades toward this opacity, most recent year is fully opaque.
ALPHA_MIN, ALPHA_MAX = 0.2, 1.0

LINE_WIDTH = 5

# Width (in single years) of the centered rolling-mean window used to smooth
# each country's m1x grid before peak-finding, along each axis.
SMOOTH_AGE_WINDOW = 5
SMOOTH_YEAR_WINDOW = 5


def _smoothed_grid(group):
    """One country's m1x, as a year x age grid, smoothed with a 2D centered
    rolling-mean box across both age and year. HFD's by-age, by-year
    conditional ASFR can be noisy in either dimension — especially for
    smaller-population countries/years — so an unsmoothed idxmax can pick
    out a one-year/one-age sampling spike rather than the underlying peak.
    The box is applied as two separable 1D rolling-mean passes (across
    age, then across year), which is mathematically equivalent to a single
    2D box average. Grid cells with no raw observation stay NaN rather
    than letting the rolling window fabricate a value for them from their
    neighbors."""
    pivot = group.pivot_table(index="year", columns="age", values="m1x", aggfunc="mean")
    by_age = pivot.T.rolling(SMOOTH_AGE_WINDOW, center=True, min_periods=1).mean().T
    by_year = by_age.rolling(SMOOTH_YEAR_WINDOW, center=True, min_periods=1).mean()
    return by_year.where(pivot.notna())


def _interpolated_peak(row):
    """The age (float) and value of row's max, refined to sub-year
    precision by fitting a parabola through the max and its two immediate
    age-neighbors and taking the vertex — since the underlying peak of a
    smooth fertility-by-age curve need not fall exactly on a whole year of
    age, it's just where HFD happens to sample it. Falls back to the
    discrete (whole-year) max when a neighbor is missing or the three
    points are colinear/inverted."""
    row = row.dropna()
    age0 = row.idxmax()
    value0 = row[age0]
    value_lo = row.get(age0 - 1)
    value_hi = row.get(age0 + 1)
    if value_lo is None or value_hi is None:
        return float(age0), value0
    denom = value_lo - 2 * value0 + value_hi
    if denom >= 0:  # not a strict local max under the parabola fit
        return float(age0), value0
    offset = 0.5 * (value_lo - value_hi) / denom
    offset = max(-1.0, min(1.0, offset))
    peak_value = value0 - 0.25 * (value_lo - value_hi) * offset
    return age0 + offset, peak_value


def compute_peaks(df):
    """One row per (code, year): the age (float, sub-year-interpolated)
    and value of that year's cond ASFR1 (m1x) peak, found on the
    2D-smoothed curve (see _smoothed_grid and _interpolated_peak)."""
    rows = []
    for code, group in df.groupby("code"):
        grid = _smoothed_grid(group)
        for year, row in grid.iterrows():
            if row.notna().sum() == 0:
                continue
            peak_age, peak_value = _interpolated_peak(row)
            rows.append({"code": code, "year": year, "peak_age": peak_age, "peak_value": peak_value})
    return pd.DataFrame(rows, columns=["code", "year", "peak_age", "peak_value"]).sort_values(["code", "year"])


def _country_colors(codes):
    """One isolum color per code, sampled evenly across the colormap in
    region order so geographically grouped countries also land at spread-out
    (rather than adjacent-and-similar) points on the map."""
    n = len(codes)
    cmap = cc.cm.isolum
    return {code: cmap(i / max(n - 1, 1)) for i, code in enumerate(codes)}


def _rgba(color, alpha):
    r, g, b = (round(c * 255) for c in color[:3])
    return f"rgba({r}, {g}, {b}, {alpha:.3f})"


def plot(peaks):
    codes = order_by_region(sorted(peaks["code"].unique()))
    colors = _country_colors(codes)
    year_min, year_max = peaks["year"].min(), peaks["year"].max()

    def alpha_for(year):
        if year_max == year_min:
            return ALPHA_MAX
        t = (year - year_min) / (year_max - year_min)
        return ALPHA_MIN + t * (ALPHA_MAX - ALPHA_MIN)

    fig = go.Figure()
    for code in codes:
        rows = peaks[peaks["code"] == code].sort_values("year")
        if rows.empty:
            continue
        color = colors[code]
        name = COUNTRY_NAMES.get(code, code)
        years = rows["year"].tolist()
        ages = rows["peak_age"].tolist()
        values = [v * 100 for v in rows["peak_value"].tolist()]

        # Dummy (off-canvas) trace so the legend gets one solid-color entry
        # per country, independent of how many segments/points it actually
        # has.
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                line=dict(color=_rgba(color, 1.0), width=LINE_WIDTH),
                name=name,
                legendgroup=code,
            )
        )

        # One line segment per year-to-year step, each faded to the
        # midpoint year of that step, so the connecting line itself fades
        # in with time rather than sitting at one fixed opacity.
        for i in range(len(rows) - 1):
            seg_alpha = alpha_for((years[i] + years[i + 1]) / 2)
            fig.add_trace(
                go.Scatter(
                    x=ages[i : i + 2],
                    y=values[i : i + 2],
                    mode="lines",
                    line=dict(color=_rgba(color, seg_alpha), width=LINE_WIDTH),
                    hoverinfo="skip",
                    showlegend=False,
                    legendgroup=code,
                )
            )

        # Invisible markers just to carry per-year hover tooltips — no
        # visible dots on the trajectory itself.
        fig.add_trace(
            go.Scatter(
                x=ages,
                y=values,
                mode="markers",
                marker=dict(color=_rgba(color, 1.0), size=8, opacity=0),
                showlegend=False,
                legendgroup=code,
                customdata=years,
                hovertemplate=f"{name}<br>Year %{{customdata}}<br>Peak age %{{x:.1f}}<br>Peak cond ASFR1 %{{y:.1f}}%<extra></extra>",
            )
        )

    fig.update_xaxes(title_text="Age at peak conditional ASFR1")
    fig.update_yaxes(title_text="Peak conditional ASFR1 (%)")
    fig.update_layout(
        title=f"Trajectory of peak first-birth conditional ASFR, {year_min}–{year_max} — HFD",
        template="plotly_white",
        legend=dict(title_text="Country", groupclick="togglegroup"),
        autosize=True,
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    peaks = compute_peaks(df)
    fig = plot(peaks)
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")

    fig.write_image(OUTPUT_PNG, width=1200, height=1100, scale=2)
    print(f"Saved {OUTPUT_PNG}")
