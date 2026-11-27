"""Births per woman at ages 25-44 by mother's education, European countries, 2008-2024.

Numerator: Eurostat demo_faeduc, live births by mother's single year of age and ISCED 2011
level (register data). Births with unknown education are spread over the known levels in
proportion, within each age. Denominator: Eurostat lfsa_pgaed, women by 5-year age group and
ISCED level (EU Labour Force Survey, thousands). Rates are per 5-year age group; the partial TFR
is 5 x the sum of the 25-29 ... 40-44 rates.

Births and population come from different sources (registers vs a survey) and classify
education separately, so a jump in one year can be a classification change rather than
behaviour. Year-on-year changes above BREAK in any education group are flagged.

Inputs (eurostat/data/, not tracked in git):
  demo_faeduc.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_faeduc?format=SDMX-CSV&compressed=false
  lfsa_pgaed.csv   https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfsa_pgaed?format=SDMX-CSV&compressed=false&startPeriod=2008

Writes eurostat/outputs/fertility_by_education_europe.{csv,html} (country dropdown) and
fertility_by_education_europe_change.{csv,html} (change from START to the latest year).
"""

import pandas as pd
import plotly.graph_objects as go

from _common import DATA, NAMES, OUTDIR
from common.plotting import write_html

AGES = ["Y25-29", "Y30-34", "Y35-39", "Y40-44"]
EDU = [  # code, label, color (low to high, matches the US chart)
    ("ED0-2", "Lower secondary or less", "#eb6834"),
    ("ED3_4", "Upper secondary", "#eda100"),
    ("ED5-8", "Tertiary", "#2a78d6"),
]
ED = [c for c, _, _ in EDU]
LABEL = {c: lab for c, lab, _ in EDU}
START = 2015
MIN_YEARS = 10
BREAK = 0.20
DEFAULT = "SE"  # country shown first
XMAX = 45  # change chart x-range (%); longer bars are clipped and labelled


def births():
    b = pd.read_csv(DATA / "demo_faeduc.csv")
    b = b[b.age.str.fullmatch(r"Y\d\d") & b.isced11.isin(ED + ["UNK", "TOTAL"])].copy()
    a = b.age.str[1:].astype(int)
    b = b[a.between(25, 44)].copy()
    lo = (a[b.index] // 5) * 5
    b["age"] = "Y" + lo.astype(str) + "-" + (lo + 4).astype(str)
    b = b.groupby(["geo", "TIME_PERIOD", "age", "isced11"]).OBS_VALUE.sum(min_count=1).unstack()
    known = b[ED].sum(axis=1)
    for e in ED:
        b[e] = b[e] / known * b["TOTAL"]
    return b[ED].stack().rename("births")


def population():
    p = pd.read_csv(DATA / "lfsa_pgaed.csv")
    p = p[(p.sex == "F") & p.age.isin(AGES) & p.isced11.isin(ED)]
    return p.set_index(["geo", "TIME_PERIOD", "age", "isced11"]).OBS_VALUE.mul(1000).rename("women")


def rates():
    d = pd.concat([births(), population()], axis=1, join="inner").dropna().reset_index()
    d.columns = ["geo", "year", "age", "ed", "births", "women"]
    d = d[d.groupby(["geo", "year"]).age.transform("nunique") == len(AGES)]
    by_ed = (d.births / d.women).groupby([d.geo, d.year, d.ed]).sum().mul(5).unstack()
    g = d.groupby(["geo", "year", "age"])[["births", "women"]].sum()
    by_ed["all"] = (g.births / g.women).groupby(["geo", "year"]).sum() * 5
    by_ed = by_ed.dropna(subset=ED)
    n = by_ed.groupby(level=0).size()
    return by_ed[by_ed.index.get_level_values(0).isin(n[n >= MIN_YEARS].index)]


def breaks(t):
    out = {}
    for g, s in t.groupby(level=0):
        s = s.droplevel(0)[ED]
        ch = (s / s.shift(1) - 1).abs()
        out[g] = sorted({int(y) for y in ch.index for e in ED if ch.loc[y, e] > BREAK})
    return out


def country_chart(t, brk):
    geos = sorted(t.index.get_level_values(0).unique(), key=lambda g: NAMES.get(g, g))
    start = geos.index(DEFAULT)
    fig = go.Figure()
    for i, g in enumerate(geos):
        s = t.loc[g]
        for e, lab, color in EDU + [("all", "All women", "#6b6b6b")]:
            fig.add_trace(go.Scatter(
                x=s.index, y=s[e], name=lab, visible=i == start, legendgroup=lab,
                mode="lines+markers", marker=dict(size=7),
                line=dict(color=color, width=2, dash="dash" if e == "all" else "solid"),
                hovertemplate=f"{lab}: %{{y:.2f}}<extra></extra>",
            ))
    k = len(EDU) + 1
    buttons = []
    for i, g in enumerate(geos):
        vis = [j // k == i for j in range(len(geos) * k)]
        name = NAMES.get(g, g)
        note = f" (possible break: {', '.join(map(str, brk[g]))})" if brk[g] else ""
        buttons.append(dict(label=name, method="update",
                            args=[{"visible": vis}, {"title.text": f"{name}: births per woman at ages 25-44, by education{note}"}]))
    first = NAMES.get(DEFAULT, DEFAULT)
    note = f" (possible break: {', '.join(map(str, brk[DEFAULT]))})" if brk[DEFAULT] else ""
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        title=dict(text=f"{first}: births per woman at ages 25-44, by education{note}", y=0.98, yanchor="top"),
        yaxis_title="Births per woman, ages 25-44",
        updatemenus=[dict(buttons=buttons, active=start, x=1, y=1.09, xanchor="right", yanchor="bottom",
                          direction="down", showactive=True)],
        legend=dict(orientation="h", x=0, y=1.0, xanchor="left", yanchor="bottom"),
        margin=dict(l=60, r=20, t=120, b=40),
    )
    return fig


def change_table(t, brk):
    rows = []
    for g, s in t.groupby(level=0):
        s = s.droplevel(0)
        if START not in s.index or s.index.max() < 2021:
            continue
        last = s.index.max()
        r = dict(geo=g, country=NAMES.get(g, g), last=last,
                 break_years=" ".join(str(y) for y in brk[g] if START < y <= last))
        for e in ED + ["all"]:
            r[f"{e}_{START}"] = s.loc[START, e]
            r[f"{e}_last"] = s.loc[last, e]
            r[f"{e}_change"] = (s.loc[last, e] / s.loc[START, e] - 1) * 100
        rows.append(r)
    return pd.DataFrame(rows).sort_values("all_change")


def change_chart(c):
    lab = []
    for _, r in c.iterrows():
        off = [f"{LABEL[e].lower()} {r[f'{e}_change']:+.0f}%" for e in ED if abs(r[f"{e}_change"]) > XMAX]
        lab.append(f"{r.country} ({START}-{r['last']}){' †' if r.break_years else ''}"
                   + (f"<br><sub>off scale: {', '.join(off)}</sub>" if off else ""))
    fig = go.Figure()
    for e, name, color in EDU:
        x = c[f"{e}_change"]
        fig.add_trace(go.Bar(
            y=lab, x=x.clip(-XMAX, XMAX), name=name, orientation="h", marker_color=color,
            customdata=c[[f"{e}_{START}", f"{e}_last"]],
            hovertemplate=f"{name}: %{{x:+.0f}}% (%{{customdata[0]:.2f}} → %{{customdata[1]:.2f}})<extra></extra>",
        ))
    fig.add_trace(go.Scatter(
        y=lab, x=c["all_change"], name="All women", mode="markers",
        marker=dict(symbol="line-ns-open", size=16, color="#1a1a1a", line=dict(width=3)),
        hovertemplate="All women: %{x:+.0f}%<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#6b6b6b", width=1))
    fig.update_layout(
        template="plotly_white", barmode="group", bargap=0.25,
        title=f"Change in births per woman at ages 25-44, by education, {START} to latest year",
        xaxis_title="Change (%)", height=max(500, 46 * len(c) + 160),
        legend=dict(orientation="h", x=0, y=1.0, xanchor="left", yanchor="bottom"),
        margin=dict(l=190, r=20, t=110, b=50),
    )
    fig.update_xaxes(ticksuffix="%", range=[-XMAX, XMAX])
    return fig


def main():
    t = rates()
    brk = breaks(t)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    t.round(3).rename(columns=LABEL).to_csv(OUTDIR / "fertility_by_education_europe.csv")
    c = change_table(t, brk)
    c.round(3).to_csv(OUTDIR / "fertility_by_education_europe_change.csv", index=False)
    print(c.round(2).to_string())
    write_html(country_chart(t, brk), OUTDIR / "fertility_by_education_europe.html")
    write_html(change_chart(c), OUTDIR / "fertility_by_education_europe_change.html")


if __name__ == "__main__":
    main()
