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

from common.coupling_hfd import (FIRST_YEAR, FT_CODES, ILO_CODES, NSO_CODES, X_AGES, Y_OPTS, coupling,
                                 hfd_first_birth_rates, uk_first_birth_rates)
from common.paths import outputs_dir
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows

OUTDIR = outputs_dir("ILO")

# 2x2 grid: % with a child by an age against coupling in the age group leading up to it.
# Rows: coupling at 15-24, 25-34. Columns: % with a child by the middle of that age range,
# and by its end (the same layout as the eurostat young-adults chart).
GRID = [(20, "15-24"), (25, "15-24"), (30, "25-34"), (35, "25-34")]
GRID_Y = {f"mother {a}": f"% of women with a child by {a}" for a, _ in GRID}


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
             for k in {**Y_OPTS, **GRID_Y}}
        series.append({"name": names[code], "code": code, "color": colors[i % len(colors)],
                       "years": years, "x": x, "y": y})
    return series


def grid_axes():
    """Axis titles for the grid, and the 15-24 row's own 0-60% range on both axes (its values
    stay below 60%; as the eurostat 18-24 chart), shared within the row; the 25-34 row keeps 0-100%."""
    axes = {}
    for n, xa in [("", "15-24"), ("2", "15-24"), ("3", "25-34"), ("4", "25-34")]:
        axes[f"xaxis{n}"] = dict(title_text=f"% married or cohabiting, {xa}", showticklabels=True)
        axes[f"yaxis{n}"] = dict(title_text="% with a child" if n in ("", "3") else None)
    for n, m in [("", None), ("2", "x")]:
        axes[f"xaxis{n}"] |= dict(range=[0, 60], matches=m)
        axes[f"yaxis{n}"] |= dict(range=[0, 60], matches=m and "y")
    return axes


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"y_{k}": s["y"][k][i] for k in Y_OPTS}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr.csv", index=False)
    write_trend_arrows(
        OUTDIR / "coupling_vs_cond_asfr.html", [s | {"label": s["code"]} for s in series],
        {a: f"% married or cohabiting, {a}" for a in X_AGES}, Y_OPTS, "25-34", "25-29",
        title="Each country's linear trend, first to latest year (points: every country-year)",
        x_suffix="%", y_suffix="%")
    # 2x2 grid, one figure: shared x and y, one 0-to-top range for every panel and both axes,
    # so slopes and levels compare across panels.
    write_trend_arrows(
        OUTDIR / "coupling_vs_mothers_grid.html", [s | {"label": s["code"]} for s in series],
        {xa: f"% married or cohabiting, {xa}" for _, xa in GRID}, GRID_Y,
        title="% of women with a child against % married or cohabiting, by age range",
        x_suffix="%", y_suffix="%", equal=True,
        panels=[{"x": xa, "y": f"mother {a}", "title": f"{when} of age range: with a child by {a}"}
                for (a, xa), when in zip(GRID, ["Middle", "End"] * 2)],
        layout=dict(showlegend=False, **grid_axes()))
    write_ratio_lines(
        OUTDIR / "coupling_vs_mothers_grid_ratio.html", [s | {"label": s["code"]} for s in series],
        [{"x": xa, "y": f"mother {a}", "title": f"{when}: child by {a} ÷ couple {xa}"}
         for (a, xa), when in zip(GRID, ["Middle", "End"] * 2)],
        title="% of women with a child ÷ % married or cohabiting, by year", height=800)
    for s in series:
        print(f"{s['name']:40s} {s['years'][0]}-{s['years'][-1]}",
              {a: sum(v is not None for v in s["x"][a]) for a in X_AGES})
