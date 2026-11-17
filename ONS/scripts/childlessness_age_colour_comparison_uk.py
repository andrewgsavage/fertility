"""England & Wales fertility/childlessness by age, on a shared age-based
colour scale (rather than a discrete qualitative or per-series palette) --
top panel: this repo's own Kulu, Kuang, Christison & Berrington (2025)
Figure 11 data (first_birth_rates_by_education_uk.py), England & Wales,
15-29 age group only; bottom panel: Resolution Foundation "Bye Bye Baby"
Figure 6 age-band data (digitized by this repo, resolution/data/grads.csv
+ nongrads.csv), 25-29 age group only, graduates vs non-graduates. Both
panels use age -> colour via the same Viridis mapping (20-45), so a given
colour means the same age in either panel; each panel's own second
dimension (education level for the top panel, graduate/non-graduate for
the bottom) is carried by line style instead, so colour is comparable
across panels without being overloaded within either one. Only the
under-30 age group is plotted from each source by request -- both sources
also cover older age groups (see first_birth_rates_by_education_uk.py and
RF_AGE_GROUPS below), just not shown here.

Both panels share a single continuous *year* x-axis (not categorical
periods), but the two sources' own native resolution is very different:
Kulu et al.'s own data is only published per 5-year *reporting* period
(first_birth_rates_by_education_uk.py's PERIODS), so each period's point
is plotted at that period's own midpoint year (e.g. "1990-94" -> 1992);
the Resolution Foundation series is digitized at ~0.2-year resolution and
plotted unaveraged/as-is (reporting year, not birth year -- resolution/
scripts/plot_grads_nongrads.py's "Year" mode), which is also why it
extends further (to ~2022) than Kulu et al.'s own period coverage (ending
2015-17).
"""

import bisect
import pathlib

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from first_birth_rates_by_education_uk import FIRST_BIRTH_RATES, PERIODS

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
RF_DATA_DIR = _REPO_ROOT / "resolution" / "data"

OUTPUT = "outputs/childlessness_age_colour_comparison_uk.html"

# Only the under-30 age group from each source -- see module docstring.
KULU_AGE_GROUPS = ["15-29"]
KULU_MEAN_AGE = {"15-29": 22, "30-49": 39.5}
EDU_SERIES = ["Low", "Medium", "High"]
EDU_DASH = {"Low": "solid", "Medium": "dash", "High": "dot"}

RF_AGE_GROUPS = ["25-29"]
RF_MEDIAN_AGE = {"25-29": 27, "30-34": 32, "35-39": 37, "40-44": 42}
RF_DASH = {"Graduates": "dot", "Non-graduates": "solid"}

COLORSCALE = "Viridis"
AGE_RANGE = (20, 45)

# Where the direct line labels sit -- both panels' data span this year, so
# one shared x keeps every label lined up vertically rather than trailing
# off at each line's own (staggered) end point.
LABEL_X = 2000


def _age_color(age):
    frac = (age - AGE_RANGE[0]) / (AGE_RANGE[1] - AGE_RANGE[0])
    frac = min(max(frac, 0), 1)
    return pc.sample_colorscale(COLORSCALE, frac)[0]


def _interp(series_x, series_y, x):
    """Linearly interpolate y at x from parallel (sorted-x) sequences --
    used to place each line's label at LABEL_X even though the underlying
    series (Kulu et al.'s period midpoints, the RF digitized points) aren't
    necessarily sampled exactly there."""
    if x <= series_x[0]:
        return series_y[0]
    if x >= series_x[-1]:
        return series_y[-1]
    i = bisect.bisect_left(series_x, x)
    x0, x1 = series_x[i - 1], series_x[i]
    y0, y1 = series_y[i - 1], series_y[i]
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def _load_rf_series(path):
    """{age_group: DataFrame[X, Y]} from a grads/nongrads-style digitized CSV
    (two-row header: age group label + X/Y sub-columns)."""
    header = pd.read_csv(path, header=None, nrows=2)
    top = header.iloc[0].ffill()
    columns = pd.MultiIndex.from_arrays([top, header.iloc[1]])
    df = pd.read_csv(path, header=None, skiprows=2, names=columns)
    series = {}
    for group in RF_AGE_GROUPS:
        sub = df[group].dropna()
        series[group] = sub.sort_values("X")
    return series


def _period_midpoint(period):
    """"1990-94" -> 1992.0; "2015-17" -> 2016.0 -- same century as the
    period's own start year."""
    start_s, end_s = period.split("-")
    start = int(start_s)
    end = (start // 100) * 100 + int(end_s)
    return (start + end) / 2


def rf_childlessness_by_age_group():
    """{education: {age_group: [(reporting_year, pct_with_child_0_100), ...]}},
    unaveraged, at the digitized data's own resolution. The source's own
    figure/CSV is childlessness; flipped to % with a child here (100 -
    childless%)."""
    result = {}
    for education, fname in [("Graduates", "grads.csv"), ("Non-graduates", "nongrads.csv")]:
        series = _load_rf_series(RF_DATA_DIR / fname)
        result[education] = {}
        for group in RF_AGE_GROUPS:
            years = series[group]["X"]
            pct_with_child = 100 - series[group]["Y"] * 100
            result[education][group] = list(zip(years, pct_with_child))
    return result


def plot():
    rf_data = rf_childlessness_by_age_group()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08)

    # (row, y_at_LABEL_X, label, colour) -- direct labels (positioned right
    # above each line at LABEL_X, see the drawing loop below) replace the
    # colour-scale/dash-style legends below.
    line_labels = []
    all_years = []

    period_years = [_period_midpoint(p) for p in PERIODS]
    all_years.extend(period_years)
    for age_group in KULU_AGE_GROUPS:
        for series in EDU_SERIES:
            points = FIRST_BIRTH_RATES[age_group]["England & Wales"][series]
            values = [v for v, _lo, _hi in points]
            color = _age_color(KULU_MEAN_AGE[age_group])
            fig.add_trace(
                go.Scatter(
                    x=period_years, y=values, mode="lines+markers", name=f"{series}, aged {age_group}",
                    line=dict(width=2, color=color, dash=EDU_DASH[series]),
                    marker=dict(size=6), showlegend=False,
                    customdata=PERIODS,
                    hovertemplate=f"{series} educated, aged {age_group}<br>%{{customdata}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=1, col=1,
            )
            line_labels.append((1, _interp(period_years, values, LABEL_X), f"{series} education", color))

    for education, by_group in rf_data.items():
        for group in RF_AGE_GROUPS:
            years, pct = zip(*by_group[group])
            all_years.extend(years)
            color = _age_color(RF_MEDIAN_AGE[group])
            fig.add_trace(
                go.Scatter(
                    x=years, y=pct, mode="lines", name=f"{education}, aged {group}",
                    line=dict(width=1.5, color=color, dash=RF_DASH[education]),
                    showlegend=False,
                    hovertemplate=f"{education}, aged {group}<br>%{{x:.1f}}<br>%{{y:.1f}}% with child<extra></extra>",
                ),
                row=2, col=1,
            )
            line_labels.append((2, _interp(list(years), list(pct), LABEL_X), education, color))

    for row, y, label, color in line_labels:
        fig.add_annotation(
            x=LABEL_X, y=y, text=label, showarrow=False,
            xanchor="center", yanchor="bottom", yshift=10,
            font=dict(size=12, color=color), bgcolor="rgba(255,255,255,0.75)",
            row=row, col=1,
        )

    # Panel titles, top-left of each subplot's own plot area (not the shared
    # figure title, and not an axis title) -- positioned via "x/y domain"
    # refs rather than data coordinates, so they stay pinned to the corner
    # regardless of each panel's own y-range.
    PANEL_TITLES = {
        1: "Relative fertility rate, England & Wales, ages 15-29",
        2: "% with child, ages 25-29",
    }
    for row, title in PANEL_TITLES.items():
        axis_suffix = "" if row == 1 else str(row)
        fig.add_annotation(
            x=0, y=1, xref=f"x{axis_suffix} domain", yref=f"y{axis_suffix} domain",
            xanchor="left", yanchor="bottom", yshift=4,
            text=f"<b>{title}</b>", showarrow=False, font=dict(size=13),
        )

    x_range = [min(all_years), max(all_years)]
    fig.update_xaxes(range=x_range, showticklabels=False, row=1, col=1)
    fig.update_xaxes(range=x_range, row=2, col=1)
    fig.update_yaxes(rangemode="tozero", row=2, col=1)

    fig.update_layout(
        template="plotly_white", autosize=True,
        showlegend=False,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


if __name__ == "__main__":
    fig = plot()
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
