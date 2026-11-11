"""Tertiary attainment among 25-34-year-olds: women minus men, by country, 1992-2025.

Eurostat edat_lfse_03 (population by educational attainment, % of age group,
ISCED 2011 levels 5-8, ages 25-34). Download into eurostat/data/ (not tracked in git):
  edat_lfse_03.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/edat_lfse_03/A..Y25-34.PC.ED5-8.?format=SDMX-CSV
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

from _common import DATA, NAMES, write_html

SHOWN = ["Spain", "Italy", "France", "Germany", "Poland", "Sweden", "Finland", "Netherlands"]


def load():
    d = pd.read_csv(DATA / "edat_lfse_03.csv")
    d = d[d.sex.isin(["F", "M"]) & d.geo.isin(NAMES)]
    w = d.pivot_table(index=["geo", "TIME_PERIOD"], columns="sex", values="OBS_VALUE").dropna().reset_index()
    w["gap"] = w.F - w.M
    w["country"] = w.geo.map(NAMES)
    return w.rename(columns={"TIME_PERIOD": "year"})


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        x = d[d.country == c].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.gap, mode="lines", name=c,
            line=dict(color=colors[i % len(colors)], width=1.5),
            visible=True if c in SHOWN else "legendonly",
            customdata=x[["F", "M"]],
            hovertemplate=c + " %{x}: %{y:+.1f} pp (women %{customdata[0]:.1f}%, men %{customdata[1]:.1f}%)<extra></extra>",
        ))
    fig.add_hline(y=0, line=dict(color="grey", width=1))
    fig.update_yaxes(title_text="Women minus men, percentage points", zeroline=False)
    fig.update_layout(
        template="plotly_white",
        title="Tertiary-educated share of 25-34s: women minus men (click names to add countries)",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(r=150, t=60),
        hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    write_html(plot(load()), "tertiary_gender_gap_europe.html")
