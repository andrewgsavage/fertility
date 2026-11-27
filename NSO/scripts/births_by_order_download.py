"""Download Mexico's and Brazil's birth records and count births by year of birth, mother's age
and birth order. Each raw file is deleted once counted; the counts are kept.

  Mexico  INEGI Estadística de Nacimientos Registrados (ENR) microdata, one DBF per
          registration year, 1985-2025. Order = ORDEN_PART (order of this birth, 10 = 10+;
          it agrees with HIJOS_VIVO, children born alive including this one). Year of birth
          ANO_NAC (two digits in files registered up to 1998), mother's age at the birth EDAD_MADN; 99 or
          9999 = not stated. Many births are registered years later, so births of year Y are
          summed over all registration years.
  Brazil  DATASUS SINASC live-birth declarations by mother's residence, national file per year
          of birth (DNBR<year>.dbc on ftp.datasus.gov.br), 1996-2024. Order = QTDFILVIVO
          (previous live-born children) + 1, capped at 10; mother's age IDADEMAE.

    pixi run python NSO/scripts/births_by_order_download.py [mex] [bra]

Writes NSO/data/<mex|bra>/counts/<file>.csv per raw file, then
NSO/intermediate/births_by_order_<mex|bra>.csv: year, age, order, births
(age -1 / order -1 = not stated), and births_by_file_<mex|bra>.csv: year, file, births
(file = registration year for Mexico, year of birth for Brazil).
"""

import io
import sys
import time
import urllib.request
import zipfile

import numpy as np
import pandas as pd
import requests

from common.dbf import dbc_to_dbf, read_dbf, to_int
from common.paths import data_dir, intermediate_dir

UA = {"User-Agent": "Mozilla/5.0"}
MEX_URL = "https://www.inegi.org.mx/contenidos/programas/natalidad/microdatos/{y}/natalidad_base_datos_{y}_dbf.zip"
MEX_YEARS = range(1985, 2026)
BRA_URL = "ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Dados/DNRES/DNBR{y}.dbc"
BRA_YEARS = range(1996, 2025)
MAX_ORDER = 10


def counts(year, age, order):
    age = np.where((age >= 10) & (age <= 60), age, -1)
    order = np.where(order >= 1, np.minimum(order, MAX_ORDER), -1)
    df = pd.DataFrame({"year": year, "age": age, "order": order})
    return df.value_counts().rename("births").reset_index()


def mex_file(reg_year):
    r = requests.get(MEX_URL.format(y=reg_year), headers=UA, timeout=600)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = next(n for n in z.namelist() if n.lower().startswith("nacim") and n.lower().endswith(".dbf"))
    tmp = data_dir("NSO") / "mex" / name
    tmp.write_bytes(z.read(name))
    try:
        d = read_dbf(tmp, {"ANO_NAC", "EDAD_MADN", "ORDEN_PART"})
        year = to_int(d["ANO_NAC"])
        width = d["ANO_NAC"].dtype.itemsize
        if width == 2:  # two-digit years, in files registered up to 1998; 99 = not stated
            year = np.where(year < 99, 1900 + year, -1)
        year = np.where((year >= 1900) & (year <= reg_year), year, -1)
        out = counts(year, to_int(d["EDAD_MADN"]), to_int(d["ORDEN_PART"]))
        del d
    finally:
        tmp.unlink()
    return out


def bra_file(birth_year):
    folder = data_dir("NSO") / "bra"
    dbc, dbf = folder / f"DNBR{birth_year}.dbc", folder / f"DNBR{birth_year}.dbf"
    for attempt in range(30):  # the FTP data connection often times out, sometimes for minutes
        try:
            with urllib.request.urlopen(BRA_URL.format(y=birth_year), timeout=120) as resp:
                dbc.write_bytes(resp.read())
            break
        except OSError as e:
            print(f"  DNBR{birth_year} attempt {attempt + 1}: {e}")
            time.sleep(10)
    else:
        raise RuntimeError(f"DNBR{birth_year}: download failed")
    try:
        dbc_to_dbf(dbc, dbf)
        d = read_dbf(dbf, {"IDADEMAE", "QTDFILVIVO"})
        prev = to_int(d["QTDFILVIVO"])
        order = np.where((prev >= 0) & (prev < 99), prev + 1, -1)
        out = counts(np.full(len(order), birth_year), to_int(d["IDADEMAE"]), order)
        del d
    finally:
        dbc.unlink(missing_ok=True)
        dbf.unlink(missing_ok=True)
    return out


def run(code, years, fetch):
    folder = data_dir("NSO") / code / "counts"
    folder.mkdir(parents=True, exist_ok=True)
    for y in years:
        path = folder / f"{y}.csv"
        if path.exists():
            continue
        t = time.time()
        c = fetch(y)
        c.to_csv(path, index=False)
        print(f"{code} {y}: {c.births.sum():,} births in {time.time() - t:.0f}s", flush=True)
    all_ = pd.concat([pd.read_csv(folder / f"{y}.csv").assign(file=y) for y in years])
    out = intermediate_dir("NSO")
    out.mkdir(parents=True, exist_ok=True)
    by_order = all_.groupby(["year", "age", "order"], as_index=False).births.sum()
    by_order.to_csv(out / f"births_by_order_{code}.csv", index=False)
    # births by year of birth and file (registration year for Mexico), for late-registration completion
    by_file = all_[all_.year > 0].groupby(["year", "file"], as_index=False).births.sum()
    by_file.to_csv(out / f"births_by_file_{code}.csv", index=False)
    print(f"Saved {out / f'births_by_order_{code}.csv'} and births_by_file_{code}.csv")


if __name__ == "__main__":
    which = sys.argv[1:] or ["mex", "bra"]
    if "mex" in which:
        run("mex", MEX_YEARS, mex_file)
    if "bra" in which:
        run("bra", BRA_YEARS, bra_file)
