"""US women 15-50 and births in the past 12 months, by single year of age and whether the woman
lives in a couple (married with spouse present, or cohabiting), from the American Community
Survey 1-year Public Use Microdata Sample (PUMS).

Couple: MSP == 1 (now married, spouse present) or an unmarried partner of the household
reference person (the partner herself, or the reference person of a household that has
one). Cohabiting couples where neither partner is the reference person (e.g. a couple
living in her parents' home) are not identified by the ACS and count as not in a couple.
Married women with spouse absent and separated women count as not in a couple.
Births: FER == 1 (gave birth in the past 12 months; universe women 15-50).
Relationship code: REL (2008) / RELP (2010-2018) 13 = unmarried partner, 0 = reference
person; RELSHIPP (2019 on) 22/24 = opposite- and same-sex unmarried partner, 20 = reference
person.

Inputs (download into ACS/data/ - not tracked in git): the national person-record zip
for each year, renamed acs_pus_<year>.zip, from
  https://www2.census.gov/programs-surveys/acs/data/pums/<year>/1-Year/csv_pus.zip
for <year> in YEARS (e.g. https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pus.zip).
No API key is needed for these files (the Census microdata API now needs one).

Output: ACS/outputs/acs_births_by_union.csv, weighted (PWGTP) counts by year x age:
women, coupled (women in a couple), births_coupled, births_uncoupled.
"""

import zipfile

import pandas as pd

from common.paths import data_dir, outputs_dir

YEARS = [2008, 2010, 2019, 2024]
COLS = ["SERIALNO", "PWGTP", "AGEP", "SEX", "MSP", "FER", "REL", "RELP", "RELSHIPP"]


def read_year(year):
    zpath = data_dir("ACS") / f"acs_pus_{year}.zip"
    parts = []
    with zipfile.ZipFile(zpath) as z:
        for name in sorted(n for n in z.namelist() if n.lower().endswith(".csv")):
            with z.open(name) as f:
                header = pd.read_csv(f, nrows=0).columns
            use = [c for c in COLS if c in header]
            with z.open(name) as f:
                for chunk in pd.read_csv(f, usecols=use, chunksize=500_000, dtype={"SERIALNO": str}):
                    parts.append(chunk)
    return pd.concat(parts, ignore_index=True)


def tabulate(year):
    p = read_year(year)
    if "RELSHIPP" in p:
        ref = p.RELSHIPP == 20
        partner = p.RELSHIPP.isin([22, 24])
    else:
        rel = p.RELP if "RELP" in p else p.REL  # REL in 2008, same codes
        ref = rel == 0
        partner = rel == 13
    with_partner = set(p.loc[partner, "SERIALNO"])
    cohab = partner | (ref & p.SERIALNO.isin(with_partner))
    w = p[(p.SEX == 2) & p.AGEP.between(15, 50)].copy()
    w["coupled"] = (w.MSP == 1) | cohab.loc[w.index]
    w["birth"] = w.FER == 1
    w["wt"] = w.PWGTP
    g = w.groupby("AGEP")
    out = pd.DataFrame({
        "women": g.wt.sum(),
        "coupled": w[w.coupled].groupby("AGEP").wt.sum(),
        "births_coupled": w[w.coupled & w.birth].groupby("AGEP").wt.sum(),
        "births_uncoupled": w[~w.coupled & w.birth].groupby("AGEP").wt.sum(),
    }).fillna(0).reset_index().rename(columns={"AGEP": "age"})
    out.insert(0, "year", year)
    return out


def main():
    d = pd.concat([tabulate(y) for y in YEARS])
    path = outputs_dir("ACS") / "acs_births_by_union.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(path, index=False)
    s = d.groupby("year")[["women", "coupled", "births_coupled", "births_uncoupled"]].sum()
    s["asfr_sum"] = d.assign(f=(d.births_coupled + d.births_uncoupled) / d.women).groupby("year").f.sum()
    s["coupled_share"] = s.coupled / s.women
    s["births_in_couples_share"] = s.births_coupled / (s.births_coupled + s.births_uncoupled)
    print(s[["asfr_sum", "coupled_share", "births_in_couples_share"]].round(3))
    print("wrote", path)


if __name__ == "__main__":
    main()
