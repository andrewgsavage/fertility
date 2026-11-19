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

import pandas as pd
import plotly.colors as pc

from common.coupling_ew import dual_dropdown_fig
from common.coupling_hfd import UN_HFD_CODES as HFD_CODES
from common.coupling_hfd import UN_MIN_POINTS as MIN_POINTS
from common.coupling_hfd import UN_X_AGES as X_AGES
from common.coupling_hfd import Y_OPTS, hfd_first_birth_rates
from common.paths import outputs_dir
from common.plotting import write_html

OUTDIR = outputs_dir("UN")


def build_series():
    rates = hfd_first_birth_rates()
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
        y = {k: [None if pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years] for k in Y_OPTS}
        series.append({"name": country, "color": colors[len(series) % len(colors)], "years": years,
                       "x": x, "y": y})
    return series


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"y_{k}": s["y"][k][i] for k in Y_OPTS}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_un.csv", index=False)
    fig = dual_dropdown_fig(
        series, {a: a for a in X_AGES}, Y_OPTS, "25-29", "25-29",
        "First-birth rate or % with a child vs women married or in a union, UN data (marker grows with year)",
        "% of women married or in a union")
    write_html(fig, OUTDIR / "coupling_vs_cond_asfr_un.html")
    for s in series:
        print(f"{s['name']:12s}", s["years"])
