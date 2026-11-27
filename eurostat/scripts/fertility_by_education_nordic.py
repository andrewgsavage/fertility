"""Births per woman by education in the Nordic countries, with births and women both from the
population registers.

Births: Eurostat demo_faeduc (eurostat/data/demo_faeduc.csv, see fertility_by_education_europe.py),
which the Nordic offices compile from their registers. Births with unknown education are
spread over the known levels in proportion, within each age.
Women by education and age, from each office's register-based education statistics (downloaded
by this script into eurostat/data/nordic/ if missing):
  Finland  StatFin 12bq, women by level of education and 5-year age, 31 December.
           https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/vkour/12bq.px
  Sweden   SCB TAB4320, women by level of education and single year of age, 31 December.
           https://api.scb.se/ov0104/v2beta/api/v2/tables/TAB4320/data
  Denmark  Statistics Denmark HFUDD11, women by highest education completed and 5-year age.
           https://api.statbank.dk/v1/data
  Norway   SSB 08921, women by educational attainment and age (25-29, 30-39, 40-49), 1 October.
           https://data.ssb.no/api/v0/en/table/08921
Levels: low = basic / compulsory (ISCED 0-2); medium = upper secondary and post-secondary
non-tertiary (ISCED 3-4); tertiary = ISCED 5-8. Sweden's "post-secondary less than 3 years"
(ISCED97 4+5B) and Norway's tertiary vocational (fagskole) are counted as tertiary.
Unknown education is dropped from the population.

Births per woman = 5 x the sum of the 5-year rates over 25-44 (Finland, Sweden, Denmark). For
Norway the population has a 30-39 band, so its figure covers 25-39 (5 x rate 25-29 + 10 x rate
30-39).

Also births per 1,000 women aged 20-24 by education (education is unfinished for many at
these ages, so "low" there includes women still in upper secondary school).

Also births per 1,000 women by education and 5-year age group (Norway: 20-24, 25-29, 30-39), in
the first and last year of each country's consistent span, charted as the % change at 25+.

Writes eurostat/outputs/fertility_by_education_nordic.{csv,html},
fertility_by_education_nordic_20_24.{csv,html} and fertility_by_education_nordic_by_age.csv (for education_curves_facet.py).
"""

import json
import urllib.request

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from _common import DATA, NAMES, OUTDIR
from common.plotting import write_html

RAW = DATA / "nordic"
YEARS = list(range(2008, 2026))
AGES5 = [(20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]
# Years whose birth coding is consistent: the education shares of births jump in Sweden in 2013
# (low-educated share 11% -> 15%), Norway in 2008 and 2011 (unknown 10-13% -> 3.5%) and Finland in
# 2022 (low-educated 12.5% -> 5% as unknown rises to 8%). Years outside these spans are dropped.
SPANS = {"FI": (2007, 2021), "SE": (2013, 2024), "DK": (2008, 2024), "NO": (2011, 2022)}
EDU = [("low", "Lower secondary or less", "#eb6834"),
       ("medium", "Upper secondary", "#eda100"),
       ("tertiary", "Tertiary", "#2a78d6")]
COUNTRIES = ["FI", "SE", "DK", "NO"]


def fetch(name, url, body=None):
    path = RAW / name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    return json.loads(path.read_text(encoding="utf-8"))


def jsonstat_frame(j):
    """Flatten a JSON-stat 2 dataset (or PxWeb v1 json-stat wrapper) to a long DataFrame."""
    if "dataset" in j:
        j = j["dataset"]
    ids = j.get("id") or j["dimension"]["id"]
    dims = j["dimension"]
    cats = []
    for d in ids:
        idx = dims[d]["category"]["index"]
        order = sorted(idx, key=idx.get) if isinstance(idx, dict) else idx
        cats.append(order)
    import itertools
    rows = list(itertools.product(*cats))
    df = pd.DataFrame(rows, columns=ids)
    v = j["value"]
    df["value"] = [v.get(str(i)) for i in range(len(rows))] if isinstance(v, dict) else v
    return df


def pop_fi():
    q = {"query": [
        {"code": "alue_23_20260101", "selection": {"filter": "item", "values": ["SSS"]}},
        {"code": "ikaryhma_10_20180101", "selection": {"filter": "item", "values": [f"{a}-{b}" for a, b in AGES5]}},
        {"code": "sukupuoli_9_20180101", "selection": {"filter": "item", "values": ["2"]}},
        {"code": "koulutusaste_17_20180101", "selection": {"filter": "item", "values": ["SSS", "3", "4", "5", "6", "7", "8"]}},
    ], "response": {"format": "json-stat2"}}
    d = jsonstat_frame(fetch("fi_12bq.json", "https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/vkour/12bq.px", q))
    d = d.rename(columns={"timeperiod_y": "year", "ikaryhma_10_20180101": "age", "koulutusaste_17_20180101": "lev"})
    w = d.pivot_table(index=["year", "age"], columns="lev", values="value", aggfunc="sum")
    out = pd.DataFrame({
        "medium": w["3"] + w["4"],
        "tertiary": w[["5", "6", "7", "8"]].sum(axis=1),
    })
    out["low"] = w["SSS"] - out.medium - out.tertiary  # basic education or no post-comprehensive
    return out.stack().rename("women")


def pop_se():
    body = {"selection": [
        {"variableCode": "Region", "valueCodes": ["00"]},
        {"variableCode": "UtbildningsNiva", "valueCodes": ["1", "2", "3", "4", "5", "6", "7"]},
        {"variableCode": "Alder", "valueCodes": [str(a) for a in range(20, 45)]},
        {"variableCode": "Kon", "valueCodes": ["2"]},
        {"variableCode": "ContentsCode", "valueCodes": ["000000I2"]},
        {"variableCode": "Tid", "valueCodes": ["*"]},
    ]}
    d = jsonstat_frame(fetch("se_tab4320.json",
                             "https://api.scb.se/ov0104/v2beta/api/v2/tables/TAB4320/data?lang=en&outputFormat=json-stat2", body))
    lev = {"1": "low", "2": "low", "3": "medium", "4": "medium", "5": "tertiary", "6": "tertiary", "7": "tertiary"}
    d["ed"] = d.UtbildningsNiva.map(lev)
    a = d.Alder.astype(int)
    d["age"] = ((a // 5) * 5).astype(str) + "-" + ((a // 5) * 5 + 4).astype(str)
    d["year"] = d.Tid
    return d.groupby(["year", "age", "ed"]).value.sum().rename("women")


def pop_dk():
    body = {"table": "HFUDD11", "format": "JSONSTAT", "lang": "en", "variables": [
        {"code": "BOPOMR", "values": ["000"]}, {"code": "HERKOMST", "values": ["TOT"]},
        {"code": "HFUDD", "values": ["H10", "H20", "H30", "H35", "H40", "H50", "H60", "H70", "H80"]},
        {"code": "ALDER", "values": [f"{a}-{b}" for a, b in AGES5]},
        {"code": "KØN", "values": ["K"]}, {"code": "Tid", "values": ["*"]},
    ]}
    d = jsonstat_frame(fetch("dk_hfudd11.json", "https://api.statbank.dk/v1/data", body))
    lev = {"H10": "low", "H20": "medium", "H30": "medium", "H35": "medium",
           "H40": "tertiary", "H50": "tertiary", "H60": "tertiary", "H70": "tertiary", "H80": "tertiary"}
    d["ed"] = d.HFUDD.map(lev)
    return d.rename(columns={"ALDER": "age", "Tid": "year"}).groupby(["year", "age", "ed"]).value.sum().rename("women")


def pop_no():
    q = {"query": [
        {"code": "Region", "selection": {"filter": "item", "values": ["0"]}},
        {"code": "Kjonn", "selection": {"filter": "item", "values": ["2"]}},
        {"code": "Alder", "selection": {"filter": "item", "values": ["20-24", "25-29", "30-39"]}},
        {"code": "UtdanNivaa", "selection": {"filter": "item", "values": ["01", "02a", "11", "03a", "04a"]}},
        {"code": "ContentsCode", "selection": {"filter": "item", "values": ["Personer"]}},
    ], "response": {"format": "json-stat2"}}
    d = jsonstat_frame(fetch("no_08921.json", "https://data.ssb.no/api/v0/en/table/08921", q))
    lev = {"01": "low", "02a": "medium", "11": "tertiary", "03a": "tertiary", "04a": "tertiary"}
    d["ed"] = d.UtdanNivaa.map(lev)
    return d.rename(columns={"Alder": "age", "Tid": "year"}).groupby(["year", "age", "ed"]).value.sum().rename("women")


def births():
    b = pd.read_csv(DATA / "demo_faeduc.csv")
    b = b[b.geo.isin(COUNTRIES) & b.age.str.fullmatch(r"Y\d\d")
          & b.isced11.isin(["ED0-2", "ED3_4", "ED5-8", "TOTAL"])].copy()
    a = b.age.str[1:].astype(int)
    b = b[a.between(20, 44)].copy()
    a = a[b.index]
    lo = (a // 5) * 5
    b["age5"] = lo.astype(str) + "-" + (lo + 4).astype(str)
    b["age10"] = b.age5.where(lo < 30, b.age5.where(lo >= 40, "30-39"))
    b["ed"] = b.isced11.map({"ED0-2": "low", "ED3_4": "medium", "ED5-8": "tertiary", "TOTAL": "TOTAL"})
    return b


def rates(geo, pop, ages_col, lo_age=25):
    b = births()
    b = b[b.geo == geo].groupby(["TIME_PERIOD", ages_col, "ed"]).OBS_VALUE.sum(min_count=1).unstack()
    known = b[["low", "medium", "tertiary"]].sum(axis=1)
    for e in ["low", "medium", "tertiary"]:
        b[e] = b[e] / known * b["TOTAL"]
    b = b[["low", "medium", "tertiary"]].stack().rename("births")
    b.index = b.index.set_names(["year", "age", "ed"])
    p = pop.copy()
    p.index = p.index.set_names(["year", "age", "ed"])
    p.index = p.index.set_levels(p.index.levels[0].astype(int), level=0)
    d = pd.concat([b, p], axis=1, join="inner").dropna().reset_index()
    y0, y1 = SPANS[geo]
    d = d[d.year.between(y0, y1)]
    by_age = (d.births / d.women * 1000).groupby([d.year, d.age, d.ed]).sum().unstack()
    g = d.groupby(["year", "age"])[["births", "women"]].sum()
    by_age["all"] = g.births / g.women * 1000
    by_age = by_age.reset_index()
    by_age.insert(0, "geo", geo)
    young = d[d.age == "20-24"].set_index(["year", "ed"])
    young = (young.births / young.women * 1000).unstack()
    young["all"] = (d[d.age == "20-24"].groupby("year").births.sum()
                    / d[d.age == "20-24"].groupby("year").women.sum() * 1000)
    young.insert(0, "geo", geo)
    d = d[d.age != "20-24"]
    width = d.age.map(lambda s: int(s.split("-")[1]) - int(s.split("-")[0]) + 1)
    d["contrib"] = d.births / d.women * width
    n_ages = d.groupby(["year", "ed"]).age.transform("nunique")
    d = d[n_ages == d.age.nunique()]
    t = d.groupby(["year", "ed"]).contrib.sum().unstack()
    g = d.groupby(["year", "age"])[["births", "women"]].sum()
    gw = pd.Series([int(a.split("-")[1]) - int(a.split("-")[0]) + 1 for a in g.index.get_level_values(1)], index=g.index)
    t["all"] = (g.births / g.women * gw).groupby("year").sum()
    t.insert(0, "geo", geo)
    return t.reset_index(), young.reset_index(), by_age


def chart(t, title, ytitle, fmt, no_note):
    fig = make_subplots(rows=2, cols=2, shared_yaxes=True, shared_xaxes=True,
                        vertical_spacing=0.12, horizontal_spacing=0.05,
                        subplot_titles=[f"{NAMES[g]}{no_note if g == 'NO' else ''}" for g in COUNTRIES])
    for i, g in enumerate(COUNTRIES):
        s = t[t.geo == g].set_index("year")
        row, col = i // 2 + 1, i % 2 + 1
        for e, lab, color in EDU + [("all", "All women", "#6b6b6b")]:
            fig.add_trace(go.Scatter(
                x=s.index, y=s[e], name=lab, legendgroup=lab, showlegend=i == 0, mode="lines+markers",
                marker=dict(size=6), line=dict(color=color, width=2, dash="dash" if e == "all" else "solid"),
                hovertemplate=f"{NAMES[g]} %{{x}}, {lab}: %{{y:{fmt}}}<extra></extra>",
            ), row=row, col=col)
    fig.update_layout(template="plotly_white", height=640,
                      title=title,
                      title_y=0.98, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1.06, xanchor="left", yanchor="bottom"),
                      margin=dict(l=60, r=20, t=120, b=40))
    fig.update_yaxes(title_text=ytitle, col=1)
    return fig


def main():
    parts = [rates("FI", pop_fi(), "age5"), rates("SE", pop_se(), "age5"),
             rates("DK", pop_dk(), "age5"), rates("NO", pop_no(), "age10")]
    t = pd.concat([p[0] for p in parts], ignore_index=True)
    y = pd.concat([p[1] for p in parts], ignore_index=True)
    a = pd.concat([p[2] for p in parts], ignore_index=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    t.round(3).rename(columns={e: lab for e, lab, _ in EDU}).to_csv(OUTDIR / "fertility_by_education_nordic.csv", index=False)
    pd.set_option("display.width", 200)
    y.round(1).rename(columns={e: lab for e, lab, _ in EDU}).to_csv(OUTDIR / "fertility_by_education_nordic_20_24.csv", index=False)
    a.round(1).rename(columns={e: lab for e, lab, _ in EDU}).to_csv(OUTDIR / "fertility_by_education_nordic_by_age.csv", index=False)
    print(t.round(2).to_string())
    print(a.round(0).to_string())
    print(y.round(0).to_string())
    write_html(chart(t, "Births per woman at ages 25-44 by education, register data", "Births per woman", ".2f",
                     " (ages 25-39)"), OUTDIR / "fertility_by_education_nordic.html")
    write_html(chart(y, "Births per 1,000 women aged 20-24 by education, register data",
                     "Births per 1,000 women", ".0f", ""), OUTDIR / "fertility_by_education_nordic_20_24.html")


if __name__ == "__main__":
    main()
