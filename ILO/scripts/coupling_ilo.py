"""Share of people married or in a union (cohabiting), by country, sex and 10-year age band.

ILOSTAT POP_XWAP_SEX_AGE_MTS_NB_A: working-age population by sex, age and marital status,
from national labour force and household surveys. Share = MTS_AGGREGATE_2 (married /
union / cohabiting) / MTS_AGGREGATE_TOTAL.

Many European, North American and Oceanian surveys code legal marital status only, so
cohabiting couples count as single, and ILO's "union" category there holds civil
partnerships (UK 0.3% of 25-34s). In those countries a year is kept only if ILO reports
union / cohabiting as at least 2% of 25-34s; elsewhere cohabitation is either recorded
(Latin America, sub-Saharan Africa) or rare (East Asia, MENA).

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

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"

AGES = {"AGE_10YRBANDS_Y15-24": "15-24", "AGE_10YRBANDS_Y25-34": "25-34", "AGE_10YRBANDS_Y35-44": "35-44"}
SEXES = {"SEX_F": "women", "SEX_M": "men"}

# Cohabitation is common here, and most of these surveys record legal marital status only.
COHAB_MISSED_UNLESS_REPORTED = {
    "ALB", "AND", "AUT", "BEL", "BGR", "BIH", "BLR", "CHE", "CYP", "CZE", "DEU", "DNK", "ESP", "EST",
    "FIN", "FRA", "GBR", "GRC", "HRV", "HUN", "IRL", "ISL", "ITA", "LTU", "LUX", "LVA", "MDA", "MKD",
    "MLT", "MNE", "NLD", "NOR", "POL", "PRT", "ROU", "RUS", "SRB", "SVK", "SVN", "SWE", "UKR", "KOS",
    "USA", "CAN", "AUS", "NZL",
}
MIN_UNION_SHARE = 2.0
MIN_YEARS = 8
BREAK_PTS = 10.0

SHOWN = ["S Korea", "Japan", "Mexico", "Türkiye", "Thailand", "Chile", "Canada", "Colombia", "Iran", "Viet Nam"]
SHORT = {"Korea, Republic of": "S Korea", "Republic of Korea": "S Korea", "Iran, Islamic Republic of": "Iran",
         "Hong Kong, China": "Hong Kong", "Bolivia, Plurinational State of": "Bolivia",
         "Venezuela, Bolivarian Republic of": "Venezuela", "Russian Federation": "Russia",
         "Moldova, Republic of": "Moldova", "Republic of Moldova": "Moldova","Occupied Palestinian Territory": "Palestine",
         "Lao People's Democratic Republic": "Laos"}


def load():
    d = pd.read_csv(DATA / "POP_XWAP_SEX_AGE_MTS_NB_A.csv.gz", low_memory=False,
                    usecols=["ref_area", "source", "sex", "classif1", "classif2", "time", "obs_value"])
    d = d[d.classif1.isin(AGES) & d.sex.isin(["SEX_F", "SEX_M", "SEX_T"])
          & d.classif2.isin(["MTS_AGGREGATE_TOTAL", "MTS_AGGREGATE_2", "MTS_DETAILS_UNION"])]
    # A few country-years have more than one survey source; keep the one with most years.
    nyears = d.groupby(["ref_area", "source"]).time.nunique().rename("n").reset_index()
    best = nyears.sort_values("n").groupby("ref_area").tail(1)
    d = d.merge(best[["ref_area", "source"]])
    p = d.pivot_table(index=["ref_area", "time", "sex", "classif1"], columns="classif2",
                      values="obs_value").reset_index()
    p["share"] = 100 * p.MTS_AGGREGATE_2 / p.MTS_AGGREGATE_TOTAL
    p["union_share"] = 100 * p.MTS_DETAILS_UNION.fillna(0) / p.MTS_AGGREGATE_TOTAL

    # Which country-years record cohabitation: union share of all 25-34s.
    ref = p[(p.sex == "SEX_T") & (p.classif1 == "AGE_10YRBANDS_Y25-34")][["ref_area", "time", "union_share"]]
    ref = ref.rename(columns={"union_share": "union_25_34"})
    p = p.merge(ref, how="left")
    ok = ~p.ref_area.isin(COHAB_MISSED_UNLESS_REPORTED) | (p.union_25_34 >= MIN_UNION_SHARE)
    p = p[ok & p.sex.isin(SEXES)].dropna(subset=["share"])

    names = pd.read_csv(DATA / "ref_area.csv", encoding="utf-8-sig").set_index("ref_area")["ref_area.label"]
    p["country"] = p.ref_area.map(names).replace(SHORT)
    p["age"] = p.classif1.map(AGES)
    p["sex"] = p.sex.map(SEXES)
    p = p.merge(longest_unbroken(p).reset_index(), on=["ref_area", "time"])
    keep = p[p.age == "25-34"].groupby("country").time.nunique()
    p = p[p.country.isin(keep[keep >= MIN_YEARS].index)]
    return p.rename(columns={"time": "year"})[["country", "ref_area", "sex", "age", "year", "share"]]


def longest_unbroken(p):
    """Years in each country's longest run without a coding break.

    A break is a jump of BREAK_PTS or more in the 25-34 share (mean of women and men)
    between consecutive survey years, e.g. Thailand 63% -> 20% in 2020-21.
    """
    s = p[p.age == "25-34"].groupby(["ref_area", "time"]).share.mean().reset_index()
    s["seg"] = s.groupby("ref_area").share.transform(lambda v: (v.diff().abs() >= BREAK_PTS).cumsum())
    size = s.groupby(["ref_area", "seg"]).time.transform("size")
    best = size == s.assign(size=size).groupby("ref_area")["size"].transform("max")
    # Ties: keep the most recent run.
    s = s[best]
    s = s[s.seg == s.groupby("ref_area").seg.transform("max")]
    return s.set_index("ref_area")[["time"]]


def plot(d, sex):
    d = d[d.sex == sex]
    shown = [SHORT.get(c, c) for c in SHOWN]
    order = [c for c in shown if c in set(d.country)] + sorted(set(d.country) - set(shown))
    colors = pc.qualitative.Dark24
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=[f"Aged {a}" for a in AGES.values()])
    for i, c in enumerate(order):
        for j, a in enumerate(AGES.values(), start=1):
            x = d[(d.country == c) & (d.age == a)].sort_values("year")
            fig.add_trace(go.Scatter(
                x=x.year, y=x.share, mode="lines", name=c, legendgroup=c, showlegend=j == 1,
                line=dict(color=colors[i % len(colors)], width=1.8),
                visible=True if c in shown else "legendonly",
                hovertemplate=f"{c}, {sex} {a}, %{{x}}: %{{y:.1f}}%<extra></extra>"), row=1, col=j)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    fig.update_yaxes(title_text=f"% of {sex} married or cohabiting", row=1, col=1)
    fig.update_layout(template="plotly_white",
                      title=f"{sex.capitalize()} married or cohabiting, by age (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=170, t=80), hovermode="closest")
    return fig


def write_html(fig, name):
    out = OUTDIR / name
    fig.write_html(out, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = out.read_text(encoding="utf-8")
    out.write_text(html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1),
                   encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    d = load()
    d.round(2).to_csv(OUTDIR / "coupling_ilo.csv", index=False)
    for sex in SEXES.values():
        write_html(plot(d, sex), f"coupling_ilo_{sex}.html")
    print(d.country.nunique(), "countries")
    t = d[(d.age == "25-34") & d.year.isin([2010, 2019, 2023])].pivot_table(
        index="country", columns=["sex", "year"], values="share").round(1)
    print(t.dropna().to_string())
