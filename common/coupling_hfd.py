"""First-birth rates and % of women with a child for every HFD country (plus the UK from
ONS), and coupling rates from ILO, national statistics offices and the FT, shared by
ILO/scripts/coupling_vs_cond_asfr.py and the UN, eurostat and DHS equivalents.

y: first births per childless woman (HFD mi.txt, m1x), pooled over the chosen single ages
   with HFD childless-women exposures (exposRRpa.txt, E0x) as weights. UK: England and
   Wales reconstruction from ONS cohort table 3 (ages 21-45 only).
x: % married or cohabiting (coupling()), from the CSV outputs of ILO/scripts/coupling_ilo.py,
   NSO/scripts/coupling_nso.py and FT/scripts/ft_coupling.py.
"""

import pandas as pd

from common import coupling_ew as ew
from common.hfd import age_to_int, read_hfd
from common.paths import outputs_dir

Y_RANGES = {"15-19": (15, 19), "20-24": (20, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39),
            "40-44": (40, 44), "20-29": (20, 29), "30-39": (30, 39)}
Y_OPTS = ew.y_options(Y_RANGES)
X_AGES = ["15-24", "25-34", "35-44", "20-24", "25-29", "30-34", "35-39"]
ILO_CODES = {"CAN": "Canada", "CHL": "Chile", "JPN": "Japan", "KOR": "S Korea", "RUS": "Russia", "BLR": "Belarus"}
NSO_CODES = {"DNK": "Denmark", "FIN": "Finland", "NLD": "Netherlands", "USA": "US"}
FT_CODES = {"POL": "Poland", "ESP": "Spain", "UK": "UK"}
FIRST_YEAR = 1990


def _read_hfd(name, cols):
    d = read_hfd(name, cols)
    d["age"] = age_to_int(d.age)
    return d


def hfd_first_birth_rates():
    m = _read_hfd("mi.txt", ["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"])
    e = _read_hfd("exposRRpa.txt", ["code", "year", "age", "E0x", "E1x", "E2x", "E3x", "E4px"])
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
    ilo = pd.read_csv(outputs_dir("ILO") / "coupling_ilo.csv")
    ilo = ilo[(ilo.sex == "women") & ilo.ref_area.isin(ilo_codes)].rename(columns={"ref_area": "code"})
    ft = pd.read_csv(outputs_dir("FT") / "ft_coupling_25_34.csv")
    ft = ft[ft.country.isin(ft_codes.values())].rename(columns={"value": "share"})
    ft["code"] = ft.country.map({v: k for k, v in ft_codes.items()})
    ft["age"] = "25-34"
    nso = pd.read_csv(outputs_dir("NSO") / "coupling_nso.csv")
    nso = nso[(nso.sex == "Women") & nso.country.isin(NSO_CODES.values())].copy()
    nso["code"] = nso.country.map({v: k for k, v in NSO_CODES.items()})
    return pd.concat([ilo[["code", "year", "age", "share"]], ft[["code", "year", "age", "share"]],
                      nso[["code", "year", "age", "share"]]])


# UN World Marriage Data countries with HFD rates (UN/scripts/coupling_vs_cond_asfr_un.py).
UN_X_AGES = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44"]
UN_HFD_CODES = {
    "Austria": "AUT", "Bulgaria": "BGR", "Belarus": "BLR", "Canada": "CAN", "Chile": "CHL", "Czechia": "CZE",
    "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN", "Hungary": "HUN", "Ireland": "IRL", "Iceland": "ISL",
    "Japan": "JPN", "S Korea": "KOR", "Lithuania": "LTU", "Norway": "NOR", "Poland": "POL", "Russia": "RUS",
    "Sweden": "SWE", "Taiwan": "TWN", "Ukraine": "UKR",
}
UN_MIN_POINTS = 2
