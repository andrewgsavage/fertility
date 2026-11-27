"""Per-country timelines, 2005-2024: young-age fertility as fitted segments, with smartphone
and family-policy events.

Rows per country: ASFR at 20-24 and 25-29, all births and first births. Each row is the
BIC-chosen piecewise-linear fit to log ASFR (0-2 breaks), coloured by % a year, as in
smartphone_milestones.py; a button switches to each year's % change from the year before.

- All births: smartphone_milestones.load_asfr (Eurostat demo_frate, HFD asfrRR, HFC, Uruguay).
- First births: Eurostat demo_fordagec (order 1, single years of age) over demo_pjan women
  (mean of 1 January this year and next), averaged over the five ages, for the countries whose
  all-births rates come from Eurostat (France from 2013, a series break); HFD asfrRRbo ASFR1 for
  the HFD countries. None for Australia, New Zealand and Uruguay.
- Smartphones: first year mobile internet use among 16-24s passes 60% (Eurostat I_IUMP);
  elsewhere the Google Trends app-store search take-off year + 3, the median gap between the
  two where both exist.
- Policies: research/data/policy_events.csv, major national changes found by the same search
  for every country (see the Country timelines page).

Outputs (eurostat/outputs/): country_timelines_<region>.html, one per region; prints the
events as a Markdown table and each chart's height.
"""

import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import REPO, data_dir
from common.plotting import write_html
from smartphone_milestones import (COUNTRIES, FALL, HFD_CODES, LAST_YEAR, LIMIT, MID, PEAK_FROM, REGIONS,
                                   RISE, SHORT, group_means, load_asfr, milestones, slope_breaks, year_of)
from young_fertility import DATA, NAMES, OUTDIR

HFD_BO = data_dir("HFD") / "HFD" / "asfrRRbo.txt"
ORDER_FROM = {"FRA": 2013}
SEARCH_LAG = 3  # median years from app-store search take-off to mobile internet >60%
ROWS = [("all", "20-24", "20–24"), ("all", "25-29", "25–29"),
        ("first", "20-24", "1st birth 20–24"), ("first", "25-29", "1st birth 25–29")]
PER_COUNTRY = 78  # px per country: five rows plus the gap
GAP = 10  # px between countries
SHOCKS = {2008: "2008 crash", 2020: "COVID-19"}
SYMBOL = {"phone": "📱", "cash": "💶", "leave": "🍼", "childcare": "🧸", "housing": "🏠", "abortion": "⚖️"}
KIND_NAME = {"phone": "Smartphones", "cash": "Cash benefit", "leave": "Parental leave", "childcare": "Childcare",
             "housing": "Housing aid", "abortion": "Abortion law"}
# Ring round a policy icon: blue for an expansion or liberalisation, red for a cut or restriction.
RING = {"pro": RISE, "lib": RISE, "cut": FALL, "restrict": FALL}
POLICIES = REPO / "research" / "data" / "policy_events.csv"


def load_events():
    """Major family-policy changes, 2004-2025: iso3, year, month, domain, direction, description, size,
    source, url."""
    return pd.read_csv(POLICIES, dtype={"month": "Int64"})




# ---------- first-birth rates ----------

def single_age(path, extra):
    d = pd.read_csv(path, low_memory=False)
    d = d[d.age.str.fullmatch(r"Y\d+") & d.geo.isin(NAMES)].copy()
    d["a"] = d.age.str[1:].astype(int)
    d = d[d.a.between(20, 29)]
    for k, v in extra.items():
        d = d[d[k].astype(str) == v]
    iso = {v[0]: k for k, v in COUNTRIES.items()}
    d["iso"] = d.geo.map(NAMES).map(iso)
    return d.dropna(subset=["iso", "OBS_VALUE"])[["iso", "TIME_PERIOD", "a", "OBS_VALUE"]]


def eurostat_first(isos):
    """{ISO3: {"20-24": Series, "25-29": Series}} of first births per woman."""
    b = single_age(DATA / "change_matrix" / "demo_fordagec.csv", {"ord_brth": "1"})
    w = single_age(DATA / "change_matrix" / "demo_pjan.csv", {"sex": "F"})
    w = pd.concat([w, w.assign(TIME_PERIOD=w.TIME_PERIOD - 1)]).groupby(["iso", "TIME_PERIOD", "a"], as_index=False).OBS_VALUE.mean()
    x = b.merge(w, on=["iso", "TIME_PERIOD", "a"], suffixes=("_b", "_w"))
    x = x[(x.OBS_VALUE_w > 0) & x.iso.isin(isos)].assign(rate=lambda f: f.OBS_VALUE_b / f.OBS_VALUE_w)
    x = x[x.TIME_PERIOD >= x.iso.map(ORDER_FROM).fillna(0)]
    return {c: group_means(g, "TIME_PERIOD", "a", "rate") for c, g in x.groupby("iso")}


def hfd_first(code):
    d = pd.read_csv(HFD_BO, sep=r"\s+", skiprows=2, dtype={"Age": str})
    d = d[(d.Code == code) & d.Age.str.isdigit()].astype({"Age": int, "ASFR1": float})
    return group_means(d, "Year", "Age", "ASFR1")


def load_first(eurostat_isos):
    out = eurostat_first(eurostat_isos)
    for c, code in HFD_CODES.items():
        out[c] = hfd_first(code)
    return {c: {a: s[s.index <= LAST_YEAR] for a, s in v.items()} for c, v in out.items()}


# ---------- events ----------

def country_events(c, m):
    """[(year, kind, direction, text)] for one country; direction is None for smartphones."""
    ev = []
    if m["mobile"]:
        ev.append((year_of(m["mobile"]), "phone", None, f"Mobile internet use among 16–24s passed 60% ({m['mobile']})"))
    elif m["search"]:
        ev.append((m["search"] + SEARCH_LAG, "phone", None,
                   f"Smartphones, estimated: app-store search take-off ({m['search']}) + {SEARCH_LAG}"))
    for e in load_events().query("iso3 == @c").itertuples():
        what = {"pro": "", "cut": "Cut: ", "lib": "Liberalised: ", "restrict": "Restricted: "}[e.direction]
        ev.append((e.year, e.domain, e.direction, what + e.description))
    return sorted(ev)


# ---------- chart ----------

def yearly_changes(s):
    """[(year, % change from the year before)] from PEAK_FROM, consecutive years only."""
    s = s.dropna()
    s = s[s.index >= PEAK_FROM]
    return [(y, 100 * (s[y] / s[y - 1] - 1)) for y in s.index if y - 1 in s.index]


def region_chart(region, countries, ms, fits, series):
    n = len(countries)
    label = lambda c: SHORT.get(COUNTRIES[c][0], COUNTRIES[c][0])
    plot_h = PER_COUNTRY * n
    fig = make_subplots(rows=n, cols=1, shared_xaxes=True, vertical_spacing=GAP / plot_h)
    scale = [[0, FALL], [0.5, MID], [1, RISE]]
    for i, c in enumerate(countries, start=1):
        head = f"<b>{label(c)}</b>"
        cats = [head] + [r[2] for r in ROWS]
        ys, base, length, val, text = [], [], [], [], []
        for kind, age, name in ROWS:
            res = fits[c].get((kind, age))
            if res is None:
                continue
            br, sl, t0, t1 = res
            edges = [t0, *br, t1]
            for a, b, v in zip(edges[:-1], edges[1:], sl):
                ys.append(name), base.append(a), length.append(b - a), val.append(v)
                text.append(f"{label(c)}, {name}, {a}–{b}: {v:+.1f}% a year")
        fig.add_trace(go.Bar(
            x=length, y=ys, base=base, width=1, orientation="h",
            marker=dict(color=val, colorscale=scale, cmin=-LIMIT, cmax=LIMIT, line=dict(color="#fcfcfb", width=1),
                        showscale=i == 1, colorbar=dict(title="% a year", ticksuffix="%", len=min(1, 300 / plot_h),
                                                        y=1, yanchor="top", thickness=12)),
            hovertext=text, hoverinfo="text", showlegend=False), row=i, col=1)
        ys, base, val, text = [], [], [], []
        for kind, age, name in ROWS:
            s = series[c].get((kind, age))
            if s is None or fits[c].get((kind, age)) is None:
                continue
            for y, v in yearly_changes(s):
                ys.append(name), base.append(y - 1), val.append(v)
                text.append(f"{label(c)}, {name}, {y - 1}–{y}: {v:+.1f}%")
        fig.add_trace(go.Bar(
            x=[1] * len(ys), y=ys, base=base, width=1, orientation="h", visible=False,
            marker=dict(color=val, colorscale=scale, cmin=-LIMIT, cmax=LIMIT, line=dict(color="#fcfcfb", width=1),
                        showscale=i == 1, colorbar=dict(title="% change", ticksuffix="%", len=min(1, 300 / plot_h),
                                                        y=1, yanchor="top", thickness=12)),
            hovertext=text, hoverinfo="text", showlegend=False), row=i, col=1)
        ev = country_events(c, ms[c])
        seen = {}
        xs, syms, tips, rings = [], [], [], []
        for y, k, d, t in ev:
            off = seen.get(y, 0)
            seen[y] = off + 1
            xs.append(y + 0.75 * off), syms.append(SYMBOL[k]), tips.append(f"{y}: {t}")
            rings.append(RING.get(d, "rgba(0,0,0,0)"))
        fig.add_trace(go.Scatter(x=xs, y=[head] * len(xs), mode="markers", hoverinfo="skip", showlegend=False,
                                 marker=dict(symbol="circle", size=17, color="rgba(0,0,0,0)",
                                             line=dict(color=rings, width=2))), row=i, col=1)
        fig.add_trace(go.Scatter(x=xs, y=[head] * len(xs), mode="text", text=syms, textfont=dict(size=12),
                                 hovertext=tips, hoverinfo="text", showlegend=False), row=i, col=1)
        fig.update_yaxes(categoryorder="array", categoryarray=cats[::-1], range=[-0.5, len(cats) - 0.4],
                         tickfont=dict(size=10, color="#6b6b68"), showgrid=False, row=i, col=1)
    for y, name in SHOCKS.items():
        fig.add_vline(x=y, line=dict(color="#9a9995", width=1, dash="dot"))
        fig.add_annotation(x=y, y=1, yref="paper", yanchor="bottom", yshift=4, text=name, showarrow=False,
                           font=dict(size=10, color="#6b6b68"))
    legend = "   ".join(f"{SYMBOL[k]} {KIND_NAME[k]}" for k in SYMBOL) + "<br>" +         f"<span style='color:{RISE}'>○</span> Expansion or liberalisation   "         f"<span style='color:{FALL}'>○</span> Cut or restriction"
    fig.add_annotation(x=0, xref="paper", xanchor="left", y=1, yref="paper", yanchor="bottom", yshift=22,
                       align="left", text=legend, showarrow=False, font=dict(size=12))
    # Trace order per country: trend bars, yearly bars, rings, icons.
    trend = [j % 4 != 1 for j in range(4 * n)]
    yearly = [j % 4 != 0 for j in range(4 * n)]
    fig.update_layout(updatemenus=[dict(
        type="buttons", direction="right", showactive=True, x=0, xanchor="left", y=1 + 58 / plot_h,
        yanchor="bottom", pad=dict(r=0, t=0), font=dict(size=11),
        buttons=[dict(label="Trend", method="restyle", args=[{"visible": trend}]),
                 dict(label="Year by year", method="restyle", args=[{"visible": yearly}])])])
    fig.update_xaxes(range=[PEAK_FROM - 0.5, 2026.4], dtick=5, gridcolor="#ecebe8")
    fig.update_xaxes(showticklabels=True, row=n, col=1)
    height = plot_h + 128
    fig.update_layout(template="plotly_white", barmode="overlay", hovermode="closest", height=height,
                      title=None, margin=dict(t=98, l=110, r=20, b=30))
    return fig, height


def slug(region):
    return re.sub(r"[^a-z]+", "_", region.lower().replace("ü", "u")).strip("_")


def main():
    ms = milestones()
    asfr = load_asfr()
    eurostat_isos = [c for c in asfr if c not in HFD_CODES and c not in ("AUS", "NZL", "URY")]
    first = load_first(eurostat_isos)
    fits, series = {}, {}
    for c in ms:
        fits[c], series[c] = {}, {}
        for kind, src in (("all", asfr), ("first", first)):
            for age in ("20-24", "25-29"):
                s = src.get(c, {}).get(age)
                series[c][(kind, age)] = s
                fits[c][(kind, age)] = None if s is None else slope_breaks(s)
    for region in REGIONS:
        countries = sorted((c for c in ms if ms[c]["region"] == region), key=lambda c: COUNTRIES[c][0])
        fig, height = region_chart(region, countries, ms, fits, series)
        name = f"country_timelines_{slug(region)}.html"
        write_html(fig, OUTDIR / name)
        print(f"{name}: {height}px")
    print("\n| Country | Year | Change | Size | Source |\n|---|--:|---|---|---|")
    ev = load_events().assign(country=lambda d: d.iso3.map(lambda c: COUNTRIES[c][0])).sort_values(["country", "year"])
    for e in ev.itertuples():
        size = "" if pd.isna(e.size) else e.size
        print(f"| {e.country} | {e.year} | {SYMBOL[e.domain]} { {"cut": "Cut: ", "restrict": "Restricted: "}.get(e.direction, "")}{e.description} | {size} "
              f"| [{e.source}]({e.url}) |")


if __name__ == "__main__":
    main()
