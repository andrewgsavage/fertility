"""NEET rate of 15-29-year-olds by sex, by country, 2003-2025.

Eurostat lfsi_neet_a (young people neither in employment nor in education and
training, % of population). Download into eurostat/data/ (not tracked in git):
  lfsi_neet_a.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfsi_neet_a?format=SDMX-CSV
Use the dropdown to switch between men, women and the gap.
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

from _common import DATA, NAMES, write_html

SHOWN = ["Spain", "Italy", "France", "Germany", "Poland", "Sweden", "Finland", "Netherlands"]
VIEWS = [("M", "Men", "%"), ("F", "Women", "%"), ("gap", "Men minus women (pp)", " pp")]


def load():
    d = pd.read_csv(DATA / "lfsi_neet_a.csv")
    d = d[(d.age == "Y15-29") & (d.unit == "PC_POP") & d.sex.isin(["F", "M"]) & d.geo.isin(NAMES)]
    w = d.pivot_table(index=["geo", "TIME_PERIOD"], columns="sex", values="OBS_VALUE").dropna().reset_index()
    w["gap"] = w.M - w.F
    w["country"] = w.geo.map(NAMES)
    return w.rename(columns={"TIME_PERIOD": "year"})


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for v, (col, label, unit) in enumerate(VIEWS):
        for i, c in enumerate(order):
            x = d[d.country == c].sort_values("year")
            fig.add_trace(go.Scatter(
                x=x.year, y=x[col], mode="lines", name=c, legendgroup=c,
                showlegend=(v == 0),
                line=dict(color=colors[i % len(colors)], width=1.5),
                visible=(True if c in SHOWN else "legendonly") if v == 0 else False,
                hovertemplate=c + " %{x}: %{y:.1f}" + unit + "<extra></extra>",
            ))
    n = len(order)
    buttons = [
        dict(label=label, method="update",
             args=[{"visible": [(True if order[j % n] in SHOWN else "legendonly") if j // n == v else False
                                for j in range(n * len(VIEWS))]},
                   {"yaxis.title.text": ("% of men aged 15-29", "% of women aged 15-29", "Men minus women, percentage points")[v]}])
        for v, (_, label, _) in enumerate(VIEWS)
    ]
    fig.update_yaxes(title_text="% of men aged 15-29")
    fig.update_layout(
        template="plotly_white",
        title="NEET rate, ages 15-29 (click names to add countries)",
        updatemenus=[dict(type="buttons", direction="right", buttons=buttons, x=0, y=1.12, xanchor="left")],
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(r=150, t=90),
        hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    write_html(plot(load()), "neet_by_sex_europe.html")
