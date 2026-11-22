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

from common.coupling_hfd import UN_HFD_CODES as HFD_CODES
from common.coupling_hfd import UN_MIN_POINTS as MIN_POINTS
from common.coupling_hfd import UN_X_AGES as X_AGES
from common.coupling_hfd import Y_OPTS, hfd_first_birth_rates
from common.paths import outputs_dir
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows

OUTDIR = outputs_dir("UN")

# % with a child grid, as ILO/scripts/coupling_vs_cond_asfr.py: one row per 5-year coupling
# age group; columns: % with a child by the middle of the group and by its end.
GRID = [(a0 + 2, a0 + 5, f"{a0}-{a0 + 4}") for a0 in (15, 20, 25, 30)]
GRID_Y = {f"mother {a}": f"% of women with a child by {a}" for mid, end, _ in GRID for a in (mid, end)}


def grid_axes(series):
    """Axis titles, and one range per row on both axes, shared within the row: 0-60% if the
    row's values stay below 60%, else 0-100%."""
    axes = {}
    for row, (mid, end, xa) in enumerate(GRID):
        vals = [v for s in series for k in (f"mother {mid}", f"mother {end}") for v in s["y"][k] + s["x"][xa]
                if v is not None]
        top = 60 if max(vals) < 60 else 100
        for col in (0, 1):
            n = 2 * row + col + 1
            n = "" if n == 1 else str(n)
            first = "" if row == 0 else str(2 * row + 1)
            axes[f"xaxis{n}"] = dict(title_text=f"% married or in a union, {xa}", showticklabels=True,
                                     range=[0, top], matches=None if col == 0 else f"x{first}")
            axes[f"yaxis{n}"] = dict(title_text="% with a child" if col == 0 else None, range=[0, top],
                                     matches=None if col == 0 else f"y{first}")
    return axes


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
        y = {k: [None if pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years] for k in {**Y_OPTS, **GRID_Y}}
        series.append({"name": country, "label": code, "color": colors[len(series) % len(colors)], "years": years,
                       "x": x, "y": y})
    return series


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"y_{k}": s["y"][k][i] for k in Y_OPTS}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_un.csv", index=False)
    # Census and survey years only: 2 points are enough for an arrow.
    write_trend_arrows(
        OUTDIR / "coupling_vs_cond_asfr_un.html", series,
        {a: f"% of women married or in a union, {a}" for a in X_AGES}, Y_OPTS, "25-29", "25-29",
        title="Each country's linear trend, first to latest census or survey year (points: every year)",
        x_suffix="%", y_suffix="%", min_points=MIN_POINTS)
    write_trend_arrows(
        OUTDIR / "coupling_vs_mothers_grid_un.html", series,
        {xa: f"% married or in a union, {xa}" for _, _, xa in GRID}, GRID_Y,
        title="% of women with a child against % married or in a union, by 5-year age group (UN)",
        x_suffix="%", y_suffix="%", min_points=MIN_POINTS, equal=True,
        panels=[p for mid, end, xa in GRID for p in (
            {"x": xa, "y": f"mother {mid}", "title": f"Middle of age range: with a child by {mid}"},
            {"x": xa, "y": f"mother {end}", "title": f"End of age range: with a child by {end}"})],
        layout=dict(showlegend=False, height=1500, **grid_axes(series)))
    write_ratio_lines(
        OUTDIR / "coupling_vs_mothers_grid_un_ratio.html", series,
        [p for mid, end, xa in GRID for p in (
            {"x": xa, "y": f"mother {mid}", "title": f"Middle: child by {mid} ÷ couple {xa}"},
            {"x": xa, "y": f"mother {end}", "title": f"End: child by {end} ÷ couple {xa}"})],
        title="% of women with a child ÷ % married or in a union, by year (UN)", height=1500)
    for s in series:
        print(f"{s['name']:12s}", s["years"])
