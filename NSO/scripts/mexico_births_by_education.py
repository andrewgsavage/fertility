"""Mexico: birth rates by mother's education, 2015-2024.

Births: INEGI Estadistica de Nacimientos Registrados (ENR) microdata, one DBF per registration
year (natalidad_base_datos_<y>_dbf.zip). Births of year Y are those registered in Y or Y+1
(about 93% of the eventual total, a share that is stable over 2012-2022), counted by mother's
age at the birth (EDAD_MADN) and schooling (ESCOL_MAD: 1 none, 2-3 some primary, 4 primary
complete, 5 secondary, 6 preparatoria, 7 profesional, 8 other, 9 not stated).
Women: INEGI Encuesta Nacional de Ocupacion y Empleo (ENOE, ENOE-N from 2020 Q3), third
quarter of each year, sociodemographic file (SDEM): women by age (EDA) and the highest level
with at least one grade passed (CS_P13_1, CS_P13_2), weighted by FAC / FAC_TRI. Complete
interviews (R_DEF 0) of usual residents (C_RES 1 or 3).

Education groups:
  low       primary or less                     births 1-4; ENOE none, preschool, primary,
                                                or secondary with no grade passed
  medium    secondary or preparatoria           births 5-6; ENOE secundaria, preparatoria,
                                                normal, carrera tecnica
  tertiary  at least one year of profesional    births 7; ENOE profesional, master's, doctorate
Births with schooling 8 or 9 are spread in proportion within age.

    pixi run python NSO/scripts/mexico_births_by_education.py

Writes NSO/outputs/mexico_fertility_by_education.csv (year, age, ed, births, women, rate).
"""

import io
import zipfile

import numpy as np
import pandas as pd
import requests

from common.dbf import read_dbf, to_int
from common.paths import data_dir, outputs_dir

UA = {"User-Agent": "Mozilla/5.0"}
NAT_URL = "https://www.inegi.org.mx/contenidos/programas/natalidad/microdatos/{y}/natalidad_base_datos_{y}_dbf.zip"
ENOE = "https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/microdatos/"
YEARS = range(2015, 2025)
AGES = ["20-24", "25-29", "30-34", "35-39", "40-44"]
BIRTH_ED = {1: "low", 2: "low", 3: "low", 4: "low", 5: "medium", 6: "medium", 7: "tertiary"}


def age_group(age):
    out = np.full(len(age), "", dtype=object)
    for a in AGES:
        out[(age >= int(a[:2])) & (age <= int(a[3:]))] = a
    return out


def get(url):
    r = requests.get(url, headers=UA, timeout=900)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))


def birth_file(reg_year):
    folder = data_dir("NSO") / "mex_nat"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"educ_{reg_year}.csv"
    if path.exists():
        return pd.read_csv(path)
    z = get(NAT_URL.format(y=reg_year))
    name = next(n for n in z.namelist() if n.lower().startswith("nacim") and n.lower().endswith(".dbf"))
    tmp = folder / name
    tmp.write_bytes(z.read(name))
    try:
        d = read_dbf(tmp, {"ANO_NAC", "EDAD_MADN", "ESCOL_MAD"})
        year = to_int(d["ANO_NAC"])
        ed = np.array([BIRTH_ED.get(s, "unknown") for s in to_int(d["ESCOL_MAD"])], dtype=object)
        df = pd.DataFrame({"year": year, "age": age_group(to_int(d["EDAD_MADN"])), "ed": ed})
        out = df[(df.age != "") & (df.year >= 2000)].value_counts().rename("births").reset_index()
    finally:
        tmp.unlink()
    out.to_csv(path, index=False)
    print(f"registered {reg_year}: {out.births.sum():,} births at 20-44", flush=True)
    return out


def births():
    frames = []
    for y in YEARS:
        c = pd.concat([birth_file(r) for r in (y, y + 1)])
        c = c[c.year == y]
        w = c.pivot_table(index="age", columns="ed", values="births", aggfunc="sum").fillna(0)
        known = w[["low", "medium", "tertiary"]]
        known = known.div(known.sum(axis=1), axis=0).mul(w.sum(axis=1), axis=0)
        frames.append(known.stack().rename("births").reset_index().assign(year=y))
        print(f"{y}: unknown schooling {w['unknown'].sum() / w.values.sum():.1%}")
    return pd.concat(frames)


def enoe_zip(year):
    names = [f"enoe_{year}_trim3_csv.zip", f"enoe_n_{year}_trim3_csv.zip", f"{year}trim3_csv.zip"]
    for n in names:
        try:
            return get(ENOE + n)
        except (requests.HTTPError, zipfile.BadZipFile):
            continue
    raise RuntimeError(f"ENOE {year} Q3 not found")


def women_year(year):
    folder = data_dir("NSO") / "mex_enoe"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"women_{year}.csv"
    if path.exists():
        return pd.read_csv(path)
    z = enoe_zip(year)
    name = next(n for n in z.namelist() if "sdem" in n.lower() and n.lower().endswith(".csv"))
    raw = z.read(name)
    head = pd.read_csv(io.BytesIO(raw), nrows=0, encoding="latin-1").columns
    cols = {c.lower(): c for c in head}
    wt = cols.get("fac_tri") or cols["fac"]
    use = [cols[c] for c in ["r_def", "c_res", "sex", "eda", "cs_p13_1", "cs_p13_2"]] + [wt]
    d = pd.read_csv(io.BytesIO(raw), usecols=use, encoding="latin-1", low_memory=False)
    d.columns = [c.lower() for c in d.columns]
    d = d.rename(columns={wt.lower(): "w"})
    for c in d.columns:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[(d.r_def == 0) & d.c_res.isin([1, 3]) & (d.sex == 2)]
    lvl, grade = d.cs_p13_1, d.cs_p13_2
    d["ed"] = np.select(
        [lvl.isin([0, 1, 2]) | ((lvl == 3) & (grade == 0)),
         lvl.isin([3, 4, 5, 6]),
         lvl.isin([7, 8, 9])],
        ["low", "medium", "tertiary"], default="unknown")
    d["age"] = age_group(d.eda.to_numpy())
    out = d[d.age != ""].groupby(["age", "ed"]).w.sum().rename("women").reset_index()
    out.to_csv(path, index=False)
    print(f"ENOE {year} Q3: {out.women.sum() / 1e6:.1f}M women at 20-44", flush=True)
    return out


def women():
    frames = []
    for y in YEARS:
        w = women_year(y).pivot_table(index="age", columns="ed", values="women", aggfunc="sum").fillna(0)
        known = w[["low", "medium", "tertiary"]]
        known = known.div(known.sum(axis=1), axis=0).mul(w.sum(axis=1), axis=0)
        frames.append(known.stack().rename("women").reset_index().assign(year=y))
    return pd.concat(frames)


def main():
    d = births().merge(women(), on=["year", "age", "ed"])
    d["rate"] = d.births / d.women
    tot = d.groupby(["year", "age"])[["births", "women"]].sum().reset_index().assign(ed="all")
    tot["rate"] = tot.births / tot.women
    d = pd.concat([d, tot])
    out = outputs_dir("NSO")
    out.mkdir(parents=True, exist_ok=True)
    d.sort_values(["year", "ed", "age"]).round(4).to_csv(out / "mexico_fertility_by_education.csv", index=False)
    old = d[d.age != "20-24"]
    print("Births per woman 25-44:\n", (old.groupby(["ed", "year"]).rate.sum() * 5).unstack().round(2))
    print("Per 1,000 women 20-24:\n", (d[d.age == "20-24"].set_index(["ed", "year"]).rate * 1000).unstack().round(0))


if __name__ == "__main__":
    main()
