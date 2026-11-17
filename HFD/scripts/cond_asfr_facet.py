"""Conditional ASFR for first vs second births, one interactive Plotly
facet grid across every HFD country in country_names.COUNTRY_REGIONS (plus
the UK reconstruction) — replaces the old per-region tab-set of static
matplotlib grids (cond_asfr_region_grid.py) with a single page, faceted
in pairs of (first birth, second birth) subplots, three country-pairs
(six subplot columns) per row.
"""

import math
import pathlib
import sys

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from country_names import COUNTRY_REGIONS, country_title
from plot_colors import PERIOD_COLORSCALE, period_axis

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from cond_asfr_uk_ons import load_period_rates  # noqa: E402

OUTPUT = "outputs/cond_asfr_facet.html"
OUTPUT_CHANGE = "outputs/cond_asfr_facet_change.html"

SHARED_YRANGE = (0, 0.25)
# Change-since-baseline chart: each rate is divided by the same country's
# mean rate at that age over BASELINE_YEARS, and drawn on a log axis (so a
# halving and a doubling are the same distance from baseline). Ages whose
# baseline rate is under MIN_BASELINE are dropped: dividing by a tiny rate
# at the youngest and oldest ages gives wildly noisy ratios.
BASELINE_YEARS = (2009, 2011)
MIN_BASELINE = 0.005
CHANGE_YRANGE = (0.22, 3.3)
CHANGE_TICKS = [0.25, 0.5, 0.75, 1, 1.5, 2, 3]
COUNTRY_PAIRS_PER_ROW = 3
ROW_HEIGHT = 150
# Gap between the first/second-birth columns of one country's pair vs. the
# (bigger) gap that separates one country's pair from the next.
WITHIN_PAIR_GAP = 0.004
BETWEEN_PAIR_GAP = 0.028
# Matches plotly_white's default axis-title font (size/family/color), so the
# in-plot country names and column headers read as part of the same system.
LABEL_FONT = dict(size=14, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")

BIRTH_ORDERS = [(1, "m1x", "First birth"), (2, "m2x", "Second birth")]


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
    # like an HFD country everywhere else in this script.
    by_period = load_period_rates()
    uk_rows = [
        {"code": "UK_ONS", "year": year, "age": age, "m1x": c1, "m2x": c2}
        for year, ages in by_period.items()
        for age, (c1, c2) in ages.items()
    ]
    df = pd.concat([df, pd.DataFrame(uk_rows)], ignore_index=True)
    return df


def add_change_since_baseline(df):
    """Add r1x / r2x: each conditional ASFR divided by the country's mean
    rate at that age over BASELINE_YEARS (all years in the window must be
    present). NaN where the baseline is missing or below MIN_BASELINE."""
    lo, hi = BASELINE_YEARS
    df = df.copy()
    window = df[df["year"].between(lo, hi)].groupby(["code", "age"])
    for column in ("m1x", "m2x"):
        baseline = window[column].mean().where(window[column].count() == hi - lo + 1)
        baseline = baseline.where(baseline >= MIN_BASELINE).rename("baseline")
        ratio = df[column] / df.join(baseline, on=["code", "age"])["baseline"]
        df["r" + column[1:]] = ratio
    return df


def _year_color(year, ymin, ymax, alpha=0.6):
    t = 0.0 if ymax == ymin else (year - ymin) / (ymax - ymin)
    t = min(1.0, max(0.0, t))  # clip: years outside [ymin, ymax] clamp to the end color
    r, g, b = pc.sample_colorscale(PERIOD_COLORSCALE, [t])[0][4:-1].split(",")
    return f"rgba({r},{g},{b},{alpha})"


def _column_domains(ncols, within_gap, between_gap):
    """x-axis domain (x0, x1) for each of ncols columns, tighter within a
    (first birth, second birth) pair than between one pair and the next."""
    npairs = ncols // 2
    total_gap = npairs * within_gap + (npairs - 1) * between_gap
    width = (1 - total_gap) / ncols
    domains = []
    x = 0.0
    for pair in range(npairs):
        domains.append((x, x + width))
        x += width + within_gap
        domains.append((x, x + width))
        x += width + between_gap
    return domains


def make_facet(df, countries, change=False):
    """One Plotly figure with a (first birth, second birth) subplot pair per
    country, COUNTRY_PAIRS_PER_ROW pairs (2 * COUNTRY_PAIRS_PER_ROW columns)
    per row, countries continuing onto further rows rather than behind
    per-region tabs. With change, plots each rate relative to its country's
    BASELINE_YEARS mean (r1x / r2x) on a log axis instead of the raw rate."""
    ymin, ymax = period_axis(df["year"].min(), df["year"].max())
    rows_of_countries = [
        countries[i : i + COUNTRY_PAIRS_PER_ROW] for i in range(0, len(countries), COUNTRY_PAIRS_PER_ROW)
    ]
    nrows = len(rows_of_countries)
    ncols = COUNTRY_PAIRS_PER_ROW * 2

    # "First birth"/"Second birth" only head the top row, like column labels
    # in a faceted grid; country names are placed inside each row's first-
    # birth subplot instead (see the annotation loop below), so they don't
    # need their own title row on every line.
    header_row = [label for _ in range(COUNTRY_PAIRS_PER_ROW) for _, _, label in BIRTH_ORDERS]
    subplot_titles = header_row + ["" for _ in range(ncols * (nrows - 1))]

    fig = make_subplots(
        rows=nrows, cols=ncols, subplot_titles=subplot_titles,
        horizontal_spacing=0.001, vertical_spacing=min(0.01, 1 / max(nrows - 1, 1)),
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT
    for col, domain in enumerate(_column_domains(ncols, WITHIN_PAIR_GAP, BETWEEN_PAIR_GAP), start=1):
        fig.update_xaxes(domain=list(domain), col=col)

    for row, row_countries in enumerate(rows_of_countries, start=1):
        for pair, country in enumerate(row_countries):
            subset = df[df["code"] == country]
            name = country_title(country)
            hover_name = country_title(country, subset["year"].min(), subset["year"].max())
            # Country name sits inside the pair's first-birth subplot (top-left,
            # in-domain) rather than as its own subplot_titles row, so it
            # doesn't cost extra vertical space on every row.
            fig.add_annotation(
                text=f"<b>{name}</b>", x=0.04, y=0.95, xref="x domain", yref="y domain",
                xanchor="left", yanchor="top", showarrow=False,
                font=LABEL_FONT, row=row, col=pair * 2 + 1,
            )
            for order, column, label in BIRTH_ORDERS:
                col = pair * 2 + order
                if change:
                    column = "r" + column[1:]
                for year, year_rows in subset.groupby("year"):
                    year_rows = year_rows.sort_values("age")
                    if change:
                        year_rows = year_rows.dropna(subset=[column])
                        hover = (
                            f"{hover_name}, {label}<br>Year {year}<br>Age %{{x}}<br>"
                            f"%{{customdata:+.0%}} vs {BASELINE_YEARS[0]}-{BASELINE_YEARS[1]}<extra></extra>"
                        )
                        customdata = year_rows[column] - 1
                    else:
                        hover = f"{hover_name}, {label}<br>Year {year}<br>Age %{{x}}<br>%{{y:.1%}}<extra></extra>"
                        customdata = None
                    fig.add_trace(
                        go.Scatter(
                            x=year_rows["age"], y=year_rows[column],
                            mode="lines", line=dict(width=0.8, color=_year_color(year, ymin, ymax)),
                            name=str(year), legendgroup=str(year), showlegend=False,
                            customdata=customdata, hovertemplate=hover,
                        ),
                        row=row, col=col,
                    )
                fig.update_xaxes(range=[15, 45], showticklabels=(row == nrows), row=row, col=col)
                if change:
                    fig.update_yaxes(
                        type="log", range=[math.log10(r) for r in CHANGE_YRANGE],
                        tickvals=CHANGE_TICKS, ticktext=[f"{t - 1:+.0%}" if t != 1 else "0%" for t in CHANGE_TICKS],
                        showticklabels=(col == 1), row=row, col=col,
                    )
                else:
                    fig.update_yaxes(
                        range=list(SHARED_YRANGE), tickformat=".0%", showticklabels=(col == 1), row=row, col=col,
                    )

    # Dummy trace to show a colorbar for the year axis, placed next to the
    # last country's subplots when that row has empty columns to spare
    # (country count isn't always a multiple of COUNTRY_PAIRS_PER_ROW);
    # otherwise fall back to the top-right corner.
    last_row_countries = rows_of_countries[-1]
    if len(last_row_countries) < COUNTRY_PAIRS_PER_ROW:
        colorbar_row, colorbar_col = nrows, len(last_row_countries) * 2 + 1
    else:
        colorbar_row, colorbar_col = 1, ncols
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale=PERIOD_COLORSCALE, cmin=ymin, cmax=ymax,
                color=[ymin], showscale=True,
                colorbar=dict(title="Year"),
            ),
            showlegend=False,
        ),
        row=colorbar_row, col=colorbar_col,
    )
    fig.update_xaxes(visible=False, row=colorbar_row, col=colorbar_col)
    fig.update_yaxes(visible=False, row=colorbar_row, col=colorbar_col)

    fig.update_layout(
        title=(
            f"Change in Conditional ASFR since {BASELINE_YEARS[0]}-{BASELINE_YEARS[1]}, by country (log scale)"
            if change
            else "First and Second Birth Conditional ASFRs vs age, by country"
        ),
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 120,
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    all_countries = [code for codes in COUNTRY_REGIONS.values() for code in codes]
    df = add_change_since_baseline(df)
    for output, change in [(OUTPUT, False), (OUTPUT_CHANGE, True)]:
        fig = make_facet(df, all_countries, change=change)
        fig.write_html(
            output,
            include_plotlyjs="cdn",
            full_html=True,
            default_width="100%",
            default_height=f"{fig.layout.height}px",
            config={"responsive": True},
        )
        html = open(output, "r", encoding="utf-8").read()
        html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
        open(output, "w", encoding="utf-8").write(html)
        print(f"Saved {output}")
