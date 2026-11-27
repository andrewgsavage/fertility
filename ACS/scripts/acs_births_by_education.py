"""US women and births in the past 12 months, by single year of age and educational attainment,
from the American Community Survey 1-year Public Use Microdata Sample (PUMS).

Education (SCHL, same 24 codes in every year used):
  less than high school = 1-15 (no diploma), high school = 16-17 (diploma or GED),
  some college = 18-20 (some college, associate degree), bachelor's or more = 21-24.
Enrolled: SCH 2 or 3 (attended school or college in the past 3 months); SCH 1 = not enrolled.
Births: FER == 1 (gave birth in the past 12 months; universe women 15-50). Age is age at the
survey, so a birth can have happened at the previous year of age.

Inputs (download into ACS/data/ - not tracked in git): the national person-record zip
for each year, renamed acs_pus_<year>.zip, from
  https://www2.census.gov/programs-surveys/acs/data/pums/<year>/1-Year/csv_pus.zip

Output: ACS/outputs/acs_births_by_education.csv, weighted (PWGTP) counts by year x age x
education x enrolled: women, births.
"""

import zipfile

import pandas as pd

from common.paths import data_dir, outputs_dir

YEARS = [2008, 2010, 2012, 2015, 2017, 2019, 2022, 2024]
COLS = ["PWGTP", "AGEP", "SEX", "FER", "SCHL", "SCH"]
EDUCATION = [
    (1, 15, "Less than high school"),
    (16, 17, "High school"),
    (18, 20, "Some college"),
    (21, 24, "Bachelor's or more"),
]


def education(schl):
    out = pd.Series(pd.NA, index=schl.index, dtype="object")
    for lo, hi, label in EDUCATION:
        out[schl.between(lo, hi)] = label
    return out


def tabulate(year):
    parts = []
    with zipfile.ZipFile(data_dir("ACS") / f"acs_pus_{year}.zip") as z:
        for name in sorted(n for n in z.namelist() if n.lower().endswith(".csv")):
            with z.open(name) as f:
                for c in pd.read_csv(f, usecols=COLS, chunksize=500_000):
                    parts.append(c[(c.SEX == 2) & c.AGEP.between(15, 50)])
    w = pd.concat(parts, ignore_index=True)
    w["education"] = education(w.SCHL)
    w["enrolled"] = w.SCH.isin([2, 3])
    w["births"] = w.PWGTP.where(w.FER == 1, 0)
    out = (w.groupby(["AGEP", "education", "enrolled"])
           .agg(women=("PWGTP", "sum"), births=("births", "sum"))
           .reset_index().rename(columns={"AGEP": "age"}))
    out.insert(0, "year", year)
    return out


def main():
    d = pd.concat([tabulate(y) for y in YEARS])
    path = outputs_dir("ACS") / "acs_births_by_education.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(path, index=False)
    print("wrote", path)


if __name__ == "__main__":
    main()
