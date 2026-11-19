"""Coupling-rate series from the FT's "The relationship recession is going global"
(John Burn-Murdoch, 11 January 2025), read out of the article's Flourish chart embeds.

Input (not tracked in git): save the article page from a browser ("Save page as,
complete") and copy the chart embeds from its _files folder into FT/data/:
  embed(2).html -> coupling_regions.html    % of 25-34s married or cohabiting, 44 countries
  embed(1).html -> coupling_education.html  % of 25-34s in couples, UK and US, by degree
  embed.html    -> us_counterfactual.html   US TFR change split into fewer couples / fewer births per couple

Outputs: FT/outputs/ft_coupling_25_34.html, ft_coupling_education.html and the
extracted series as CSV.
"""

import json
import pathlib
import re

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"

# Shown by default; the rest start hidden in the legend.
SHOWN = ["US", "UK", "France", "Spain", "Finland", "S Korea", "Japan", "Mexico", "Türkiye", "Thailand"]


def flourish(path):
    """Return a long DataFrame from a Flourish embed's _Flourish_data block."""
    h = path.read_text(encoding="utf-8", errors="replace")
    h = re.sub(r"new Date\((-?\d+)\)", lambda m: str(pd.Timestamp(int(m.group(1)), unit="ms").year), h)

    def grab(name):
        m = re.search(r"\b" + name + r"\s*=\s*(?=[\[{])", h)
        return json.JSONDecoder().raw_decode(h, m.end())[0]

    cols = grab("_Flourish_data_column_names")["data"]
    rows = []
    for r in grab("_Flourish_data")["data"]:
        for s, v in zip(cols["value"], r["value"]):
            if v not in (None, ""):
                rows.append({"facet": r["facet"], "year": int(r["label"]), "series": s, "value": float(v)})
    return pd.DataFrame(rows)


def plot_countries(d):
    d = d[~d.series.isin(["Region average", "Individual country"])]
    fig = go.Figure()
    colors = pc.qualitative.Dark24
    regions = list(dict.fromkeys(d.facet))
    i = 0
    for reg in regions:
        for c in sorted(d[d.facet == reg].series.unique()):
            x = d[(d.facet == reg) & (d.series == c)].sort_values("year")
            fig.add_trace(go.Scatter(
                x=x.year, y=x.value, mode="lines", name=c,
                legendgroup=reg, legendgrouptitle_text=reg,
                line=dict(color=colors[i % len(colors)], width=2 if c in SHOWN else 1.5),
                visible=True if c in SHOWN else "legendonly",
                hovertemplate=c + " %{x}: %{y:.1f}%<extra></extra>"))
            i += 1
    fig.update_yaxes(title_text="% of 25-34s married or cohabiting", ticksuffix="%")
    fig.update_layout(template="plotly_white",
                      title="People aged 25-34 who are married or cohabiting (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top", groupclick="toggleitem"),
                      margin=dict(r=170, t=60), hovermode="closest")
    return fig


def plot_education(d):
    d = d[d.series.isin(["Degree or higher", "Below degree"])]
    fig = make_subplots(rows=1, cols=2, subplot_titles=["UK", "US"], shared_yaxes=True)
    colors = {"Degree or higher": "#1f77b4", "Below degree": "#d62728"}
    for j, c in enumerate(["UK", "US"], start=1):
        for s, col in colors.items():
            x = d[(d.facet == c) & (d.series == s)].sort_values("year")
            fig.add_trace(go.Scatter(x=x.year, y=x.value, mode="lines", name=s, legendgroup=s,
                                     showlegend=j == 1, line=dict(color=col),
                                     hovertemplate=f"{c} {s} %{{x}}: %{{y:.1f}}%<extra></extra>"),
                          row=1, col=j)
    fig.update_yaxes(title_text="% of 25-34s in a couple", ticksuffix="%", row=1, col=1)
    fig.update_layout(template="plotly_white", title="People aged 25-34 in a couple, by education",
                      legend=dict(orientation="h", y=-0.12), margin=dict(t=80), hovermode="closest")
    return fig


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    countries = flourish(DATA / "coupling_regions.html").rename(columns={"facet": "region", "series": "country"})
    education = flourish(DATA / "coupling_education.html").rename(columns={"facet": "country"})
    # The US panel uses short series names.
    education["series"] = education.series.replace({"D o H": "Degree or higher", "No c": "Below degree"})
    us = flourish(DATA / "us_counterfactual.html").rename(columns={"facet": "period"})
    # The two US series are stacked components of the TFR change since the period's first year.
    us["series"] = us.series.map({"Counterfactual": "fewer births among couples", "Actual": "fewer couples"})
    countries.to_csv(OUTDIR / "ft_coupling_25_34.csv", index=False)
    education.to_csv(OUTDIR / "ft_coupling_education.csv", index=False)
    us.to_csv(OUTDIR / "ft_us_tfr_decomposition.csv", index=False)
    write_html(plot_countries(countries.rename(columns={"region": "facet", "country": "series"})),
               OUTDIR / "ft_coupling_25_34.html")
    write_html(plot_education(education.rename(columns={"country": "facet"})), OUTDIR / "ft_coupling_education.html")
    print(us[us.year.isin([1980, 2022])].to_string())
