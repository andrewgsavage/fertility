"""US birth rates by mother's education from birth certificates (NCHS natality public-use files),
divided by ACS women by age and education, compared with the ACS-only rates.

Inputs (NCHS/data/, not tracked in git): NatYYYYus.zip for YEARS, from
  https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/NatYYYYus.zip
(Git Bash curl fails this host's certificate check; Windows curl.exe works.) The zips use
Deflate64, so they are read through 7-Zip (7z e -so). Fixed-width fields (1-based):
  9-12 year, 75-76 MAGER mother's single year of age, 104 RESTATUS (4 = foreign resident,
  dropped), 124 MEDUC (1 8th grade or less, 2 9-12th no diploma, 3 high school/GED,
  4 some college, 5 associate, 6 bachelor's, 7 master's, 8 doctorate, 9 unknown).
Births with unknown education are spread over the known levels in proportion, within age.
Women: ACS/outputs/acs_births_by_education.csv (ACS/scripts/acs_births_by_education.py).

Writes NCHS/outputs/births_by_education_us.{csv,html}: births per woman at 25-44 by education,
registrations vs ACS, and births per 1,000 women at 20-24.
"""

import subprocess
from collections import Counter

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

YEARS = [2017, 2019, 2022, 2024]
SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
MEDUC = {b"1": "Less than high school", b"2": "Less than high school", b"3": "High school",
         b"4": "Some college", b"5": "Some college", b"6": "Bachelor's or more",
         b"7": "Bachelor's or more", b"8": "Bachelor's or more"}
EDU = [("Less than high school", "#eb6834"), ("High school", "#eda100"),
       ("Some college", "#1baf7a"), ("Bachelor's or more", "#2a78d6")]


def count(year):
    cache = data_dir("NCHS") / f"births_age_educ_{year}.csv"
    if cache.exists():
        return pd.read_csv(cache)
    c = Counter()
    zpath = data_dir("NCHS") / f"Nat{year}us.zip"
    with subprocess.Popen([SEVEN_ZIP, "e", "-so", str(zpath)], stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL) as p:
        for line in p.stdout:
            if line[103:104] == b"4":
                continue
            c[(int(line[74:76]), MEDUC.get(line[123:124], "Unknown"))] += 1
    d = pd.DataFrame([(a, e, n) for (a, e), n in c.items()], columns=["age", "education", "births"])
    d.insert(0, "year", year)
    d.to_csv(cache, index=False)
    return d


def registered(years):
    d = pd.concat([count(y) for y in years])
    w = d.pivot_table(index=["year", "age"], columns="education", values="births", aggfunc="sum").fillna(0)
    known = w[[e for e, _ in EDU]].sum(axis=1)
    total = known + w.get("Unknown", 0)
    for e, _ in EDU:
        w[e] = w[e] / known * total
    return w[[e for e, _ in EDU]].stack().rename("births").reset_index()


def main():
    reg = registered(YEARS)
    acs = pd.read_csv(outputs_dir("ACS") / "acs_births_by_education.csv")
    acs = acs[acs.year.isin(YEARS)].groupby(["year", "age", "education"])[["women", "births"]].sum().reset_index()
    m = acs.merge(reg, on=["year", "age", "education"], how="left", suffixes=("_acs", "_reg"))
    rows = []
    for (y, e), g in m.groupby(["year", "education"]):
        a = g[g.age.between(25, 44)]
        b = g[g.age.between(20, 24)]
        rows.append(dict(year=y, education=e,
                         reg_25_44=(a.births_reg / a.women).sum(), acs_25_44=(a.births_acs / a.women).sum(),
                         reg_20_24=b.births_reg.sum() / b.women.sum() * 1000,
                         acs_20_24=b.births_acs.sum() / b.women.sum() * 1000))
    for y, g in m.groupby("year"):
        a = g[g.age.between(25, 44)].groupby("age")[["women", "births_reg", "births_acs"]].sum()
        b = g[g.age.between(20, 24)]
        rows.append(dict(year=y, education="All women",
                         reg_25_44=(a.births_reg / a.women).sum(), acs_25_44=(a.births_acs / a.women).sum(),
                         reg_20_24=b.births_reg.sum() / b.women.sum() * 1000,
                         acs_20_24=b.births_acs.sum() / b.women.sum() * 1000))
    t = pd.DataFrame(rows)
    out = outputs_dir("NCHS")
    out.mkdir(parents=True, exist_ok=True)
    t.round(3).to_csv(out / "births_by_education_us.csv", index=False)
    pd.set_option("display.width", 200)
    print(t.round(2).to_string())

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.09,
                        subplot_titles=["Births per woman, ages 25-44", "Births per 1,000 women, ages 20-24"])
    for k, (col, fmt) in enumerate([("25_44", ".2f"), ("20_24", ".0f")]):
        for e, color in EDU + [("All women", "#6b6b6b")]:
            s = t[t.education == e]
            for src, dash, lab in [("reg", "solid", "birth certificates"), ("acs", "dot", "ACS survey")]:
                fig.add_trace(go.Scatter(
                    x=s.year, y=s[f"{src}_{col}"], name=f"{e}, {lab}", legendgroup=e,
                    showlegend=k == 0 and src == "reg", mode="lines+markers",
                    line=dict(color=color, width=2, dash=dash), marker=dict(size=7),
                    hovertemplate=f"{e} ({lab}), %{{x}}: %{{y:{fmt}}}<extra></extra>",
                ), row=1, col=k + 1)
    for tr in fig.data:
        if tr.showlegend:
            tr.name = tr.name.split(",")[0]
    for lab, dash in [("Birth certificates", "solid"), ("ACS survey", "dot")]:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=lab,
                                 line=dict(color="#1a1a1a", width=2, dash=dash)), row=1, col=1)
    fig.update_layout(template="plotly_white", height=480,
                      title="US birth rates by education: birth certificates vs ACS survey",
                      title_y=0.98, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1.08, xanchor="left", yanchor="bottom"),
                      margin=dict(l=50, r=20, t=120, b=40))
    fig.update_xaxes(tickvals=YEARS)
    write_html(fig, out / "births_by_education_us.html")


if __name__ == "__main__":
    main()
