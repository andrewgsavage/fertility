"""% of women with at least one child, by 5-year age group, from every DHS survey of all women
(surveys of ever-married women only are dropped: they overstate motherhood).

Indicator FE_CEBA_W_CH0 (women with no children ever born), breakdown by 5-year age group;
% with a child = 100 - that. Year = survey year (first fieldwork year).

Inputs (download into DHS/data/ - not tracked in git):
  FE_CEBA_W_CH0.json  https://api.dhsprogram.com/rest/dhs/data?indicatorIds=FE_CEBA_W_CH0&breakdown=all&f=json&perpage=20000
  surveys.json        https://api.dhsprogram.com/rest/dhs/surveys?f=json&perpage=2000
Output: DHS/outputs/dhs_mothers.csv (country, iso3, year, age, mother, n_women)
"""

import json
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"

# DHS country name -> ISO3.
ISO3 = {
    "Albania": "ALB", "Angola": "AGO", "Armenia": "ARM", "Bangladesh": "BGD", "Benin": "BEN", "Bolivia": "BOL",
    "Brazil": "BRA", "Burkina Faso": "BFA", "Burundi": "BDI", "Cambodia": "KHM", "Cameroon": "CMR",
    "Colombia": "COL", "Congo": "COG", "Congo Democratic Republic": "COD", "Cote d'Ivoire": "CIV",
    "Dominican Republic": "DOM", "Ecuador": "ECU", "Egypt": "EGY", "El Salvador": "SLV", "Eswatini": "SWZ",
    "Ghana": "GHA", "Guatemala": "GTM", "Guinea": "GIN", "Guyana": "GUY", "Haiti": "HTI", "Honduras": "HND",
    "India": "IND", "Indonesia": "IDN", "Jordan": "JOR", "Kenya": "KEN", "Liberia": "LBR", "Malawi": "MWI",
    "Mali": "MLI", "Mexico": "MEX", "Moldova": "MDA", "Morocco": "MAR", "Mozambique": "MOZ", "Myanmar": "MMR",
    "Namibia": "NAM", "Nepal": "NPL", "Nicaragua": "NIC", "Nigeria": "NGA", "Pakistan": "PAK", "Paraguay": "PRY",
    "Peru": "PER", "Philippines": "PHL", "Rwanda": "RWA", "Sao Tome and Principe": "STP", "Senegal": "SEN",
    "Sierra Leone": "SLE", "South Africa": "ZAF", "Sri Lanka": "LKA", "Tanzania": "TZA", "Thailand": "THA",
    "Togo": "TGO", "Tunisia": "TUN", "Turkey": "TUR", "Uganda": "UGA", "Ukraine": "UKR", "Vietnam": "VNM",
    "Yemen": "YEM", "Zambia": "ZMB", "Zimbabwe": "ZWE", "Trinidad and Tobago": "TTO", "Azerbaijan": "AZE",
    "Botswana": "BWA", "Central African Republic": "CAF", "Chad": "TCD", "Comoros": "COM", "Eritrea": "ERI",
    "Ethiopia": "ETH", "Gabon": "GAB", "Gambia": "GMB", "Kazakhstan": "KAZ", "Kyrgyz Republic": "KGZ",
    "Lesotho": "LSO", "Madagascar": "MDG", "Maldives": "MDV", "Mauritania": "MRT", "Niger": "NER",
    "Papua New Guinea": "PNG", "Tajikistan": "TJK", "Timor-Leste": "TLS", "Turkmenistan": "TKM", "Uzbekistan": "UZB",
}
AGES = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]


def load():
    d = pd.DataFrame(json.loads((DATA / "FE_CEBA_W_CH0.json").read_text("utf-8"))["Data"])
    s = pd.DataFrame(json.loads((DATA / "surveys.json").read_text("utf-8"))["Data"])
    all_women = set(s[s.UniverseOfWomen.str.startswith("All")].SurveyId)
    d = d[(d.CharacteristicCategory == "Age (5-year groups)") & d.CharacteristicLabel.isin(AGES)
          & d.SurveyId.isin(all_women) & (d.SurveyType == "DHS") & (d.IsPreferred == 1)]
    out = pd.DataFrame({
        "country": d.CountryName, "iso3": d.CountryName.map(ISO3), "year": d.SurveyYear.astype(int),
        "age": d.CharacteristicLabel, "mother": 100 - d.Value.astype(float),
        "n_women": d.DenominatorUnweighted})
    # Two surveys in one year (rare): keep the larger sample.
    return out.sort_values("n_women").drop_duplicates(["country", "year", "age"], keep="last") \
        .sort_values(["country", "year", "age"])


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    m = load()
    m.to_csv(OUTDIR / "dhs_mothers.csv", index=False)
    print(m.groupby("country").year.agg(lambda s: sorted(set(s))).to_string())
    print("no ISO3:", sorted(set(m[m.iso3.isna()].country)))
