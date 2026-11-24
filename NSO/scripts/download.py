"""Download the national-statistics-office tables behind the FT's coupling series, where
they are open and machine-readable. Writes into NSO/data/ (not tracked in git).

  Netherlands  CBS StatLine 37620: persons in households by position, sex and single-year
               age, 1 January 1995-2025 (population register).
  Denmark      Statistics Denmark FAM100N: adults by family type, sex and single-year age,
               1 January 1986-2026; BEFOLK1: population by sex and single-year age.
  Finland      Statistics Finland 12c6: population by family status, sex and single-year age,
               31 December 1992-2025.
  US           Census Bureau CPS ASEC Table AD-3 (living arrangements of adults), ages 18-24
               and 25-34, 1967-2023.

Living arrangements (living_arrangements_nso.py) also needs every household position from
CBS 37620 (nl_37620_pos_*.json) and every family status from Statistics Finland 12c6
(fi_12c6_status.json): children living with parents, living alone, other.

Statistics Canada (17-10-0060) blocks scripted downloads with a browser check, so Canada is
not included; ILO covers it.
"""

import json
import pathlib

import requests

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
UA = {"User-Agent": "Mozilla/5.0"}


def get(url, out, **kw):
    r = requests.get(url, headers=UA, timeout=300, **kw)
    r.raise_for_status()
    (DATA / out).write_bytes(r.content)
    print(f"{out}: {len(r.content):,} bytes")


def netherlands():
    cols = ["Geslacht", "Leeftijd", "Perioden", "TotaalPersonenInHuishoudens_1", "TotaalSamenwonendePersonen_5",
            "PartnerInNietGehuwdPaarZonderKi_6", "PartnerInGehuwdPaarZonderKinderen_7",
            "PartnerInNietGehuwdPaarMetKinderen_8", "PartnerInGehuwdPaarMetKinderen_9"]
    base = "https://opendata.cbs.nl/ODataApi/odata/37620"
    for sex in ["3000", "4000"]:
        get(f"{base}/TypedDataSet", f"nl_37620_{sex}.json",
            params={"$format": "json", "$filter": f"Geslacht eq '{sex}    '", "$select": ",".join(cols)})
    get(f"{base}/Leeftijd", "nl_37620_leeftijd.json", params={"$format": "json"})
    get(f"{base}/Perioden", "nl_37620_perioden.json", params={"$format": "json"})


def denmark():
    # CSV (not BULK) lets the region variable be eliminated, giving all-Denmark totals.
    get("https://api.statbank.dk/v1/data/FAM100N/CSV", "dk_fam100n.csv",
        params={"lang": "en", "FAMTYP": "*", "KØN": "*", "ALDER": "*", "Tid": "*"})
    get("https://api.statbank.dk/v1/data/BEFOLK1/CSV", "dk_befolk1.csv",
        params={"lang": "en", "KØN": "1,2", "ALDER": "*", "CIVILSTAND": "TOT", "Tid": "*"})


def finland():
    url = "https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/perh/12c6.px"
    meta = requests.get(url, headers=UA, timeout=60).json()
    codes = {v["text"]: v for v in meta["variables"]}
    query = {"query": [
        {"code": codes["Area"]["code"], "selection": {"filter": "item", "values": ["SSS"]}},
        {"code": codes["Family status"]["code"],
         "selection": {"filter": "item", "values": ["SSS", "1", "2", "3", "4"]}},
        {"code": codes["Sex"]["code"], "selection": {"filter": "item", "values": ["1", "2"]}},
        {"code": codes["Age"]["code"], "selection": {"filter": "all", "values": ["*"]}},
        {"code": codes["Year"]["code"], "selection": {"filter": "all", "values": ["*"]}},
    ], "response": {"format": "json-stat2"}}
    r = requests.post(url, headers=UA, json=query, timeout=300)
    r.raise_for_status()
    (DATA / "fi_12c6.json").write_text(json.dumps(r.json()), encoding="utf-8")
    print(f"fi_12c6.json: {len(r.content):,} bytes")


def us():
    base = "https://www2.census.gov/programs-surveys/demo/tables/families/time-series/adults"
    for t in ["ad3-18-24", "ad3-25-34"]:
        get(f"{base}/{t}.xls", f"us_{t}.xls")


def netherlands_positions():
    base = "https://opendata.cbs.nl/ODataApi/odata/37620"
    for sex in ["3000", "4000"]:
        get(f"{base}/TypedDataSet", f"nl_37620_pos_{sex}.json",
            params={"$format": "json", "$filter": f"Geslacht eq '{sex}    '"})


def finland_status():
    url = "https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/perh/12c6.px"
    meta = requests.get(url, headers=UA, timeout=60).json()
    codes = {v["text"]: v for v in meta["variables"]}
    query = {"query": [
        {"code": codes["Area"]["code"], "selection": {"filter": "item", "values": ["SSS"]}},
        {"code": codes["Family status"]["code"],
         "selection": {"filter": "item", "values": ["SSS", "1", "2", "3", "4", "5", "6", "7", "8", "9"]}},
        {"code": codes["Sex"]["code"], "selection": {"filter": "item", "values": ["1", "2"]}},
        {"code": codes["Age"]["code"], "selection": {"filter": "all", "values": ["*"]}},
        {"code": codes["Year"]["code"], "selection": {"filter": "all", "values": ["*"]}},
    ], "response": {"format": "json-stat2"}}
    r = requests.post(url, headers=UA, json=query, timeout=300)
    r.raise_for_status()
    (DATA / "fi_12c6_status.json").write_text(json.dumps(r.json()), encoding="utf-8")
    print(f"fi_12c6_status.json: {len(r.content):,} bytes")


if __name__ == "__main__":
    DATA.mkdir(exist_ok=True)
    netherlands()
    denmark()
    finland()
    us()
    netherlands_positions()
    finland_status()
