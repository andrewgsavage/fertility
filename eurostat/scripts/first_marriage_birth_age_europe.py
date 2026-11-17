"""Mean age at first marriage (women) and mean age of mothers at first birth, by country.

Eurostat demo_nind (FAGEMAR1) and demo_find (AGEMOTH1). Solid line = first marriage, dotted = first birth.

Inputs (download into eurostat/data/ - not tracked in git):
  demo_nind.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_nind/?format=SDMX-CSV
  demo_find_all.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_find/?format=SDMX-CSV
"""

import pathlib
import shutil

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "first_marriage_birth_age_europe.html"
DOCS = _SCRIPT_DIR.parent.parent / "docs" / "_static" / "eurostat" / "first_marriage_birth_age_europe.html"

NAMES = {
    "AL": "Albania", "AM": "Armenia", "AT": "Austria", "AZ": "Azerbaijan", "BE": "Belgium",
    "BG": "Bulgaria", "BY": "Belarus", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "GE": "Georgia", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IS": "Iceland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "MD": "Moldova",
    "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "RU": "Russia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UA": "Ukraine",
}
SHOWN = ["France", "Germany", "Italy", "Spain", "Sweden", "Poland", "Czechia"]


def load():
    n = pd.read_csv(DATA / "demo_nind.csv")
    f = pd.read_csv(DATA / "demo_find_all.csv")
    m = n[n.indic_de == "FAGEMAR1"][["geo", "TIME_PERIOD", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "marriage"})
    b = f[f.indic_de == "AGEMOTH1"][["geo", "TIME_PERIOD", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "birth"})
    d = m.merge(b, on=["geo", "TIME_PERIOD"], how="outer").rename(columns={"TIME_PERIOD": "year"})
    d = d[d.geo.isin(NAMES)]
    d["country"] = d.geo.map(NAMES)
    return d[["country", "year", "marriage", "birth"]]


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        col = colors[i % len(colors)]
        vis = True if c in SHOWN else "legendonly"
        x = d[d.country == c].sort_values("year")
        xm, xb = x.dropna(subset=["marriage"]), x.dropna(subset=["birth"])
        fig.add_trace(go.Scatter(x=xm.year, y=xm.marriage, mode="lines+markers", name=c, legendgroup=c,
                                 line=dict(color=col, width=2), marker=dict(size=4), visible=vis,
                                 hovertemplate=c + " first marriage %{x}: %{y:.1f}<extra></extra>"))
        fig.add_trace(go.Scatter(x=xb.year, y=xb.birth, mode="lines+markers", name=c + " (first birth)",
                                 legendgroup=c, showlegend=False, line=dict(color=col, width=2, dash="dot"),
                                 marker=dict(size=4), visible=vis,
                                 hovertemplate=c + " first birth %{x}: %{y:.1f}<extra></extra>"))
    fig.update_yaxes(title_text="Mean age, years")
    fig.update_layout(template="plotly_white",
                      title="Mean age at first marriage (women, solid) and first birth (dotted)",
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
    rows = SHOWN + ["Finland", "Hungary", "Netherlands"]
    for y in (1990, 2000, 2010, 2020, 2023):
        print(y)
        print(d[d.year == y].set_index("country").drop(columns="year").round(1).reindex(rows).to_string())
