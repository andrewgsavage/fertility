"""Birth rate by age and mother's education, other European countries, for the age-curve facet
(education_curves_facet.py).

Births: Eurostat demo_faeduc (register data) by mother's single year of age, summed to 5-year
groups 20-24 ... 40-44; unknown education spread over the known levels in proportion, within age.
Women by education and age:
  Estonia     Statistics Estonia register tables, via NSO/scripts/estonia_fertility_by_education.py
              (births also from there: RV142U, which has 40+ instead of 40-44), 2017-2025.
  the others  Eurostat lfsa_pgaed, EU Labour Force Survey, 2008-2024. Cells flagged "u" (low
              reliability) are dropped, so small groups can be missing.
Levels: ISCED 0-2, 3-4, 5-8.

Writes eurostat/outputs/fertility_by_education_europe_curves.csv.
"""

import importlib.util

import pandas as pd

from _common import DATA, OUTDIR
from common.paths import REPO

LFS = ["CZ", "EL", "HR", "HU", "LV", "MK", "PL", "PT", "RO", "RS", "SI", "SK", "TR"]
AGES = ["20-24", "25-29", "30-34", "35-39", "40-44"]
EDU = [("low", "ED0-2"), ("medium", "ED3_4"), ("tertiary", "ED5-8")]


def lfs_rates():
    codes = {c: e for e, c in EDU}
    b = pd.read_csv(DATA / "demo_faeduc.csv")
    b = b[b.geo.isin(LFS) & b.age.str.fullmatch(r"Y\d\d") & b.isced11.isin(list(codes) + ["TOTAL"])].copy()
    a = b.age.str[1:].astype(int)
    b = b[a.between(20, 44)].copy()
    lo = (a[b.index] // 5) * 5
    b["age5"] = lo.astype(str) + "-" + (lo + 4).astype(str)
    b = b.groupby(["geo", "TIME_PERIOD", "age5", "isced11"]).OBS_VALUE.sum(min_count=1).unstack()
    known = b[list(codes)].sum(axis=1)
    for c in codes:
        b[c] = b[c] / known * b["TOTAL"]
    b = b[list(codes)].rename(columns=codes).stack().rename("births")
    b.index = b.index.set_names(["geo", "year", "age", "ed"])

    p = pd.read_csv(DATA / "lfsa_pgaed.csv")
    p = p[(p.sex == "F") & p.geo.isin(LFS) & p.age.isin(["Y" + x for x in AGES]) & p.isced11.isin(list(codes))]
    p = p[~p.OBS_FLAG.fillna("").str.contains("u")]
    p = p.assign(age=p.age.str[1:], ed=p.isced11.map(codes), women=p.OBS_VALUE * 1000)
    p = p.rename(columns={"TIME_PERIOD": "year"}).set_index(["geo", "year", "age", "ed"]).women
    return pd.concat([b, p], axis=1, join="inner").dropna().reset_index()


def estonia_rates():
    path = REPO / "NSO" / "scripts" / "estonia_fertility_by_education.py"
    spec = importlib.util.spec_from_file_location("estonia_fertility_by_education", path)
    ee = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ee)
    d = ee.births().merge(ee.women(), on=["year", "age", "ed"])
    d.insert(0, "geo", "EE")
    return d[["geo", "year", "age", "ed", "births", "women"]]


def curves():
    d = pd.concat([estonia_rates(), lfs_rates()], ignore_index=True)
    d["rate"] = d.births / d.women * 1000
    t = d.pivot_table(index=["geo", "year", "age"], columns="ed", values="rate").reset_index()
    return t


def main():
    t = curves()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    t.round(1).to_csv(OUTDIR / "fertility_by_education_europe_curves.csv", index=False)
    pd.set_option("display.width", 200)
    print(t.groupby("geo").agg(y0=("year", "min"), y1=("year", "max"), n=("year", "size"),
                               low_max=("low", "max"), med_max=("medium", "max"), ter_max=("tertiary", "max"),
                               missing=("tertiary", lambda x: x.isna().sum())).round(0).to_string())


if __name__ == "__main__":
    main()
