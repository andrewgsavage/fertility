"""Share of adults living in a couple household, next to mean age at first birth, by country.

Left panel: persons aged 25-49 in couple households (married or cohabiting, with or without
children) as a share of all persons aged 25-49, EU Labour Force Survey (lfst_hhindws),
2006-2025. Right panel: mean age of mother at first birth (demo_find, AGEMOTH1).

Inputs (download into eurostat/data/ - not tracked in git):
  lfst_hhindws_couples.csv        https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/A..Y25-49+Y18-24.A_CPL+A1+TOTAL.THS_PER.POP.?format=SDMX-CSV
  demo_find_firstbirth_age.csv    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_find/A.AGEMOTH1.?format=SDMX-CSV
"""

import pathlib

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "couples_firstbirth_age_europe.html"

NAMES = {
    "AT": "Austria", "BA": "Bosnia & Herzegovina", "BE": "Belgium", "BG": "Bulgaria", "CY": "Cyprus",
    "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "EU27_2020": "EU27", "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UK": "United Kingdom",
}
SHOWN = ["EU27", "Italy", "Spain", "Germany", "France", "Sweden", "Poland", "Finland", "United Kingdom"]


def load(age="Y25-49"):
    h = pd.read_csv(DATA / "lfst_hhindws_couples.csv")
    h = h[(h.sex == "T") & (h.age == age)]
    h = h.pivot_table(index=["geo", "TIME_PERIOD"], columns="phhcomp", values="OBS_VALUE").reset_index()
    h["couple"] = 100 * h.A_CPL / h.TOTAL
    h["country"] = h.geo.map(NAMES)
    h = h.dropna(subset=["country", "couple"]).rename(columns={"TIME_PERIOD": "year"})
    b = pd.read_csv(DATA / "demo_find_firstbirth_age.csv")
    b = b.assign(country=b.geo.map(NAMES)).dropna(subset=["country"])
    b = b.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "age"})[["country", "year", "age"]]
    return h[["country", "year", "couple"]], b


def plot(h, b):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08, subplot_titles=(
        "Aged 25-49 living in a couple household", "Mean age at first birth"))
    colors = pc.qualitative.Dark24
    order = SHOWN + sorted((set(h.country) | set(b.country)) - set(SHOWN))
    for i, c in enumerate(order):
        vis = True if c in SHOWN else "legendonly"
        col = colors[i % len(colors)]
        for j, (d, ycol, fmt) in enumerate([(h, "couple", "%{y:.1f}%"), (b, "age", "%{y:.1f}")]):
            x = d[d.country == c].sort_values("year")
            if x.empty:
                continue
            fig.add_trace(go.Scatter(
                x=x.year, y=x[ycol], mode="lines", name=c, legendgroup=c, showlegend=(j == 0),
                line=dict(color=col, width=2.5 if c == "EU27" else 1.5), visible=vis,
                hovertemplate=c + " %{x}: " + fmt + "<extra></extra>",
            ), row=1, col=j + 1)
    fig.update_yaxes(ticksuffix="%", title_text="% of age group", row=1, col=1)
    fig.update_yaxes(title_text="Years", row=1, col=2)
    fig.update_layout(
        template="plotly_white",
        title="Couple households and first-birth age (click names to add countries)",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(r=150, t=90), hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    fig = plot(*load())
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
