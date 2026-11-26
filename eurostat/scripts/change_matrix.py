"""Factor-by-country change matrix, country detail and per-factor scatters.

For about 20 low-fertility countries, compares how fertility outcomes and
proposed factors changed between 2010 and 2019 (every country has data for
both years, and the window ends before COVID).

Outcomes:
- TFR: HFD tfrRR.txt (context only; countries are sorted, and factors fitted,
  on the change in % of women with a child by 30).
- First- and second-birth conditional rates by age: HFD mi.txt pooled with
  exposRRpa.txt exposures (UK: ONS cohort table 3).
- Mothers by 30 / by 45, mothers with a second child, mean age at first
  birth: a synthetic cohort run through each year's HFD period fertility
  table by birth order (pft.txt, q1x..q5px). The UK has no HFD pft, so it
  uses the ONS-based England & Wales reconstruction in
  ONS/scripts/outcome_grid_uk.py.
- Uruguay (not in HFD): TFR from MSP births over INE women; with a child by age
  from HFC first-birth rates to 2011 and MSP/INE/SIP estimates for 2013 and 2021
  (uruguay_outcomes; MSP, INE and SIP files via HFC/scripts/uruguay_by_order.py).
- Women in a couple: registers, CPS, ILO and FT by age; Eurostat lfst_hhindws
  as a lower-quality 18-24 row (Denmark and Sweden dropped for series breaks).

Factors (downloaded on first run into eurostat/data/change_matrix/):
- Eurostat: isoc_ci_im_i (mobile internet 16-24), lfsa_etpgan (temporary
  contracts 15-29), lfsi_neet_a (NEET men 15-29), yth_demo_030 (women's
  age leaving home), ilc_caindformal (formal childcare under 3),
  edat_lfse_03 (tertiary attainment, women 25-34).
- Eurostat EU-SILC: ilc_lvho05a (overcrowding rate 25-29), ilc_lvho07a
  (housing cost overburden rate 25-29); no 25-34 band is published.
- World Bank SL.UEM.1524.ZS (youth unemployment, ILO modelled).
- OECD analytical house price indicators (price-to-income ratio).

Child:coupling ratios and coupling by age (country detail):
- % of women with a child: HFD exposRRpa.txt (UK: ONS cohort table 3).
- Coupling: NSO/outputs/coupling_nso.csv, ILO/outputs/coupling_ilo.csv,
  UN/outputs/coupling_un.csv, FT/outputs/ft_coupling_25_34.csv and
  ONS/outputs/coupling_by_age_ew.csv; each falls back to a copy in
  eurostat/data/change_matrix/main/ when the branch doesn't have it.

Ideal and intended number of children (women, by age): GGS/outputs/ideal_matrix_europe.csv
(Eurobarometer 2011 to GGS-II 2020-23, from published tables) and GSS/outputs/ideal_matrix_us.csv
(GSS, pooled survey years). Ends up to 3 years from the window's ends.

Run with cwd = eurostat/.
"""

import io
import itertools
import json
import math
import pathlib
import sys
import urllib.request
import zipfile

import pandas as pd
import plotly.graph_objects as go

ROOT = pathlib.Path(__file__).resolve().parents[2]
CACHE = ROOT / "eurostat" / "data" / "change_matrix"
HFD = ROOT / "HFD" / "data" / "HFD"
OUT = ROOT / "eurostat" / "outputs"
sys.path.insert(0, str(ROOT / "ONS" / "scripts"))

BASE, END = 2010, 2019
PRECEDING = (2005, 2010)  # same countries and order, for what moved before the fall

# ISO3 -> (Eurostat code, name, HFD code)
COUNTRIES = {
    "FIN": ("FI", "Finland"), "NOR": ("NO", "Norway"), "SWE": ("SE", "Sweden"), "DNK": ("DK", "Denmark"),
    "NLD": ("NL", "Netherlands"), "BEL": ("BE", "Belgium"), "IRL": ("IE", "Ireland"), "GBR": ("UK", "UK (E&W)"),
    "AUT": ("AT", "Austria"), "CHE": ("CH", "Switzerland"), "ESP": ("ES", "Spain"), "PRT": ("PT", "Portugal"),
    "SVN": ("SI", "Slovenia"), "EST": ("EE", "Estonia"), "LTU": ("LT", "Lithuania"), "CZE": ("CZ", "Czechia"),
    "HUN": ("HU", "Hungary"), "BGR": ("BG", "Bulgaria"), "USA": (None, "United States"),
    "CAN": (None, "Canada"), "JPN": (None, "Japan"), "KOR": (None, "South Korea"),
    # No usable HFD birth-order series for 2010-2019, except Croatia.
    "DEU": ("DE", "Germany"), "FRA": ("FR", "France"), "ITA": ("IT", "Italy"), "GRC": ("EL", "Greece"),
    "POL": ("PL", "Poland"), "ROU": ("RO", "Romania"), "HRV": ("HR", "Croatia"), "LVA": ("LV", "Latvia"),
    "SVK": ("SK", "Slovakia"), "CYP": ("CY", "Cyprus"), "MLT": ("MT", "Malta"),
    "ISL": ("IS", "Iceland"), "AUS": (None, "Australia"), "NZL": (None, "New Zealand"),
    "CHL": (None, "Chile"), "URY": (None, "Uruguay"), "TWN": (None, "Taiwan"),  # Uruguay is not in HFD: see uruguay_outcomes()
}
# Region, for grouping countries in the matrix. "English-speaking" is outside Europe; GBR and IRL sit with Western Europe.
REGION_MEMBERS = {
    "Nordic": ("DNK", "FIN", "ISL", "NOR", "SWE"),
    "Western Europe": ("AUT", "BEL", "CHE", "DEU", "FRA", "GBR", "IRL", "NLD"),
    "Southern Europe": ("CYP", "ESP", "GRC", "ITA", "MLT", "PRT"),
    "Central & Eastern Europe": ("BGR", "CZE", "EST", "HRV", "HUN", "LTU", "LVA", "POL", "ROU", "SVK", "SVN"),
    "English-speaking": ("AUS", "CAN", "NZL", "USA"),
    "East Asia": ("JPN", "KOR", "TWN"),
    "Latin America": ("CHL", "URY"),
}
REGIONS = {iso: r for r, members in REGION_MEMBERS.items() for iso in members}
assert set(REGIONS) == set(COUNTRIES), set(COUNTRIES) ^ set(REGIONS)
HFD_TFR_CODES = {"GBRTENW": "GBR", "DEUTNP": "DEU", "FRATNP": "FRA"}
# % with a child by 30 where HFD has no birth-order table for 2010-2019: first-birth rates summed to age 29.
# France's birth-order series breaks between 2006 and 2013, so only 2013 onward is used.
ESTIMATE_HFC = ("ITA", "POL", "ISL")
ESTIMATE_EUROSTAT = ("GRC", "MLT", "CYP", "DEU", "LVA", "SVK", "ROU", "FRA")
EUROSTAT_ORDER_FROM = {"FRA": 2013}
CHILD_AGES = (25, 30, 35, 40)
# How far a census year may sit from the window's ends. Uruguay's with-a-child estimates after 2011
# are for 2013 and 2021 only.
CENSUS_TOL = {"AUS": 2, "NZL": 3, "FRA": 3, "URY": 2}
# Countries whose % with a child is known only in some years: a child:coupling ratio uses the same year
# for both, not the nearest within two years.
RATIO_SAME_YEAR = ("URY",)
COUPLING_TOL = {"AUS": 2}  # ILO series for Australia ends in 2017
COUPLING_TOL_ROWS = ("couple_under_25", "couple_25_34")
# Abortions per 100 births of the same order (eurostat/scripts/abortion_parity.py). England & Wales and
# Spain start in 2013, so their 2010 end may sit three years off.
ABORTION_ORDER = OUT / "abortion_order_ratio.csv"
ABORTION_AGES = {"20_24": "20–24", "25_29": "25–29", "30_34": "30–34", "35": "35+"}
# DHSC publishes parity for 20–34 as one group, so England & Wales's 20–34 ratio fills each of its
# 5-year cells. Those cells are indicative: faded and left out of counts and fits.
ABORTION_SPREAD = {"GBR": ("20–34", ("20–24", "25–29", "30–34"))}
ABORTION_SPREAD_NOTE = ("Indicative: DHSC publishes parity for 20–34 as one group, so this is the 20–34 value. "
                        "It averages the three 5-year groups and hides differences between them.")
ABORTION_ROWS = {f"abort_{kind}_{a}": (col, age) for kind, col in (("first", "first_pregnancies"), ("later", "later_pregnancies"))
                 for a, age in ABORTION_AGES.items()}
ABORTION_TOL = {"GBR": 3, "ESP": 3}
ABORTION_NAMES = {"England & Wales": "GBR"}
# Census women in a couple. Every country is shown; a change counts in summaries only if another series confirms it:
# within 3 points of EU-LFS at 25-49, a national register, the FT or ILO, and not contradicted by another of them.
CENSUS_COUPLE_PASSED = {
    (2011, 2021): ("AUS", "AUT", "CAN", "CZE", "DNK", "EST", "FIN", "FRA", "GBR", "IRL", "NLD"),
    (2001, 2011): ("DEU", "DNK", "FIN", "GBR", "NLD", "POL"),
    (2006, 2011): ("CAN",),
    (2010, 2020): ("JPN", "KOR"),
    (2005, 2010): ("JPN", "KOR"),
}
CENSUS_COUPLE_ROWS = {"couple_census_20_24": ("Y20-24",), "couple_census_25_29": ("Y25-29",),
                      "couple_census_30_34": ("Y30-34",), "couple_census_25_34": ("Y25-29", "Y30-34"),
                      "couple_census_35_39": ("Y35-39",)}
# Lets 2005 reach the 2001 round. New Zealand's nearest censuses are 2013 and 2018.
CENSUS_COUPLE_TOL = {**{c: 4 for c in COUNTRIES}, "NZL": 3}
CENSUS_COUPLE_SOURCES = {"AUS": "ABS census", "CAN": "Statistics Canada census", "NZL": "Stats NZ census",
                         "GBR": "ONS census, England and Wales", "JPN": "Japan census", "KOR": "Korea census"}
# Women with a spouse by actual status, registered or not, and women of stated status.
# Japan: Statistics Bureau census via IPSS Population Statistics table 6-22, unknown status excluded
# (not the 2015-20 imputed values, which IPSS table 6-24 uses). Korea: KOSIS census tables
# DT_1IN1005 (2010) and DT_1IN2010 (2020), Korean nationals; 2005 table includes foreigners.
JP_COUPLES = {
    2005: {"Y20-24": (373193, 3594020), "Y25-29": (1559535, 4077733), "Y30-34": (3025065, 4814114), "Y35-39": (3135144, 4249123)},
    2010: {"Y20-24": (294389, 3096818), "Y25-29": (1303214, 3516523), "Y30-34": (2460055, 4044480), "Y35-39": (3317927, 4755116)},
    2020: {"Y20-24": (195541, 2748299), "Y25-29": (978633, 2756563), "Y30-34": (1842521, 3036367), "Y35-39": (2447690, 3481229)},
}
KR_COUPLES = {
    2005: {"Y20-24": (107851, 1746221), "Y25-29": (727599, 1813515), "Y30-34": (1592897, 2036369), "Y35-39": (1777875, 2047117)},
    2010: {"Y20-24": (55513, 1430049), "Y25-29": (521499, 1736144), "Y30-34": (1252830, 1828951), "Y35-39": (1663574, 2038914)},
    2020: {"Y20-24": (28197, 1522680), "Y25-29": (278457, 1609335), "Y30-34": (753196, 1452932), "Y35-39": (1267689, 1752500)},
}
# ONS census via Nomis, women 25-34 living in a couple and all women, England and Wales:
# ST004 (2001), LC1108EW (2011), RM067 (2021). 2011 and 2021 publish 16-24, not 20-24: the UK's 20-24 cell
# uses 16-24 for 2011-2021, faded and left out of counts, and Eurostat's whole-UK 20-24 for 2001-2011.
EW_COUPLES = {2001: {"Y25-34": (2370854, 3753600)},
              2011: {"Y25-34": (2243996, 3739779), "Y16-24": (519518, 3097772), "Y35-49": (4142440, 5999359)},
              2021: {"Y25-34": (2353019, 4108906), "Y16-24": (389167, 2878801), "Y35-49": (4068921, 5868344)}}
CENSUS_COUPLE_WIDER_BAND = {"couple_census_20_24": {"GBR": "Y16-24"}, "couple_census_35_39": {"GBR": "Y35-49"}}
# Stats NZ CEN23_POP_010, women, partnered and non-partnered, New Zealand.
NZ_COUPLES = {
    2013: {"Y20-24": (42657, 90738), "Y25-29": (72933, 50901), "Y30-34": (89664, 36891), "Y35-39": (98970, 34806)},
    2018: {"Y20-24": (35487, 84417), "Y25-29": (80166, 55440), "Y30-34": (100236, 36660), "Y35-39": (100932, 31257)},
    2023: {"Y20-24": (34029, 108519), "Y25-29": (76917, 77382), "Y30-34": (114825, 63654), "Y35-39": (116580, 51117)},
}
# European Social Survey integrated files, downloaded by hand after login to eurostat/data/ess/.
# Two rounds are pooled at each point; a country needs both rounds and this many women aged 25-34.
# Ideal and intended number of children. Europe compares Eurobarometer 2011 with GGS-II (2020-23), so the end
# sits 1-3 years after 2019; the US pools GSS survey years around 2005, 2010 and 2018.
IDEAL_FILES = (ROOT / "GGS" / "outputs" / "ideal_matrix_europe.csv", ROOT / "GSS" / "outputs" / "ideal_matrix_us.csv")
IDEAL_ROWS = ("ideal_young", "ideal_30s", "intended_young", "intended_30s")
IDEAL_TOL = {c: 3 for c in COUNTRIES}
ESS_POINTS = {2005: (2, 3), 2011: (5, 6), 2017: (8, 9)}
ESS_MIN_WOMEN = 150
ESS_TOL = {c: 2 for c in COUNTRIES}
CENSUS_SOURCES = {"AUS": "ABS census, children ever born; mean of the two 5-year age groups either side",
                  "NZL": "Stats NZ census, children born; mean of the two 5-year age groups either side"}
# Stats NZ Aotearoa Data Explorer, women with no children and total stated, New Zealand:
# CEN18_POP_005 for 2006, 2013 and 2018, CEN23_MAO_048 for 2023.
NZ_CENSUS = {  # year: {age group start: (no children, total stated)}
    2006: {20: (97431, 124062), 25: (65100, 115209), 30: (46014, 136188), 35: (28836, 149019), 40: (22221, 153300)},
    2013: {20: (103599, 131955), 25: (70605, 122148), 30: (44175, 124833), 35: (27309, 132015), 40: (24180, 151257)},
    2018: {20: (116163, 137526), 25: (93420, 149820), 30: (53772, 146694), 35: (29622, 140604), 40: (23100, 141894)},
    2023: {20: (134757, 150915), 25: (114111, 163932), 30: (81312, 186786), 35: (42999, 172965), 40: (28848, 158571)},
}
M30_ESTIMATES = {**{c: "estimate, Human Fertility Collection first-birth rates" for c in ESTIMATE_HFC},
                 **{c: "estimate, Eurostat first births per woman" for c in ESTIMATE_EUROSTAT},
                 "FRA": "estimate, Eurostat first births per woman, 2013 onward (series break)",
                 "URY": "estimate, Human Fertility Collection first-birth rates to 2011; "
                        "MSP births by age × SIP first-birth shares over INE women, 2013 and 2021"}
EU2ISO = {v[0]: k for k, v in COUNTRIES.items() if v[0]}
EUROSTAT_COUPLE_BREAKS = ("DNK", "SWE")  # jumps of 15-25 points between years
MIN_FIT_N = 10  # below this a cross-country correlation isn't shown

EUROSTAT = {
    "demo_find": "A.TOTFERRT.",
    "demo_fordagec": "A.NR..1.",
    "demo_pjan": "A.NR..F.",
    "lfst_hhindws": "A.F.Y18-24+Y25-49.A_CPL+TOTAL.THS_PER.POP.",
    "isoc_ci_im_i": "A.I_IUMP.PC_IND.Y16_24.",
    "lfsa_etpgan": "A.PC.T..TOTAL.",
    "lfsi_neet_a": "",
    "yth_demo_030": "",
    "ilc_caindformal": "A.Y_LT3.H0.PC.",
    "edat_lfse_03": "A..Y25-34.PC.ED5-8.",
    "ilc_lvho05a": "A.PC.TOTAL.Y25-29.T.",
    "ilc_lvho07a": "A.PC.TOTAL.Y25-29.T.",
    "ilc_lvps08": "A.Y20-24+Y25-29+Y25-34.F.PC.",
}
LFS_ALONE = "A.F.Y18-24.A1_NCH+TOTAL.THS_PER.POP."  # lfst_hhindws: one adult, no children


def fetch(name, url):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        print("downloading", url)
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    return path


def eurostat(code):
    key = EUROSTAT[code]
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}/{key}?format=SDMX-CSV"
    if code in ("demo_fordagec", "demo_pjan"):
        url += "&startPeriod=2000&endPeriod=2024"
    d = pd.read_csv(fetch(f"{code}.csv", url), low_memory=False)
    d = d[d.geo.isin(EU2ISO)].copy()
    d["iso"] = d.geo.map(EU2ISO)
    d["year"] = d.TIME_PERIOD.astype(int)
    # Drop observations Eurostat flags "u" (low reliability).
    d = d[~d.OBS_FLAG.fillna("").astype(str).str.contains("u")]
    return d.dropna(subset=["OBS_VALUE"])


def series(d):
    """DataFrame(iso, year, value) -> {iso: {year: value}}"""
    out = {}
    for iso, year, v in d[["iso", "year", "value"]].itertuples(index=False):
        if pd.notna(v):
            out.setdefault(iso, {})[int(year)] = float(v)
    return out


# ---------- factors ----------

def census_couple_table(code, extra="&unit=NR", statuses=("TOTAL", "CPL", "UNK")):
    """{(geo, age, status): women} from a Eurostat census table."""
    ages = "".join(f"&age={a}" for a in ("Y20-24", "Y25-29", "Y30-34", "Y35-39"))
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/" + code +
           "?lang=EN&sex=F&geoLevel=country" + extra + "".join(f"&hhstatus={h}" for h in statuses) + ages)
    d = json.loads(fetch(f"{code}_couples_20_39.json", url).read_text(encoding="utf-8"))
    cats = [sorted(d["dimension"][k]["category"]["index"], key=d["dimension"][k]["category"]["index"].get) for k in d["id"]]
    out = {}
    for pos, combo in enumerate(itertools.product(*cats)):
        v = d["value"].get(str(pos))
        if v is not None:
            r = dict(zip(d["id"], combo))
            out[(r["geo"], r["age"], r["hhstatus"])] = v
    return out


def australia_couples():
    """{year: {age: (in a couple, total)}}, married or de facto, from the Time Series Profile table T05."""
    url = "https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_TSP_AUS_for_AUS_short-header.zip"
    row = {}
    with zipfile.ZipFile(fetch("abs_2021_TSP_AUS.zip", url)) as z:
        for name in z.namelist():
            if "_T05" in name and name.endswith(".csv"):
                row.update(pd.read_csv(io.BytesIO(z.read(name))).iloc[0].to_dict())
    return {year: {f"Y{a}-{b}": (row[f"C{year % 100}_{a}_{b}_Mar_RegM_F"] + row[f"C{year % 100}_{a}_{b}_Mar_DFM_F"],
                                 row[f"C{year % 100}_{a}_{b}_Tot_F"]) for a, b in ((20, 24), (25, 29), (30, 34), (35, 39))}
            for year in (2011, 2016, 2021)}


def canada_couples():
    """{year: {age: (in a couple, total)}}, married or common-law, Statistics Canada table 98-10-0125-01."""
    url = "https://www150.statcan.gc.ca/n1/tbl/csv/98100125-eng.zip"
    with zipfile.ZipFile(fetch("statcan_98100125.zip", url)) as z:
        with z.open("98100125.csv") as fh:
            d = pd.read_csv(fh, low_memory=False)
    d = d[(d.GEO == "Canada") & (d["Gender (3a)"] == "Women+")]
    cols = {"Y20-24": "Age (16):20 to 24 years[3]", "Y25-29": "Age (16):25 to 29 years[4]", "Y30-34": "Age (16):30 to 34 years[5]",
            "Y35-39": "Age (16):35 to 39 years[6]"}
    out = {}
    for year, x in d.groupby("Census year (4)"):
        x = x.set_index("Marital status (13)")
        out[int(year)] = {a: (float(x.loc["Married or living common-law", c]), float(x.loc["Total - Marital status", c]))
                          for a, c in cols.items()}
    return out


def load_ess_couples():
    """% of women 25-34 living with a partner, pooled ESS rounds: ({iso: {year: %}}, {iso: {year: standard error}})."""
    geo = {**EU2ISO, "GB": "GBR", "GR": "GRC"}
    wanted = ("cntry", "gndr", "agea", "pspwght", "partner", "icpart1", "rshpsts")
    frames = []
    for round_ in sorted(r for rounds in ESS_POINTS.values() for r in rounds):
        files = list((CACHE.parent / "ess").glob(f"ESS{round_}e*.zip"))
        if not files:
            print(f"ESS round {round_} not found; the ESS row is left out")
            return {}, {}
        with zipfile.ZipFile(files[0]) as z:
            with z.open(next(n for n in z.namelist() if n.lower().endswith(".csv"))) as fh:
                d = pd.read_csv(fh, usecols=lambda c: c in wanted, low_memory=False)
        # "partner" (rounds 1-4) and "icpart1" (rounds 5-8): 1 lives with a partner, 2 does not.
        # "rshpsts" (round 9): 1-6 type of relationship with the partner in the household, 66 no partner.
        if "partner" in d or "icpart1" in d:
            couple = (d["partner"] if "partner" in d else d["icpart1"]).map({1: 1.0, 2: 0.0})
        else:
            couple = d["rshpsts"].map({**{v: 1.0 for v in range(1, 7)}, 66: 0.0})
        d = d.assign(round=round_, couple=couple)
        frames.append(d[(d.gndr == 2) & d.agea.between(25, 34) & d.couple.notna()])
    d = pd.concat(frames)
    d = d[d.cntry.isin(geo)]
    shares, errors = {}, {}
    for cntry, g in d.groupby("cntry"):
        for year, rounds in ESS_POINTS.items():
            x = g[g["round"].isin(rounds)]
            if x["round"].nunique() < 2 or len(x) < ESS_MIN_WOMEN:
                continue
            share = (x.couple * x.pspwght).sum() / x.pspwght.sum()
            effective_n = x.pspwght.sum() ** 2 / (x.pspwght ** 2).sum()
            shares.setdefault(geo[cntry], {})[year] = 100 * share
            errors.setdefault(geo[cntry], {})[year] = 100 * (share * (1 - share) / effective_n) ** 0.5
    return shares, errors


def load_census_couples():
    """% of women in a couple, of those with a stated status, at each census."""
    tables = {2001: (census_couple_table("cens_01nhtype", "", ("TOTAL", "MAR", "CSU", "UNK")), ("MAR", "CSU")),
              2011: (census_couple_table("cens_11fs_r3"), ("CPL",)),
              2021: (census_couple_table("cens_21fe_r2", "&unit=NR&isced11=TOTAL"), ("CPL",))}
    national = {"AUS": australia_couples(), "CAN": canada_couples(),
                "NZL": {y: {a: (c, c + n) for a, (c, n) in v.items()} for y, v in NZ_COUPLES.items()},
                "GBR": EW_COUPLES, "JPN": JP_COUPLES, "KOR": KR_COUPLES}
    rows = {k: {} for k in CENSUS_COUPLE_ROWS}
    sources = {k: {} for k in CENSUS_COUPLE_ROWS}
    for key, ages in CENSUS_COUPLE_ROWS.items():
        for iso, (geo, _) in COUNTRIES.items():
            if not geo:
                continue
            for year, (t, couple) in tables.items():
                try:
                    stated = sum(t[(geo, a, "TOTAL")] - t.get((geo, a, "UNK"), 0) for a in ages)
                    rows[key].setdefault(iso, {})[year] = 100 * sum(t[(geo, a, h)] for a in ages for h in couple) / stated
                except KeyError:
                    continue
        for iso, by_year in national.items():
            # A national table may publish 25-34 only as one band.
            use = ages if all(a in next(iter(by_year.values())) for a in ages) else (f"{ages[0][:3]}-{ages[-1][-2:]}",)
            if not all(a in next(iter(by_year.values())) for a in use):
                continue
            rows[key][iso] = {y: 100 * sum(v[a][0] for a in use) / sum(v[a][1] for a in use) for y, v in by_year.items()}
            sources[key][iso] = CENSUS_COUPLE_SOURCES[iso]
        # A wider band stands in only for windows its years cover; a narrower band elsewhere stays.
        for iso, band in CENSUS_COUPLE_WIDER_BAND.get(key, {}).items():
            by_year = {y: v[band] for y, v in national[iso].items() if band in v}
            if near_year(by_year, BASE, CENSUS_COUPLE_TOL[iso]) and near_year(by_year, END, CENSUS_COUPLE_TOL[iso]):
                rows[key][iso] = {y: 100 * c / t for y, (c, t) in by_year.items()}
                sources[key][iso] = f"{CENSUS_COUPLE_SOURCES[iso]}, {band[1:].replace('-', '–')}"
        for iso in rows[key]:
            sources[key].setdefault(iso, "Eurostat census")
    return rows, sources


def load_factors():
    f = {}

    d = eurostat("lfst_hhindws")
    p = d.pivot_table(index=["iso", "year", "age"], columns="phhcomp", values="OBS_VALUE").reset_index()
    p["value"] = 100 * p.A_CPL / p.TOTAL
    f["couple_25_49"] = series(p[p.age == "Y25-49"])
    f["couple_18_24"] = series(p[p.age == "Y18-24"])
    for key in ("couple_25_49", "couple_18_24"):
        for iso in EUROSTAT_COUPLE_BREAKS:
            f[key].pop(iso, None)

    d = eurostat("isoc_ci_im_i").rename(columns={"OBS_VALUE": "value"})
    f["mobile_internet"] = series(d)

    d = eurostat("lfsa_etpgan")
    d = d[(d.age == "Y15-29") & (d.sex == "T")].rename(columns={"OBS_VALUE": "value"})
    f["temp_contracts"] = series(d)

    d = eurostat("lfsi_neet_a")
    d = d[(d.age == "Y15-29") & (d.sex == "M") & (d.unit == "PC_POP")]
    if "training" in d.columns:
        d = d[d.training == "NO_FE_NO_NFE"]
    if "wstatus" in d.columns:
        d = d[d.wstatus == "NEMP"]
    f["neet_men"] = series(d.rename(columns={"OBS_VALUE": "value"}))

    d = eurostat("yth_demo_030")
    f["leaving_home"] = series(d[d.sex == "F"].rename(columns={"OBS_VALUE": "value"}))

    d = eurostat("ilc_caindformal")
    d = d.assign(value=100 - d.OBS_VALUE)
    f["childcare"] = series(d)

    d = eurostat("edat_lfse_03")
    f["tertiary_women"] = series(d[d.sex == "F"].rename(columns={"OBS_VALUE": "value"}))

    d = eurostat("ilc_lvps08")
    for age in ("20-24", "25-29", "25-34"):
        f[f"parents_{age.replace('-', '_')}"] = series(d[d.age == f"Y{age}"].rename(columns={"OBS_VALUE": "value"}))

    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/{LFS_ALONE}?format=SDMX-CSV"
    d = pd.read_csv(fetch("lfst_hhindws_alone.csv", url), low_memory=False)
    d = d[d.geo.isin(EU2ISO) & ~d.OBS_FLAG.fillna("").astype(str).str.contains("u")].dropna(subset=["OBS_VALUE"])
    d = d.assign(iso=d.geo.map(EU2ISO), year=d.TIME_PERIOD.astype(int))
    p = d.pivot_table(index=["iso", "year"], columns="phhcomp", values="OBS_VALUE").reset_index()
    f["alone_18_24"] = series(p.assign(value=100 * p.A1_NCH / p.TOTAL))
    for iso in EUROSTAT_COUPLE_BREAKS:
        f["alone_18_24"].pop(iso, None)

    d = pd.read_csv(ROOT / "NSO" / "outputs" / "living_arrangements_nso.csv")
    d = d[(d.age == "25-34") & (d.sex == "Women") & d.country.isin(NSO_ISO)]
    f["alone_25_34"] = series(d.assign(iso=d.country.map(NSO_ISO), value=d.alone))

    for code, key in (("ilc_lvho05a", "overcrowded_25_29"), ("ilc_lvho07a", "overburden_25_29")):
        f[key] = series(eurostat(code).rename(columns={"OBS_VALUE": "value"}))

    WB_CODES = [c for c in COUNTRIES if c != "TWN"]  # the World Bank has no Taiwan series
    url = ("https://api.worldbank.org/v2/country/" + ";".join(WB_CODES)
           + "/indicator/SL.UEM.1524.ZS?format=json&per_page=5000&date=2000:2023")
    rows = json.loads(fetch(f"wb_youth_unemployment_{len(WB_CODES)}.json", url).read_text())[1]
    f["youth_unemployment"] = {}
    for r in rows:
        if r["value"] is not None:
            f["youth_unemployment"].setdefault(r["countryiso3code"], {})[int(r["date"])] = r["value"]

    url = ("https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/"
           ".A.HPI_YDH..?startPeriod=2000&endPeriod=2024&format=csvfilewithlabels")
    d = pd.read_csv(fetch("oecd_price_to_income.csv", url))
    d = d[d.REF_AREA.isin(COUNTRIES) & (d.MEASURE == "HPI_YDH")].rename(columns={"REF_AREA": "iso", "TIME_PERIOD": "year", "OBS_VALUE": "value"})
    f["price_to_income"] = series(d)
    return f


def load_ideals():
    """({row key: {iso: {year: mean children}}}, {row key: {iso: source}})"""
    d = pd.concat([pd.read_csv(f) for f in IDEAL_FILES if f.exists()])
    series_, sources = {k: {} for k in IDEAL_ROWS}, {k: {} for k in IDEAL_ROWS}
    for r in d.itertuples():
        series_[r.key].setdefault(r.iso, {})[int(r.year)] = r.value
        sources[r.key][r.iso] = r.source
    return series_, sources


def load_abortion_order():
    """{row key: {iso: {year: abortions per 100 births of the same order}}}"""
    d = pd.read_csv(ABORTION_ORDER)
    iso = {**{v[1]: k for k, v in COUNTRIES.items()}, **ABORTION_NAMES}
    d = d[d.country.isin(iso)].assign(iso=lambda x: x.country.map(iso))
    for c, (wide, narrow) in ABORTION_SPREAD.items():
        w = d[(d.iso == c) & (d.age == wide)]
        d = pd.concat([d[~((d.iso == c) & d.age.isin(narrow))], *[w.assign(age=a) for a in narrow]])
    out = {}
    for key, (col, age) in ABORTION_ROWS.items():
        out[key] = series(d[d.age == age].rename(columns={col: "value"}))
    return out


# (key, label, direction, factor page or None, group)
# direction +1: a rise is proposed to lower fertility; -1: a fall is.
COUPLE_GROUP = "Women in a couple"
RATIO_GROUP = "Couples with a child"
PARENTS_GROUP = "Women living with their parents"
ALONE_GROUP = "Women living alone"
UNSIGNED = ("alone_18_24", "alone_25_34")  # no proposed direction: coloured by rise or fall, left out of counts
ABORTION_GROUPS = {"first": "First pregnancies ended by abortion", "later": "Later pregnancies ended by abortion"}
IDEAL_GROUP = "Ideal number of children"
INTENDED_GROUP = "Intended number of children"
GROUP_NOTES = {COUPLE_GROUP: "% of women living with a partner, married or not",
               ABORTION_GROUPS["first"]: "abortions to women with no children per 100 first births",
               ABORTION_GROUPS["later"]: "abortions to mothers per 100 second or later births",
               RATIO_GROUP: "% of women with a child by the given age ÷ % in a couple in the age band",
               PARENTS_GROUP: "% of women in the age band",
               ALONE_GROUP: "% of women in the age band; purple rose, grey fell, no proposed direction",
               IDEAL_GROUP: "women's mean personal ideal: Eurobarometer 2011 to GGS-II 2020–23; US: GSS ideal for a family",
               INTENDED_GROUP: "women's mean intended number, including children already born: Eurobarometer 2011 to GGS-II 2020–23"}
FACTORS = [
    ("couple_18_24", "18–24 · EU-LFS", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_under_25", "Under 25 · registers, ILO", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_25_34", "25–34 · registers, ILO, FT", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_25_29", "25–29 · registers, ONS", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_30_34", "30–34 · registers, ONS", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_35_39", "35–39 · registers, ONS", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_census_20_24", "20–24 · census", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_census_25_29", "25–29 · census", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_census_30_34", "30–34 · census", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_census_25_34", "25–34 · census", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_census_35_39", "35–39 · census", -1, "partnership-formation", COUPLE_GROUP),
    ("couple_ess_25_34", "25–34 · ESS survey", -1, "partnership-formation", COUPLE_GROUP),
    *[(k, ABORTION_AGES[k.split("_", 2)[2]], +1, "abortion-by-age", ABORTION_GROUPS[k.split("_", 2)[1]])
      for k in ABORTION_ROWS],
    ("parents_20_24", "20–24 · EU-SILC", +1, "living-arrangements", PARENTS_GROUP),
    ("parents_25_29", "25–29 · EU-SILC", +1, "living-arrangements", PARENTS_GROUP),
    ("parents_25_34", "25–34 · EU-SILC", +1, "living-arrangements", PARENTS_GROUP),
    ("alone_18_24", "18–24 · EU-LFS", +1, "living-arrangements", ALONE_GROUP),
    ("alone_25_34", "25–34 · registers, CPS", +1, "living-arrangements", ALONE_GROUP),
    ("ideal_young", "Women under 30 · Eurobarometer, GGS, GSS", -1, "ideal-family-size", IDEAL_GROUP),
    ("ideal_30s", "Women in their 30s · Eurobarometer, GGS, GSS", -1, "ideal-family-size", IDEAL_GROUP),
    ("intended_young", "Women under 30 · Eurobarometer, GGS", -1, "ideal-family-size", INTENDED_GROUP),
    ("intended_30s", "Women in their 30s · Eurobarometer, GGS", -1, "ideal-family-size", INTENDED_GROUP),
    ("leaving_home", "Women's age leaving home", +1, "leaving-home", "Life course"),
    ("tertiary_women", "Women 25–34 with a degree", +1, "education", "Life course"),
    ("youth_unemployment", "Unemployment, 15–24", +1, "job-insecurity", "Work and costs"),
    ("temp_contracts", "Temporary contracts, 15–29", +1, "job-insecurity", "Work and costs"),
    ("neet_men", "Young men not in work or study", +1, "left-behind-young-men", "Work and costs"),
    ("price_to_income", "House price to income", +1, "housing", "Work and costs"),
    ("overcrowded_25_29", "Overcrowded, 25–29", +1, "housing", "Work and costs"),
    ("overburden_25_29", "Housing cost overburden, 25–29", +1, "housing", "Work and costs"),
    ("childcare", "Under-3s in formal childcare", -1, None, "Policy"),
    ("mobile_internet", "Mobile internet use, 16–24", +1, "smartphones", "Technology"),
]
UNITS = {"leaving_home": " yrs", "price_to_income": " (index)", "youth_unemployment": "%"}
UNITS.update({k: " children" for k in IDEAL_ROWS} | {k: " per 100 births" for k in ABORTION_ROWS})
DP = {k: 2 for k in IDEAL_ROWS}  # means of about 2 children: 1 dp hides the change


# ---------- outcomes ----------

def load_tfr():
    d = pd.read_csv(HFD / "tfrRR.txt", sep=r"\s+", skiprows=2)
    out = {}
    for code, year, tfr in d[["Code", "Year", "TFR"]].itertuples(index=False):
        iso = HFD_TFR_CODES.get(code, code)
        if iso in COUNTRIES:
            out.setdefault(iso, {})[int(year)] = float(tfr)
    # Where HFD doesn't span both windows, use one other source for the whole series.
    missing = [c for c in COUNTRIES if any(value_near(out.get(c, {}), y) is None for y in (*PRECEDING, END))]
    d = eurostat("demo_find")
    other = series(d.rename(columns={"OBS_VALUE": "value"}))
    url = ("https://api.worldbank.org/v2/country/AUS;NZL/indicator/SP.DYN.TFRT.IN"
           "?format=json&per_page=500&date=2000:2023")
    for r in json.loads(fetch("wb_tfr_aus_nzl.json", url).read_text())[1]:
        if r["value"] is not None:
            other.setdefault(r["countryiso3code"], {})[int(r["date"])] = r["value"]
    other["URY"] = uruguay_outcomes()["tfr"]
    for c in missing:
        if c in other:
            out[c] = other[c]
    return out


_URUGUAY = {}


def uruguay_outcomes():
    """Uruguay, which HFD doesn't cover: {"tfr": {year: TFR}, age: {year: % with a child}}.

    TFR: MSP live births by mother's age over INE women at 30 June, 1996-2021.
    With a child by age: first births per woman summed to the age before, as for the other estimates.
    To 2011, Human Fertility Collection CPFR1 (Latin American Fertility Database, birth certificates
    and the Perinatal Information System); for 2013 and 2021, MSP/INE rates by 5-year group times the
    share of first births in each group in SIP microdata (HFC/scripts/uruguay_by_order.py).
    """
    if _URUGUAY:
        return _URUGUAY
    sys.path.insert(0, str(ROOT / "HFC" / "scripts"))
    import uruguay_by_order as ury
    asfr = (ury.births() / ury.women()).dropna()
    _URUGUAY["tfr"] = {int(y): float(5 * r.sum()) for y, r in asfr.iterrows()}
    url = "https://www.fertilitydata.org/File/GetFile/Country/URY%5CURY_ASFRstand_BO.txt"
    d = pd.read_csv(fetch("hfc_URY_ASFRstand_BO.txt", url), skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    d = d[(d.Year1 == d.Year2) & (d.AgeDef.str.strip() == "ACY")].dropna(subset=["CPFR1"]).drop_duplicates(["Year1", "Age", "CPFR1"])
    for age in CHILD_AGES:
        x = d[d.Age == age]
        if x.Year1.duplicated().any():
            raise ValueError("repeated HFC years for URY")
        _URUGUAY[age] = {int(y): 100 * float(v) for y, v in zip(x.Year1, x.CPFR1)}
    for year in ury.SIP_URLS:
        share, _ = ury.sip_shares(year)
        first = (5 * asfr.loc[year] * share["TFR1"]).reindex(ury.GROUPS)
        for age in CHILD_AGES:
            _URUGUAY[age][year] = 100 * float(first.iloc[:(age - 15) // 5].sum())
    return _URUGUAY


def synthetic(qs):
    """qs: list of (age, q1..q5) -> outcome dict for one period table."""
    s = [1.0, 0, 0, 0, 0, 0]
    first_age = 0.0
    by_age = {}
    for age, q in qs:
        new = [s[i] * q[i] for i in range(5)]
        first_age += (age + 0.5) * new[0]
        s = [s[0] - new[0]] + [s[i] - (new[i] if i < 5 else 0) + new[i - 1] for i in range(1, 5)] + [s[5] + new[4]]
        if age + 1 in CHILD_AGES:
            by_age[f"mothers_by_{age + 1}"] = 100 * (1 - s[0])
    ever = 1 - s[0]
    return {
        **by_age,
        "mothers_ever": 100 * ever,
        "second_child": 100 * (ever - s[1]) / ever,
        "age_first": first_age / ever,
    }


def estimated_by_age():
    """{age: {iso: {year: % with a child}}} from summed first-birth rates, for countries without HFD tables."""
    out = {age: {} for age in CHILD_AGES}
    for iso in ESTIMATE_HFC:
        url = f"https://www.fertilitydata.org/File/GetFile/Country/{iso}%5C{iso}_ASFRstand_BO.txt"
        d = pd.read_csv(fetch(f"hfc_{iso}_ASFRstand_BO.txt", url), skipinitialspace=True, na_values=".")
        d.columns = d.columns.str.strip()
        # HFC repeats years across collections and age definitions: use vital registration, age in completed years.
        d = d[(d.Year1 == d.Year2) & (d.AgeDef == "ACY") & (d.Collection == "HFD")].dropna(subset=["CPFR1"])
        for age in CHILD_AGES:
            x = d[d.Age == age]
            if x.Year1.duplicated().any():
                raise ValueError(f"repeated HFC years for {iso}")
            out[age][iso] = {int(y): 100 * float(v) for y, v in zip(x.Year1, x.CPFR1)}

    def single_age(frame):
        return frame.assign(a=pd.to_numeric(frame.age.str.extract(r"^Y(\d+)$")[0])).query(f"15 <= a < {max(CHILD_AGES)}")

    births = single_age(eurostat("demo_fordagec"))
    births = births[births.iso.isin(ESTIMATE_EUROSTAT)][["iso", "year", "a", "OBS_VALUE"]]
    women = single_age(eurostat("demo_pjan"))
    women = women[women.iso.isin(ESTIMATE_EUROSTAT)][["iso", "year", "a", "OBS_VALUE"]]
    # Women exposed in a year: the mean of 1 January this year and next.
    women = pd.concat([women, women.assign(year=women.year - 1)]).groupby(["iso", "year", "a"], as_index=False).OBS_VALUE.mean()
    x = births.merge(women, on=["iso", "year", "a"], suffixes=("_b", "_w"))
    x = x[x.OBS_VALUE_w > 0].assign(rate=lambda f: f.OBS_VALUE_b / f.OBS_VALUE_w)
    x = x[x.year >= x.iso.map(EUROSTAT_ORDER_FROM).fillna(0)]
    for age in CHILD_AGES:
        g = x[x.a < age].groupby(["iso", "year"]).rate.agg(["sum", "size"])
        for (iso, year), r in g[g["size"] == age - 15].iterrows():
            out[age].setdefault(iso, {})[int(year)] = 100 * float(r["sum"])
    return out


def australia_census():
    """{age: {year: % of women with a child}}: exact ages sit between two 5-year census groups."""
    url = "https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_TSP_AUS_for_AUS_short-header.zip"
    z = zipfile.ZipFile(fetch("abs_2021_TSP_AUS.zip", url))
    row = {}
    for name in z.namelist():
        if "_T07" in name and name.endswith(".csv"):
            row.update(pd.read_csv(io.BytesIO(z.read(name))).iloc[0].to_dict())

    def share(year, lo):
        c = f"C{year % 100}_AP_{lo}_{lo + 4}"
        return 100 * (1 - row[f"{c}_NCB_0"] / (row[f"{c}_Tot"] - row[f"{c}_NCB_NS"]))

    return {age: {y: (share(y, age - 5) + share(y, age)) / 2 for y in (2011, 2016, 2021)} for age in CHILD_AGES}


def new_zealand_census():
    """{age: {year: % of women with a child}}: exact ages sit between two 5-year census groups."""
    share = lambda year, lo: 100 * (1 - NZ_CENSUS[year][lo][0] / NZ_CENSUS[year][lo][1])
    return {age: {y: (share(y, age - 5) + share(y, age)) / 2 for y in NZ_CENSUS} for age in CHILD_AGES}


def load_parity():
    d = pd.read_csv(HFD / "pft.txt", sep=r"\s+", skiprows=2, na_values=".", dtype={"x": str})
    d["age"] = d.x.str.rstrip("-+").astype(int)
    qcols = ["q1x", "q2x", "q3x", "q4x", "q5px"]
    d[qcols] = d[qcols].fillna(0.0)
    out = {}
    for (code, year), g in d.groupby(["Code", "Year"]):
        if code not in COUNTRIES:
            continue
        g = g.sort_values("age")
        res = synthetic([(a, list(q)) for a, *q in g[["age"] + qcols].itertuples(index=False)])
        for k, v in res.items():
            out.setdefault(k, {}).setdefault(code, {})[int(year)] = v
    import outcome_grid_uk as uk  # England & Wales from ONS cohort tables
    for year, r in uk.parity_metrics(CHILD_AGES).items():
        for age in CHILD_AGES:
            out[f"mothers_by_{age}"].setdefault("GBR", {})[year] = 100 * r[f"first_by_{age}"]
        out["mothers_ever"].setdefault("GBR", {})[year] = 100 * r["ever_mother_by_45"]
        out["second_child"].setdefault("GBR", {})[year] = 100 * r["mothers_with_2plus"]
        out["age_first"].setdefault("GBR", {})[year] = r["mean_age_first"]
    census, nz = australia_census(), new_zealand_census()
    for age, by_iso in estimated_by_age().items():
        out[f"mothers_by_{age}"].update(by_iso)  # one source per country, no splice with partial HFD years
        out[f"mothers_by_{age}"]["AUS"] = census[age]
        out[f"mothers_by_{age}"]["NZL"] = nz[age]
        out[f"mothers_by_{age}"]["URY"] = uruguay_outcomes()[age]
    return out


# (key, label, group, rate column, exposure column, first age, last age)
RATE_ROWS = [
    ("first_20_24", "First-birth rate, 20–24", "First births", "m1x", "E0x", 20, 24),
    ("first_25_29", "First-birth rate, 25–29", "First births", "m1x", "E0x", 25, 29),
    ("first_30_34", "First-birth rate, 30–34", "First births", "m1x", "E0x", 30, 34),
    ("first_35_39", "First-birth rate, 35–39", "First births", "m1x", "E0x", 35, 39),
    ("second_20_24", "Second-birth rate, 20–24", "Second births", "m2x", "E1x", 20, 24),
    ("second_25_29", "Second-birth rate, 25–29", "Second births", "m2x", "E1x", 25, 29),
    ("second_30_34", "Second-birth rate, 30–34", "Second births", "m2x", "E1x", 30, 34),
    ("second_35_39", "Second-birth rate, 35–39", "Second births", "m2x", "E1x", 35, 39),
]


def load_rates(e):
    """key -> iso -> {year: conditional rate, % per year}, pooled over the band's ages."""
    from common.ons_table3 import load_table3
    mi = pd.read_csv(HFD / "mi.txt", sep=r"\s+", skiprows=2, na_values=".", dtype={"Age": str})
    mi = mi[mi.Code.isin(COUNTRIES)].copy()
    mi["age"] = mi.Age.str.rstrip("-+").astype(int)
    d = mi.merge(e[["Code", "Year", "age", "E0x", "E1x"]], on=["Code", "Year", "age"])
    uk = []
    for cohort, ages in load_table3().items():
        for age, (p1, p2) in ages.items():
            if age - 1 in ages:
                q1, q2 = ages[age - 1]
                uk.append(dict(year=cohort + age, age=age, b_m1x=max(0.0, p1 - q1), r_m1x=100 - q1,
                               b_m2x=max(0.0, p2 - q2), r_m2x=q1 - q2))
    uk = pd.DataFrame(uk)
    out = {}
    for key, _, _, col, ecol, lo, hi in RATE_ROWS:
        out[key] = {}
        g = d[d.age.between(lo, hi)].dropna(subset=[col, ecol]).copy()
        g["births"] = g[col] * g[ecol]
        for (code, year), x in g.groupby(["Code", "Year"]):
            if len(x) == hi - lo + 1 and x[ecol].sum() > 0:
                out[key].setdefault(code, {})[int(year)] = 100 * x.births.sum() / x[ecol].sum()
        x = uk[uk.age.between(lo, hi)].groupby("year").agg(b=(f"b_{col}", "sum"), r=(f"r_{col}", "sum"), n=("age", "size"))
        for year, row in x[x.n == hi - lo + 1].iterrows():
            if row.r > 0:
                out[key].setdefault("GBR", {})[int(year)] = 100 * row.b / row.r
    return out


# ---------- change calculations ----------

def value_near(s, year):
    for y in (year, year - 1, year + 1):
        if y in s:
            return s[y]
    return None


def change(s, a=None, b=None):
    if not s:
        return None
    a, b = BASE if a is None else a, END if b is None else b
    va, vb = value_near(s, a), value_near(s, b)
    return None if va is None or vb is None else vb - va


def near_year(s, year, tol=1):
    """The year used for a value: this year, else the closest within tol (earlier first)."""
    for gap in range(tol + 1):
        for y in (year - gap, year + gap):
            if y in s:
                return y
    return None


def child_change(s, iso, tols=None):
    """Change between the years nearest the window's ends, within each country's tolerance."""
    tol = (CENSUS_TOL if tols is None else tols).get(iso, 1)
    a, b = near_year(s or {}, BASE, tol), near_year(s or {}, END, tol)
    return None if a is None or b is None else s[b] - s[a]


def corr(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


def pct_change(s, a=None, b=None):
    if not s:
        return None
    a, b = BASE if a is None else a, END if b is None else b
    va, vb = value_near(s, a), value_near(s, b)
    return None if va is None or vb is None or not va else 100 * (vb / va - 1)


def median(v):
    v = sorted(v)
    n = len(v)
    return None if not n else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


# ---------- child:coupling ratios and coupling by age ----------

NSO_ISO = {"Denmark": "DNK", "Finland": "FIN", "Netherlands": "NLD", "US": "USA"}
ILO_ISO = ("CAN", "JPN", "KOR", "AUS", "CHL", "URY")
# Uruguay's ILO coupling jumps 7-9 points at every age between 2005 and 2006, when its household
# survey (ECH) was extended from towns of 5,000 or more to the whole country.
ILO_FROM = {"URY": 2006}
FT_ISO = {"Spain": "ESP", "UK": "GBR", "France": "FRA", "Germany": "DEU", "Poland": "POL"}
UN_NAMES = {**{v[1]: k for k, v in COUNTRIES.items()}, "S Korea": "KOR"}
SINGLE_AGE = ("DNK", "FIN", "NLD")
MATCHED_BANDS = [(18, 24), (25, 29), (30, 34), (35, 39)]
UN_BANDS = ["15-19", "20-24", "25-29", "30-34", "35-39"]
# Midpoint ratios: % with a child at the middle of the coupling age group.
RATIOS = [("ratio_18_24", "18-24", 21, "Child by 21 ÷ couple 18–24"),
          ("ratio_15_24", "15-24", 20, "Child by 20 ÷ couple 15–24"),
          ("ratio_25_34", "25-34", 30, "Child by 30 ÷ couple 25–34")]


def main_csv(rel):
    path = ROOT / rel
    return path if path.exists() else CACHE / "main" / path.name


def load_exposures():
    e = pd.read_csv(HFD / "exposRRpa.txt", sep=r"\s+", skiprows=2, na_values=".", dtype={"Age": str})
    e = e[e.Code.isin(COUNTRIES)].copy()
    e["age"] = e.Age.str.rstrip("-+").astype(int)
    e["all"] = e[["E0x", "E1x", "E2x", "E3x", "E4px"]].sum(axis=1)
    return e


def mothers_at_age(e, age):
    """{iso: {year: % of women with a child at this age}}"""
    g = e[e.age == age]
    out = {}
    for code, year, e0, tot in g[["Code", "Year", "E0x", "all"]].itertuples(index=False):
        if tot > 0:
            out.setdefault(code, {})[int(year)] = 100 - 100 * e0 / tot
    from common.ons_table3 import load_table3
    for cohort, ages in load_table3().items():
        if age in ages:
            out.setdefault("GBR", {})[cohort + age] = ages[age][0]
    return out


def mothers_in_band(e, lo, hi):
    g = e[e.age.between(lo, hi)].groupby(["Code", "Year"]).agg(E0x=("E0x", "sum"), tot=("all", "sum"), n=("age", "size"))
    g = g[g.n == hi - lo + 1]
    out = {}
    for (code, year), r in g.iterrows():
        out.setdefault(code, {})[int(year)] = 100 - 100 * r.E0x / r.tot
    return out


def load_coupling_sources():
    """source -> iso -> age label -> {year: % of women in a couple}"""
    src = {k: {} for k in ("nso", "ilo", "ft", "ons", "un")}

    def add(name, iso, age, year, v):
        if pd.notna(v):
            src[name].setdefault(iso, {}).setdefault(str(age), {})[int(year)] = float(v)

    d = pd.read_csv(main_csv("NSO/outputs/coupling_nso.csv"), dtype={"age": str})
    for r in d[(d.sex == "Women") & d.country.isin(NSO_ISO)].itertuples():
        add("nso", NSO_ISO[r.country], r.age, r.year, r.share)
    d = pd.read_csv(main_csv("ILO/outputs/coupling_ilo.csv"))
    for r in d[(d.sex == "women") & d.ref_area.isin(ILO_ISO)].itertuples():
        if r.year >= ILO_FROM.get(r.ref_area, 0):
            add("ilo", r.ref_area, r.age, r.year, r.share)
    d = pd.read_csv(main_csv("FT/outputs/ft_coupling_25_34.csv"))
    for r in d[d.country.isin(FT_ISO)].itertuples():
        add("ft", FT_ISO[r.country], "25-34", r.year, r.value)
    d = pd.read_csv(main_csv("ONS/outputs/coupling_by_age_ew.csv"))
    for r in d[d.sex == "Women"].itertuples():
        add("ons", "GBR", r.age.replace(" to ", "-"), r.year, r.couple)
    d = pd.read_csv(main_csv("UN/outputs/coupling_un.csv"))
    d = d[(d.sex.str.lower() == "women") & d.country.isin(UN_NAMES) & d.age.isin(UN_BANDS)]
    for r in d.itertuples():
        add("un", UN_NAMES[r.country], r.age, r.year, r.share)
    return src


def nso_band(src, iso, lo, hi):
    """A register band: the published row, else the mean of its single ages."""
    ages = src["nso"].get(iso, {})
    if f"{lo}-{hi}" in ages:
        return ages[f"{lo}-{hi}"]
    singles = [ages.get(str(a), {}) for a in range(lo, hi + 1)]
    if not all(singles):
        return {}
    years = set.intersection(*(set(s) for s in singles))
    return {y: sum(s[y] for s in singles) / len(singles) for y in years}


def divide(m, c):
    return {y: m[y] / c[y] for y in m if y in c and c[y] > 0}


def band_row(label, s):
    lo, hi = (int(x) for x in (label.split("-") * 2)[:2])
    return dict(label=label.replace("-", "–"), lo=lo, hi=hi, a=value_near(s, BASE), b=value_near(s, END))


def age_profile(iso, src, factors):
    if iso in SINGLE_AGE:
        rows = [band_row(str(a), src["nso"][iso].get(str(a), {})) for a in range(18, 40)]
        source = "national register"
    elif iso == "USA":
        rows = [band_row(a, src["nso"][iso][a]) for a in ("18-24", "25-34")]
        source = "CPS"
    elif iso in ILO_ISO:
        rows = [band_row(a, src["ilo"][iso][a]) for a in ("15-24", "25-34", "35-44") if a in src["ilo"].get(iso, {})]
        source = "ILO"
    elif iso == "GBR":
        rows = [band_row(a, src["ons"][iso][a]) for a in ("16-29", "30-34", "35-39")]
        source = "ONS"
    else:
        rows = [band_row(a, factors[k].get(iso, {})) for a, k in (("18-24", "couple_18_24"), ("25-49", "couple_25_49"))
                if factors[k].get(iso)]
        source = "Eurostat LFS"
    rows = [r for r in rows if r["a"] is not None or r["b"] is not None]
    census = None
    if iso not in SINGLE_AGE and iso in src["un"]:
        years = [y for y in set().union(*(set(s) for s in src["un"][iso].values())) if 2005 <= y <= END]
        if years:
            year = max(years)
            census = dict(year=year, rows=[dict(label=a.replace("-", "–"), lo=int(a[:2]), hi=int(a[3:]), v=src["un"][iso][a][year])
                                           for a in UN_BANDS if year in src["un"][iso].get(a, {})])
    return dict(source=source, rows=rows, census=census) if rows or census else None


def load_ratios(factors):
    e = load_exposures()
    src = load_coupling_sources()
    series = {k: {} for k, *_ in RATIOS}
    for key, band, age, _ in RATIOS:
        m = mothers_at_age(e, age)
        lo, hi = (int(x) for x in band.split("-"))
        for iso in COUNTRIES:
            # Eurostat's 18-24 series is left out: it counts couples living with parents
            # as another household type, which understates young couples.
            if iso in NSO_ISO.values():
                c = nso_band(src, iso, lo, hi)
            elif band == "25-34" and iso in src["ft"]:
                c = src["ft"][iso]["25-34"]
            else:
                c = src["ilo"].get(iso, {}).get(band, {})
            r = divide(m.get(iso, {}), c)
            if r:
                series[key][iso] = r
    matched = {}
    for lo, hi in MATCHED_BANDS:
        m = mothers_in_band(e, lo, hi)
        for iso in SINGLE_AGE:
            r = divide(m.get(iso, {}), nso_band(src, iso, lo, hi))
            matched.setdefault(iso, {})[f"{lo}–{hi}"] = r
    profiles = {iso: p for iso in COUNTRIES if (p := age_profile(iso, src, factors))}
    return series, matched, profiles


# (key, label, age for % with a child, coupling row; None = already built by load_ratios)
RATIO_ROWS = [
    ("ratio_15_24", "15–24, child by 20 · registers, ILO", 20, None),
    ("ratio_25_29", "25–29, child by 27 · registers, ONS", 27, "couple_25_29"),
    ("ratio_25_34", "25–34, child by 30 · registers, ILO, FT", 30, None),
    ("ratio_30_34", "30–34, child by 32 · registers, ONS", 32, "couple_30_34"),
    ("ratio_35_39", "35–39, child by 37 · registers, ONS", 37, "couple_35_39"),
    ("ratio_census_20_24", "20–24, child by 25 · census", 25, "couple_census_20_24"),
    ("ratio_census_25_34", "25–34, child by 30 · census", 30, "couple_census_25_34"),
    ("ratio_census_35_39", "35–39, child by 35 · census", 35, "couple_census_35_39"),
    ("ratio_ess_25_34", "25–34, child by 30 · ESS survey", 30, "couple_ess_25_34"),
]
# Summary rows: one per 5-year band, each country taking the first coupling row in this list with a
# confirmed change (then an unconfirmed one, faded). ":register" and ":ILO" split couple_under_25 by source.
# The ratio divides % with a child by the end of the band by that coupling series.
SUMMARY_BANDS = [
    ("20_24", "20–24", 25, ["couple_under_25:register", "couple_census_20_24", "couple_18_24", "couple_under_25:ILO"]),
    ("25_29", "25–29", 30, ["couple_25_29", "couple_census_25_29"]),
    ("30_34", "30–34", 35, ["couple_30_34", "couple_census_30_34"]),
    ("35_39", "35–39", 40, ["couple_35_39", "couple_census_35_39"]),
]
SUMMARY_KEYS = [f"{p}_{b}" for p in ("sum_couple", "sum_ratio") for b, *_ in SUMMARY_BANDS]
# Ratios over coupling measured only in some years: each coupling year takes the % with a child from the
# with-a-child rows (HFD, estimates and censuses) within two years of it, and the change uses the coupling
# row's tolerance, faded cells and noise flags.
RATIO_OF_SPARSE = {"ratio_census_20_24": "couple_census_20_24", "ratio_census_25_34": "couple_census_25_34",
                   "ratio_census_35_39": "couple_census_35_39",
                   "ratio_ess_25_34": "couple_ess_25_34"}


def sparse_tols(key):
    return ESS_TOL if key == "ratio_ess_25_34" else CENSUS_COUPLE_TOL


def matrix_ratios(e, factors, parity):
    out = {}
    for key, _, age, band in RATIO_ROWS:
        if band:
            if key in RATIO_OF_SPARSE:
                mothers = parity[f"mothers_by_{age}"]
                out[key] = {}
                for c, s in factors[band].items():
                    m = mothers.get(c, {})
                    r = {y: m[my] / v for y, v in s.items() if v > 0 and (my := near_year(m, y, 0 if c in RATIO_SAME_YEAR else 2)) is not None}
                    if r:
                        out[key][c] = r
            else:
                mothers = mothers_at_age(e, age)
                out[key] = {c: r for c, s in factors[band].items() if (r := divide(mothers.get(c, {}), s))}
    return out


def ratio_sources(sources):
    out = {key: sources[band] for key, _, _, band in RATIO_ROWS if band}
    out["ratio_25_34"] = sources["couple_25_34"]
    out["ratio_15_24"] = {c: v.replace("18–24", "15–24") for c, v in sources["couple_under_25"].items()}
    return out


def coupling_rows(src):
    """Coupling by age from the sources that count cohabitation at these ages."""
    young, mid, sources = {}, {}, {"couple_under_25": {}, "couple_25_34": {}}
    for iso in COUNTRIES:
        if iso in NSO_ISO.values():
            young[iso], mid[iso] = nso_band(src, iso, 18, 24), nso_band(src, iso, 25, 34)
            name = "CPS" if iso == "USA" else "national register"
            sources["couple_under_25"][iso] = f"{name}, 18–24"
            sources["couple_25_34"][iso] = name
        elif iso in ILO_ISO:
            young[iso], mid[iso] = src["ilo"][iso].get("15-24", {}), src["ilo"][iso].get("25-34", {})
            sources["couple_under_25"][iso] = "ILO, 15–24"
            sources["couple_25_34"][iso] = "ILO"
        elif iso in src["ft"]:
            mid[iso] = src["ft"][iso]["25-34"]
            sources["couple_25_34"][iso] = "FT, both sexes"
    rows = {"couple_under_25": young, "couple_25_34": mid}
    for lo, hi in ((25, 29), (30, 34), (35, 39)):
        key = f"couple_{lo}_{hi}"
        rows[key], sources[key] = {}, {}
        for iso in SINGLE_AGE:
            rows[key][iso] = nso_band(src, iso, lo, hi)
            sources[key][iso] = "national register"
        uk = src["ons"].get("GBR", {}).get(f"{lo}-{hi}")
        if uk:
            rows[key]["GBR"] = uk
            sources[key]["GBR"] = "ONS"
    return rows, sources


def ratio_directions(series, matched):
    out = {}
    for iso in COUNTRIES:
        row = {}
        for key, *_ in RATIOS:
            s = series[key].get(iso, {})
            a, b = value_near(s, BASE), value_near(s, END)
            if a is not None and b is not None:
                row[key] = [round(float(a), 3), round(float(b), 3)]
        for band, s in matched.get(iso, {}).items():
            a, b = value_near(s, BASE), value_near(s, END)
            if a is not None and b is not None:
                row[band] = [round(float(a), 3), round(float(b), 3)]
        out[iso] = row
    return out


COUPLING_LAST = "couple_ess_25_34"  # the relationships row follows the last coupling row


def ratio_row(key, label, s, order, sources):
    if key in RATIO_OF_SPARSE:
        cells = {c: child_change(s.get(c), c, sparse_tols(key)) for c in order}
        before = []
    else:
        cells = {c: change(s.get(c)) for c in order}
        before = [-v for c in order if (v := change(s.get(c), 2001, BASE)) is not None]
    return dict(key=key, label=label, group=RATIO_GROUP, kind="ratio",
                unit="", dp=2, direction=-1, cells=cells, sources=sources, before=median(before),
                after=median([-v for v in cells.values() if v is not None]))


def row_tols(key):
    """{iso: years} a row's start and end values may sit from the window's ends."""
    return (CENSUS_TOL if key.startswith("mothers_by_") else COUPLING_TOL if key in COUPLING_TOL_ROWS
            else ABORTION_TOL if key in ABORTION_ROWS else IDEAL_TOL if key in IDEAL_ROWS
            else CENSUS_COUPLE_TOL if key in CENSUS_COUPLE_ROWS else ESS_TOL if key == "couple_ess_25_34"
            else sparse_tols(key) if key in RATIO_OF_SPARSE else {})


def pick_coupling(rows_by_key, candidates, iso):
    """The first candidate row with a change for this country: confirmed first, then unconfirmed."""
    for strict in (True, False):
        for cand in candidates:
            key, _, only = cand.partition(":")
            r = rows_by_key[key]
            src = (r.get("sources") or {}).get(iso, "")
            if (only == "ILO") != src.startswith("ILO") and only:
                continue
            if r["cells"].get(iso) is None or (strict and r.get("low_confidence", {}).get(iso)):
                continue
            return r
    return None


def summary_rows(rows, ts, parity, order):
    """One coupling row and one ratio row per 5-year band, each country from its best coupling row."""
    by_key = {r["key"]: r for r in rows}
    couples, ratios = [], []
    for band, label, age, candidates in SUMMARY_BANDS:
        ck, rk = f"sum_couple_{band}", f"sum_ratio_{band}"
        c_row = dict(key=ck, label=label, group=COUPLE_GROUP, kind="factor", unit="%", direction=-1,
                     page="partnership-formation", cells={}, years={}, sources={}, low_confidence={})
        r_row = dict(key=rk, label=f"{label}, child by {age}", group=RATIO_GROUP, kind="ratio", unit="", dp=2,
                     direction=-1, cells={}, years={}, sources={}, low_confidence={})
        ts[ck], ts[rk] = {}, {}
        mothers = parity[f"mothers_by_{age}"]
        c_before, r_before = [], []
        for c in order:
            src = pick_coupling(by_key, candidates, c)
            c_row["cells"][c] = r_row["cells"][c] = None
            if src is None:
                continue
            s = ts[src["key"]][c]
            tol = row_tols(src["key"])
            where = src["label"].split(" · ")[-1] if " · " in src["label"] else ""
            detail = (src.get("sources") or {}).get(c) or where
            low = bool(src.get("low_confidence", {}).get(c))
            ts[ck][c] = s
            c_row["cells"][c], c_row["years"][c] = src["cells"][c], src["years"][c]
            c_row["sources"][c], c_row["low_confidence"][c] = f"{src['label'].split(' · ')[0]}, {detail}", low
            if (v := change(s, 2001, BASE)) is not None:
                c_before.append(-v)
            m = mothers.get(c, {})
            ratio = {y: m[my] / v for y, v in s.items() if v > 0 and (my := near_year(m, y, 0 if c in RATIO_SAME_YEAR else 2)) is not None}
            if not ratio:
                continue
            ts[rk][c] = ratio
            r_row["cells"][c] = child_change(ratio, c, tol)
            if r_row["cells"][c] is not None:
                t = tol.get(c, 1)
                r_row["years"][c] = [near_year(ratio, BASE, t), near_year(ratio, END, t)]
                r_row["sources"][c], r_row["low_confidence"][c] = c_row["sources"][c], low
            if (v := change(ratio, 2001, BASE)) is not None:
                r_before.append(-v)
        for row, before in ((c_row, c_before), (r_row, r_before)):
            row["before"] = median(before)
            row["after"] = median([-v for c, v in row["cells"].items() if v is not None and not row["low_confidence"].get(c)])
        couples.append(c_row)
        ratios.append(r_row)
    return couples, ratios


def build(reference=None):
    """reference: the main window's countries. When given, keep their order and falling set,
    and fit each row against their later fall in % with a child by 30."""
    tfr = load_tfr()
    parity = load_parity()
    factors = load_factors()
    exposures = load_exposures()
    rates = load_rates(exposures)
    new_rows, sources = coupling_rows(load_coupling_sources())
    factors.update(new_rows)
    census, census_sources = load_census_couples()
    factors.update(census)
    factors.update(load_abortion_order())
    sources.update(census_sources)
    ideals, ideal_sources = load_ideals()
    factors.update(ideals)
    sources.update(ideal_sources)
    factors["couple_ess_25_34"], ess_errors = load_ess_couples()
    sources["couple_ess_25_34"] = {c: "ESS, two rounds pooled" for c in factors["couple_ess_25_34"]}
    sources["alone_25_34"] = {c: {"NLD": "CBS register", "FIN": "Statistics Finland register", "USA": "CPS"}[c]
                              for c in factors["alone_25_34"]}
    ratios, matched, profiles = load_ratios(factors)
    ratios.update(matrix_ratios(exposures, factors, parity))
    ratio_src = ratio_sources(sources)
    m30 = parity["mothers_by_30"]
    d_tfr = {c: change(tfr.get(c)) for c in COUNTRIES}
    d_m30 = {c: change(m30.get(c)) for c in COUNTRIES}
    if reference:
        order = [c["iso"] for c in reference]
        target = {c["iso"]: c["d_m30"] for c in reference}
        falling_set = {c["iso"] for c in reference if c["d_tfr"] < -0.1}
    else:
        # Countries with the child-by-30 measure first, then the rest by TFR change.
        order = sorted([c for c in COUNTRIES if d_tfr[c] is not None],
                       key=lambda c: (d_m30[c] is None, d_tfr[c] if d_m30[c] is None else d_m30[c]))
        target = d_m30
        falling_set = {c for c in order if d_tfr[c] < -0.1}

    rows = []
    for age in CHILD_AGES:
        key = f"mothers_by_{age}"
        cells = {c: child_change(parity[key].get(c), c) for c in order}
        before = [-v for c in order if (v := change(parity[key].get(c), 2001, BASE)) is not None]
        rows.append(dict(key=key, label=f"With a child by {age}", group="Women with a child", kind="outcome", unit="%", direction=-1,
                         cells=cells, before=median(before), after=median([-v for v in cells.values() if v is not None]),
                         sources={**M30_ESTIMATES, **CENSUS_SOURCES}))
    for key, label, group, *_ in RATE_ROWS:
        cells = {c: pct_change(rates[key].get(c)) for c in order}
        before = [-v for c in order if (v := pct_change(rates[key].get(c), 2001, BASE)) is not None]
        after = [-v for v in cells.values() if v is not None]
        rows.append(dict(key=key, label=label, group=group, kind="outcome", unit="%", pct=True, direction=-1, cells=cells,
                         before=median(before), after=median(after)))
    for key, label, direction, page, group in FACTORS:
        s = factors[key]
        tols = (COUPLING_TOL if key in COUPLING_TOL_ROWS else ABORTION_TOL if key in ABORTION_ROWS
                else IDEAL_TOL if key in IDEAL_ROWS else CENSUS_COUPLE_TOL if key in CENSUS_COUPLE_ROWS
                else ESS_TOL if key == "couple_ess_25_34" else None)
        cells = {c: child_change(s.get(c), c, tols) if tols else change(s.get(c)) for c in order}
        before = [direction * change(s.get(c), 2001, BASE) for c in order if change(s.get(c), 2001, BASE) is not None]
        after = [direction * v for v in cells.values() if v is not None]
        rows.append(dict(key=key, label=label, group=group, kind="factor", unit=UNITS.get(key, "%"), **({"dp": DP[key]} if key in DP else {}), direction=direction, page=page, cells=cells,
                         before=median(before), after=median(after), sources=sources.get(key), unsigned=key in UNSIGNED))
        if key == COUPLING_LAST:
            rows += [ratio_row(k, label, ratios[k], order, ratio_src[k]) for k, label, *_ in RATIO_ROWS]
    for r in rows:
        if r["key"] in CENSUS_COUPLE_ROWS:
            r["low_confidence"] = {}
            for c, v in r["cells"].items():
                if v is not None:
                    tol = CENSUS_COUPLE_TOL[c]
                    span = near_year(factors[r["key"]][c], BASE, tol), near_year(factors[r["key"]][c], END, tol)
                    band = CENSUS_COUPLE_WIDER_BAND.get(r["key"], {}).get(c)
                    wider = bool(band) and r["sources"][c].endswith(band[1:].replace("-", "–"))
                    r["low_confidence"][c] = wider or c not in CENSUS_COUPLE_PASSED.get(span, ())
            r["after"] = median([r["direction"] * v for c, v in r["cells"].items() if v is not None and not r["low_confidence"][c]])
        if r["key"] in RATIO_OF_SPARSE and RATIO_OF_SPARSE[r["key"]] in CENSUS_COUPLE_ROWS:
            src_low = next(x for x in rows if x["key"] == RATIO_OF_SPARSE[r["key"]])["low_confidence"]
            r["low_confidence"] = {c: src_low.get(c, True) for c, v in r["cells"].items() if v is not None}
            r["after"] = median([r["direction"] * v for c, v in r["cells"].items() if v is not None and not r["low_confidence"][c]])

    for r in rows:  # spread 20–34 abortion cells: indicative, faded, out of counts and fits
        if r["key"] not in ABORTION_ROWS:
            continue
        age = ABORTION_ROWS[r["key"]][1]
        spread = [c for c, (_, narrow) in ABORTION_SPREAD.items() if age in narrow and r["cells"].get(c) is not None]
        if spread:
            r["low_confidence"] = {c: c in spread for c, v in r["cells"].items() if v is not None}
            r["low_note"] = {c: ABORTION_SPREAD_NOTE for c in spread}
            r["sources"] = {**(r.get("sources") or {}), **{c: "DHSC 20–34 value" for c in spread}}
            r["after"] = median([r["direction"] * v for c, v in r["cells"].items() if v is not None and not r["low_confidence"][c]])

    ts = {"tfr": tfr, **parity, **rates, **factors, **ratios}
    for r in rows:  # the years each cell actually compares
        tols = row_tols(r["key"])
        tol = lambda c: tols.get(c, 1)
        r["years"] = {c: [near_year(ts[r["key"]].get(c, {}), BASE, tol(c)), near_year(ts[r["key"]].get(c, {}), END, tol(c))]
                      for c, v in r["cells"].items() if v is not None}
        if r["key"] == "couple_ess_25_34":  # change smaller than two standard errors
            r["noisy"] = {c: bool(abs(r["cells"][c]) < 2 * (ess_errors[c][y0] ** 2 + ess_errors[c][y1] ** 2) ** 0.5)
                          for c, (y0, y1) in r["years"].items()}
    ess = next(x for x in rows if x["key"] == "couple_ess_25_34")
    for r in rows:
        if r["key"] == "ratio_ess_25_34":
            r["noisy"] = {c: ess["noisy"].get(c, True) for c in r["years"]}

    # Summary rows go first in each group; the existing rows become its expandable detail.
    sum_couple, sum_ratio = summary_rows(rows, ts, parity, order)
    couple = [r for r in rows if r["group"] == COUPLE_GROUP]
    ratio = [r for r in rows if r["group"] == RATIO_GROUP]
    for r in couple + ratio:
        r["detail"] = True
    first = next(i for i, r in enumerate(rows) if r["group"] == COUPLE_GROUP)
    rest = [r for r in rows[first:] if r["group"] not in (COUPLE_GROUP, RATIO_GROUP)]
    rows = rows[:first] + sum_couple + couple + sum_ratio + ratio + rest
    for r in rows:
        r["long"] = f"{r['group']}, {r['label']}" if r["group"] in GROUP_NOTES else r["label"]
        if r["group"] in GROUP_NOTES:
            r["group_note"] = GROUP_NOTES[r["group"]]

    for r in rows:
        low = r.get("low_confidence", {})
        pairs = [(r["direction"] * v, -target[c]) for c, v in r["cells"].items()
                 if v is not None and target[c] is not None and not low.get(c)]
        r["n"] = len(pairs)  # countries in the fit
        r["fit"] = corr([p[0] for p in pairs], [p[1] for p in pairs]) if r["kind"] == "factor" and len(pairs) >= MIN_FIT_N else None
        vals = sorted(abs(v) for v in r["cells"].values() if v is not None)
        r["scale"] = vals[int(0.9 * (len(vals) - 1))] if vals else 1
        falling = [c for c in order if c in falling_set and r["cells"][c] is not None and not low.get(c)]
        r["toward_fewer_in_falling"] = sum(1 for c in falling if r["direction"] * r["cells"][c] > 0)
        r["n_falling"] = 0 if r.get("unsigned") else len(falling)

    countries = [dict(iso=c, name=COUNTRIES[c][1], region=REGIONS[c], region_rank=list(REGION_MEMBERS).index(REGIONS[c]), m30_source=M30_ESTIMATES.get(c), d_tfr=d_tfr[c], d_m30=d_m30[c], tfr_base=value_near(tfr[c], BASE), tfr_end=value_near(tfr[c], END),
                      m30_base=value_near(m30.get(c, {}), BASE), m30_end=value_near(m30.get(c, {}), END)) for c in order]
    extra = dict(profiles=profiles, ratio_dirs=ratio_directions(ratios, matched),
                 ratio_labels={k: label for k, _, _, label in RATIOS},
                 matched_bands=[f"{lo}–{hi}" for lo, hi in MATCHED_BANDS])
    return countries, rows, ts, extra


# ---------- outputs ----------

def write_json(countries, rows, ts):
    keep = {k: {c: {y: round(v, 3) for y, v in s.items() if 2000 <= y <= 2024} for c, s in ser.items() if c in COUNTRIES}
            for k, ser in ts.items()}
    data = dict(base=BASE, end=END, countries=countries, rows=rows, series=keep)
    (OUT / "change_matrix.json").write_text(json.dumps(data, ensure_ascii=False, default=lambda o: None), encoding="utf-8")
    csv = ["row,country,change"]
    for r in rows:
        for c, v in r["cells"].items():
            csv.append(f"{r['key']},{c},{'' if v is None else round(v, 3)}")
    (OUT / "change_matrix.csv").write_text("\n".join(csv), encoding="utf-8")


def scatters(countries, rows):
    d_m30 = {c["iso"]: c["d_m30"] for c in countries}
    names = {c["iso"]: c["name"] for c in countries}
    for r in rows:
        if r["kind"] != "factor":
            continue
        pts = [(c, v, d_m30[c]) for c, v in r["cells"].items()
               if v is not None and d_m30[c] is not None and not r.get("low_confidence", {}).get(c)]
        fig = go.Figure(go.Scatter(
            x=[p[1] for p in pts], y=[p[2] for p in pts], mode="markers+text", text=[p[0] for p in pts],
            textposition="top center", textfont=dict(size=10, color="#6b7280"),
            marker=dict(size=9, color="#2a78d6",
                        symbol=["circle-open" if p[0] in M30_ESTIMATES else "circle" for p in pts],
                        line=dict(color=["#2a78d6" if p[0] in M30_ESTIMATES else "white" for p in pts],
                                  width=[2 if p[0] in M30_ESTIMATES else 1 for p in pts])),
            customdata=[names[p[0]] + (" (estimated child by 30)" if p[0] in M30_ESTIMATES else "") for p in pts],
            hovertemplate="%{customdata}<br>Change in factor: %{x:." + str(r.get("dp", 1)) + "f}<br>Change in % with a child by 30: %{y:+.1f}<extra></extra>"))
        stat = f"{r['toward_fewer_in_falling']} of {r['n_falling']} falling countries towards fewer births"
        fig.update_layout(
            template="plotly_white", height=420, margin=dict(l=60, r=20, t=50, b=50),
            title=dict(text=f"{r['long']}, {BASE}–{END}: {stat}, n = {r['n']}", font=dict(size=13)),
            xaxis_title=f"Change in {r['long'][0].lower() + r['long'][1:]}", yaxis_title="Change in % with a child by 30 (points)")
        fig.add_hline(y=0, line=dict(color="#d1d5db", width=1))
        fig.add_vline(x=0, line=dict(color="#d1d5db", width=1))
        fig.write_html(OUT / f"change_scatter_{r['key']}.html", include_plotlyjs="cdn", full_html=True)


def render_preceding(reference):
    """The same matrix for the years before the fall, written as its own page."""
    global BASE, END
    main_window = BASE, END
    BASE, END = PRECEDING
    try:
        countries, rows, ts, _ = build(reference)
        keys = (["tfr"] + [f"mothers_by_{a}" for a in CHILD_AGES] + [k for k, *_ in RATE_ROWS] + [k for k, *_ in FACTORS]
                + [k for k, *_ in RATIO_ROWS] + SUMMARY_KEYS)
        slim = {k: {c: {y: round(v, 3) for y, v in s.items() if 2000 <= y <= 2023} for c, s in ts[k].items() if c in COUNTRIES}
                for k in keys}
        note = (f"Fit: correlation across countries between the factor's {BASE}–{END} change and the later fall in % of women "
                f"with a child by 30 ({main_window[0]}–{main_window[1]}); positive means it was already moving towards fewer "
                "births where the later fall was largest. Shown for factors with 10 or more countries.")
        falling = f"Countries where TFR fell by more than 0.1 in {main_window[0]}–{main_window[1]}, and this row moved towards fewer births"
        for name, rs in ((f"change_matrix_{BASE}_{END}.html", rows), (f"change_matrix_no_second_{BASE}_{END}.html", without_second(rows))):
            data = json.dumps(dict(base=BASE, end=END, countries=countries, rows=rs, series=slim, fit_note=note, falling_note=falling),
                              ensure_ascii=False, default=lambda o: None).replace("NaN", "null")
            tpl = pathlib.Path(__file__).resolve().parent / "templates"
            html = (tpl / "change_matrix.html").read_text(encoding="utf-8")
            html = html.replace("__DATA__", data).replace("__PAGES__", "../../factors/").replace(
                "__PROFILE__", "../../factors/country-detail.html")
            (OUT / name).write_text(html, encoding="utf-8")
        render_first_second(countries, rows, ts, BASE, END, f"change_matrix_first_second_{BASE}_{END}.html", main_window)
        return rows
    finally:
        BASE, END = main_window


# ---------- first vs second births only ----------

PAIR_AGES = [("20–24", "first_20_24", "second_20_24", "abort_first_20_24", "abort_later_20_24"),
             ("25–29", "first_25_29", "second_25_29", "abort_first_25_29", "abort_later_25_29"),
             ("30–34", "first_30_34", "second_30_34", "abort_first_30_34", "abort_later_30_34"),
             ("35–39", "first_35_39", "second_35_39", "abort_first_35", "abort_later_35")]
PAIR_LABELS = {"first": "First-birth rate", "second": "Second-birth rate",
               "abort_first": "First pregnancies aborted", "abort_later": "Later pregnancies aborted"}
PAIR_NOTES = {"first": "% change in first births per woman with no children",
              "second": "% change in second births per mother of one"}


def first_second_rows(countries, rows):
    """Birth-rate and abortion rows, one group per metric with a row per age, on shared colour scales."""
    by_key = {r["key"]: r for r in rows}
    out = []
    for i, (kind, metric) in enumerate(PAIR_LABELS.items()):
        for age, *keys in PAIR_AGES:
            key = keys[i]
            r = dict(by_key[key])
            age = "35+" if key.endswith("_35") else age
            r.update(group=metric, label=age, long=f"{metric}, {age}", age=age,
                     page=None if kind in ("first", "second") else r.get("page"), detail=False)
            if kind in PAIR_NOTES:
                r["group_note"] = PAIR_NOTES[kind]
            out.append(r)
    for prefix in (("first", "second"), ("abort_",)):
        same = [r for r in out if r["key"].startswith(prefix)]
        vals = sorted(abs(v) for r in same for v in r["cells"].values() if v is not None)
        for r in same:
            r["scale"] = vals[int(0.9 * (len(vals) - 1))] if vals else 1
    keep = [c for c in countries if any(by_key[k]["cells"].get(c["iso"]) is not None for _, *ks in PAIR_AGES for k in ks)]
    return keep, out


def render_first_second(countries, rows, ts, base, end, name, window=None):
    keep, out = first_second_rows(countries, rows)
    keys = ["tfr", "mothers_by_30"] + [k for _, *ks in PAIR_AGES for k in ks]
    slim = {k: {c: {y: round(v, 3) for y, v in s.items() if 2000 <= y <= 2023} for c, s in ts[k].items() if c in COUNTRIES}
            for k in keys}
    w = window or (base, end)
    falling = f"Countries where TFR fell by more than 0.1 in {w[0]}–{w[1]}, and this row moved towards fewer births"
    data = json.dumps(dict(base=base, end=end, countries=keep, rows=out, series=slim, falling_note=falling),
                      ensure_ascii=False, default=lambda o: None).replace("NaN", "null")
    tpl = pathlib.Path(__file__).resolve().parent / "templates"
    html = (tpl / "change_matrix.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", data).replace("__PAGES__", "../../factors/").replace(
        "__PROFILE__", "../../factors/country-detail.html")
    (OUT / name).write_text(html, encoding="utf-8")
    csv = ["age,row,country,change_pct"]
    for r in out:
        for c in keep:
            v = r["cells"].get(c["iso"])
            csv.append(f"{r['age']},{r['group']},{c['iso']},{'' if v is None else round(v, 2)}")
    (OUT / name.replace(".html", ".csv")).write_text("\n".join(csv), encoding="utf-8")
    return keep, out


def without_second(rows):
    """The matrix minus second-birth rates and abortions of later pregnancies."""
    return [r for r in rows if not r["key"].startswith(("second_", "abort_later_"))]


def render(countries, rows, ts, extra):
    keys = ["tfr"] + [f"mothers_by_{a}" for a in CHILD_AGES] + ["mothers_ever", "second_child", "age_first", "couple_25_49"] + [k for k, *_ in RATE_ROWS] + [
        k for k, *_ in FACTORS] + sorted({k for k, *_ in RATIOS} | {k for k, *_ in RATIO_ROWS}) + SUMMARY_KEYS
    slim = {k: {c: {y: round(v, 3) for y, v in s.items() if 2000 <= y <= 2023} for c, s in ts[k].items() if c in COUNTRIES}
            for k in keys}
    data = json.dumps(dict(base=BASE, end=END, countries=countries, rows=rows, series=slim, **extra),
                      ensure_ascii=False, default=lambda o: None).replace("NaN", "null")
    tpl = pathlib.Path(__file__).resolve().parent / "templates"
    html = (tpl / "change_matrix.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", data).replace("__PAGES__", "../../factors/").replace(
        "__PROFILE__", "../../factors/country-detail.html")
    (OUT / "change_matrix.html").write_text(html, encoding="utf-8")
    data_ns = json.dumps(dict(base=BASE, end=END, countries=countries, rows=without_second(rows), series=slim, **extra),
                         ensure_ascii=False, default=lambda o: None).replace("NaN", "null")
    html_ns = (tpl / "change_matrix.html").read_text(encoding="utf-8").replace("__DATA__", data_ns).replace(
        "__PAGES__", "../../factors/").replace("__PROFILE__", "../../factors/country-detail.html")
    (OUT / "change_matrix_no_second.html").write_text(html_ns, encoding="utf-8")
    html = (tpl / "country_profiles.html").read_text(encoding="utf-8")
    html = html.replace("__DATA__", data).replace("__BASE__", str(BASE)).replace("__END__", str(END))
    (OUT / "country_profiles.html").write_text(html, encoding="utf-8")


def main():
    countries, rows, ts, extra = build()
    write_json(countries, rows, ts)
    render(countries, rows, ts, extra)
    render_first_second(countries, rows, ts, BASE, END, "change_matrix_first_second.html")
    scatters(countries, rows)
    for r in render_preceding(countries):
        fit = "  n/a" if r["fit"] is None else f"{r['fit']:+.2f}"
        print(f"PRE {r['key']:20s} n={r['n']:2d} fit {fit} toward-fewer {r['toward_fewer_in_falling']}/{r['n_falling']} median {r['after']}")
    for c in countries:
        m30 = "n/a" if c["d_m30"] is None else f"{c['d_m30']:+.1f}"
        print(f"{c['iso']} TFR {c['d_tfr']:+.2f} child by 30 {m30}")
    for r in rows:
        fit = "  n/a" if r["fit"] is None else f"{r['fit']:+.2f}"
        print(f"{r['label']:34s} fit {fit} n={r['n']:2d} toward-fewer {r.get('toward_fewer_in_falling')}/{r.get('n_falling')}"
              f" before {r.get('before')} after {r.get('after')}")
    for iso, row in extra["ratio_dirs"].items():
        print(iso, extra["profiles"].get(iso, {}).get("source"), row)


if __name__ == "__main__":
    main()
