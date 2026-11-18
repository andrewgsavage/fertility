"""First-birth conditional ASFR (or % of women with a child) against the share of young adults living in
a couple, Eurostat EU-LFS, for every European country that also has HFD conditional rates.
Connected time series, 2006 onward, with separate dropdowns for x (sex x age group) and y.

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
import pathlib
import sys

import pandas as pd
import plotly.colors as pc

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"
sys.path.insert(0, str(REPO / "ILO" / "scripts"))
sys.path.insert(0, str(REPO / "ONS" / "scripts"))

import coupling_vs_cond_asfr as hfd  # noqa: E402
import coupling_vs_cond_asfr_ew as ew  # noqa: E402

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


def load_couples():
    j = json.loads((DATA / "lfst_hhindws_couple_ages.json").read_text("utf-8"))
    dims = j["id"]
    cats = [list(j["dimension"][d]["category"]["index"]) for d in dims]
    idx = pd.MultiIndex.from_product(cats, names=dims)
    flat = {int(k): v for k, v in j["value"].items()}
    s = pd.Series([flat.get(i) for i in range(len(idx))], index=idx, name="v").reset_index().dropna(subset=["v"])
    w = s.pivot_table(index=["sex", "age", "geo", "time"], columns="phhcomp", values="v").reset_index()
    w["share"] = 100 * w.A_CPL / w.TOTAL
    w["x"] = w.sex.map(SEXES) + " " + w.age.map(AGES)
    w["year"] = w.time.astype(int)
    return w[["geo", "year", "x", "share"]].dropna()


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
        y = {k: [None if k not in r or pd.isna(r.at[yr, k]) else float(r.at[yr, k]) for yr in years]
             for k in hfd.Y_OPTS}
        series.append({"name": NAMES[geo], "geo": geo, "color": colors[len(series) % len(colors)],
                       "years": years, "x": x, "y": y, "hidden": geo in HIDDEN})
    return series, x_opts


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    series, x_opts = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"couple_{k}": s["x"][k][i] for k in x_opts},
             **{f"y_{k}": s["y"][k][i] for k in hfd.Y_OPTS}} for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_eurostat.csv", index=False)
    fig = ew.dual_dropdown_fig(
        series, {k: k for k in x_opts}, hfd.Y_OPTS, X_DEFAULT, "20-24",
        "First-birth rate or % with a child vs young adults living in a couple, EU-LFS (marker grows with year)",
        "% living in a couple")
    ew.coupling_by_age_ew.OUTDIR = OUTDIR
    ew.coupling_by_age_ew.write_html(fig, "coupling_vs_cond_asfr_eurostat.html")
    for s in series:
        v = [v for v in s["x"][X_DEFAULT] if v is not None]
        print(f"{s['name']:12s} {s['years'][0]}-{s['years'][-1]}  women 18-24: {v[0]:.1f} -> {v[-1]:.1f}" if v else s["name"])
