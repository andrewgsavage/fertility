"""Abortions as a share of births + abortions, by country, from 1960.

Eurostat abortions (demo_fabort) and live births (demo_gind). England & Wales
comes from DHSC + HFD (ONS/scripts/abortion_share_uk.py) instead of Eurostat's
UK series, which stops in 2016.

Inputs (download into eurostat/data/ — not tracked in git):
  demo_fabort_total.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_fabort/A.NR.TOTAL.?format=SDMX-CSV
  demo_gind_lbirth.csv   https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_gind/A.LBIRTH.?format=SDMX-CSV
"""

import pathlib
import sys

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "abortion_share_europe.html"

sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / "ONS" / "scripts"))
import abortion_share_uk as ew  # noqa: E402

NAMES = {
    "AL": "Albania", "AM": "Armenia", "AT": "Austria", "AZ": "Azerbaijan", "BE": "Belgium",
    "BG": "Bulgaria", "BY": "Belarus", "CH": "Switzerland", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "GE": "Georgia", "HR": "Croatia", "HU": "Hungary", "IS": "Iceland",
    "IT": "Italy", "LT": "Lithuania", "LV": "Latvia", "MD": "Moldova", "ME": "Montenegro",
    "MK": "North Macedonia", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "RU": "Russia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "UA": "Ukraine",
}
# Skipped: DE_TOT and FX duplicate DE and FR; UK is replaced by England & Wales.
SHOWN = ["England & Wales", "France", "Spain", "Germany", "Italy", "Finland", "Sweden",
         "Czechia", "Hungary", "Poland"]


def load():
    keep = ["geo", "TIME_PERIOD", "OBS_VALUE"]
    a = pd.read_csv(DATA / "demo_fabort_total.csv")[keep].rename(columns={"OBS_VALUE": "abortions"})
    b = pd.read_csv(DATA / "demo_gind_lbirth.csv")[keep].rename(columns={"OBS_VALUE": "births"})
    d = a.merge(b, on=["geo", "TIME_PERIOD"]).rename(columns={"TIME_PERIOD": "year"})
    d = d[d.geo.isin(NAMES)]
    d["country"] = d.geo.map(NAMES)
    d["share"] = 100 * d.abortions / (d.abortions + d.births)

    ab = ew.abortions_total()
    births = {y: sum(v.values()) for y, v in ew.births().items()}
    births.update(ew.ONS_BIRTHS)
    years = sorted(y for y in ab if y in births)
    e = pd.DataFrame({"year": years, "country": "England & Wales",
                      "share": [100 * ab[y] / (ab[y] + births[y]) for y in years]})
    return pd.concat([d[["year", "country", "share"]], e])


def plot(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        x = d[d.country == c].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.share, mode="lines", name=c,
            line=dict(color=colors[i % len(colors)], width=2.5 if c == "England & Wales" else 1.5),
            visible=True if c in SHOWN else "legendonly",
            hovertemplate=c + " %{x}: %{y:.1f}%<extra></extra>",
        ))
    fig.update_yaxes(title_text="% of births + abortions", ticksuffix="%", rangemode="tozero")
    fig.update_layout(
        template="plotly_white",
        title="Abortions as a share of births + abortions (click names to add countries)",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(r=150, t=60),
        hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    fig = plot(load())
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
