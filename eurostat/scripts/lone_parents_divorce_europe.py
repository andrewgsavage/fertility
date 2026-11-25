"""Lone mothers and fathers aged 25-49, and the crude divorce rate, by European country.

1. Lone-parent share: persons aged 25-49 living as the single adult in a household with
   children (phhcomp A1_CH), as a % of all persons aged 25-49 living in a household with
   children (A_CH = single adult + couple + other households with children). EU Labour Force
   Survey (lfst_hhindws), 2006-2025. Children are under 15, or 15-24 and economically inactive
   and living with a parent. Lone parents include never-partnered parents as well as those who
   separated. The EU-LFS household data has a methodology break in 2021, so lines are split
   there (Sweden, Slovenia and Greece drop by half or more at the break).
2. Crude divorce rate: divorces per 1,000 population (demo_ndivind, GDIVRT). Divorces end
   legal marriages only; a fall can mean fewer marriages to dissolve as well as more stable ones.

Inputs (download into eurostat/data/ - not tracked in git):
  lfst_hhindws_lone.csv
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/A.F+M.Y25-49.A1_CH+A_CPL_CH+A_OTH_CH+A_CH+TOTAL.THS_PER.POP.?format=SDMX-CSV
  demo_ndivind.csv
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_ndivind/?format=SDMX-CSV
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("eurostat")
OUTDIR = outputs_dir("eurostat")

NAMES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "EU27_2020": "EU27", "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland", "PT": "Portugal",
    "RO": "Romania", "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia",
    "TR": "Turkey", "UK": "United Kingdom",
}
SHOWN = ["EU27", "Germany", "France", "Italy", "Spain", "Poland", "Netherlands", "Lithuania",
         "Ireland", "United Kingdom"]
SEXES = {"F": "Women", "M": "Men"}
BREAK = 2021


def load_lone():
    h = pd.read_csv(DATA / "lfst_hhindws_lone.csv")
    h = h.pivot_table(index=["sex", "geo", "TIME_PERIOD"], columns="phhcomp", values="OBS_VALUE").reset_index()
    h["lone"] = 100 * h.A1_CH / h.A_CH
    h["country"] = h.geo.map(NAMES)
    h["sex"] = h.sex.map(SEXES)
    h = h.dropna(subset=["country", "lone", "sex"]).rename(columns={"TIME_PERIOD": "year"})
    return h[["country", "geo", "sex", "year", "lone"]]


def load_divorce():
    d = pd.read_csv(DATA / "demo_ndivind.csv")
    d = d[d.indic_de == "GDIVRT"]
    d = d.assign(country=d.geo.map(NAMES)).dropna(subset=["country", "OBS_VALUE"])
    return d.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "divorce_rate"})[
        ["country", "geo", "year", "divorce_rate"]]


def split_at_break(x, col):
    """Insert a gap between BREAK-1 and BREAK so the line doesn't join across the LFS break."""
    gap = pd.DataFrame({"year": [BREAK - 0.5], col: [float("nan")]})
    return pd.concat([x[x.year < BREAK], gap, x[x.year >= BREAK]])[["year", col]]


def order(countries):
    return [c for c in SHOWN if c in countries] + sorted(set(countries) - set(SHOWN))


def plot_lone(h):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=[
        "Lone mothers (% of women 25-49 living with children)",
        "Lone fathers (% of men 25-49 living with children)"])
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order(set(h.country))):
        for j, sex in enumerate(SEXES.values(), start=1):
            x = split_at_break(h[(h.country == c) & (h.sex == sex)].sort_values("year"), "lone")
            fig.add_trace(go.Scatter(
                x=x.year, y=x.lone, mode="lines", name=c, legendgroup=c, showlegend=j == 1,
                line=dict(color=colors[i % len(colors)], width=1.8), connectgaps=False,
                visible=True if c in SHOWN else "legendonly",
                hovertemplate=f"{c}, {sex.lower()} 25-49, %{{x}}: %{{y:.1f}}%<extra></extra>"), row=1, col=j)
    fig.add_vline(x=BREAK - 0.5, line=dict(color="grey", dash="dot", width=1))
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_layout(template="plotly_white", title="Lone parents aged 25-49 (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=170, t=80), hovermode="closest")
    return fig


def plot_divorce(d):
    fig = go.Figure()
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order(set(d.country))):
        x = d[(d.country == c) & (d.year >= 1990)].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.divorce_rate, mode="lines", name=c, line=dict(color=colors[i % len(colors)], width=1.8),
            visible=True if c in SHOWN else "legendonly",
            hovertemplate=f"{c}, %{{x}}: %{{y:.1f}} per 1,000<extra></extra>"))
    fig.update_yaxes(title_text="Divorces per 1,000 population", rangemode="tozero")
    fig.update_layout(template="plotly_white", title="Crude divorce rate (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=170, t=80), hovermode="closest")
    return fig


if __name__ == "__main__":
    h = load_lone()
    d = load_divorce()
    h.round(2).to_csv(OUTDIR / "lone_parents_europe.csv", index=False)
    d.to_csv(OUTDIR / "divorce_rate_europe.csv", index=False)
    write_html(plot_lone(h), OUTDIR / "lone_parents_europe.html")
    write_html(plot_divorce(d), OUTDIR / "divorce_rate_europe.html")
    w = h[h.sex == "Women"].pivot_table(index="country", columns="year", values="lone")
    print(w[[2010, 2019, 2021, 2025]].round(1).to_string())
    print(d.pivot_table(index="country", columns="year", values="divorce_rate")[[2000, 2010, 2019, 2023]].to_string())
