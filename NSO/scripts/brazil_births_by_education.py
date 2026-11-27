"""Brazil: birth rates by mother's education, annual.

Births: DATASUS SINASC live-birth declarations by mother's residence (DNBR<year>.dbc on
ftp.datasus.gov.br), counted by mother's age (IDADEMAE) and schooling (ESCMAEAGR1, the
aggregated schooling of the 2010 birth form: 00 none ... 05 secondary incomplete, 06 secondary
complete, 07 tertiary incomplete, 08 tertiary complete, 09 unknown, 10-12 incomplete or
unspecified). Earlier files have only years of schooling (ESCMAE), which can't be matched to
the survey's levels, so the series starts with the first file that has ESCMAEAGR1.
Women: IBGE PNAD Continua, third-quarter microdata, women by age (V2009) and highest level
attained (VD3004), weighted by V1028.

Education groups (PNAD VD3004 codes in brackets):
  low       below secondary complete        (1 none, 2-3 fundamental, 4 medio incompleto)
  medium    secondary complete, or tertiary incomplete   (5, 6)
  tertiary  tertiary complete               (7)
Code 12 (secondary, completion not stated; 10-20% of births) is split between low and medium in
proportion to codes 5 and 6 at the same age. Births with unknown schooling are spread in
proportion within age.

    pixi run python NSO/scripts/brazil_births_by_education.py

Writes NSO/outputs/brazil_fertility_by_education.csv (year, age, ed, births, women, rate).
"""

import io
import re
import time
import urllib.request
import zipfile

import numpy as np
import pandas as pd
import requests

from common.dbf import dbc_to_dbf, read_dbf, to_int
from common.paths import data_dir, outputs_dir

YEARS = range(2014, 2025)
BRA_URL = "ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/DNBR{y}.dbc"
PNADC = "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/{y}/"
AGES = ["20-24", "25-29", "30-34", "35-39", "40-44"]
SCHOOL = {0: "low", 1: "low", 2: "low", 3: "low", 4: "low", 5: "low", 10: "low", 11: "low",
          6: "medium", 7: "medium", 8: "tertiary"}
PNAD_ED = {1: "low", 2: "low", 3: "low", 4: "low", 5: "medium", 6: "medium", 7: "tertiary"}
# 0-based [start, end) positions in the PNADC fixed-width file (input_PNADC_trimestral.txt)
COLS = {"V1028": (49, 64), "V2007": (94, 95), "V2009": (103, 106), "VD3004": (404, 405)}


def age_group(age):
    out = np.full(len(age), "", dtype=object)
    for a in AGES:
        out[(age >= int(a[:2])) & (age <= int(a[3:]))] = a
    return out


def birth_counts(year):
    folder = data_dir("NSO") / "bra" / "educ"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{year}.csv"
    if path.exists():
        return pd.read_csv(path)
    dbc, dbf = folder / f"DNBR{year}.dbc", folder / f"DNBR{year}.dbf"
    for attempt in range(40):  # the FTP data connection often times out
        try:
            with urllib.request.urlopen(BRA_URL.format(y=year), timeout=120) as resp:
                dbc.write_bytes(resp.read())
            break
        except OSError as e:
            print(f"  DNBR{year} attempt {attempt + 1}: {e}", flush=True)
            time.sleep(10)
    else:
        raise RuntimeError(f"DNBR{year}: download failed")
    dbc_to_dbf(dbc, dbf)
    d = read_dbf(dbf, {"IDADEMAE", "ESCMAEAGR1"})
    df = pd.DataFrame({"age": age_group(to_int(d["IDADEMAE"])), "code": to_int(d["ESCMAEAGR1"])})
    del d
    out = df[df.age != ""].value_counts().rename("births").reset_index()
    out.to_csv(path, index=False)
    dbc.unlink(missing_ok=True)
    dbf.unlink(missing_ok=True)
    print(f"SINASC {year}: {out.births.sum():,} births at 20-44", flush=True)
    return out


def women_year(year):
    folder = data_dir("NSO") / "bra_pnadc"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"women_{year}.csv"
    if path.exists():
        return pd.read_csv(path)
    listing = requests.get(PNADC.format(y=year), timeout=60).text
    name = sorted(set(re.findall(rf"PNADC_03{year}[^\"]*\.zip", listing)))[-1]
    r = requests.get(PNADC.format(y=year) + name, timeout=1800)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    txt = next(n for n in z.namelist() if n.lower().endswith(".txt"))
    rows = []
    with z.open(txt) as f:
        for line in io.TextIOWrapper(f, encoding="latin-1"):
            if line[94:95] != "2":
                continue
            rows.append((float(line[49:64]), int(line[103:106]), line[404:405]))
    d = pd.DataFrame(rows, columns=["w", "age", "level"])
    d["ed"] = pd.to_numeric(d.level, errors="coerce").map(PNAD_ED).fillna("unknown")
    d["age"] = age_group(d.age.to_numpy())
    out = d[d.age != ""].groupby(["age", "ed"]).w.sum().rename("women").reset_index()
    out.to_csv(path, index=False)
    print(f"PNADC {year} Q3 ({name}): {out.women.sum() / 1e6:.1f}M women at 20-44", flush=True)
    return out


def birth_groups(c):
    """Births by age and group. Code 12 (secondary, completion not stated) is split between
    secondary incomplete (low) and complete (medium) in proportion to codes 5 and 6 at that age."""
    w = c.pivot_table(index="age", columns="code", values="births", aggfunc="sum").fillna(0)
    share_done = w[6] / (w[5] + w[6])
    out = pd.DataFrame({e: w[[k for k, v in SCHOOL.items() if v == e and k in w]].sum(axis=1)
                        for e in ["low", "medium", "tertiary"]})
    out["low"] += w.get(12, 0) * (1 - share_done)
    out["medium"] += w.get(12, 0) * share_done
    out["unknown"] = w.sum(axis=1) - out.sum(axis=1)
    return out.stack().rename("births").reset_index().rename(columns={"code": "ed", "level_1": "ed"})


def spread(df, value):
    w = df.pivot_table(index="age", columns="ed", values=value, aggfunc="sum").fillna(0)
    known = w[["low", "medium", "tertiary"]]
    return known.div(known.sum(axis=1), axis=0).mul(w.sum(axis=1), axis=0).stack().rename(value)


def main():
    frames = []
    for y in YEARS:
        raw = birth_counts(y)
        b = birth_groups(raw)
        unk = b[b.ed == "unknown"].births.sum() / b.births.sum()
        c12 = raw[raw.code == 12].births.sum() / raw.births.sum()
        print(f"{y}: unknown schooling {unk:.1%}, secondary with completion not stated {c12:.1%}")
        frames.append(pd.concat([spread(b, "births"), spread(women_year(y), "women")], axis=1)
                      .reset_index().assign(year=y))
    d = pd.concat(frames)
    d["rate"] = d.births / d.women
    tot = d.groupby(["year", "age"])[["births", "women"]].sum().reset_index().assign(ed="all")
    tot["rate"] = tot.births / tot.women
    d = pd.concat([d, tot])
    out = outputs_dir("NSO")
    out.mkdir(parents=True, exist_ok=True)
    d.sort_values(["year", "ed", "age"]).round(4).to_csv(out / "brazil_fertility_by_education.csv", index=False)
    old = d[d.age != "20-24"]
    print("Births per woman 25-44:\n", (old.groupby(["ed", "year"]).rate.sum() * 5).unstack().round(2))
    print("Per 1,000 women 20-24:\n", (d[d.age == "20-24"].set_index(["ed", "year"]).rate * 1000).unstack().round(0))


if __name__ == "__main__":
    main()
