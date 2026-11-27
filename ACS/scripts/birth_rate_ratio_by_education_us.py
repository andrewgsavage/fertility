"""US birth rate by education and age, 2022 and 2024 relative to 2008-2012.

Reads ACS/outputs/acs_births_by_education.csv (from acs_births_by_education.py: ACS PUMS women
by year, single age, education and school enrolment, with births in the last 12 months) and
writes ACS/outputs/birth_rate_ratio_by_education_us.csv: for each education level and 5-year
age band, the mean birth rate in 2022 and 2024 divided by the mean of 2008, 2010 and 2012
(the ACS years tabulated around 2010).
Rates are computed by single year of age and averaged unweighted within the band, so a change
in the age mix within a band doesn't move the ratio. Women enrolled in school are left out.
Used for the education grid on docs/theory/family-transitions.md.
"""

import pandas as pd

from common.paths import outputs_dir

EDU = ["Less than high school", "High school", "Some college", "Bachelor's or more"]
BANDS = [(20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]
BASE = [2008, 2010, 2012]
LATEST = [2022, 2024]


def main():
    d = pd.read_csv(outputs_dir("ACS") / "acs_births_by_education.csv")
    d = d[~d.enrolled]
    g = d.groupby(["year", "age", "education"])[["births", "women"]].sum()
    g = g.assign(all=g.births / g.women)
    tot = d.groupby(["year", "age"])[["births", "women"]].sum()
    rows = []
    for ed in EDU + ["All women"]:
        r = tot.births / tot.women if ed == "All women" else g.xs(ed, level="education")["all"]
        for lo, hi in BANDS:
            band = r[(r.index.get_level_values("age") >= lo) & (r.index.get_level_values("age") <= hi)]
            mean = lambda ys: band[band.index.get_level_values("year").isin(ys)].groupby("age").mean().mean()
            rows.append({"education": ed, "age": f"{lo}-{hi}", "base": mean(BASE), "latest": mean(LATEST),
                         "ratio": mean(LATEST) / mean(BASE)})
    out = pd.DataFrame(rows)
    out.round(4).to_csv(outputs_dir("ACS") / "birth_rate_ratio_by_education_us.csv", index=False)
    print(out.pivot(index="education", columns="age", values="ratio").reindex(EDU + ["All women"]).round(2))


if __name__ == "__main__":
    main()
