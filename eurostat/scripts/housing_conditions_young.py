"""Housing conditions of young adults by country: overcrowding, cost overburden and tenure.

Levels by country, and how the change in each relates to the change in coupling at
25-34 and in first-birth rates across European countries.

Eurostat EU-SILC tables, downloaded on first run into eurostat/data/housing_young/
(not tracked in git):
  ilc_lvho05a.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_lvho05a?format=SDMX-CSV&compressed=false
                   overcrowding rate by age, sex and poverty status (total population)
  ilc_lvho07a.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_lvho07a?format=SDMX-CSV&compressed=false
                   housing cost overburden rate by age, sex and poverty status
  ilc_lvps05.csv   https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_lvps05?format=SDMX-CSV&compressed=false
                   distribution of population by sex, age and tenure status (2015 onwards)

The overcrowding and cost overburden tables have no 25-34 band; 25-29 is the closest.
Tenure is published for 25-34 only from 2015. ilc_lvho02 (tenure by household type)
has no age split, so it isn't used.

Outcomes come from eurostat/outputs/change_matrix.json (run change_matrix.py first):
women 25-34 in a couple from the 2011 and 2021 censuses (couple_census_25_34), and
first-birth conditional rates at 25-29 and 30-34 (HFD mi.txt / exposRRpa.txt; UK from
ONS cohort table 3).

Windows: housing change against coupling over the census window 2011->2021; against
first-birth rates over 2010->2022 (tenure: 2015->2022). Each end takes the stated year,
else the nearest within one year.

Writes eurostat/outputs/housing_young_levels.html, housing_young_tenure.html,
housing_young_change_scatter.html and housing_young_change_corr.csv.
"""

import json
import math
import urllib.request

import pandas as pd
import plotly.graph_objects as go

from _common import DATA, OUTDIR
from change_matrix import CENSUS_COUPLE_PASSED, COUNTRIES, EU2ISO
from common.plotting import write_html

CACHE = DATA / "housing_young"
API = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{}?format=SDMX-CSV&compressed=false"
# Census coupling changes that another series confirms (the change matrix's rule); the rest are open markers.
CONFIRMED = CENSUS_COUPLE_PASSED[(2011, 2021)]
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#9ca3af"

MEASURES = {  # key: (label, short label, base year for first births)
    "overcrowded_25_29": ("Overcrowded, 25–29", "% overcrowded, 25–29", 2010),
    "overburden_25_29": ("Housing cost overburden, 25–29", "% with housing costs > 40% of income, 25–29", 2010),
    "owner_25_34": ("Owner-occupiers, 25–34", "% owner-occupiers, 25–34", 2015),
    "rent_market_25_34": ("Renting at market rent, 25–34", "% renting at market rent, 25–34", 2015),
    "rent_reduced_25_34": ("Renting at reduced rent or free, 25–34", "% renting at reduced rent or free, 25–34", 2015),
}
OUTCOMES = {  # key: (label, matrix series, base, end, percent change)
    "couple": ("Women 25–34 in a couple (census), change in points", "couple_census_25_34", 2011, 2021, False),
    "first_25_29": ("First-birth rate 25–29, % change", "first_25_29", None, 2022, True),
    "first_30_34": ("First-birth rate 30–34, % change", "first_30_34", None, 2022, True),
}


def fetch(code):
    path = CACHE / f"{code}.csv"
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(API.format(code), headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    d = pd.read_csv(path, low_memory=False)
    d = d[d.geo.isin(EU2ISO)].dropna(subset=["OBS_VALUE"]).copy()
    d = d[~d.OBS_FLAG.fillna("").astype(str).str.contains("u")]  # low reliability
    d["iso"] = d.geo.map(EU2ISO)
    d["year"] = d.TIME_PERIOD.astype(int)
    return d


def as_series(d):
    out = {}
    for iso, year, v in d[["iso", "year", "OBS_VALUE"]].itertuples(index=False):
        out.setdefault(iso, {})[int(year)] = float(v)
    return out


def load_housing():
    h = {}
    for code, key in (("ilc_lvho05a", "overcrowded_25_29"), ("ilc_lvho07a", "overburden_25_29")):
        d = fetch(code)
        h[key] = as_series(d[(d.age == "Y25-29") & (d.sex == "T") & (d.rskpovth == "TOTAL")])
    d = fetch("ilc_lvps05")
    d = d[(d.age == "Y25-34") & (d.sex == "T")]
    for tenure, key in (("OWN", "owner_25_34"), ("RENT_MKT", "rent_market_25_34"), ("RENT_FR", "rent_reduced_25_34")):
        h[key] = as_series(d[d.tenure == tenure])
    return h


def near(s, year, tol=1):
    for gap in range(tol + 1):
        for y in (year - gap, year + gap):
            if y in s:
                return y
    return None


def change(s, a, b, pct=False):
    ya, yb = near(s or {}, a), near(s or {}, b)
    if ya is None or yb is None:
        return None
    if pct:
        return 100 * (s[yb] / s[ya] - 1) if s[ya] else None
    return s[yb] - s[ya]


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx, syy = sum((x - mx) ** 2 for x in xs), sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


def load_outcomes():
    s = json.loads((OUTDIR / "change_matrix.json").read_text(encoding="utf-8"))["series"]
    return {k: {c: {int(y): v for y, v in ys.items()} for c, ys in s[src].items()}
            for k, (_, src, *_r) in OUTCOMES.items()}


def pairs(housing, outcomes):
    """(measure, outcome) -> list of (iso, x change, y change), plus the window used."""
    out = {}
    for m, (_, _, fb_base) in MEASURES.items():
        for o, (_, _, base, end, pct) in OUTCOMES.items():
            a = base if base is not None else fb_base
            if o == "couple" and m.endswith("25_34"):
                continue  # tenure by age starts in 2015, after the 2011 census
            pts = []
            for iso in sorted(set(housing[m]) & set(outcomes[o])):
                x = change(housing[m][iso], a, end)
                y = change(outcomes[o][iso], a, end, pct)
                if x is not None and y is not None:
                    pts.append((iso, x, y))
            out[(m, o)] = (pts, a, end)
    return out


def scatter_page(results):
    fig = go.Figure()
    keys = list(results)
    buttons = []
    for i, (m, o) in enumerate(keys):
        pts, a, b = results[(m, o)]
        r = pearson([p[1] for p in pts], [p[2] for p in pts])
        weak = [o == "couple" and p[0] not in CONFIRMED for p in pts]
        fig.add_trace(go.Scatter(
            x=[p[1] for p in pts], y=[p[2] for p in pts], mode="markers+text", text=[p[0] for p in pts],
            textposition="top center", textfont=dict(size=10, color="#6b7280"), visible=i == 0,
            marker=dict(size=9, color=BLUE, symbol=["circle-open" if w else "circle" for w in weak],
                        line=dict(color=[BLUE if w else "white" for w in weak], width=[2 if w else 1 for w in weak])),
            customdata=[COUNTRIES[p[0]][1] + (" (census change not confirmed by another source)" if w else "")
                        for p, w in zip(pts, weak)],
            hovertemplate="%{customdata}<br>Housing: %{x:+.1f}<br>Outcome: %{y:+.1f}<extra></extra>"))
        rtxt = "n/a" if r is None else f"{r:+.2f}"
        title = f"{MEASURES[m][0]} vs {OUTCOMES[o][0].split(',')[0]}, {a}–{b}: r = {rtxt}, n = {len(pts)}"
        if o == "couple":
            conf = [p for p in pts if p[0] in CONFIRMED]
            rc = pearson([p[1] for p in conf], [p[2] for p in conf])
            title += f"<br>confirmed census changes only: r = {'n/a' if rc is None else f'{rc:+.2f}'}, n = {len(conf)}"
        buttons.append(dict(label=f"{MEASURES[m][0]} · {OUTCOMES[o][0].split(',')[0]}", method="update",
                            args=[{"visible": [j == i for j in range(len(keys))]},
                                  {"title.text": title, "xaxis.title.text": f"Change in {MEASURES[m][1]} (points)",
                                   "yaxis.title.text": OUTCOMES[o][0]}]))
    first = buttons[0]["args"][1]
    fig.update_layout(
        template="plotly_white", height=480, margin=dict(l=60, r=20, t=90, b=50),
        title=dict(text=first["title.text"], font=dict(size=13), y=0.9),
        xaxis_title=first["xaxis.title.text"], yaxis_title=first["yaxis.title.text"],
        updatemenus=[dict(buttons=buttons, direction="down", x=0, xanchor="left", y=1.2, yanchor="top")])
    fig.add_hline(y=0, line=dict(color="#d1d5db", width=1))
    fig.add_vline(x=0, line=dict(color="#d1d5db", width=1))
    write_html(fig, OUTDIR / "housing_young_change_scatter.html")


def levels_page(housing):
    fig = go.Figure()
    keys = ["overcrowded_25_29", "overburden_25_29"]
    buttons = []
    for i, k in enumerate(keys):
        rows = []
        for iso, s in housing[k].items():
            y0, y1 = near(s, 2010), max(s)
            if y0 is not None and y1 >= 2023:
                rows.append((COUNTRIES[iso][1], s[y0], s[y1], y0, y1))
        rows.sort(key=lambda r: r[2])
        names = [r[0] for r in rows]
        vis = i == 0
        fig.add_trace(go.Scatter(  # connector
            x=sum([[r[1], r[2], None] for r in rows], []), y=sum([[r[0], r[0], None] for r in rows], []),
            mode="lines", line=dict(color="#d1d5db", width=2), hoverinfo="skip", showlegend=False, visible=vis))
        fig.add_trace(go.Scatter(
            x=[r[1] for r in rows], y=names, mode="markers", name="2010", visible=vis,
            marker=dict(size=9, color=GREY, line=dict(color="white", width=1)),
            customdata=[r[3] for r in rows], hovertemplate="%{y}, %{customdata}: %{x:.1f}%<extra></extra>"))
        fig.add_trace(go.Scatter(
            x=[r[2] for r in rows], y=names, mode="markers", name="Latest", visible=vis,
            marker=dict(size=9, color=BLUE, line=dict(color="white", width=1)),
            customdata=[r[4] for r in rows], hovertemplate="%{y}, %{customdata}: %{x:.1f}%<extra></extra>"))
        buttons.append(dict(label=MEASURES[k][0], method="update",
                            args=[{"visible": [j // 3 == i for j in range(3 * len(keys))]},
                                  {"xaxis.title.text": MEASURES[k][1], "yaxis.categoryarray": names}]))
    fig.update_layout(
        template="plotly_white", height=760, margin=dict(l=110, r=20, t=70, b=50),
        xaxis_title=MEASURES[keys[0]][1], yaxis=dict(categoryorder="array", categoryarray=buttons[0]["args"][1]["yaxis.categoryarray"]),
        legend=dict(orientation="h", x=1, xanchor="right", y=1.06),
        updatemenus=[dict(buttons=buttons, direction="down", x=0, xanchor="left", y=1.09, yanchor="top")])
    write_html(fig, OUTDIR / "housing_young_levels.html")


def tenure_page(housing):
    rows = []
    for iso in housing["owner_25_34"]:
        s = housing["owner_25_34"][iso]
        y = max(s)
        if y < 2023:
            continue
        vals = [housing[k].get(iso, {}).get(y) for k in ("owner_25_34", "rent_market_25_34", "rent_reduced_25_34")]
        if None in vals:
            continue
        own15 = housing["owner_25_34"][iso].get(2015)
        rows.append((COUNTRIES[iso][1], y, *vals, own15))
    rows.sort(key=lambda r: r[2])
    names = [r[0] for r in rows]
    fig = go.Figure()
    for j, (label, color) in enumerate((("Owner", BLUE), ("Market rent", ORANGE), ("Reduced rent or free", AQUA))):
        fig.add_trace(go.Bar(
            y=names, x=[r[2 + j] for r in rows], orientation="h", name=label,
            marker=dict(color=color, line=dict(color="white", width=1)),
            customdata=[r[1] for r in rows], hovertemplate="%{y}, %{customdata}: %{x:.1f}%<extra>" + label + "</extra>"))
    fig.add_trace(go.Scatter(
        y=[r[0] for r in rows if r[5] is not None], x=[r[5] for r in rows if r[5] is not None], mode="markers",
        name="Owners, 2015", marker=dict(symbol="line-ns-open", size=14, color="#111827", line=dict(width=2)),
        hovertemplate="%{y}, 2015 owners: %{x:.1f}%<extra></extra>"))
    fig.update_layout(
        template="plotly_white", barmode="stack", bargap=0.25, height=780, margin=dict(l=110, r=20, t=50, b=50),
        xaxis=dict(title="% of people aged 25–34, by tenure (latest year)", range=[0, 100]),
        legend=dict(orientation="h", x=0, y=1.05))
    write_html(fig, OUTDIR / "housing_young_tenure.html")


def main():
    housing = load_housing()
    outcomes = load_outcomes()
    results = pairs(housing, outcomes)
    lines = ["measure,outcome,base,end,n,r,n_confirmed,r_confirmed"]
    for (m, o), (pts, a, b) in results.items():
        r = pearson([p[1] for p in pts], [p[2] for p in pts])
        conf = [p for p in pts if p[0] in CONFIRMED] if o == "couple" else []
        rc = pearson([p[1] for p in conf], [p[2] for p in conf])
        fmt = lambda v: "" if v is None else round(v, 3)
        lines.append(f"{m},{o},{a},{b},{len(pts)},{fmt(r)},{len(conf) if conf else ''},{fmt(rc)}")
        print(f"{m:20s} {o:12s} {a}-{b} n={len(pts):2d} r={'n/a' if r is None else f'{r:+.2f}'}"
              f"  confirmed n={len(conf)} r={'n/a' if rc is None else f'{rc:+.2f}'}")
    (OUTDIR / "housing_young_change_corr.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    scatter_page(results)
    levels_page(housing)
    tenure_page(housing)
    for k in MEASURES:  # headline levels
        vals = {COUNTRIES[c][1]: (max(s), s[max(s)]) for c, s in housing[k].items()}
        lo, hi = min(vals.items(), key=lambda x: x[1][1]), max(vals.items(), key=lambda x: x[1][1])
        print(k, "lowest", lo, "highest", hi)


if __name__ == "__main__":
    main()
