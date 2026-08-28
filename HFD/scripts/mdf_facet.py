"""Microdemographic Framework (Shaw 2025) metrics for docs/hfd/mdf.md: one
interactive Plotly facet grid across every country in
country_names.COUNTRY_REGIONS (including the ONS-reconstructed UK series),
TMR/CPM/TFR
overlaid on a dual y-axis per country panel (TMR left, CPM/TFR right) --
same pairing as the paper's own Fig. 1, extended with TFR on the right
axis. Replaces the old per-region tab-set of static matplotlib grids
(mdf_metrics.py) with a single page, faceted six countries per row, in the
same style as cond_asfr_facet.py's first-vs-second-birth grid. TCR is
skipped (it's just 1 - TMR, so redundant alongside TMR here).

TFR = TMR x CPM. TMR (Total Maternal Rate) is HFD's TFR1 (period first-birth
TFR) -- the share of women who become mothers under current age-specific
rates. CPM (Children per Mother) is TFR / TFR1 -- average family size among
those who become mothers.
"""

import datetime
import pathlib
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
OUTPUT = "outputs/mdf_facet.html"

XLIM = (1950, datetime.date.today().year)
COUNTRIES_PER_ROW = 6
ROW_HEIGHT = 190
# Range tops set to TMR=100%/CPM,TFR=4 (rather than the data's actual max --
# TMR reaches 130%, CPM/TFR ~4.75 -- so a handful of peaks get clipped) so
# the two axes' default auto-ticks divide the same 0-1 fraction of the
# panel height and land on the same gridlines.
TMR_YRANGE = (0, 1.0)
COUNT_YRANGE = (0, 4)

TMR_COLOR = "#2a78d6"
CPM_COLOR = "#2a9d5c"
TFR_COLOR = "#8a8a8a"
# Matches plotly_white's default axis-title font (size/family/color), so the
# per-panel country titles read as part of the same system as the
# first-vs-second-birth facet grid.
LABEL_FONT = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")

# Same regions/countries as docs/hfd/first-vs-second-birth.md
# (country_names.COUNTRY_REGIONS) -- its UK_ONS placeholder (an ONS
# reconstruction reaching back to 1965) is used as-is here rather than also
# showing HFD's own GBR_NP series, which only starts in 2013.
MDF_REGIONS = COUNTRY_REGIONS


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


def make_facet(df, countries):
    """One Plotly figure with a dual-axis (TMR left, CPM/TFR right) subplot
    per country, COUNTRIES_PER_ROW countries per row, continuing onto
    further rows rather than behind per-region tabs -- same continuous-grid
    convention as cond_asfr_facet.py's first-vs-second-birth page."""
    rows_of_countries = [
        countries[i : i + COUNTRIES_PER_ROW] for i in range(0, len(countries), COUNTRIES_PER_ROW)
    ]
    nrows = len(rows_of_countries)
    ncols = COUNTRIES_PER_ROW

    # Country name only, no year range -- at COUNTRIES_PER_ROW=6 the column
    # width is too narrow for "Country (1950-2024)" without overlapping its
    # neighbour; the year range is still available in the hover tooltip.
    subplot_titles = []
    for row_countries in rows_of_countries:
        for code in row_countries:
            subplot_titles.append(f"<b>{country_title(code)}</b>")
        subplot_titles += [""] * (ncols - len(row_countries))

    specs = [[{"secondary_y": True} for _ in range(ncols)] for _ in range(nrows)]
    fig = make_subplots(
        rows=nrows, cols=ncols, specs=specs, subplot_titles=subplot_titles,
        horizontal_spacing=0.035, vertical_spacing=min(0.05, 1 / max(nrows - 1, 1)),
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT

    for row, row_countries in enumerate(rows_of_countries, start=1):
        for col, code in enumerate(row_countries, start=1):
            subset = df[df["code"] == code].sort_values("year")
            name = country_title(code, subset["year"].min(), subset["year"].max())
            is_first_panel = row == 1 and col == 1

            # CPM/TFR (children count) is the primary/left axis, TMR
            # (percent) the secondary/right axis -- swapped from a first
            # attempt at this chart so the count axis, which is easier to
            # read at a glance, sits on the left.
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["CPM"], mode="lines",
                    line=dict(width=1.6, color=CPM_COLOR), name="CPM", legendgroup="CPM",
                    showlegend=is_first_panel,
                    hovertemplate=f"{name}<br>CPM<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=row, col=col, secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["TFR"], mode="lines",
                    line=dict(width=1.6, color=TFR_COLOR), name="TFR", legendgroup="TFR",
                    showlegend=is_first_panel,
                    hovertemplate=f"{name}<br>TFR<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=row, col=col, secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["TMR"], mode="lines",
                    line=dict(width=1.6, color=TMR_COLOR), name="TMR", legendgroup="TMR",
                    showlegend=is_first_panel,
                    hovertemplate=f"{name}<br>TMR<br>%{{x}}<br>%{{y:.1%}}<extra></extra>",
                ),
                row=row, col=col, secondary_y=True,
            )

            fig.update_xaxes(range=list(XLIM), showticklabels=(row == nrows), row=row, col=col)
            # Default (auto) ticks on both axes -- ranges are set (see
            # COUNT_YRANGE/TMR_YRANGE above) so they land on the same
            # gridlines rather than needing explicit tickvals.
            fig.update_yaxes(
                range=list(COUNT_YRANGE), showticklabels=(col == 1),
                row=row, col=col, secondary_y=False,
            )
            # Right-axis tick labels only on the last country of each row (its
            # actual last column, since the final row isn't always full), to
            # avoid every panel repeating them -- the left axis's tick labels
            # are already deduped to the first column above.
            fig.update_yaxes(
                range=list(TMR_YRANGE), tickformat=".0%", showgrid=False,
                showticklabels=(col == len(row_countries)),
                row=row, col=col, secondary_y=True,
            )

    # Link every panel's x-axis to the first one so dragging to zoom/pan on
    # any single country pans/zooms the whole grid together, rather than
    # each of the 25+ panels zooming independently.
    fig.update_xaxes(matches="x")

    fig.update_layout(
        title=dict(text="TMR, CPM and TFR vs year, by country", y=0.99, yanchor="top"),
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 90,
        margin=dict(t=90, b=40),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.02, yanchor="bottom"),
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    all_countries = [code for codes in MDF_REGIONS.values() for code in codes]
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
    print(f"Saved {OUTPUT} (height={fig.layout.height}px)")
