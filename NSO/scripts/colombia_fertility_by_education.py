"""Colombia: birth rates by mother's education, 2010-2024.

Births: DANE Estadisticas Vitales (EEVV) birth microdata, one release per year or group of years
(microdatos.dane.gov.co, direct download), by year of birth (ANO), mother's age group
(EDAD_MADRE, 5-year codes) and last level of study passed (NIV_EDUM).
Women: DANE Gran Encuesta Integrada de Hogares (GEIH), July-September of each year, person file:
women by age (P6040) and highest level reached with the last grade passed, weighted by the
monthly expansion factor over three. 2010-2020 are the "empalme" files, reweighted by DANE to
the 2018-census frame of the redesigned GEIH (P6210, weight FEX_C); 2022-2024 the redesigned GEIH
(P3042, weight FEX_C18). 2021 is left out: its public file is still weighted to the 2005-census frame
(FEX_C_2011). 2020 was interviewed by telephone.

Education groups:
  low       lower secondary or less   births 01-03, 13 (preschool, primary, basic secondary, none);
                                      GEIH none, preschool, primary, basic secondary
  medium    upper secondary            births 04-06 (media academica, media tecnica, normalista);
                                      GEIH media, normalista, and tertiary with no year passed
  tertiary  at least one year passed   births 07-12 (tecnica profesional to doctorate);
            of tertiary                GEIH superior (2010-2020) or tecnica profesional to doctorate
Births with education 99 (not stated) are spread in proportion within age.

    pixi run python NSO/scripts/colombia_fertility_by_education.py

Writes NSO/outputs/colombia_fertility_by_education.csv (year, age, ed, births, women, rate).
"""

import io
import re
import zipfile

import pandas as pd
import requests

from common.paths import data_dir, outputs_dir

UA = {"User-Agent": "Mozilla/5.0"}
SITE = "https://microdatos.dane.gov.co/index.php/catalog/"
YEARS = [y for y in range(2010, 2025) if y != 2021]  # 2021 GEIH is on the 2005-census frame
AGES = ["20-24", "25-29", "30-34", "35-39", "40-44"]
AGE_CODE = {3: "20-24", 4: "25-29", 5: "30-34", 6: "35-39", 7: "40-44"}
BIRTH_RELEASES = [375, 377, 420, 475, 519, 652, 696, 732, 775, 807, 876, 878]  # 2008-2011 ... 2024
BIRTH_ED = {1: "low", 2: "low", 3: "low", 13: "low", 4: "medium", 5: "medium", 6: "medium",
            **{k: "tertiary" for k in range(7, 13)}}
GEIH = {2010: 765, 2011: 755, 2012: 760, 2013: 761, 2014: 756, 2015: 762, 2016: 757, 2017: 763,
        2018: 758, 2019: 759, 2020: 764, 2022: 771, 2023: 782, 2024: 819}
Q3 = ("julio", "agosto", "septiembre")


def folder():
    d = data_dir("NSO") / "col"
    d.mkdir(parents=True, exist_ok=True)
    return d


def files(cid):
    """(download id, file name) pairs listed on a catalog entry's get-microdata page."""
    html = requests.get(f"{SITE}{cid}/get-microdata", headers=UA, timeout=120).text
    ids = list(dict.fromkeys(re.findall(rf"catalog/{cid}/download/(\d+)", html)))
    names = [n.strip() for n in re.findall(r"Nombre del archivo\s*</[^>]+>\s*<[^>]+>\s*([^<]+)<", html)]
    return list(zip(ids, names))


def download(cid, fid, name):
    path = folder() / f"{cid}_{fid}_{re.sub(r'[^A-Za-z0-9._-]', '_', name)}"
    if not path.exists():
        with requests.get(f"{SITE}{cid}/download/{fid}", headers=UA, stream=True, timeout=1800) as r:
            r.raise_for_status()
            tmp = path.with_suffix(".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            tmp.rename(path)
    return path


def members(z, prefix=""):
    """Every file in a zip, opening nested zips: (name, zipfile, member)."""
    for m in z.namelist():
        if m.lower().endswith(".zip"):
            yield from members(zipfile.ZipFile(io.BytesIO(z.read(m))), prefix + m + "/")
        elif not m.endswith("/"):
            yield prefix + m, z, m


def read_csv(raw, **kw):
    head = raw[:2000].decode("latin-1")
    sep = max([";", ",", "\t", "|"], key=head.count)
    t = pd.read_csv(io.BytesIO(raw), sep=sep, encoding="latin-1", decimal="," if sep == ";" else ".",
                    low_memory=False, **kw)
    t.columns = [c.strip().upper() for c in t.columns]
    return t


def births():
    out = []
    for cid in BIRTH_RELEASES:
        fs = [(i, n) for i, n in files(cid) if re.search(r"nac", n, re.I)]
        fs = sorted(fs, key=lambda x: "txt" in x[1].lower())  # non-txt first; 2012-2013 has text only in "txt"
        for fid, name in fs:
            z = zipfile.ZipFile(download(cid, fid, name))
            tables = [(n, zz, m) for n, zz, m in members(z) if n.lower().endswith((".csv", ".txt"))]
            if not tables:
                continue
            for n, zz, m in tables:
                b = read_csv(zz.read(m), usecols=lambda c: c.strip().upper() in ("ANO", "EDAD_MADRE", "NIV_EDUM"))
                if not {"ANO", "EDAD_MADRE", "NIV_EDUM"} <= set(b.columns):
                    continue
                b = b.apply(pd.to_numeric, errors="coerce")
                b = b.assign(age=b.EDAD_MADRE.map(AGE_CODE), ed=b.NIV_EDUM.map(BIRTH_ED).fillna("unknown"))
                out.append(b.dropna(subset=["age"]).groupby(["ANO", "age", "ed"]).size().rename("births")
                           .reset_index().rename(columns={"ANO": "year"}))
            break  # one copy of each release
    b = pd.concat(out).groupby(["year", "age", "ed"]).births.sum().unstack(fill_value=0)
    known = b[["low", "medium", "tertiary"]]
    b = known.mul(known.sum(axis=1) + b.get("unknown", 0), axis=0).div(known.sum(axis=1), axis=0)
    b = b.stack().rename("births").reset_index()
    return b[b.year.isin(YEARS)]


def person_files(year):
    cid = GEIH[year]
    fs = files(cid)
    if year >= 2022:
        fs = [(i, n) for i, n in fs if any(q in n.lower() for q in Q3)]
    for fid, name in fs:
        z = zipfile.ZipFile(download(cid, fid, name))
        for n, zz, m in members(z):
            low = n.lower()
            if "caracter" in low and low.endswith(".csv") and any(q in low for q in Q3 + ("dta", "csv")):
                if year < 2022 and not any(q in low for q in Q3):
                    continue
                yield zz.read(m)


def women(year):
    parts = []
    for raw in person_files(year):
        if year < 2022:
            t = read_csv(raw, usecols=lambda c: c.strip().upper() in ("P6020", "P6040", "P6210", "P6210S1", "FEX_C"))
            sex, lev, grade, w = t.P6020, t.P6210, t.P6210S1, t.FEX_C
            ed = lev.map({1: "low", 2: "low", 3: "low", 4: "low", 5: "medium", 6: "tertiary"})
            ed = ed.mask((lev == 6) & (grade == 0), "medium")
        else:
            t = read_csv(raw, usecols=lambda c: c.strip().upper() in ("P3271", "P6040", "P3042", "P3042S1", "FEX_C18"))
            sex, lev, grade, w = t.P3271, t.P3042, t.P3042S1, t.FEX_C18
            ed = lev.map({1: "low", 2: "low", 3: "low", 4: "low", 5: "medium", 6: "medium", 7: "medium",
                          **{k: "tertiary" for k in range(8, 14)}})
            ed = ed.mask((lev >= 8) & (lev <= 13) & (grade == 0), "medium")
        w = pd.to_numeric(w.astype(str).str.replace(",", "."), errors="coerce")
        age = pd.to_numeric(t.P6040, errors="coerce")
        d = pd.DataFrame({"age": pd.cut(age, [19, 24, 29, 34, 39, 44], labels=AGES).astype(str),
                          "ed": ed, "w": w})[pd.to_numeric(sex, errors="coerce") == 2]
        parts.append(d[d.age.isin(AGES)].dropna())
    if len(parts) < 3:  # 3 months; some years split each month into urban and rural files
        raise RuntimeError(f"GEIH {year}: found {len(parts)} July-September person files")
    print(year, len(parts), "person files")
    d = pd.concat(parts)
    known = d.groupby(["age", "ed"]).w.sum() / 3
    return known.rename("women").reset_index().assign(year=year)


def main():
    b = births()
    w = pd.concat([women(y) for y in YEARS], ignore_index=True)
    d = b.merge(w, on=["year", "age", "ed"])
    tot = d.groupby(["year", "age"])[["births", "women"]].sum().reset_index().assign(ed="all")
    d = pd.concat([d, tot], ignore_index=True)
    d["rate"] = (d.births / d.women).round(4)
    d["births"] = d.births.round(0)
    d["women"] = d.women.round(0)
    d = d.sort_values(["year", "ed", "age"])[["age", "ed", "births", "year", "women", "rate"]]
    out = outputs_dir("NSO") / "colombia_fertility_by_education.csv"
    d.to_csv(out, index=False)
    print(d.pivot_table(index="age", columns=["ed", "year"], values="rate").iloc[:, ::4].round(3).to_string())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
