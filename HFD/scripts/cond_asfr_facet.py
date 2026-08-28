"""Conditional ASFR for first vs second births, one interactive Plotly
facet grid across every HFD country in country_names.COUNTRY_REGIONS (plus
the UK reconstruction) — replaces the old per-region tab-set of static
matplotlib grids (cond_asfr_region_grid.py) with a single page, faceted
in pairs of (first birth, second birth) subplots, three country-pairs
(six subplot columns) per row.
"""

import pathlib
import sys

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from country_names import COUNTRY_REGIONS, country_title

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from cond_asfr_uk_ons import load_period_rates  # noqa: E402

OUTPUT = "outputs/cond_asfr_facet.html"

SHARED_YRANGE = (0, 0.25)
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


def _year_color(year, ymin, ymax, alpha=0.6):
    t = 0.0 if ymax == ymin else (year - ymin) / (ymax - ymin)
    r, g, b = pc.sample_colorscale("Turbo", [t])[0][4:-1].split(",")
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


def make_facet(df, countries):
    """One Plotly figure with a (first birth, second birth) subplot pair per
    country, COUNTRY_PAIRS_PER_ROW pairs (2 * COUNTRY_PAIRS_PER_ROW columns)
    per row, countries continuing onto further rows rather than behind
    per-region tabs."""
    ymin, ymax = df["year"].min(), df["year"].max()
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
                for year, year_rows in subset.groupby("year"):
                    year_rows = year_rows.sort_values("age")
                    fig.add_trace(
                        go.Scatter(
                            x=year_rows["age"], y=year_rows[column],
                            mode="lines", line=dict(width=0.8, color=_year_color(year, ymin, ymax)),
                            name=str(year), legendgroup=str(year), showlegend=False,
                            hovertemplate=f"{hover_name}, {label}<br>Year {year}<br>Age %{{x}}<br>%{{y:.1%}}<extra></extra>",
                        ),
                        row=row, col=col,
                    )
                fig.update_xaxes(range=[15, 45], showticklabels=(row == nrows), row=row, col=col)
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
                colorscale="Turbo", cmin=ymin, cmax=ymax,
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
        title="First and Second Birth Conditional ASFRs vs age, by country",
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 120,
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    all_countries = [code for codes in COUNTRY_REGIONS.values() for code in codes]
    fig = make_facet(df, all_countries)

    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height=f"{fig.layout.height}px",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
