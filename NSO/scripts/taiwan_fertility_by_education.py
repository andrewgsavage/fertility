"""Taiwan: birth rates by mother's age and education, 2016-2025, from the household register.

Births: Ministry of the Interior open data, births by sex, mother's original nationality, age and
education, by registration date (data.gov.tw dataset 32945, API ODRP028), one file per year.
Women: women 15+ in the household register at the end of each year by age, marital status and
education (data.gov.tw 32944 for 2015-2018, wide files; 117988 for 2019-2025, long zips). Rates
use the mean of the year-end counts before and after, so the series starts in 2016.
All births are counted, including those to mothers whose original nationality is foreign; mothers
who are not yet citizens are not in the household register, so rates are slightly overstated.

Education groups:
  low       junior high or less     國小畢業以下, 國中畢業
  medium    senior high             高中畢業 (academic and vocational)
  tertiary  junior college or more  專科, 大學, 碩士, 博士

    pixi run python NSO/scripts/taiwan_fertility_by_education.py

Writes NSO/outputs/taiwan_fertility_by_education.csv (year, age, ed, births, women, rate).
"""

import io
import re
import time
import zipfile

import pandas as pd
import requests

from common.paths import data_dir, outputs_dir

UA = {"User-Agent": "Mozilla/5.0"}
API = "https://data.gov.tw/api/v2/rest/dataset/"
BIRTHS, WOMEN_OLD, WOMEN_NEW = "32945", "32944", "117988"
YEARS = range(2016, 2026)
AGES = ["20-24", "25-29", "30-34", "35-39", "40-44"]
ED = {"國小": "low", "國中": "low", "高中": "medium", "專": "tertiary", "大": "tertiary",
      "碩": "tertiary", "博": "tertiary"}


def folder():
    d = data_dir("NSO") / "twn"
    d.mkdir(parents=True, exist_ok=True)
    return d


def urls(dataset):
    """File download URL per ROC year, from the resource descriptions ('113嬰兒出生數...')."""
    dist = requests.get(API + dataset, headers=UA, timeout=60).json()["result"]["distribution"]
    out = {}
    for x in dist:
        m = re.match(r"\s*(\d{3})", x.get("resourceDescription") or "")
        u = x.get("resourceDownloadUrl") or ""
        if m and "rs-opendata/api" not in u:
            out.setdefault(int(m.group(1)), u)
    return out


def fetch(dataset, roc, url):
    path = folder() / f"{dataset}_{roc}.bin"
    for attempt in range(5):  # ris.gov.tw returns 503 now and then
        if path.exists():
            break
        r = requests.get(url, headers=UA, timeout=900)
        if r.status_code == 503 and attempt < 4:
            time.sleep(30)
            continue
        r.raise_for_status()
        path.write_bytes(r.content)
    b = path.read_bytes()
    if b[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(b))
        b = z.read(z.namelist()[0])
    return pd.read_csv(io.BytesIO(b), encoding="utf-8-sig", dtype=str)


def age5(s):
    s = s.str.replace("～", "-").str.replace("~", "-").str.replace("歲", "").str.replace(" ", "")
    return s.where(s.isin(AGES))


def ed_group(s):
    return s.map(lambda e: next((g for k, g in ED.items() if str(e).startswith(k)), None))


def births():
    out = []
    for roc, url in sorted(urls(BIRTHS).items()):
        if roc + 1911 not in YEARS:
            continue
        b = fetch(BIRTHS, roc, url)
        b.columns = ["year", "according", "site", "sex", "nation", "age", "edu", "births"]
        b = b.assign(age=age5(b.age), ed=ed_group(b.edu), births=pd.to_numeric(b.births, errors="coerce"))
        out.append(b.dropna(subset=["age", "ed"]).groupby(["age", "ed"]).births.sum().reset_index()
                   .assign(year=roc + 1911))
    return pd.concat(out, ignore_index=True)


def women_year(roc, url, wide):
    p = fetch(WOMEN_OLD if wide else WOMEN_NEW, roc, url)
    if wide:
        cols = [c for c in p.columns if c.endswith("_女_人數")]
        p = p.melt(["年齡"], cols, "col", "population").rename(columns={"年齡": "age"})
        p["edu"] = p.col.str.split("_").str[1]
    else:
        p = p[p.statistic_yyy.str.strip().str.isdigit() & (p.sex == "女")]
    p = p.assign(age=age5(p.age), ed=ed_group(p.edu), population=pd.to_numeric(p.population, errors="coerce"))
    return p.dropna(subset=["age", "ed"]).groupby(["age", "ed"]).population.sum()


def women():
    end = {}
    for wide, ds in [(True, WOMEN_OLD), (False, WOMEN_NEW)]:
        for roc, url in urls(ds).items():
            if roc + 1911 >= YEARS[0] - 1 and roc not in end:
                end[roc] = women_year(roc, url, wide)
    out = []
    for y in YEARS:
        a, b = end.get(y - 1912), end.get(y - 1911)
        if a is not None and b is not None:
            out.append(((a + b) / 2).rename("women").reset_index().assign(year=y))
    return pd.concat(out, ignore_index=True)


def main():
    d = births().merge(women(), on=["year", "age", "ed"])
    tot = d.groupby(["year", "age"])[["births", "women"]].sum().reset_index().assign(ed="all")
    d = pd.concat([d, tot], ignore_index=True)
    d["rate"] = (d.births / d.women).round(4)
    d = d.sort_values(["year", "ed", "age"])[["age", "ed", "births", "year", "women", "rate"]]
    out = outputs_dir("NSO") / "taiwan_fertility_by_education.csv"
    d.to_csv(out, index=False)
    print(d.pivot_table(index=["age"], columns=["ed", "year"], values="rate").iloc[:, ::3].round(3).to_string())
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
