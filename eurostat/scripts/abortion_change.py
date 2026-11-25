"""Abortions and births by age since 2013, per country, and per 1,000 women.

Reads eurostat/outputs/abortion_by_age.csv (built by abortion_by_age.py) and adds the
female population by age, so abortions and births can also be shown per 1,000 women.

Women by age (age-group denominators: Under 20 = women 15-19, 35+ = women 35-44):
  eurostat/data/demo_pjan_f.csv   Eurostat demo_pjan, women aged 15-44 on 1 January, 2004 onward
      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_pjan/A.NR.Y15+...+Y44.F.?format=SDMX-CSV&startPeriod=2004
      The mean of 1 January of the year and of the next year approximates the mid-year population.
  ONS/data/mye_components/myebtablesenglandwales20112025.xlsx  ONS mid-year estimates, England & Wales, MYEB1
      https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland
  HFD/data/HFD/exposRR.txt   Human Fertility Database female exposures: Scotland, US, Japan,
      and England & Wales before 2011.

Outputs (eurostat/outputs/):
  abortion_change.csv                  country, year, age, abortions, births, women, rates
  abortion_change_index.html           abortions and births indexed to 2013 = 100, per country
  abortion_change_pregnancies.html     births + abortions stacked, per country
"""

import numpy as np
import openpyxl
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from abortion_by_age import AGES, COLORS, NAMES
from common.hfd import HFD_DIR
from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("eurostat")
OUTDIR = outputs_dir("eurostat")
BASE = 2013
AGE_SPAN = {"Under 20": (15, 19), "20–24": (20, 24), "25–29": (25, 29), "30–34": (30, 34), "35+": (35, 44)}
HFD_POP = {"Scotland": "GBR_SCO", "United States (43 areas)": "USA", "Japan": "JPN", "England & Wales": "GBRTENW"}
AB, BI = "#c0392b", "#2f6db5"


def age_group(a):
    for g, (lo, hi) in AGE_SPAN.items():
        if lo <= a <= hi:
            return g


def eurostat_women():
    x = pd.read_csv(DATA / "demo_pjan_f.csv")
    x = x[x.geo.isin(NAMES)]
    x["age"] = x.age.str[1:].astype(int).map(age_group)
    x = x.groupby(["geo", "TIME_PERIOD", "age"]).OBS_VALUE.sum().rename("jan1").reset_index()
    nxt = x.assign(TIME_PERIOD=x.TIME_PERIOD - 1).rename(columns={"jan1": "jan1_next"})
    x = x.merge(nxt, on=["geo", "TIME_PERIOD", "age"], how="left")
    x["women"] = x[["jan1", "jan1_next"]].mean(axis=1)
    x["country"] = x.geo.map(NAMES)
    return x.rename(columns={"TIME_PERIOD": "year"})[["country", "year", "age", "women"]]


def hfd_women():
    rows = []
    codes = {v: k for k, v in HFD_POP.items()}
    with open(HFD_DIR / "exposRR.txt", encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) == 4 and p[0] in codes and p[1].isdigit():
                g = age_group(int("".join(ch for ch in p[2] if ch.isdigit())))
                if g:
                    rows.append((codes[p[0]], int(p[1]), g, float(p[3])))
    d = pd.DataFrame(rows, columns=["country", "year", "age", "women"])
    return d.groupby(["country", "year", "age"], as_index=False).women.sum()


def ons_women():
    ws = openpyxl.load_workbook(data_dir("ONS") / "mye_components" / "myebtablesenglandwales20112025.xlsx",
                                read_only=True)["MYEB1"]
    it = ws.iter_rows(values_only=True)
    next(it)
    head = next(it)
    years = {i: int(h.split("_")[1]) for i, h in enumerate(head) if str(h).startswith("population_")}
    tot = {}
    for r in it:
        if r[3] != "f" or r[4] is None:
            continue
        g = age_group(int(r[4]))
        if g:
            for i, y in years.items():
                tot[(y, g)] = tot.get((y, g), 0) + r[i]
    return pd.DataFrame([("England & Wales", y, g, n) for (y, g), n in tot.items()],
                        columns=["country", "year", "age", "women"])


def load():
    d = pd.read_csv(OUTDIR / "abortion_by_age.csv")
    hfd = hfd_women()
    ons = ons_women()
    hfd = hfd[~((hfd.country == "England & Wales") & hfd.year.isin(ons.year))]
    w = pd.concat([eurostat_women(), hfd, ons])
    d = d.merge(w, on=["country", "year", "age"], how="left")
    d["abortion_rate"] = 1000 * d.abortions / d.women
    d["birth_rate"] = 1000 * d.births / d.women
    # Countries with a 2013 value and a latest year after 2017.
    last = d.groupby("country").year.max()
    has_base = set(d[d.year == BASE].country)
    keep = [c for c in last.index if c in has_base and last[c] >= 2018]
    return d[d.country.isin(keep) & (d.year >= 2004)].sort_values(["country", "year", "age"])


def changes(d):
    b = d[d.year == BASE].set_index(["country", "age"])
    l = d[d.year == d.groupby("country").year.transform("max")].set_index(["country", "age"])
    c = pd.DataFrame({
        "latest": l.year, "ab0": b.abortions, "ab1": l.abortions, "bi0": b.births, "bi1": l.births,
        "r0": b.abortions_per_100_births, "r1": l.abortions_per_100_births,
        "ar0": b.abortion_rate, "ar1": l.abortion_rate, "br0": b.birth_rate, "br1": l.birth_rate})
    c["d_ab"] = 100 * (c.ab1 / c.ab0 - 1)
    c["d_bi"] = 100 * (c.bi1 / c.bi0 - 1)
    c["ln_ab"] = np.log(c.ab1 / c.ab0)
    c["ln_bi"] = -np.log(c.bi1 / c.bi0)  # births falling pushes the ratio up
    c["ln_r"] = c.ln_ab + c.ln_bi
    return c.reset_index()


def age_buttons(labels, n_per_age, extra_all=None, y=1.08):
    """Buttons that show one age group's traces. labels: list of ages, traces ordered age-major."""
    total = n_per_age * len(labels)
    btns = []
    for i, a in enumerate(labels):
        vis = [i * n_per_age <= k < (i + 1) * n_per_age for k in range(total)]
        btns.append(dict(label=a, method="restyle", args=[{"visible": vis}]))
    return [dict(type="buttons", direction="right", x=0, xanchor="left", y=y, yanchor="bottom",
                 showactive=True, active=1, buttons=btns)]


# Per-country small multiples with an age selector -------------------
def small_multiples(d, kind, cols=5):
    countries = sorted(d.country.unique())
    rows = -(-len(countries) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[c.replace(" (43 areas)", "") for c in countries],
                        horizontal_spacing=0.04, vertical_spacing=0.3 / rows * 1.5)
    per_age = 0
    for a in AGES:
        start = len(fig.data)
        for i, c in enumerate(countries):
            r, k = i // cols + 1, i % cols + 1
            s = d[(d.country == c) & (d.age == a)].sort_values("year")
            first = i == 0
            if kind == "index":
                b = s[s.year == BASE].iloc[0]
                for col, name, color, dash in [("abortions", "Abortions", AB, "solid"),
                                               ("births", "Live births", BI, "dash")]:
                    fig.add_trace(go.Scatter(
                        x=s.year, y=100 * s[col] / b[col], mode="lines", name=name, legendgroup=name,
                        showlegend=first, visible=(a == "20–24"), line=dict(color=color, dash=dash, width=1.8),
                        customdata=s[col], hovertemplate=f"{c} {a} %{{x}}: %{{customdata:,.0f}} "
                                                         f"({name.lower()}, index %{{y:.0f}})<extra></extra>"),
                        row=r, col=k)
            else:
                for col, name, color in [("births", "Live births", BI), ("abortions", "Abortions", AB)]:
                    fig.add_trace(go.Scatter(
                        x=s.year, y=s[col], mode="lines", stackgroup=f"{c}{a}", name=name, legendgroup=name,
                        showlegend=first, visible=(a == "20–24"), line=dict(color=color, width=0.5),
                        customdata=100 * s.abortions / (s.abortions + s.births),
                        hovertemplate=f"{c} {a} %{{x}}: %{{y:,.0f}} {name.lower()}"
                                      f"<br>Abortion share of pregnancies %{{customdata:.0f}}%<extra></extra>"),
                        row=r, col=k)
        per_age = len(fig.data) - start
    if kind == "index":
        fig.add_hline(y=100, line=dict(color="#999", width=1))
        fig.update_yaxes(type="log", tickvals=[25, 50, 100, 200, 400], tickfont=dict(size=9))
        title = f"Abortions and live births, {BASE} = 100"
    else:
        fig.update_yaxes(rangemode="tozero", tickfont=dict(size=9))
        title = "Pregnancies ending in a live birth or an abortion"
    fig.update_xaxes(range=[2004, 2025], dtick=10, tickfont=dict(size=9))
    fig.update_annotations(font_size=11)
    h = 165 * rows + 150
    fig.update_layout(template="plotly_white", height=h, title=dict(text=title, y=0.995, yanchor="top"),
                      updatemenus=age_buttons(AGES, per_age, y=1 + 55 / h),
                      legend=dict(orientation="h", x=1, xanchor="right", y=1 + 55 / h, yanchor="bottom"),
                      margin=dict(t=120, l=45, r=15, b=30), hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    c = changes(d)
    out = d.copy()
    out["women"] = out.women.round(0)
    out[["abortion_rate", "birth_rate"]] = out[["abortion_rate", "birth_rate"]].round(2)
    out.to_csv(OUTDIR / "abortion_change.csv", index=False)
    write_html(small_multiples(d, "index"), OUTDIR / "abortion_change_index.html")
    write_html(small_multiples(d, "stack"), OUTDIR / "abortion_change_pregnancies.html")

    pd.set_option("display.width", 250)
    print(sorted(d.country.unique()))
    print(d[d.women.isna()].groupby("country").year.agg(["min", "max", "count"]))
    t = c[c.age.isin(["Under 20", "20–24"])].copy()
    t["ar"] = t.ar0.round(1).astype(str) + " → " + t.ar1.round(1).astype(str)
    t["br"] = t.br0.round(1).astype(str) + " → " + t.br1.round(1).astype(str)
    print(t[["country", "age", "latest", "ar", "br", "r0", "r1"]].to_string())
