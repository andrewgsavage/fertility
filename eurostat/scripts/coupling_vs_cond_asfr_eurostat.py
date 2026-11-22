"""First-birth conditional ASFR (or % of women with a child) against the share of young adults living in
a couple, Eurostat EU-LFS, for every European country that also has HFD conditional rates.
Trend arrows (common/trend_arrows.py), 2006 onward, with separate dropdowns for x (sex x age
group) and y.

x: persons living in a couple household (married or cohabiting, own household; people living
   with their parents are not counted) as % of all persons in the group, by sex, ages 18-24,
   20-49 and 25-49. Eurostat lfst_hhindws (EU-LFS), phhcomp A_CPL / TOTAL, wstatus POP.
y: first births per childless woman, pooled over the chosen ages, or % of women with a child
   by 25/30/35/40 or among women aged 20-24 ... 35-39 (HFD mi.txt and exposRRpa.txt; UK = England and Wales ONS reconstruction), via
   ILO/scripts/coupling_vs_cond_asfr.py.

Input (download into eurostat/data/ - not tracked in git):
  lfst_hhindws_couple_ages.json
    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/lfst_hhindws?lang=en
    &sex=F&sex=M&age=Y18-24&age=Y20-49&age=Y25-49&phhcomp=A_CPL&phhcomp=TOTAL&wstatus=POP&unit=THS_PER
"""

import json

import pandas as pd
import plotly.colors as pc

from common import coupling_hfd as hfd
from common.paths import data_dir, outputs_dir
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows
from leaving_home_vs_tfr import CODE_REGION, REGION_COLOR

DATA = data_dir("eurostat")
OUTDIR = outputs_dir("eurostat")

HFD_CODES = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CZ": "CZE", "DK": "DNK", "EE": "EST", "IE": "IRL", "ES": "ESP",
    "HR": "HRV", "LT": "LTU", "HU": "HUN", "NL": "NLD", "PL": "POL", "PT": "PRT", "SI": "SVN", "SK": "SVK",
    "FI": "FIN", "SE": "SWE", "NO": "NOR", "UK": "UK",
}
NAMES = {"AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CZ": "Czechia", "DK": "Denmark", "EE": "Estonia",
         "IE": "Ireland", "ES": "Spain", "HR": "Croatia", "LT": "Lithuania", "HU": "Hungary", "NL": "Netherlands",
         "PL": "Poland", "PT": "Portugal", "SI": "Slovenia", "SK": "Slovakia", "FI": "Finland", "SE": "Sweden",
         "NO": "Norway", "UK": "UK"}
# Start hidden: Denmark and Sweden jump 15-25 points between years at 25-49 (breaks), and
# Denmark falls to 1% at 18-24; Norway has only 2021 onward at about 3%.
HIDDEN = {"DK", "SE", "NO"}
AGES = {"Y18-24": "18-24", "Y20-49": "20-49", "Y25-49": "25-49"}
SEXES = {"F": "women", "M": "men"}
X_DEFAULT = "women 18-24"
Y_DEFAULT = "mother 25"
# Page chart: % with a child by the middle (21) and the end (25) of 18-24, as the ILO grid.
PANEL_Y = {"mother 21": "% of women with a child by 21", "mother 25": "% of women with a child by 25"}


def load_couples():
    j = json.loads((DATA / "lfst_hhindws_couple_ages.json").read_text("utf-8"))
    dims = j["id"]
    cats = [list(j["dimension"][d]["category"]["index"]) for d in dims]
    idx = pd.MultiIndex.from_product(cats, names=dims)
    flat = {int(k): v for k, v in j["value"].items()}
    status = {int(k): v for k, v in j.get("status", {}).items()}
    s = pd.Series([flat.get(i) for i in range(len(idx))], index=idx, name="v").reset_index()
    s["u"] = ["u" in status.get(i, "") for i in range(len(idx))]
    s = s.dropna(subset=["v"])
    w = s.pivot_table(index=["sex", "age", "geo", "time"], columns="phhcomp", values="v").reset_index()
    w["share"] = 100 * w.A_CPL / w.TOTAL
    # Eurostat's "u" flag (low reliability: small sample) on the couple count.
    u = s[s.phhcomp == "A_CPL"].set_index(["sex", "age", "geo", "time"]).u
    w["u"] = [bool(u.get(k, False)) for k in zip(w.sex, w.age, w.geo, w.time)]
    w["x"] = w.sex.map(SEXES) + " " + w.age.map(AGES)
    w["year"] = w.time.astype(int)
    return w[["geo", "year", "x", "share", "u"]].dropna()


def build_series():
    rates = pd.concat([hfd.hfd_first_birth_rates(), hfd.uk_first_birth_rates()], ignore_index=True)
    cp = load_couples()
    x_opts = [f"{s} {a}" for s in SEXES.values() for a in AGES.values()]
    colors = pc.qualitative.Dark24
    series = []
    for geo, code in HFD_CODES.items():
        r = rates[rates.code == code].set_index("year")
        c = cp[cp.geo == geo].pivot_table(index="year", columns="x", values="share")
        years = sorted(set(r.index) & set(c.index))
        if len(years) < 2:
            print("too few overlapping years:", geo, years)
            continue
        x = {k: [None if k not in c or pd.isna(c.at[y, k]) else float(c.at[y, k]) for y in years] for k in x_opts}
        uf = cp[cp.geo == geo].pivot_table(index="year", columns="x", values="u", aggfunc="max")
        flags = {k: [bool(k in uf and y in uf.index and uf.at[y, k] == 1) for y in years] for k in x_opts}
        y = {k: [None if k not in r or pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years]
             for k in {**hfd.Y_OPTS, **PANEL_Y}}
        series.append({"name": NAMES[geo], "geo": geo, "color": colors[len(series) % len(colors)],
                       "years": years, "x": x, "y": y, "hidden": geo in HIDDEN,
                       "flags": flags, "flag_note": "low reliability (Eurostat u)"})
    return series, x_opts


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    series, x_opts = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"couple_{k}": s["x"][k][i] for k in x_opts},
             **{f"y_{k}": s["y"][k][i] for k in hfd.Y_OPTS}} for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_eurostat.csv", index=False)
    # Coloured and grouped by region, as on the leaving-home trend arrows.
    regions = list(REGION_COLOR)
    by_region = sorted(series, key=lambda s: regions.index(CODE_REGION[s["geo"]]))
    styled = [s | {"label": s["geo"], "group": CODE_REGION[s["geo"]], "color": REGION_COLOR[CODE_REGION[s["geo"]]]}
              for s in by_region]
    title = "Each country's linear trend, first to latest year (points: every country-year)"
    write_trend_arrows(
        OUTDIR / "coupling_vs_cond_asfr_eurostat_trends.html", styled,
        {k: f"% living in a couple, {k}" for k in x_opts}, hfd.Y_OPTS, X_DEFAULT, Y_DEFAULT,
        title=title, x_suffix="%", y_suffix="%", legend="series")
    # Without dropdowns: women 18-24 in a couple against % with a child by the middle and the
    # end of that age range, in the style of ILO/scripts/coupling_vs_cond_asfr.py's grid.
    write_trend_arrows(
        OUTDIR / "coupling_vs_cond_asfr_eurostat_default.html", styled,
        {X_DEFAULT: f"% living in a couple, {X_DEFAULT}"}, PANEL_Y,
        title="% of women with a child against % living in a couple, women 18-24",
        x_suffix="%", y_suffix="%", legend="series", equal=True,
        panels=[{"x": X_DEFAULT, "y": "mother 21", "title": "Middle of age range: with a child by 21"},
                {"x": X_DEFAULT, "y": "mother 25", "title": "End of age range: with a child by 25"}],
        # 0-60% on both axes, as the 15-24 row of the ILO grid.
        layout=dict(xaxis=dict(title_text="% living in a couple, women 18-24", range=[0, 60]),
                    xaxis2=dict(title_text="% living in a couple, women 18-24", range=[0, 60]),
                    yaxis=dict(range=[0, 60]), yaxis2=dict(range=[0, 60]),
                    yaxis_title_text="% with a child",
                    legend=dict(orientation="h", y=-0.25, yanchor="top")))
    write_ratio_lines(
        OUTDIR / "coupling_vs_cond_asfr_eurostat_ratio.html", styled,
        [{"x": X_DEFAULT, "y": "mother 21", "title": "Middle: child by 21 ÷ couple 18-24"},
         {"x": X_DEFAULT, "y": "mother 25", "title": "End: child by 25 ÷ couple 18-24"}],
        title="% of women with a child ÷ % of women 18-24 living in a couple, by year", legend=True)
    for s in series:
        v = [v for v in s["x"][X_DEFAULT] if v is not None]
        print(f"{s['name']:12s} {s['years'][0]}-{s['years'][-1]}  women 18-24: {v[0]:.1f} -> {v[-1]:.1f}" if v else s["name"])
