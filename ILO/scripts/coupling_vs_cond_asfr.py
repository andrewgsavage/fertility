"""First-birth conditional ASFR against the coupling rate, every country with both, as
connected time series, with separate age choices for the coupling rate (x) and the
first-birth rate (y).

y: first births per childless woman (HFD mi.txt, m1x), pooled over the chosen single ages
   with HFD childless-women exposures (exposRRpa.txt, E0x) as weights. UK: England and
   Wales reconstruction from ONS cohort table 3 (ages 21-45 only).
x: % married or cohabiting.
   - ILO, women, 15-24 / 25-34 / 35-44 (coupling_ilo.py), where ILO records cohabitation.
   - FT, both sexes, 25-34 only (FT/scripts/ft_coupling.py), for HFD countries ILO lacks.

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
X_AGES = ["15-24", "25-34", "35-44"]
ILO_CODES = {"CAN": "Canada", "CHL": "Chile", "JPN": "Japan", "KOR": "S Korea", "RUS": "Russia", "BLR": "Belarus"}
FT_CODES = {"DNK": "Denmark", "FIN": "Finland", "NLD": "Netherlands", "POL": "Poland", "ESP": "Spain",
            "USA": "US", "UK": "UK"}
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
    return pd.concat(out, axis=1).reset_index()


def uk_first_birth_rates():
    r = ew.first_birth_rates({k: v for k, v in Y_RANGES.items() if v[0] >= 21})
    return r.reset_index().rename(columns={"index": "year"}).assign(code="UK")


def coupling():
    ilo = pd.read_csv(OUTDIR / "coupling_ilo.csv")
    ilo = ilo[(ilo.sex == "women") & ilo.ref_area.isin(ILO_CODES)].rename(columns={"ref_area": "code"})
    ft = pd.read_csv(REPO / "FT" / "outputs" / "ft_coupling_25_34.csv")
    ft = ft[ft.country.isin(FT_CODES.values())].rename(columns={"value": "share"})
    ft["code"] = ft.country.map({v: k for k, v in FT_CODES.items()})
    ft["age"] = "25-34"
    return pd.concat([ilo[["code", "year", "age", "share"]], ft[["code", "year", "age", "share"]]])


def build_series():
    rates = pd.concat([hfd_first_birth_rates(), uk_first_birth_rates()], ignore_index=True)
    cp = coupling()
    names = {**{k: f"{v} (ILO, women)" for k, v in ILO_CODES.items()},
             **{k: f"{v} (FT, both sexes)" for k, v in FT_CODES.items()}}
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
             for k in Y_RANGES}
        series.append({"name": names[code], "code": code, "color": colors[i % len(colors)],
                       "years": years, "x": x, "y": y})
    return series


if __name__ == "__main__":
    series = build_series()
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in X_AGES},
             **{f"first_birth_{k}": s["y"][k][i] for k in Y_RANGES}}
            for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr.csv", index=False)
    fig = ew.dual_dropdown_fig(
        series, {a: a for a in X_AGES}, {k: k for k in Y_RANGES}, "25-34", "25-29",
        "First-birth rate vs coupling rate, by country (marker grows with year)",
        "% married or cohabiting", "First births per childless woman")
    ew.coupling_by_age_ew.OUTDIR = OUTDIR
    ew.coupling_by_age_ew.write_html(fig, "coupling_vs_cond_asfr.html")
    for s in series:
        print(f"{s['name']:40s} {s['years'][0]}-{s['years'][-1]}",
              {a: sum(v is not None for v in s["x"][a]) for a in X_AGES})
