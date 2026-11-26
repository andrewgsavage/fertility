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

Uruguay is not in HFD. Its panel uses HFC's Latin American Fertility Database
TFR and TFR1 (1978-1988, 1993, 1996-2011) plus the 2013 and 2021 estimates from
HFC/scripts/uruguay_by_order.py (HFC/outputs/ury_tfr_by_order.csv). Missing years
are left as gaps, so the two estimate years show as isolated markers.
"""

import datetime

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.country_names import COUNTRY_REGIONS, country_title
from common.hfd import read_hfd
from common.ons_mdf import load_period_metrics as load_uk_ons_metrics
from common.paths import outputs_dir
from common.plotting import write_html

OUTPUT = outputs_dir("HFD") / "mdf_facet.html"
URY_CODE = "URY_HFC"
URY_CSV = outputs_dir("HFC") / "ury_tfr_by_order.csv"
EXTRA_NAMES = {URY_CODE: "Uruguay, HFC"}

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
    df = read_hfd(
        "tfrRRbo.txt",
        [
            "code", "year", "TFR", "TFR1", "TFR2", "TFR3", "TFR4", "TFR5p",
            "TFR40", "TFR40_1", "TFR40_2", "TFR40_3", "TFR40_4", "TFR40_5p",
        ],
        engine="python",
    )
    df = df.dropna(subset=["TFR", "TFR1"])
    df["TMR"] = df["TFR1"]
    df["CPM"] = df["TFR"] / df["TFR1"]
    df = df[["code", "year", "TFR", "TMR", "CPM"]]

    uk_ons = load_uk_ons_metrics()
    uk_ons_df = pd.DataFrame(
        [{"code": "UK_ONS", "year": year, "TMR": tmr, "CPM": cpm, "TFR": tfr} for year, (tmr, cpm, tfr) in uk_ons.items()],
    )

    ury = pd.read_csv(URY_CSV).set_index("year")
    ury = ury.reindex(range(ury.index.min(), ury.index.max() + 1)).rename_axis("year").reset_index()
    ury_df = pd.DataFrame({"code": URY_CODE, "year": ury["year"], "TFR": ury["TFR"], "TMR": ury["TFR1"],
                           "CPM": ury["TFR"] / ury["TFR1"]})

    return pd.concat([df, uk_ons_df, ury_df], ignore_index=True).sort_values(["code", "year"])


def _name(code, *years):
    return country_title(EXTRA_NAMES.get(code, code), *years)


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
            subplot_titles.append(f"<b>{_name(code)}</b>")
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
            name = _name(code, subset["year"].min(), subset["year"].max())
            # Uruguay's series has gaps and two isolated estimate years: markers keep them visible.
            mode = "lines+markers" if code in EXTRA_NAMES else "lines"
            is_first_panel = row == 1 and col == 1

            # CPM/TFR (children count) is the primary/left axis, TMR
            # (percent) the secondary/right axis -- swapped from a first
            # attempt at this chart so the count axis, which is easier to
            # read at a glance, sits on the left.
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["CPM"], mode=mode, marker=dict(size=3),
                    line=dict(width=1.6, color=CPM_COLOR), name="CPM", legendgroup="CPM",
                    showlegend=is_first_panel,
                    hovertemplate=f"{name}<br>CPM<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=row, col=col, secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["TFR"], mode=mode, marker=dict(size=3),
                    line=dict(width=1.6, color=TFR_COLOR), name="TFR", legendgroup="TFR",
                    showlegend=is_first_panel,
                    hovertemplate=f"{name}<br>TFR<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                ),
                row=row, col=col, secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(
                    x=subset["year"], y=subset["TMR"], mode=mode, marker=dict(size=3),
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
    all_countries.insert(all_countries.index("CHL") + 1, URY_CODE)
    fig = make_facet(df, all_countries)

    write_html(fig, OUTPUT, height=f"{fig.layout.height}px", log=False)
    print(f"Saved {OUTPUT} (height={fig.layout.height}px)")
