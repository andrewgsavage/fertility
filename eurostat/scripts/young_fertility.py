"""Shared helpers for the smartphone and social media charts.

Young fertility = births per woman across ages 20-29 (5 x (ASFR 20-24 + ASFR 25-29)),
from Eurostat demo_frate. Internet-use series come from Eurostat isoc_ci_*.

Inputs (download into eurostat/data/ - not tracked in git; the large ISOC files are
filtered to the slim CSVs below by _slim() on first use):
  demo_frate.csv        https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_frate/?format=SDMX-CSV
  isoc_ci_ac_i.csv      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_ci_ac_i/?format=SDMX-CSV   (I_IUSNET)
  isoc_ci_im_i.csv      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_ci_im_i/?format=SDMX-CSV   (I_IUMP)
"""

import pathlib

import pandas as pd

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = SCRIPT_DIR.parent / "data"
OUTDIR = SCRIPT_DIR.parent / "outputs"

NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium",
    "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IS": "Iceland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "ME": "Montenegro",
    "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland",
    "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia",
    "SK": "Slovakia", "TR": "Turkey", "UK": "United Kingdom", "XK": "Kosovo",
}
SHOWN = ["Germany", "France", "Spain", "Italy", "Sweden", "Poland", "Romania", "Netherlands",
         "United Kingdom", "Hungary"]

SLIMS = {
    "sn_slim.csv": ("isoc_ci_ac_i", "I_IUSNET"),
    "imp_slim.csv": ("isoc_ci_im_i", "I_IUMP"),
}


def _slim(name):
    path = DATA / name
    if not path.exists():
        src, indic = SLIMS[name]
        d = pd.read_csv(DATA / f"{src}.csv",
                        usecols=["indic_is", "unit", "ind_type", "geo", "TIME_PERIOD", "OBS_VALUE"])
        d = d.dropna(subset=["OBS_VALUE"])
        d = d[(d.indic_is == indic) & (d.unit == "PC_IND")
              & d.ind_type.isin(["Y16_24", "Y25_34", "IND_TOTAL"])]
        d.to_csv(path, index=False)
    return pd.read_csv(path)


def internet_use(name, ind_type="Y16_24"):
    """Wide table: rows year, columns country name."""
    d = _slim(name)
    d = d[(d.ind_type == ind_type) & d.geo.isin(NAMES)]
    d = d.assign(country=d.geo.map(NAMES))
    return d.pivot(index="TIME_PERIOD", columns="country", values="OBS_VALUE")


def young_fertility():
    """Wide table: rows year, columns country name; births per woman across ages 20-29."""
    d = pd.read_csv(DATA / "demo_frate.csv", usecols=["age", "geo", "TIME_PERIOD", "OBS_VALUE"])
    d = d[d.age.isin(["Y20-24", "Y25-29"]) & d.geo.isin(NAMES)]
    d = d.pivot_table(index=["geo", "TIME_PERIOD"], columns="age", values="OBS_VALUE").dropna()
    d["v"] = 5 * (d["Y20-24"] + d["Y25-29"])
    d = d.reset_index()
    d["country"] = d.geo.map(NAMES)
    return d.pivot(index="TIME_PERIOD", columns="country", values="v")


def write_html(fig, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output, include_plotlyjs="cdn", full_html=True,
                   default_width="100%", default_height="100%", config={"responsive": True})
    html = output.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    output.write_text(html, encoding="utf-8")
    print(f"Saved {output}")
