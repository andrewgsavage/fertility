"""England & Wales fertility/childlessness by age, on a shared age-based
colour scale (rather than a discrete qualitative or per-series palette) --
top panel: this repo's own Kulu, Kuang, Christison & Berrington (2025)
Figure 11 data (first_birth_rates_by_education_uk.py), England & Wales
only, both age groups (15-29 and 30-49) combined onto one chart; bottom
panel: Resolution Foundation "Bye Bye Baby" Figure 6 age-band data
(digitized by this repo, resolution/data/grads.csv + nongrads.csv),
graduates vs non-graduates. Both panels use age -> colour via the same
Viridis mapping (20-45), so a given colour means the same age in either
panel; each panel's own second dimension (education level for the top
panel, graduate/non-graduate for the bottom) is carried by line style
instead, so colour is comparable across panels without being overloaded
within either one.

Both panels share the same x-axis: Kulu et al.'s own 5-year *reporting*
periods (categorical, matching first_birth_rates_by_education_uk.py's
PERIODS), not birth year -- so the Resolution Foundation panel's own
densely-sampled reporting-year data (resolution/scripts/plot_grads_nongrads.py's
"Year" mode, not its birth-year-converted mode) is bucketed into the same
six periods here, each point averaged from every digitized value whose
reporting year falls in that period's range, before plotting. Points
outside 1990-2017 (Kulu's own period coverage) are dropped rather than
given a period of their own.
"""

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

KULU_AGE_GROUPS = ["15-29", "30-49"]
KULU_MEAN_AGE = {"15-29": 22, "30-49": 39.5}
EDU_SERIES = ["Low", "Medium", "High"]
EDU_DASH = {"Low": "solid", "Medium": "dash", "High": "dot"}

RF_AGE_GROUPS = ["25-29", "30-34", "35-39", "40-44"]
RF_MEDIAN_AGE = {"25-29": 27, "30-34": 32, "35-39": 37, "40-44": 42}
RF_DASH = {"Graduates": "dot", "Non-graduates": "solid"}

COLORSCALE = "Viridis"
AGE_RANGE = (20, 45)


def _age_color(age):
    frac = (age - AGE_RANGE[0]) / (AGE_RANGE[1] - AGE_RANGE[0])
    frac = min(max(frac, 0), 1)
    return pc.sample_colorscale(COLORSCALE, frac)[0]


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


def _period_bounds(period):
    """"1990-94" -> (1990, 1994); "2015-17" -> (2015, 2017) -- same century
    as the period's own start year."""
    start_s, end_s = period.split("-")
    start = int(start_s)
    end = (start // 100) * 100 + int(end_s)
    return start, end


def _bucket_by_period(x_values, y_values):
    """Mean y per PERIODS bucket, keyed by period label; buckets with no
    points falling in range are omitted."""
    bounds = {p: _period_bounds(p) for p in PERIODS}
    sums = {p: [] for p in PERIODS}
    for x, y in zip(x_values, y_values):
        for p, (lo, hi) in bounds.items():
            if lo <= x <= hi:
                sums[p].append(y)
                break
    return {p: sum(ys) / len(ys) for p, ys in sums.items() if ys}


def rf_childlessness_by_age_group():
    """{education: {age_group: {period: pct_childless_0_100}}}, bucketed
    into Kulu et al.'s own PERIODS from the digitized reporting-year data."""
    result = {}
    for education, fname in [("Graduates", "grads.csv"), ("Non-graduates", "nongrads.csv")]:
        series = _load_rf_series(RF_DATA_DIR / fname)
        result[education] = {}
        for group in RF_AGE_GROUPS:
            pct = series[group]["Y"] * 100
            result[education][group] = _bucket_by_period(series[group]["X"], pct)
    return result


def plot():
    rf_data = rf_childlessness_by_age_group()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
        subplot_titles=["Kulu et al. Figure 11 -- England & Wales, by education (both age groups)", 'Resolution Foundation "Bye Bye Baby" Figure 6 (5-year age band)'],
    )

    for age_group in KULU_AGE_GROUPS:
        for series in EDU_SERIES:
            points = FIRST_BIRTH_RATES[age_group]["England & Wales"][series]
            values = [v for v, _lo, _hi in points]
            fig.add_trace(
                go.Scatter(
                    x=PERIODS, y=values, mode="lines+markers", name=f"{series}, aged {age_group}",
                    line=dict(width=2, color=_age_color(KULU_MEAN_AGE[age_group]), dash=EDU_DASH[series]),
                    marker=dict(size=5), showlegend=False,
                    hovertemplate=f"{series} educated, aged {age_group}<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=1, col=1,
            )

    for education, by_group in rf_data.items():
        for group in RF_AGE_GROUPS:
            by_period = by_group[group]
            periods = [p for p in PERIODS if p in by_period]
            pct = [by_period[p] for p in periods]
            fig.add_trace(
                go.Scatter(
                    x=periods, y=pct, mode="lines+markers", name=f"{education}, aged {group}",
                    line=dict(width=1.5, color=_age_color(RF_MEDIAN_AGE[group]), dash=RF_DASH[education]),
                    marker=dict(size=5), showlegend=False,
                    hovertemplate=f"{education}, aged {group}<br>%{{x}}<br>%{{y:.1f}}% childless<extra></extra>",
                ),
                row=2, col=1,
            )

    # Dummy invisible-marker trace: the standard Plotly trick for a
    # colorbar not tied to a real heatmap/marker-coloured trace. Shared by
    # both panels (age means the same colour throughout the figure).
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale=COLORSCALE, cmin=AGE_RANGE[0], cmax=AGE_RANGE[1],
                color=[AGE_RANGE[0]], showscale=True,
                colorbar=dict(title="Age", x=1.02, y=0.85, yanchor="middle", len=0.28, thickness=15),
            ),
            showlegend=False, hoverinfo="skip",
        ),
        row=1, col=1,
    )

    # Two dash-style legends -- each panel's own second dimension, kept
    # separate from the shared age colour scale above.
    for series, dash in EDU_DASH.items():
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode="lines", name=series,
                line=dict(width=2, color="#555555", dash=dash),
                legend="legend2", showlegend=True, hoverinfo="skip",
            ),
        )
    for education, dash in RF_DASH.items():
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode="lines", name=education,
                line=dict(width=2, color="#555555", dash=dash),
                legend="legend3", showlegend=True, hoverinfo="skip",
            ),
        )

    fig.update_xaxes(
        type="category", categoryorder="array", categoryarray=PERIODS,
        showticklabels=False, row=1, col=1,
    )
    fig.update_xaxes(
        type="category", categoryorder="array", categoryarray=PERIODS,
        title_text="Reporting period", tickangle=-45, row=2, col=1,
    )
    fig.update_yaxes(title_text="Relative first-birth rate<br>(ref: Low educated, 2000-04)", row=1, col=1)
    fig.update_yaxes(title_text="% childless", row=2, col=1)

    fig.update_layout(
        title="England & Wales fertility/childlessness by age -- Kulu et al. Fig. 11 vs Resolution Foundation Fig. 6, coloured by age",
        template="plotly_white", autosize=True,
        legend2=dict(title="Education level", x=1.02, y=0.62, xanchor="left", yanchor="top"),
        legend3=dict(title="Resolution Fdn. education", x=1.02, y=0.25, xanchor="left", yanchor="top"),
        margin=dict(r=170, t=70),
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
