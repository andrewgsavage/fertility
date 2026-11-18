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

Inputs (not tracked in git): HFD/data/HFD/mi.txt and exposRRpa.txt (humanfertility.org),
plus the CSV outputs of coupling_ilo.py and ft_coupling.py.
"""

import pathlib
import sys

import pandas as pd
import plotly.colors as pc

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
HFD = REPO / "HFD" / "data" / "HFD"
sys.path.insert(0, str(REPO / "ONS" / "scripts"))

import coupling_vs_cond_asfr_ew as ew  # noqa: E402

OUTDIR = ROOT / "outputs"
Y_RANGES = {"15-19": (15, 19), "20-24": (20, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39),
            "40-44": (40, 44), "20-29": (20, 29), "30-39": (30, 39)}
Y_OPTS = ew.y_options(Y_RANGES)
X_AGES = ["15-24", "25-34", "35-44", "20-24", "25-29", "30-34", "35-39"]
ILO_CODES = {"CAN": "Canada", "CHL": "Chile", "JPN": "Japan", "KOR": "S Korea", "RUS": "Russia", "BLR": "Belarus"}
NSO_CODES = {"DNK": "Denmark", "FIN": "Finland", "NLD": "Netherlands", "USA": "US"}
FT_CODES = {"POL": "Poland", "ESP": "Spain", "UK": "UK"}
FIRST_YEAR = 1990


def read_hfd(name, cols):
    d = pd.read_csv(HFD / name, sep=r"\s+", skiprows=3, names=cols, na_values=".")
    d["age"] = d.age.astype(str).str.rstrip("-+").astype(int)
    return d


def hfd_first_birth_rates():
    m = read_hfd("mi.txt", ["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"])
    e = read_hfd("exposRRpa.txt", ["code", "year", "age", "E0x", "E1x", "E2x", "E3x", "E4px"])
    d = m.merge(e[["code", "year", "age", "E0x"]], on=["code", "year", "age"])
    d["births"] = d.m1x * d.E0x
    out = []
    for name, (lo, hi) in Y_RANGES.items():
        g = d[d.age.between(lo, hi)].dropna(subset=["births"]).groupby(["code", "year"]).agg(
            births=("births", "sum"), E0x=("E0x", "sum"), n=("age", "size"))
        g = g[g.n == hi - lo + 1]
        out.append((100 * g.births / g.E0x).rename(name))
    # % with a child at an age: 100 - childless women's share of all exposure at that age and year.
    e["mother"] = 100 - 100 * e.E0x / e[["E0x", "E1x", "E2x", "E3x", "E4px"]].sum(axis=1)
    for a in ew.CHILDLESS_AGES:
        out.append(e[e.age == a].set_index(["code", "year"]).mother.rename(f"mother {a}"))
    # % of women in a 5-year age group with a child: pooled exposures.
    e["all"] = e[["E0x", "E1x", "E2x", "E3x", "E4px"]].sum(axis=1)
    for gname, (lo, hi) in ew.MOTHER_GROUPS.items():
        g = e[e.age.between(lo, hi)].groupby(["code", "year"]).agg(E0x=("E0x", "sum"), all=("all", "sum"),
                                                                    n=("age", "size"))
        g = g[g.n == hi - lo + 1]
        out.append((100 - 100 * g.E0x / g["all"]).rename(f"mothers {gname}"))
    return pd.concat(out, axis=1).reset_index()


def uk_first_birth_rates():
    r = ew.first_birth_rates({k: v for k, v in Y_RANGES.items() if v[0] >= 21}).join(ew.mothers_ew(), how="outer")
    return r.reset_index().rename(columns={"index": "year"}).assign(code="UK")


def coupling(ilo_codes=ILO_CODES, ft_codes=FT_CODES):
    ilo = pd.read_csv(OUTDIR / "coupling_ilo.csv")
    ilo = ilo[(ilo.sex == "women") & ilo.ref_area.isin(ilo_codes)].rename(columns={"ref_area": "code"})
    ft = pd.read_csv(REPO / "FT" / "outputs" / "ft_coupling_25_34.csv")
    ft = ft[ft.country.isin(ft_codes.values())].rename(columns={"value": "share"})
    ft["code"] = ft.country.map({v: k for k, v in ft_codes.items()})
    ft["age"] = "25-34"
    nso = pd.read_csv(REPO / "NSO" / "outputs" / "coupling_nso.csv")
    nso = nso[(nso.sex == "Women") & nso.country.isin(NSO_CODES.values())].copy()
    nso["code"] = nso.country.map({v: k for k, v in NSO_CODES.items()})
    return pd.concat([ilo[["code", "year", "age", "share"]], ft[["code", "year", "age", "share"]],
                      nso[["code", "year", "age", "share"]]])


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
    fig = ew.dual_dropdown_fig(
        series, {a: a for a in X_AGES}, Y_OPTS, "25-34", "25-29",
        "First-birth rate or % with a child vs coupling rate, by country (marker grows with year)",
        "% married or cohabiting")
    ew.coupling_by_age_ew.OUTDIR = OUTDIR
    ew.coupling_by_age_ew.write_html(fig, "coupling_vs_cond_asfr.html")
    for s in series:
        print(f"{s['name']:40s} {s['years'][0]}-{s['years'][-1]}",
              {a: sum(v is not None for v in s["x"][a]) for a in X_AGES})
