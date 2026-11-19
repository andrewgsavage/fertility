"""First-birth conditional ASFR against the coupling rate, every country with both, as
connected time series, with separate age choices for the coupling rate (x) and the
first-birth rate (y).

y: first births per childless woman (HFD mi.txt, m1x), pooled over the chosen single ages
   with HFD childless-women exposures (exposRRpa.txt, E0x) as weights. UK: England and
   Wales reconstruction from ONS cohort table 3 (ages 21-45 only).
x: % married or cohabiting.
   - ILO, women, 15-24 / 25-34 / 35-44 (coupling_ilo.py), where ILO records cohabitation.
   - National statistics offices, women, any age band (NSO/scripts/coupling_nso.py): Denmark,
     Finland, Netherlands (registers, single-year ages) and the US (CPS, 25-34 only).
   - FT, both sexes, 25-34 only (FT/scripts/ft_coupling.py), for the rest.
The rates and coupling loaders are in common/coupling_hfd.py (shared with UN/, eurostat/, DHS/).

Inputs (not tracked in git): HFD/data/HFD/mi.txt and exposRRpa.txt (humanfertility.org),
plus the CSV outputs of coupling_ilo.py and ft_coupling.py.
"""

import pandas as pd
import plotly.colors as pc

from common.coupling_ew import dual_dropdown_fig
from common.coupling_hfd import (FIRST_YEAR, FT_CODES, ILO_CODES, NSO_CODES, X_AGES, Y_OPTS, coupling,
                                 hfd_first_birth_rates, uk_first_birth_rates)
from common.paths import outputs_dir
from common.plotting import write_html

OUTDIR = outputs_dir("ILO")


def build_series():
    rates = pd.concat([hfd_first_birth_rates(), uk_first_birth_rates()], ignore_index=True)
    cp = coupling()
    names = {**{k: f"{v} (ILO, women)" for k, v in ILO_CODES.items()},
             **{k: f"{v} (register, women)" for k, v in NSO_CODES.items()},
             **{k: f"{v} (FT, both sexes)" for k, v in FT_CODES.items()}}
    names["USA"] = "US (CPS, women)"
    names["UK"] = "UK (FT, both sexes; births E&W)"
    colors = pc.qualitative.D3 + ["#000000", "#e6ab02", "#1b9e77"]
    series = []
    for i, code in enumerate(names):
        r = rates[rates.code == code].set_index("year")
        c = cp[cp.code == code]
        years = sorted(y for y in set(r.index) & set(c.year) if y >= FIRST_YEAR)
        if not years:
            print("no overlap:", code)
            continue
        x = {a: [c[(c.age == a) & (c.year == y)].share.squeeze() if ((c.age == a) & (c.year == y)).any()
                 else None for y in years] for a in X_AGES}
        y = {k: [None if k not in r or pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years]
             for k in Y_OPTS}
        series.append({"name": names[code], "code": code, "color": colors[i % len(colors)],
                       "years": years, "x": x, "y": y})
    return series


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"y_{k}": s["y"][k][i] for k in Y_OPTS}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr.csv", index=False)
    fig = dual_dropdown_fig(
        series, {a: a for a in X_AGES}, Y_OPTS, "25-34", "25-29",
        "First-birth rate or % with a child vs coupling rate, by country (marker grows with year)",
        "% married or cohabiting")
    write_html(fig, OUTDIR / "coupling_vs_cond_asfr.html")
    for s in series:
        print(f"{s['name']:40s} {s['years'][0]}-{s['years'][-1]}",
              {a: sum(v is not None for v in s["x"][a]) for a in X_AGES})
