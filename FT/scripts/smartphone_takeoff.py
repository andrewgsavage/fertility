"""Reproduce and stress-test the smartphone chart in the FT's "Why birth rates are falling
everywhere all at once" (John Burn-Murdoch, 16 May 2026).

The FT dates smartphone take-off per country ("surveys of smartphone adoption and Google
searches for app stores"), re-indexes each country's TFR to years since take-off, and
plots the % gap between TFR and a linear trend fitted to the ten years up to take-off.

Steps:
1. FT method check: recover the FT's take-off years from its aligned chart, and rebuild its
   "% vs pre-smartphone trend" series from its own TFR with a linear fit over k = -10..0.
2. Search dating: take-off = first year a country's app-store search index (Google Trends,
   see google_trends_app_stores.py) reaches TAKEOFF_SHARE of its 2004-2024 peak year.
3. Extension: the same comparison for every country with a search-dated take-off, using
   UN WPP 2024 TFR (via Our World in Data, estimates to 2023).
4. Placebo: move each country's take-off year by -6..+4 years and recompute the gap 5-7
   years later. If the drop is tied to smartphones, the true date should stand out.

Inputs: FT/data/birth_rates_2026/v<id>.html (Flourish embeds), FT/intermediate/
google_trends_app_stores.csv, OWID/data/children-born-per-woman.csv.
Outputs (FT/outputs/): smartphone_takeoff_years.csv, smartphone_ft_check.csv,
smartphone_vs_trend.csv/.html, smartphone_placebo.csv/.html.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from common.flourish import flourish
from common.paths import data_dir, intermediate_dir, outputs_dir
from common.plotting import write_html

FT_DATA = data_dir("FT") / "birth_rates_2026"
TRENDS = intermediate_dir("FT") / "google_trends_app_stores.csv"
TFR = data_dir("OWID") / "children-born-per-woman.csv"
OUT = outputs_dir("FT")

TAKEOFF_SHARE = 0.25  # search index share of its peak year that marks take-off
PRE = 10  # years before take-off in the trend fit (k = -PRE..0, as the FT)
POST = 12
WINDOW = (5, 7)  # years after take-off averaged for the placebo comparison
SHIFTS = range(-6, 5)
FT_COUNTRIES = ["US", "UK", "Australia", "Indonesia", "Mexico", "Egypt", "Iran", "Senegal"]

# Trends country name -> OWID entity, where they differ.
OWID_NAMES = {"US": "United States", "UK": "United Kingdom", "S Korea": "South Korea",
              "Türkiye": "Turkey", "Viet Nam": "Vietnam", "Czechia": "Czechia"}


def ft_wide(vid):
    d = flourish(FT_DATA / f"v{vid}.html")
    return d.pivot(index="year", columns="series", values="value")


def ft_takeoff_years():
    """The FT's take-off year per country: the shift that maps its calendar-year TFR
    (slide 3) onto its years-since-take-off TFR (slide 4)."""
    cal, aligned = ft_wide(28990485), ft_wide(28990534)
    years = {}
    for c in aligned.columns:
        a = aligned[c].dropna()
        err = {y: (cal[c].reindex(a.index + y).to_numpy() - a.to_numpy()) for y in range(1995, 2020)}
        years[c] = min(err, key=lambda y: np.nanmax(np.abs(err[y])) if np.isfinite(err[y]).any() else 9)
    return pd.Series(years, name="ft_takeoff")


def gap_vs_trend(tfr, takeoff, pre=PRE, post=POST):
    """% gap of TFR from a linear trend fitted on years takeoff-pre..takeoff, for k=-pre..post."""
    fit_years = np.arange(takeoff - pre, takeoff + 1)
    y = tfr.reindex(fit_years)
    if y.isna().any():
        return None
    slope, intercept = np.polyfit(fit_years, y.to_numpy(), 1)
    k = np.arange(-pre, post + 1)
    actual = tfr.reindex(takeoff + k).to_numpy()
    return pd.Series(100 * (actual / (intercept + slope * (takeoff + k)) - 1), index=k)


def search_takeoff_years():
    t = pd.read_csv(TRENDS)
    t["year"] = t.month.str[:4].astype(int)
    idx = t.groupby(["country", "year"]).value.sum().unstack("country") / 12  # annual mean, 4 terms summed
    years = {}
    for c in idx.columns:
        s = idx[c]
        if s.max() < 20:  # too little search volume for a series
            continue
        years[c] = int(s.index[s >= TAKEOFF_SHARE * s.max()][0])
    return pd.Series(years, name="search_takeoff"), idx


def wpp_tfr():
    d = pd.read_csv(TFR)
    return d.pivot(index="year", columns="entity", values="fertility_rate_hist")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wpp = wpp_tfr()

    # 1. FT method check.
    ft_years = ft_takeoff_years()
    cal, ft_gap = ft_wide(28990485), ft_wide(28990605)
    check = []
    for c, y in ft_years.items():
        mine = gap_vs_trend(cal[c], y)
        ours_wpp = gap_vs_trend(wpp[OWID_NAMES.get(c, c)], y)
        for k in ft_gap.index:
            check.append({"country": c, "k": k, "ft": ft_gap.at[k, c],
                          "rebuilt_ft_tfr": mine.get(k), "rebuilt_wpp_tfr": ours_wpp.get(k)})
    check = pd.DataFrame(check)
    check.round(3).to_csv(OUT / "smartphone_ft_check.csv", index=False)
    err = (check.ft - check.rebuilt_ft_tfr).abs().max()
    print(f"FT take-off years: {ft_years.to_dict()}; max |FT - rebuilt| = {err:.3f} pp")

    # 2. Search dating.
    search_years, idx = search_takeoff_years()
    years = pd.concat([search_years, ft_years], axis=1)
    years.index.name = "country"
    years.to_csv(OUT / "smartphone_takeoff_years.csv")
    print(years.loc[[c for c in FT_COUNTRIES if c in years.index]])

    # 3. Extension with WPP TFR.
    gaps = {}
    for c, y in search_years.items():
        name = OWID_NAMES.get(c, c)
        if name in wpp:
            g = gap_vs_trend(wpp[name], y)
            if g is not None:
                gaps[c] = g
    gaps = pd.DataFrame(gaps)
    gaps.index.name = "k"
    gaps.round(2).to_csv(OUT / "smartphone_vs_trend.csv")

    fig = go.Figure()
    for c in gaps.columns:
        s = gaps[c].dropna()
        fig.add_trace(go.Scatter(x=s.index, y=s, mode="lines", name=c, showlegend=False,
                                 line=dict(color="rgba(120,120,120,0.35)", width=1),
                                 hovertemplate=f"{c}<br>%{{x:+d}} yrs: %{{y:.1f}}%<extra></extra>"))
    med = gaps.median(axis=1)[gaps.count(axis=1) >= len(gaps.columns) / 2]
    fig.add_trace(go.Scatter(x=med.index, y=med, mode="lines", name=f"Median, {len(gaps.columns)} countries",
                             line=dict(color="#c0392b", width=3)))
    ft_med = ft_gap.median(axis=1)
    fig.add_trace(go.Scatter(x=ft_med.index, y=ft_med, mode="lines", name="FT chart median, 8 countries",
                             line=dict(color="#1f4e8c", width=3, dash="dash")))
    fig.add_vline(x=0, line=dict(color="#888", width=1))
    fig.add_hline(y=0, line=dict(color="#888", width=1))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=40, b=50),
                      title="TFR vs pre-take-off linear trend, take-off dated from app-store searches",
                      xaxis_title="Years since smartphone take-off",
                      yaxis=dict(title="% gap from trend", range=[-50, 50]),
                      legend=dict(orientation="h", y=-0.18))
    write_html(fig, OUT / "smartphone_vs_trend.html")

    # 4. Placebo: shift each country's take-off year.
    rows = []
    for c, y in search_years.items():
        name = OWID_NAMES.get(c, c)
        if name not in wpp:
            continue
        for s in SHIFTS:
            g = gap_vs_trend(wpp[name], y + s, post=WINDOW[1])
            if g is None or g.loc[WINDOW[0]:WINDOW[1]].isna().any():
                continue
            rows.append({"country": c, "shift": s, "gap": g.loc[WINDOW[0]:WINDOW[1]].mean(), "ft": False})
    for c, y in ft_years.items():
        for s in SHIFTS:
            g = gap_vs_trend(cal[c], y + s, post=WINDOW[1])
            if g is None or g.loc[WINDOW[0]:WINDOW[1]].isna().any():
                continue
            rows.append({"country": c, "shift": s, "gap": g.loc[WINDOW[0]:WINDOW[1]].mean(), "ft": True})
    placebo = pd.DataFrame(rows)
    placebo.round(2).to_csv(OUT / "smartphone_placebo.csv", index=False)
    summary = placebo.groupby(["ft", "shift"]).gap.agg(["median", "count"]).unstack("ft")
    print(summary.round(2))
    ft_placebo = placebo[placebo.ft].groupby("shift").gap.median()
    placebo = placebo[~placebo.ft]

    fig = go.Figure()
    fig.add_trace(go.Box(x=placebo["shift"], y=placebo.gap, boxpoints="all", jitter=0.4, pointpos=0,
                         marker=dict(color="rgba(120,120,120,0.5)", size=5),
                         line=dict(color="#555"), fillcolor="rgba(0,0,0,0)",
                         name=f"{placebo.country.nunique()} countries, search dates, UN WPP TFR",
                         customdata=placebo.country,
                         hovertemplate="%{customdata}: %{y:.1f}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=ft_placebo.index, y=ft_placebo, mode="lines+markers",
                             name="FT's 8 countries, FT dates and TFR (median)",
                             line=dict(color="#1f4e8c", width=3), marker=dict(size=8),
                             hovertemplate="Moved %{x:+d} yrs: %{y:.1f}%<extra></extra>"))
    fig.add_vline(x=0, line=dict(color="#c0392b", width=1, dash="dot"))
    fig.add_hline(y=0, line=dict(color="#888", width=1))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=40, b=50),
                      legend=dict(orientation="h", y=-0.2),
                      title=f"TFR gap from trend {WINDOW[0]}–{WINDOW[1]} years after a take-off date moved by N years",
                      xaxis=dict(title="Take-off date moved by (years; 0 = dated take-off)", dtick=1),
                      yaxis_title="% gap from pre-date linear trend")
    write_html(fig, OUT / "smartphone_placebo.html")


if __name__ == "__main__":
    main()
