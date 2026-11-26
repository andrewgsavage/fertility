"""Redraw the charts in the FT's "Why birth rates are falling everywhere all at once"
(John Burn-Murdoch, 16 May 2026) from their own data.

Input: FT/outputs/ft_birth_rates_everywhere.csv (ft_birth_rates_everywhere.py).
Output: FT/outputs/ft_br_<chart>.html, one per FT chart.

Differences from the FT: charts the FT drew with two y-axes (children per mother vs
share of women who are mothers) are split into two rows instead. Flourish helper series
are folded in: `cr`/`tfr` and `D o H`/`No c` are unlabelled copies of the labelled series
in other facets, and `lo`/`hi` in the socialising chart only set its y-axis range.
"""

import textwrap

import plotly.colors as pc
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from common.paths import outputs_dir
from common.plotting import write_html

OUT = outputs_dir("FT")
INPUT = OUT / "ft_birth_rates_everywhere.csv"

PALETTE = pc.qualitative.D3
GREY = "rgba(140,140,140,0.45)"
LAYOUT = dict(template="plotly_white", margin=dict(l=60, r=20, t=110, b=60), hovermode="x unified",
              legend=dict(orientation="h", y=-0.15))
ALIASES = {"cr": "Coupling rate", "tfr": "TFR", "D o H": "Degree or higher", "No c": "Below degree"}


def colors(names):
    return {n: PALETTE[i % len(PALETTE)] for i, n in enumerate(names)}


def lines(d, title, ytitle, xtitle=None, order=None, dash=None):
    """One line per series, no facets."""
    order = order or list(dict.fromkeys(d.series))
    col = colors(order)
    fig = go.Figure()
    for s in order:
        x = d[d.series == s].sort_values("year")
        fig.add_trace(go.Scatter(x=x.year, y=x.value, mode="lines", name=s,
                                 line=dict(color=col[s], width=2, dash=(dash or {}).get(s))))
    fig.update_layout(title=title, yaxis_title=ytitle, xaxis_title=xtitle, **LAYOUT)
    return fig


def facets(d, title, ytitle, cols, order=None, shared_y=True, height=None, highlight=None, ranges=None,
           mode="lines"):
    """Small multiples by facet, one colour per series shared across facets."""
    names = list(dict.fromkeys(d.facet))
    series = order or list(dict.fromkeys(d.series))
    col = colors(series)
    rows = -(-len(names) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=names, shared_yaxes=shared_y,
                        horizontal_spacing=0.06 if shared_y else 0.09, vertical_spacing=0.12)
    for i, f in enumerate(names):
        r, c = divmod(i, cols)
        for s in series:
            x = d[(d.facet == f) & (d.series == s)].sort_values("year")
            if x.empty:
                continue
            color, width = col[s], 2
            if highlight is not None and s != highlight:
                color, width = GREY, 1.2
            fig.add_trace(go.Scatter(x=x.year, y=x.value, mode=mode, name=s, legendgroup=s,
                                     showlegend=i == 0 or s not in fig_names(fig),
                                     line=dict(color=color, width=width), marker=dict(size=8)),
                          row=r + 1, col=c + 1)
        if ranges and f in ranges:
            fig.update_yaxes(range=ranges[f], row=r + 1, col=c + 1)
    fig.update_layout(title=title, height=height or 300 * rows + 120, **LAYOUT)
    fig.update_yaxes(title_text=ytitle, col=1)
    return fig


def fig_names(fig):
    return {t.name for t in fig.data}


def coupling(d):
    """Six regions: grey country lines, coloured region average, as the FT."""
    d = d[d.series != "Individual country"]
    regions = list(dict.fromkeys(d.facet))
    fig = make_subplots(rows=2, cols=3, subplot_titles=regions, shared_yaxes=True, shared_xaxes="all",
                        horizontal_spacing=0.05, vertical_spacing=0.12)
    for i, reg in enumerate(regions):
        r, c = divmod(i, 3)
        g = d[d.facet == reg]
        for s in sorted(g.series.unique()):
            x = g[g.series == s].sort_values("year")
            avg = s == "Region average"
            fig.add_trace(go.Scatter(x=x.year, y=x.value, mode="lines",
                                     name="Region average" if avg else "Individual country",
                                     legendgroup="avg" if avg else "country", showlegend=i == 0 and s in (
                                         "Region average", sorted(set(g.series) - {"Region average"})[0]),
                                     line=dict(color="#c0392b" if avg else GREY, width=3 if avg else 1.2),
                                     hovertemplate=f"{s}: %{{y:.0f}}%<extra></extra>"),
                          row=r + 1, col=c + 1)
    fig.update_layout(title="Relationship rates among young adults are declining around the world",
                      height=720, **{**LAYOUT, "hovermode": "closest"})
    fig.update_yaxes(title_text="% of 25–34s married or cohabiting", col=1)
    return fig


def children_per_mother(d):
    countries = list(dict.fromkeys(d.facet))
    rows = {"Children per mother (left axis)": "Children per mother",
            "Share of women who have children (right axis)": "% of women who have children"}
    fig = make_subplots(rows=2, cols=len(countries), subplot_titles=countries, shared_yaxes=True,
                        horizontal_spacing=0.04, vertical_spacing=0.1)
    col = colors(list(rows.values()))
    for r, (s, label) in enumerate(rows.items()):
        for c, f in enumerate(countries):
            x = d[(d.facet == f) & (d.series == s)].sort_values("year")
            fig.add_trace(go.Scatter(x=x.year, y=x.value, mode="lines", name=label, legendgroup=label,
                                     showlegend=c == 0, line=dict(color=col[label], width=2)),
                          row=r + 1, col=c + 1)
        fig.update_yaxes(title_text=label, row=r + 1, col=1)
    fig.update_layout(title="The number of children per mother has stabilised. But fewer women are becoming mothers",
                      height=620, **LAYOUT)
    return fig


def main():
    d = pd.read_csv(INPUT)
    d["series"] = d.series.replace(ALIASES)
    c = {k: g for k, g in d.groupby("chart")}
    charts = {
        "tfr_by_region": lines(c["tfr_by_region"],
                               "Birth rates have steeply declined in the past 15 years across different cultures and levels of economic development",
                               "Children per woman"),
        "mexico_vs_us": lines(c["mexico_vs_us"], "Mexico now has a lower birth rate than America",
                              "Children per woman"),
        "japan_productivity": facets(c["japan_productivity"],
                                     "Japan’s working-age population is as productive as ever but shrinking",
                                     "1995 = 100", cols=3, shared_y=False, highlight="Japan", height=440),
        "ideal_vs_actual": facets(c["ideal_vs_actual"],
                                  "There is a widening gap between the number of children people would like and the number they have",
                                  "Children per woman", cols=4, mode="lines+markers", height=420),
        "coupling_25_34": coupling(c["coupling_25_34"]),
        "children_per_mother": children_per_mother(c["children_per_mother"]),
        "coupling_by_education": facets(c["coupling_by_education"],
                                        "The decline of long-term relationships has been steepest among people without a degree",
                                        "% of 25–34s in couples", cols=2, height=420),
        "coupling_vs_tfr": facets(c["coupling_vs_tfr"], "Fewer couples mean fewer children", "2010 = 100",
                                  cols=4, height=620),
        "earnings_gap": facets(c["earnings_gap"],
                               "Young women in the bottom half of the income distribution are rapidly gaining on men",
                               "Women’s earnings as % of men’s, ages 24–28", cols=2, height=420),
        "smartphone_tfr_calendar": lines(c["smartphone_tfr_slide3"], "Could digital media be affecting birth rates?",
                                         "Total fertility rate"),
        "smartphone_tfr_aligned": lines(c["smartphone_tfr_aligned"],
                                        "Total fertility rate, by years before/since smartphones",
                                        "Total fertility rate", xtitle="Years since smartphone take-off"),
        "smartphone_tfr_vs_trend": lines(c["smartphone_tfr_vs_trend"],
                                         "% change in TFR relative to pre-smartphone trend",
                                         "% vs pre-smartphone trend", xtitle="Years since smartphone take-off"),
        "left_right_by_sex": facets(c["left_right_by_sex"],
                                    "An ideological divide has opened up between young men and women who didn’t go to university",
                                    "Left–right placement, under-30s (0 = left)", cols=2, height=420),
    }
    soc = c["socialising"]
    ranges = {f: [g[g.series == "lo"].value.iloc[0], g[g.series == "hi"].value.iloc[0]]
              for f, g in soc.groupby("facet")}
    charts["socialising"] = facets(soc[soc.series == "smooth"].assign(series="Smoothed"),
                                   "Young people are socialising much less than in the past", None, cols=2,
                                   shared_y=False, ranges=ranges, height=620)
    for fig in charts.values():
        fig.update_layout(showlegend=len(fig_names(fig)) > 1,
                          title_text="<br>".join(textwrap.wrap(fig.layout.title.text, 70)))
    for name, fig in charts.items():
        write_html(fig, OUT / f"ft_br_{name}.html")


if __name__ == "__main__":
    main()
