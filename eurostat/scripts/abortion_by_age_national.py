"""Abortions (and some births) by age from national sources, for abortion_by_age.py.

Where a country has a national series, it replaces Eurostat's for the years it
covers. Each loader returns rows of country, year, age group, abortions, and
abortions_unknown_age (the share of abortions with no age, spread across the
known groups in proportion). Age groups: Under 20, 20–24, 25–29, 30–34, 35+.

Files read (not tracked in git):
  eurostat/data/national/se_aborter_2025.xlsx  Socialstyrelsen, Statistik om aborter 2025, tables
      https://www.socialstyrelsen.se/contentassets/cd298b78f0ad45c8a044d38623470348/2026-6-10342-tabeller.xlsx
  eurostat/data/national/no_abr_a2.csv  FHI Abortregisteret table A2, whole country, counts
      POST https://statistikk-data.fhi.no/api/open/v1/abr/Table/283/data  (BOFYLKE_K=ZZ, MEASURE_TYPE=ANTALL, csv2)
  ONS/data/scotland/residence_age.csv  Public Health Scotland, terminations by health board and age
      https://www.opendata.nhs.scot/dataset/termination-of-pregnancy-in-scotland
  ONS/data/scotland/nrs_births_ts_2024.xlsx  NRS births time series 2024, Table 2 (births by mother's age)
      https://nrscotland.gov.uk/publications/births-time-series-data-2024
  ONS/data/2025birthregistrations.xlsx  ONS births in England and Wales: birth registrations, Table 10
      https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/birthsinenglandandwalesbirthregistrations
  ONS/data/abortion-statistics-2023-england-and-wales-residents.ods  DHSC, Table 3b (2013-2023)

Transcribed below: DHSC 2014 tables (England & Wales 2004-2012), Destatis
(Germany 2012-2025), IGJ (Netherlands 2020-2024), CDC (US 2013-2022) and MHLW
(Japan FY2003-2024), each with its source.
"""

import openpyxl
import pandas as pd

from common import ons_abortion as ew
from common.paths import data_dir

NAT = data_dir("eurostat") / "national"
ONS = data_dir("ONS")

AGES = ["Under 20", "20–24", "25–29", "30–34", "35+"]
COLS = ["country", "year", "age", "abortions", "abortions_unknown_age"]


def _spread(country, year, known, total):
    """Scale {age: n} up to total; returns rows with the unknown share."""
    s = sum(known.values())
    return [(country, year, a, n * total / s, 1 - s / total) for a, n in known.items()]


# --- England & Wales ---------------------------------------------------------
# DHSC, Abortion statistics 2014, complete tables, Table 3b (residents), 2004-2012.
# https://assets.publishing.service.gov.uk/media/5a801a13ed915d74e622c7a1/2014_complete_tables.xlsx
EW_YEARS = list(range(2004, 2013))
EW_OLD = {
    "Under 16": [3756, 3786, 3990, 4376, 4113, 3823, 3718, 3258, 2925],
    "16-17": [14136, 14237, 14629, 15913, 15273, 14093, 12742, 11341, 9948],
    "18-19": [21250, 21076, 22667, 23666, 23303, 22151, 21809, 20324, 18507],
    "20–24": [52701, 53342, 55340, 56963, 56172, 54749, 55481, 55909, 54558],
    "25–29": [37759, 38330, 40396, 41704, 41896, 40634, 40800, 42321, 41882],
    "30–34": [28064, 27836, 28153, 27257, 26985, 26701, 27978, 29579, 30353],
    "35+": [27749, 27809, 28562, 28620, 27554, 26949, 27046, 27199, 26949],
}
EW_ODS = {"Under 20": ["Under 18", "18 to 19"], "20–24": ["20 to 24"], "25–29": ["25 to 29"],
          "30–34": ["30 to 34"], "35+": ["35 or over"]}


def england_wales_abortions():
    rows = []
    for i, y in enumerate(EW_YEARS):
        k = {"Under 20": sum(EW_OLD[a][i] for a in ("Under 16", "16-17", "18-19"))}
        k.update({a: EW_OLD[a][i] for a in AGES[1:]})
        rows += [("England & Wales", y, a, n, 0.0) for a, n in k.items()]
    t = ew.read_ods_sheet(ew.ODS, "Table_3b")
    header = next(r for r in t if len(r) > 2 and r[1] == "Age group")
    years = {i: int(h[:4]) for i, h in enumerate(header) if h[:4].isdigit()}
    num = {r[1]: r for r in t if r and r[0] == "Numbers"}
    for i, y in years.items():
        for a, labels in EW_ODS.items():
            rows.append(("England & Wales", y, a, sum(float(num[l][i]) for l in labels), 0.0))
    return pd.DataFrame(rows, columns=COLS)


def england_wales_births():
    """ONS Table 10: live births by mother's age, 1938-2025."""
    ws = openpyxl.load_workbook(ONS / "2025birthregistrations.xlsx", read_only=True)["Table_10"]
    m = {"Under 20": "Under 20", "20 to 24": "20–24", "25 to 29": "25–29", "30 to 34": "30–34",
         "35 to 39": "35+", "40 and over": "35+"}
    rows = [(r[0], m[r[3]], r[4]) for r in ws.iter_rows(min_row=7, values_only=True)
            if r[0] and r[1] == "England, Wales and Elsewhere" and r[2] == "Mother" and r[3] in m]
    d = pd.DataFrame(rows, columns=["year", "age", "births"]).groupby(["year", "age"], as_index=False).births.sum()
    return d.assign(country="England & Wales")


# --- Scotland -----------------------------------------------------------------
def scotland_abortions():
    d = pd.read_csv(ONS / "scotland" / "residence_age.csv")
    d = d[d.HBR != "RA2704"]  # residence outside Scotland or unknown
    d["n"] = pd.to_numeric(d.NumberofTerminations, errors="coerce")
    m = {"Under 20": "Under 20", "20 - 24": "20–24", "25 - 29": "25–29", "30 - 34": "30–34",
         "35 - 39": "35+", "40 Plus": "35+"}
    rows = []
    for y, g in d.groupby("YearofTermination"):
        total = g[g.ageGroup == "All ages"].n.sum()
        known = g[g.ageGroup.isin(m)].assign(age=lambda x: x.ageGroup.map(m)).groupby("age").n.sum()
        rows += _spread("Scotland", int(y), known.to_dict(), total)
    return pd.DataFrame(rows, columns=COLS)


def scotland_births():
    """NRS births time series Table 2, births by mother's age, 1945-2024."""
    rows = list(openpyxl.load_workbook(ONS / "scotland" / "nrs_births_ts_2024.xlsx",
                                       read_only=True)["Table_2"].iter_rows(values_only=True))
    header = next(r for r in rows if r[0] == "Age of mother")
    years = {i: int(h) for i, h in enumerate(header) if h and str(h).isdigit()}
    m = {"under 20": "Under 20", "20 to 24": "20–24", "25 to 29": "25–29", "30 to 34": "30–34",
         "35 to 39": "35+", "40 to 44": "35+", "45 to 49": "35+", "50 and over": "35+"}
    out = []
    lab = {r[0]: r for r in rows if r[0]}
    for i, y in years.items():
        num = lambda v: float(v) if isinstance(v, (int, float)) else 0.0  # noqa: E731
        known = {}
        for k, a in m.items():
            known[a] = known.get(a, 0.0) + num(lab[k][i])
        total = num(lab["All"][i])
        s = sum(known.values())
        out += [(y, a, n * total / s) for a, n in known.items()]  # spread "Not stated"
    return pd.DataFrame(out, columns=["year", "age", "births"]).assign(country="Scotland")


# --- Sweden -------------------------------------------------------------------
def sweden_abortions():
    """Socialstyrelsen Table 1, 1983-2025 (no data for 2013; new collection method from 2014)."""
    ws = openpyxl.load_workbook(NAT / "se_aborter_2025.xlsx", read_only=True)["1. Antal"]
    rows = list(ws.iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows) if r and r[0] == "År")
    head = rows[h]
    col = {name: j for j, name in enumerate(head) if name}
    m = {"-19 år": "Under 20", "20-24 år": "20–24", "25-29 år": "25–29", "30-34 år": "30–34",
         "35-39 år": "35+", "40+ år": "35+"}
    out = []
    for r in rows[h + 1:]:
        y = str(r[0] or "").rstrip("*")
        if not y.isdigit() or not isinstance(r[col["Totalt"]], (int, float)):
            continue
        known = {}
        for k, a in m.items():
            known[a] = known.get(a, 0) + r[col[k]]
        out += _spread("Sweden", int(y), known, r[col["Totalt"]])
    return pd.DataFrame(out, columns=COLS)


# --- Norway -------------------------------------------------------------------
def norway_abortions():
    """FHI Abortregisteret table A2, whole country, 1979-2025."""
    d = pd.read_csv(NAT / "no_abr_a2.csv", sep=";")
    d["n"] = pd.to_numeric(d.Antall, errors="coerce")
    m = {"Under 20 år": "Under 20", "20-24 år": "20–24", "25-29 år": "25–29", "30-34 år": "30–34",
         "35-39 år": "35+", "40 år og over": "35+"}
    out = []
    for y, g in d.groupby("År"):
        total = g[g.Alder.str.startswith("Alle")].n.sum()
        known = g[g.Alder.isin(m)].assign(age=lambda x: x.Alder.map(m)).groupby("age").n.sum()
        out += _spread("Norway", int(y), known.to_dict(), total)
    return pd.DataFrame(out, columns=COLS)


# --- Germany ------------------------------------------------------------------
# Destatis, Schwangerschaftsabbrüche nach Altersgruppen, 2012-2022 and from 2023.
# https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Gesundheit/Schwangerschaftsabbrueche/_inhalt.html
DE_YEARS = list(range(2012, 2026))
DE = {
    "<15": [373, 322, 369, 337, 330, 280, 240, 294, 264, 259, 284, 304, 305, 255],
    "15-18": [3462, 3297, 3191, 2970, 2750, 2729, 2506, 2392, 2430, 2183, 2444, 2512, 2750, 2790],
    "18-20": [6654, 5969, 5246, 5246, 4985, 4904, 4952, 4673, 4462, 4040, 4604, 4949, 5150, 5080],
    "20–24": [25625, 23723, 21761, 20646, 19797, 19942, 19832, 19780, 19113, 17904, 19591, 20123,
              19955, 19745],
    "25–29": [24888, 24407, 24030, 24323, 24365, 24859, 24361, 23511, 22593, 21154, 23339, 23777,
              23910, 24105],
    "30–34": [22199, 21785, 21706, 21835, 22341, 23127, 23773, 24043, 24370, 23187, 25195, 25035,
              24475, 23690],
    "35-39": [15469, 15452, 15838, 16368, 16790, 17643, 17652, 18134, 18655, 17973, 19675, 20499,
              20780, 20870],
    "40-44": [7440, 7137, 6822, 6787, 6673, 7018, 7025, 7444, 7411, 7300, 8144, 8252, 8405, 8425],
    "45-49": [688, 695, 738, 701, 677, 691, 631, 607, 627, 580, 629, 747, 695, 730],
    "50+": [17, 15, 14, 24, 13, 16, 14, 15, 23, 16, 22, 20, 25, 15],
}
DE_TOTAL = [106815, 102802, 99715, 99237, 98721, 101209, 100986, 100893, 99948, 94596, 103927,
            106218, 106455, 105710]


def germany_abortions():
    out = []
    for i, y in enumerate(DE_YEARS):
        k = {"Under 20": DE["<15"][i] + DE["15-18"][i] + DE["18-20"][i],
             "20–24": DE["20–24"][i], "25–29": DE["25–29"][i], "30–34": DE["30–34"][i],
             "35+": DE["35-39"][i] + DE["40-44"][i] + DE["45-49"][i] + DE["50+"][i]}
        assert abs(sum(k.values()) - DE_TOTAL[i]) <= 25, y  # 2024+ cells are rounded to 5
        out += [("Germany", y, a, n, 0.0) for a, n in k.items()]
    return pd.DataFrame(out, columns=COLS)


# --- Netherlands --------------------------------------------------------------
# IGJ, Jaarrapportage Wet afbreking zwangerschap, bijlage: Tabel F (2021 report,
# 2019-2021) and Tabel E (2024 report, 2022-2024). These count every abortion
# done in the Netherlands, including women living abroad, so each year is scaled
# to the number of women living in the Netherlands (Tabel A / Bijlage 3).
# https://zoek.officielebekendmakingen.nl/blg-1050878.pdf
# https://zoek.officielebekendmakingen.nl/blg-1220761.pdf
NL_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
NL = {
    "<15": [70, 58, 101, 81, 107, 65],
    "15-19": [2583, 2297, 2282, 2621, 2783, 2749],
    "20–24": [6645, 6135, 6034, 7392, 8285, 8370],
    "25–29": [7863, 7688, 7171, 8215, 9158, 9200],
    "30–34": [7340, 7294, 7440, 8340, 9269, 9243],
    "35-39": [5378, 5410, 5489, 6115, 6707, 6707],
    "40-44": [2128, 2231, 2313, 2562, 2749, 2788],
    "45+": [221, 242, 217, 267, 254, 289],
    "unknown": [5, 9, 2, 13, 20, 27],
}
NL_TOTAL = [32233, 31364, 31049, 35606, 39332, 39438]
NL_RESIDENT = {2020: 28532, 2021: 28089, 2022: 32339, 2023: 36024, 2024: 35647}


def netherlands_abortions():
    out = []
    for i, y in enumerate(NL_YEARS):
        assert sum(v[i] for v in NL.values()) == NL_TOTAL[i], y
        if y not in NL_RESIDENT:
            continue
        k = {"Under 20": NL["<15"][i] + NL["15-19"][i], "20–24": NL["20–24"][i],
             "25–29": NL["25–29"][i], "30–34": NL["30–34"][i],
             "35+": NL["35-39"][i] + NL["40-44"][i] + NL["45+"][i]}
        out += _spread("Netherlands", y, k, NL_RESIDENT[y])
    d = pd.DataFrame(out, columns=COLS)  # unknown share: age not filled in
    unk = {y: NL["unknown"][NL_YEARS.index(y)] / NL_TOTAL[NL_YEARS.index(y)] for y in NL_RESIDENT}
    d["abortions_unknown_age"] = d.year.map(unk)
    return d


# --- United States ------------------------------------------------------------
# CDC, Abortion Surveillance — United States, 2022 (MMWR SS 73(7)), Table 4: 43
# reporting areas that reported every year 2013-2022 (excludes CA, DC, FL, ME, MD,
# NH, NJ, TN, WY). % of known-age abortions by age, the total known-age count, and
# the abortion ratio per 1,000 live births. Abortions = % x total; births in the
# same areas = abortions / ratio x 1,000 (so births carry the ratio's rounding).
# https://pmc.ncbi.nlm.nih.gov/articles/PMC11616987/
US_YEARS = list(range(2013, 2023))
US_TOTAL = [544986, 531041, 520602, 508565, 497249, 500974, 508955, 502481, 514695, 498095]
US_PCT = {
    "<15": [0.3, 0.3, 0.3, 0.3, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
    "15-19": [11.5, 10.4, 9.8, 9.4, 9.1, 8.8, 8.7, 8.3, 8.2, 8.5],
    "20-24": [32.7, 32.2, 31.2, 30.1, 29.4, 28.6, 27.9, 28.2, 28.5, 28.5],
    "25-29": [25.9, 26.7, 27.6, 28.5, 28.9, 29.3, 29.3, 29.3, 28.7, 28.2],
    "30-34": [16.8, 17.2, 17.7, 18.0, 18.3, 18.8, 19.4, 19.7, 20.2, 20.4],
    "35-39": [9.2, 9.6, 10.0, 10.3, 10.5, 10.7, 10.8, 10.6, 10.6, 10.6],
    "40+": [3.6, 3.6, 3.6, 3.6, 3.6, 3.5, 3.7, 3.6, 3.5, 3.6],
}
US_RATIO = {
    "<15": [771, 737, 690, 724, 788, 846, 858, 809, 780, 796],
    "15-19": [297, 289, 286, 292, 300, 315, 330, 338, 366, 374],
    "20-24": [260, 253, 249, 247, 248, 254, 259, 273, 290, 284],
    "25-29": [167, 164, 165, 167, 170, 177, 182, 189, 189, 182],
    "30-34": [122, 116, 115, 113, 114, 119, 125, 127, 127, 125],
    "35-39": [149, 145, 141, 137, 135, 136, 138, 135, 132, 125],
    "40+": [247, 240, 230, 221, 213, 209, 216, 207, 198, 183],
}
US_GROUP = {"<15": "Under 20", "15-19": "Under 20", "20-24": "20–24", "25-29": "25–29",
            "30-34": "30–34", "35-39": "35+", "40+": "35+"}


def us():
    """Rows of (year, age group, abortions, births) for the 43 US reporting areas."""
    out = {}
    for i, y in enumerate(US_YEARS):
        for a, g in US_GROUP.items():
            ab = US_PCT[a][i] / 100 * US_TOTAL[i]
            b = ab / US_RATIO[a][i] * 1000
            k = (y, g)
            out[k] = (out.get(k, (0, 0))[0] + ab, out.get(k, (0, 0))[1] + b)
    return [(y, g, ab, b) for (y, g), (ab, b) in out.items()]


# --- Japan --------------------------------------------------------------------
# MHLW, Report on Public Health Administration and Services (衛生行政報告例),
# 母体保護関係, abortions by age group, fiscal years (April-March) 2003-2024.
# https://www.mhlw.go.jp/toukei/saikin/hw/eisei/05/kekka5.html          (FY2003-05)
# https://www.mhlw.go.jp/toukei/saikin/hw/eisei/09/dl/kekka5.pdf        (FY2005-09)
# https://www.mhlw.go.jp/toukei/saikin/hw/eisei_houkoku/14/dl/kekka6.pdf (FY2010-14)
# https://www.mhlw.go.jp/toukei/saikin/hw/eisei_houkoku/19/dl/kekka6.pdf (FY2015-19)
# https://www.mhlw.go.jp/toukei/saikin/hw/eisei_houkoku/24/dl/kekka5.pdf (FY2020-24)
JP_YEARS = list(range(2003, 2025))
JP = {
    "Under 20": [40475, 34745, 30119, 27367, 23985, 22837, 21535,
                 20357, 20903, 20659, 19359, 17854, 16113, 14666, 14128, 13588, 12677,
                 10271, 9093, 9569, 10053, 10844],
    "20–24": [77469, 74711, 72217, 68563, 62523, 56419, 51339,
              47089, 44087, 43269, 40268, 39851, 39430, 38561, 39270, 40408, 39807,
              35438, 30882, 30544, 32547, 33663],
    "25–29": [66297, 61881, 59911, 57698, 54653, 51726, 48621,
              45724, 42708, 40900, 37999, 36594, 35429, 33050, 32222, 31437, 31390,
              28611, 26087, 26153, 27879, 28676],
    "30–34": [63923, 61628, 59748, 57516, 52718, 49473, 45847,
              42206, 39917, 38362, 36757, 36621, 35884, 34256, 33082, 31481, 29404,
              26559, 23386, 22287, 22600, 22424],
    "35–39": [48687, 46878, 46038, 45856, 44161, 43392, 41644,
              39964, 37648, 36112, 34115, 33111, 31765, 30307, 29641, 28887, 28129,
              26018, 23435, 21947, 21379, 20386],
    "40–44": [20950, 20067, 19319, 17725, 17145, 17066, 16544,
              15983, 15697, 16133, 16477, 16558, 16368, 15782, 14876, 14508, 13588,
              13203, 12018, 11079, 11170, 10878],
    "45–49": [1853, 1666, 1663, 1572, 1447, 1379, 1302,
              1334, 1108, 1163, 1237, 1281, 1340, 1352, 1363, 1388, 1400,
              1319, 1252, 1127, 1073, 1079],
    "50+": [28, 16, 28, 26, 24, 22, 27,
            25, 21, 14, 22, 17, 18, 14, 11, 13, 11, 10, 19, 8, 15, 11],
}
JP_TOTAL = [319831, 301673, 289127, 276352, 256672, 242326, 226878,
            212694, 202106, 196639, 186253, 181905, 176388, 168015, 164621, 161741, 156429,
            141433, 126174, 122725, 126734, 127992]


def japan():
    """{(year, age group): abortions}, unknown age left out (under 0.1%)."""
    out = {}
    for a, vals in JP.items():
        g = a if a in ("Under 20", "20–24", "25–29", "30–34") else "35+"
        for y, v in zip(JP_YEARS, vals):
            out[(y, g)] = out.get((y, g), 0) + v
    for i, y in enumerate(JP_YEARS):  # check transcription against the published totals
        s = sum(v for (yy, _), v in out.items() if yy == y)
        assert 0 <= JP_TOTAL[i] - s < 200, (y, s, JP_TOTAL[i])
    return out


def national_abortions():
    """Abortions from national sources that replace Eurostat's (births come from Eurostat/HFD)."""
    return pd.concat([sweden_abortions(), norway_abortions(), germany_abortions(),
                      netherlands_abortions()], ignore_index=True)
