"""First-birth conditional ASFR against the share of women married or in a union, from UN
World Marriage Data, for every country that also has HFD conditional rates. Connected
time series (one point per census/survey year), with separate dropdowns for the 5-year
coupling age group (x) and the first-birth rate age range (y).

y: first births per childless woman, HFD mi.txt pooled with childless-women exposures
   (see ILO/scripts/coupling_vs_cond_asfr.py).
x: women married or in a consensual union, by 5-year age group (coupling_un.py output).

Inputs: UN/outputs/coupling_un.csv (run coupling_un.py first), HFD/data/HFD/mi.txt and
exposRRpa.txt (not tracked in git).
"""

import pathlib
import sys

import pandas as pd
import plotly.colors as pc

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "ILO" / "scripts"))
sys.path.insert(0, str(REPO / "ONS" / "scripts"))

import coupling_vs_cond_asfr as ilo  # noqa: E402
import coupling_vs_cond_asfr_ew as ew  # noqa: E402

OUTDIR = ROOT / "outputs"
X_AGES = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44"]
HFD_CODES = {
    "Austria": "AUT", "Bulgaria": "BGR", "Belarus": "BLR", "Canada": "CAN", "Chile": "CHL", "Czechia": "CZE",
    "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN", "Hungary": "HUN", "Ireland": "IRL", "Iceland": "ISL",
    "Japan": "JPN", "S Korea": "KOR", "Lithuania": "LTU", "Norway": "NOR", "Poland": "POL", "Russia": "RUS",
    "Sweden": "SWE", "Taiwan": "TWN", "Ukraine": "UKR",
}
MIN_POINTS = 2


def build_series():
    rates = ilo.hfd_first_birth_rates()
    un = pd.read_csv(OUTDIR / "coupling_un.csv")
    un = un[(un.sex == "Women") & un.country.isin(HFD_CODES)]
    colors = pc.qualitative.Dark24
    series = []
    for country, code in HFD_CODES.items():
        r = rates[rates.code == code].set_index("year")
        c = un[un.country == country].pivot_table(index="year", columns="age", values="share")
        years = sorted(set(r.index) & set(c.index))
        if len(years) < MIN_POINTS:
            print("too few overlapping years:", country, years)
            continue
        x = {a: [None if a not in c or pd.isna(c.at[y, a]) else float(c.at[y, a]) for y in years] for a in X_AGES}
        y = {k: [None if pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years] for k in ilo.Y_OPTS}
        series.append({"name": country, "color": colors[len(series) % len(colors)], "years": years,
                       "x": x, "y": y})
    return series


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"y_{k}": s["y"][k][i] for k in ilo.Y_OPTS}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_un.csv", index=False)
    fig = ew.dual_dropdown_fig(
        series, {a: a for a in X_AGES}, ilo.Y_OPTS, "25-29", "25-29",
        "First-birth rate or % with a child vs women married or in a union, UN data (marker grows with year)",
        "% of women married or in a union")
    ew.coupling_by_age_ew.OUTDIR = OUTDIR
    ew.coupling_by_age_ew.write_html(fig, "coupling_vs_cond_asfr_un.html")
    for s in series:
        print(f"{s['name']:12s}", s["years"])
