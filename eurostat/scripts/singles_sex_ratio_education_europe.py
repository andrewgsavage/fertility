"""Unpartnered men per unpartnered woman at ages 25-39, by education, 2021 census.

How many single men of each education level there are for each single woman with a
tertiary degree, by country. "Single" = not living in a couple (married, registered or
cohabiting); people in a couple but with an unknown status are dropped.

Inputs (not tracked in git):
  eurostat/data/cens_21fe_r2.csv
    Eurostat census 2021 "Population by family status, age groups, educational attainment
    level and NUTS 2 region", country level only:
    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/cens_21fe_r2/A..TOTAL+CPL+UNK.Y25-29+Y30-34+Y35-39.F+M.NR.AT+BE+BG+CH+CY+CZ+DE+DK+EE+EL+ES+FI+FR+HR+HU+IE+IS+IT+LI+LT+LU+LV+MT+NL+NO+PL+PT+RO+SE+SI+SK?format=SDMX-CSV
    Single = TOTAL - CPL (person in a couple) - UNK. Includes people outside private
    households. Education: low ISCED 0-2, medium 3-4, tertiary 5-8; unknown dropped.
  ONS/data/census2021/ew_resident_age_18b.json
    ONS Census 2021 custom dataset (England and Wales, usual residents):
    https://api.beta.ons.gov.uk/v1/population-types/UR/census-observations?area-type=nat&dimensions=resident_age_18b,sex,highest_qualification,living_arrangements_5a
    Single = "Not living in a couple"; household residents only. Education: low = none,
    level 1, level 2; medium = level 3 or apprenticeship; tertiary = level 4+; "Other"
    (level unknown) dropped.

Writes eurostat/outputs/singles_sex_ratio_education_europe.{csv,html}.
"""

import json

import pandas as pd
import plotly.graph_objects as go

from _common import DATA, NAMES, OUTDIR
from common.paths import data_dir
from common.plotting import write_html

AGES = ["Y25-29", "Y30-34", "Y35-39"]
ISCED = {"ED0": "low", "ED1": "low", "ED2": "low", "ED3": "medium", "ED4": "medium",
         "ED5": "tertiary", "ED6": "tertiary", "ED7": "tertiary", "ED8": "tertiary"}
EW_QUAL = {"No qualifications": "low", "Level 1": "low", "Level 2": "low",
           "Apprenticeship": "medium", "Level 3": "medium", "Level 4": "tertiary"}
EW_AGES = {"Aged 25 to 29 years", "Aged 30 to 34 years", "Aged 35 to 39 years"}


def load_eurostat():
    d = pd.read_csv(DATA / "cens_21fe_r2.csv")
    d = d[d.age.isin(AGES) & d.isced11.isin(ISCED)]
    d["edu"] = d.isced11.map(ISCED)
    w = d.pivot_table(index=["geo", "sex", "edu"], columns="hhstatus", values="OBS_VALUE",
                      aggfunc="sum").fillna(0)
    w["single"] = w["TOTAL"] - w["CPL"] - w.get("UNK", 0)
    s = w["single"].reset_index()
    s["country"] = s.geo.map(NAMES)
    return s[["country", "sex", "edu", "single"]]


def load_ew():
    obs = json.loads((data_dir("ONS") / "census2021" / "ew_resident_age_18b.json").read_text())["observations"]
    rows = []
    for o in obs:
        dims = {x["dimension_id"]: x["option"] for x in o["dimensions"]}
        if dims["resident_age_18b"] not in EW_AGES or dims["living_arrangements_5a"] != "Not living in a couple":
            continue
        q = dims["highest_qualification"]
        edu = next((v for k, v in EW_QUAL.items() if q.startswith(k)), None)
        if edu:
            rows.append(dict(country="England & Wales", sex="M" if dims["sex"] == "Male" else "F",
                             edu=edu, single=o["observation"]))
    return pd.DataFrame(rows).groupby(["country", "sex", "edu"], as_index=False).single.sum()


def ratios(s):
    w = s.pivot_table(index="country", columns=["sex", "edu"], values="single", aggfunc="sum")
    m_nt = w[("M", "low")] + w[("M", "medium")]
    f_nt = w[("F", "low")] + w[("F", "medium")]
    out = pd.DataFrame({
        "nontertiary_men_per_tertiary_woman": m_nt / w[("F", "tertiary")],
        "low_men_per_tertiary_woman": w[("M", "low")] / w[("F", "tertiary")],
        "tertiary_men_per_tertiary_woman": w[("M", "tertiary")] / w[("F", "tertiary")],
        "nontertiary_men_per_nontertiary_woman": m_nt / f_nt,
        "all_men_per_woman": (m_nt + w[("M", "tertiary")]) / (f_nt + w[("F", "tertiary")]),
        "single_tertiary_women": w[("F", "tertiary")],
        "single_nontertiary_men": m_nt,
    })
    return out.round(3).sort_values("tertiary_men_per_tertiary_woman")


SERIES = [
    ("tertiary_men_per_tertiary_woman", "Tertiary men", "#1f77b4"),
    ("nontertiary_men_per_tertiary_woman", "Non-tertiary men", "#ff7f0e"),
    ("low_men_per_tertiary_woman", "Low-educated men (ISCED 0-2)", "#d62728"),
]


def plot(r):
    fig = go.Figure()
    for col, label, color in SERIES:
        fig.add_trace(go.Bar(
            y=r.index, x=r[col], name=label, orientation="h", marker_color=color,
            hovertemplate="%{y}: %{x:.2f} " + label.lower() + " per tertiary woman<extra></extra>",
        ))
    fig.add_vline(x=1, line=dict(color="grey", dash="dot"))
    fig.update_layout(
        template="plotly_white", barmode="group",
        title="Single men per single tertiary-educated woman, ages 25-39, 2021",
        xaxis_title="Single men per single tertiary-educated woman",
        height=max(500, 26 * len(r) + 160),
        legend=dict(orientation="h", x=0, y=1.06, xanchor="left", yanchor="bottom"),
        margin=dict(l=130, t=110),
    )
    return fig


def main():
    s = pd.concat([load_eurostat(), load_ew()], ignore_index=True)
    r = ratios(s)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    r.to_csv(OUTDIR / "singles_sex_ratio_education_europe.csv")
    print(r.to_string())
    write_html(plot(r), OUTDIR / "singles_sex_ratio_education_europe.html")


if __name__ == "__main__":
    main()
