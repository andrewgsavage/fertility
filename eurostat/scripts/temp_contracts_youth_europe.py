"""Temporary employees as a share of employees aged 15-29, by country, 1995-2025.

Eurostat lfsa_etpgan (temporary employees as % of total employees, by age and
citizenship; citizen=TOTAL). Download into eurostat/data/ (not tracked in git):
  lfsa_etpgan.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfsa_etpgan/A.PC.T..TOTAL.?format=SDMX-CSV
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

from _common import DATA, NAMES, write_html

SHOWN = ["Spain", "Italy", "France", "Germany", "Netherlands", "Poland", "Portugal", "Sweden"]


def load():
    d = pd.read_csv(DATA / "lfsa_etpgan.csv")
    d = d[(d.age == "Y15-29") & d.geo.isin(NAMES)].dropna(subset=["OBS_VALUE"])
    d["country"] = d.geo.map(NAMES)
    return d.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "share"})[["country", "year", "share"]]


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        x = d[d.country == c].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.share, mode="lines", name=c,
            line=dict(color=colors[i % len(colors)], width=1.5),
            visible=True if c in SHOWN else "legendonly",
            hovertemplate=c + " %{x}: %{y:.1f}%<extra></extra>",
        ))
    fig.update_yaxes(title_text="% of employees aged 15-29", ticksuffix="%", rangemode="tozero")
    fig.update_layout(
        template="plotly_white",
        title="Temporary employees as a share of employees aged 15-29 (click names to add countries)",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(r=150, t=60),
        hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    write_html(plot(load()), "temp_contracts_youth_europe.html")
