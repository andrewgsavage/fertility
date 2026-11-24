"""Births to women in and out of a co-residential couple, by mother's age group, England and
Wales, 2002-2025, with the share of women living in a couple at those ages.

Births: ONS Births in England and Wales: birth registrations 2025, Table 6 (live births by
registration type and age of mother, 1938-2025). "In a couple" = registered within marriage
or civil partnership, or registered jointly by parents giving the same address; "not in a
couple" = sole registrations and joint registrations from different addresses. Same-address
joint registration is ONS's proxy for cohabitation; married parents who live apart count as
a couple.
Women: Table 10 (live births and age-specific fertility rate by mother's age), women =
births / ASFR x 1000. Births at 40 and over are kept as one group over women 40-44 (the
denominator of ONS's 40-and-over rate) and set against the LFS 40-44 couple share.
Couple share: ONS/outputs/coupling_by_age_ew.csv (LFS living arrangements, women married,
civil partnered or cohabiting). ONS publishes only one group under 30 (16-29; 18-29 in
2025), so births and women under 30 are pooled into 15-29.

Input (download into ONS/data/ - not tracked in git):
  2025birthregistrations.xlsx
    https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/birthsinenglandandwalesbirthregistrations/2025/2025birthregistrations.xlsx

Output: ONS/outputs/births_by_union_ew.csv (year, age, women, coupled, births_coupled,
births_uncoupled), counts; coupled = women x LFS couple share.
"""

import pandas as pd

from common.paths import data_dir, outputs_dir

XLSX = data_dir("ONS") / "2025birthregistrations.xlsx"
AREA = "England, Wales and Elsewhere"
# mother's age group in the births tables -> pooled group matching the LFS couple groups
GROUP = {"Under 20": "15-29", "20 to 24": "15-29", "25 to 29": "15-29", "30 to 34": "30-34",
         "35 to 39": "35-39", "40 to 44": "40-44", "45 and over": "40-44", "45 to 49": "40-44",
         "50 and over": "40-44", "40 and over": "40-44"}
LFS_GROUP = {"16 to 29": "15-29", "30 to 34": "30-34", "35 to 39": "35-39", "40 to 44": "40-44"}


def num(s):
    """Counts are numbers in some years and comma-grouped strings in others."""
    return pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")


def reg_class(t):
    t = t.lower()
    if t.startswith("within marriage"):
        return "coupled"
    if "same address" in t:
        return "coupled"
    if "different address" in t or t.startswith("sole"):
        return "uncoupled"
    return None  # totals and "outside marriage" / "all joint" subtotals


def births():
    d = pd.read_excel(XLSX, sheet_name="Table_6", header=5)
    d = d[(d.Country == AREA) & (d["Age of Father at birth (years)"] == "All ages")]
    d = d.rename(columns={"Year": "year", "Age of Mother at birth (years)": "mage", "Number of Live births": "n"})
    d["cls"] = d["Registration type"].map(reg_class)
    d["age"] = d.mage.map(GROUP)
    d = d.dropna(subset=["cls", "age"])
    d["n"] = num(d.n)
    b = d.pivot_table(index=["year", "age"], columns="cls", values="n", aggfunc="sum")
    return b.rename(columns=lambda c: f"births_{c}")


def women():
    t = pd.read_excel(XLSX, sheet_name="Table_10", header=5)
    t = t[(t.Country == AREA) & (t.Parent == "Mother")]
    t = t.rename(columns={"Year": "year", "Age group (years)": "mage"})
    t = t[t.mage.isin(["Under 20", "20 to 24", "25 to 29", "30 to 34", "35 to 39", "40 and over"])]
    for c in ["Number of live births", "Age-specific fertility rate"]:
        t[c] = num(t[c])
    t["women"] = t["Number of live births"] / t["Age-specific fertility rate"] * 1000
    t["age"] = t.mage.map(GROUP)
    return t.groupby(["year", "age"]).women.sum()


def main():
    c = pd.read_csv(outputs_dir("ONS") / "coupling_by_age_ew.csv")
    c = c[c.sex == "Women"].assign(age=lambda x: x.age.map(LFS_GROUP)).set_index(["year", "age"]).couple
    d = births().join(women(), how="inner").join(c, how="inner").reset_index()
    d["coupled"] = d.women * d.couple / 100
    d = d[["year", "age", "women", "coupled", "births_coupled", "births_uncoupled"]].sort_values(["year", "age"])
    path = outputs_dir("ONS") / "births_by_union_ew.csv"
    d.round(1).to_csv(path, index=False)
    print(d[d.year.isin([2010, 2024])].round(0).to_string(index=False))
    print("wrote", path)


if __name__ == "__main__":
    main()
