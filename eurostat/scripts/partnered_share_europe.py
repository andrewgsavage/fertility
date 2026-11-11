"""Share of people aged 25-49 living in a couple household, by country, 2006 onward.

Eurostat lfst_hhindws (EU-LFS population by sex, age, household composition).
Share = couple households (A_CPL, with or without children) / all persons (TOTAL), age Y25-49, both sexes.

Input (download into eurostat/data/ - not tracked in git):
  lfst_hhindws_pop.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/A.F+M+T...THS_PER.POP.?format=SDMX-CSV
"""

import pathlib
import shutil

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "partnered_share_europe.html"
DOCS = _SCRIPT_DIR.parent.parent / "docs" / "_static" / "eurostat" / "partnered_share_europe.html"

NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium", "BG": "Bulgaria",
    "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
    "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland", "FR": "France", "HR": "Croatia",
    "HU": "Hungary", "IE": "Ireland", "IS": "Iceland", "IT": "Italy", "LT": "Lithuania",
    "LU": "Luxembourg", "LV": "Latvia", "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta",
    "NL": "Netherlands", "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey",
    "UK": "United Kingdom", "EU27_2020": "EU27",
}
SHOWN = ["EU27", "France", "Germany", "Italy", "Spain", "Poland", "Czechia", "Finland", "Netherlands"]


def load():
    x = pd.read_csv(DATA / "lfst_hhindws_pop.csv")
    x = x[(x.age == "Y25-49") & (x.sex == "T") & x.phhcomp.isin(["A_CPL", "TOTAL"]) & x.geo.isin(NAMES)]
    p = x.pivot_table(index=["geo", "TIME_PERIOD"], columns="phhcomp", values="OBS_VALUE").reset_index()
    p["share"] = 100 * p.A_CPL / p.TOTAL
    p["country"] = p.geo.map(NAMES)
    return p.rename(columns={"TIME_PERIOD": "year"})[["country", "year", "share"]].dropna()


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        x = d[d.country == c].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.share, mode="lines", name=c,
            line=dict(color=colors[i % len(colors)], width=3 if c == "EU27" else 1.5),
            visible=True if c in SHOWN else "legendonly",
            hovertemplate=c + " %{x}: %{y:.1f}%<extra></extra>"))
    fig.update_yaxes(title_text="% of people aged 25-49", ticksuffix="%", rangemode="tozero")
    fig.update_layout(template="plotly_white",
                      title="People aged 25-49 living in a couple household (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=150, t=60), hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    fig = plot(d)
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    DOCS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(OUTPUT, DOCS)
    print(f"Saved {OUTPUT}")
    t = d[d.year.isin([2006, 2010, 2015, 2024])].pivot(index="country", columns="year", values="share").round(1)
    print(t.reindex(SHOWN).to_string())
