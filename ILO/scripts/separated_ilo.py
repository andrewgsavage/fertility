"""Share of people divorced or separated, by country, sex and 10-year age band (25-34, 35-44).

ILOSTAT POP_XWAP_SEX_AGE_MTS_NB_A: working-age population by sex, age and marital status,
from national labour force and household surveys. Two shares:

- sep: MTS_DETAILS_SEP (divorced or separated) / MTS_DETAILS_TOTAL, % of everyone in the band.
- sep_ever: MTS_DETAILS_SEP / (MRD + UNION + SEP + WID), % of those who have ever been married
  or in a recorded union. This removes the effect of fewer people marrying in the first place.

Marital status is a current status, so people who remarry leave the divorced category, and
the share is net of remarriage. In surveys that record legal marital status only (most of
Europe, North America and Oceania; COHAB_MISSED_UNLESS_REPORTED in coupling_ilo.py), a
divorced person now cohabiting still counts as divorced, and a cohabiting couple that splits
is never counted. Where consensual unions are recorded (Latin America, Africa), separated
includes people separated from a union.

A country keeps its survey source with the most years, then its longest run of years without
a coding break (a jump of BREAK_PTS points and BREAK_REL relative in the women's 35-44 share,
e.g. France 6.9% -> 1.5% in 2021-22).

Input (download into ILO/data/ - not tracked in git):
  POP_XWAP_SEX_AGE_MTS_NB_A.csv.gz
    https://rplumber.ilo.org/data/indicator/?id=POP_XWAP_SEX_AGE_MTS_NB_A&format=.csv.gz
  ref_area.csv  https://rplumber.ilo.org/metadata/dic/?var=ref_area&lang=en&format=.csv
"""

import pathlib

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html
from ILO.scripts.coupling_ilo import COHAB_MISSED_UNLESS_REPORTED, SHORT
from common.paths import data_dir

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = data_dir("ILO")
OUTDIR = ROOT / "outputs"

AGES = {"AGE_10YRBANDS_Y25-34": "25-34", "AGE_10YRBANDS_Y35-44": "35-44"}
SEXES = {"SEX_F": "women", "SEX_M": "men"}
CATS = ["MTS_DETAILS_TOTAL", "MTS_DETAILS_MRD", "MTS_DETAILS_UNION", "MTS_DETAILS_SEP", "MTS_DETAILS_WID"]
MIN_YEARS = 8
BREAK_PTS = 3.0
BREAK_REL = 0.3

SHOWN = ["United States", "United Kingdom", "Canada", "Austria", "Switzerland", "Czechia", "Poland",
         "S Korea", "Mexico", "Chile"]
SHORT = {**SHORT, "United States of America": "United States",
         "United Kingdom of Great Britain and Northern Ireland": "United Kingdom"}


def load():
    d = pd.read_csv(DATA / "POP_XWAP_SEX_AGE_MTS_NB_A.csv.gz", low_memory=False,
                    usecols=["ref_area", "source", "sex", "classif1", "classif2", "time", "obs_value"])
    d = d[d.classif1.isin(AGES) & d.sex.isin(SEXES) & d.classif2.isin(CATS)]
    nyears = d.groupby(["ref_area", "source"]).time.nunique().rename("n").reset_index()
    best = nyears.sort_values("n").groupby("ref_area").tail(1)
    d = d.merge(best[["ref_area", "source"]])
    p = d.pivot_table(index=["ref_area", "time", "sex", "classif1"], columns="classif2",
                      values="obs_value").reset_index()
    p = p.dropna(subset=["MTS_DETAILS_TOTAL", "MTS_DETAILS_SEP"])
    p = p[p.MTS_DETAILS_TOTAL > 0]
    ever = p[["MTS_DETAILS_MRD", "MTS_DETAILS_UNION", "MTS_DETAILS_SEP", "MTS_DETAILS_WID"]].fillna(0).sum(axis=1)
    p["sep"] = 100 * p.MTS_DETAILS_SEP / p.MTS_DETAILS_TOTAL
    p["sep_ever"] = 100 * p.MTS_DETAILS_SEP / ever
    p["legal_only"] = p.ref_area.isin(COHAB_MISSED_UNLESS_REPORTED)

    names = pd.read_csv(DATA / "ref_area.csv", encoding="utf-8-sig").set_index("ref_area")["ref_area.label"]
    p["country"] = p.ref_area.map(names).replace(SHORT)
    p["age"] = p.classif1.map(AGES)
    p["sex"] = p.sex.map(SEXES)
    p = p.merge(longest_unbroken(p), on=["ref_area", "time"])
    keep = p.groupby("country").time.nunique()
    p = p[p.country.isin(keep[keep >= MIN_YEARS].index)]
    return p.rename(columns={"time": "year"})[
        ["country", "ref_area", "sex", "age", "year", "sep", "sep_ever", "legal_only"]]


def longest_unbroken(p):
    """Years in each country's longest run without a coding break in women's 35-44 share."""
    s = p[(p.age == "35-44") & (p.sex == "women")][["ref_area", "time", "sep"]].sort_values(["ref_area", "time"])
    diff = s.groupby("ref_area").sep.diff().abs()
    prev = s.groupby("ref_area").sep.shift()
    s["seg"] = ((diff >= BREAK_PTS) & (diff >= BREAK_REL * prev)).astype(int).groupby(s.ref_area).cumsum()
    size = s.groupby(["ref_area", "seg"]).time.transform("size")
    s = s[size == size.groupby(s.ref_area).transform("max")]
    s = s[s.seg == s.groupby("ref_area").seg.transform("max")]
    return s[["ref_area", "time"]]


def plot(d, sex):
    d = d[d.sex == sex]
    order = [c for c in SHOWN if c in set(d.country)] + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    titles = [f"{a}: % of all" for a in AGES.values()] + [f"{a}: % of ever married" for a in AGES.values()]
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.1, horizontal_spacing=0.06,
                        subplot_titles=titles)
    for i, c in enumerate(order):
        legal = d[d.country == c].legal_only.any()
        label = f"{c} (legal)" if legal else c
        for j, a in enumerate(AGES.values(), start=1):
            x = d[(d.country == c) & (d.age == a)].sort_values("year")
            for r, col in enumerate(["sep", "sep_ever"], start=1):
                fig.add_trace(go.Scatter(
                    x=x.year, y=x[col], mode="lines", name=label, legendgroup=c,
                    showlegend=(j == 1 and r == 1),
                    line=dict(color=colors[i % len(colors)], width=1.8),
                    visible=True if c in SHOWN else "legendonly",
                    hovertemplate=f"{c}, {sex} {a}, %{{x}}: %{{y:.1f}}%<extra></extra>"), row=r, col=j)
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_yaxes(title_text="% of all", row=1, col=1)
    fig.update_yaxes(title_text="% of ever married", row=2, col=1)
    fig.update_layout(template="plotly_white", height=720,
                      title=f"{sex.capitalize()} currently divorced or separated (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=190, t=80), hovermode="closest")
    return fig


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    d = load()
    d.round(2).to_csv(OUTDIR / "separated_ilo.csv", index=False)
    for sex in SEXES.values():
        write_html(plot(d, sex), OUTDIR / f"separated_ilo_{sex}.html", height="720px")
    print(d.country.nunique(), "countries")
    for col in ["sep", "sep_ever"]:
        t = d[(d.age == "35-44") & (d.sex == "women") & d.year.isin([2010, 2019, 2023, 2024])].pivot_table(
            index="country", columns="year", values=col).round(1)
        print(col); print(t.dropna(thresh=2).to_string())
