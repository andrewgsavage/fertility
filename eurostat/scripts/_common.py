"""Shared helpers for the Eurostat factor-page charts."""

import pathlib

NAMES = {
    "AL": "Albania", "AT": "Austria", "BA": "Bosnia & Herzegovina", "BE": "Belgium",
    "BG": "Bulgaria", "CH": "Switzerland", "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany",
    "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland",
    "FR": "France", "HR": "Croatia", "HU": "Hungary", "IE": "Ireland", "IS": "Iceland",
    "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia", "ME": "Montenegro",
    "MK": "North Macedonia", "MT": "Malta", "NL": "Netherlands", "NO": "Norway",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "SE": "Sweden",
    "SI": "Slovenia", "SK": "Slovakia", "TR": "Turkey", "UK": "United Kingdom",
    "EU27_2020": "EU27",
}

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
OUTDIR = pathlib.Path(__file__).resolve().parent.parent / "outputs"


def write_html(fig, name):
    out = OUTDIR / name
    fig.write_html(
        out,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = out.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    out.write_text(html, encoding="utf-8")
    print(f"Saved {out}")
