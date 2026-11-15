"""Share of abortions to women who already have a child, by country and by age.

"Has a child" = at least one previous live birth (DHSC and PHS: a previous
pregnancy ending in a live birth or stillbirth). Abortions with unknown parity
are left out of the share; country-years with 15% or more unknown are dropped.

Sources:
  Eurostat demo_fabortord (abortions by age and number of previous live births, 2007-2024)
      eurostat/data/demo_fabortord.csv
      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_fabortord/?format=SDMX-CSV
  England & Wales: DHSC Table 3a, parity (% of residents' abortions), transcribed below.
  Scotland: Public Health Scotland, terminations by health board and parity (archived, 2000-2021)
      ONS/data/scotland/parity_2022.csv
      https://www.opendata.nhs.scot/dataset/termination-of-pregnancy-in-scotland
  Germany 2021-2025: Destatis, abortions by previous live births, transcribed below
      (Eurostat before 2021).
  Netherlands 2022-2024: IGJ Wafz 2024 report, Tabel F (% with no children), transcribed below.
  United States: CDC Abortion Surveillance reports (PMC copies), table "No. of previous live
      births", national Total row, data years 2014-2015 and 2018-2022; reporting areas vary
      (40-45). eurostat/data/national/us_cdc_parity.csv, with each year's PMC URL and exclusions.

Outputs:
  eurostat/outputs/abortion_parity.csv
  eurostat/outputs/abortion_parity_trend.html          one line per country
  eurostat/outputs/abortion_parity_by_age.html         one small chart per country, a line per age
"""

import pathlib
import sys

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parent.parent
DATA = _SCRIPT_DIR.parent / "data"
OUTDIR = _SCRIPT_DIR.parent / "outputs"
sys.path.insert(0, str(_SCRIPT_DIR))
from _common import write_html  # noqa: E402
from abortion_by_age import AGES, COLORS, EUROSTAT_AGE, NAMES  # noqa: E402

# England & Wales by age uses DHSC's groups (Under 20, 20–34, 35+), so 20–34 gets its own line.
AGES_X = ["Under 20", "20–24", "25–29", "30–34", "20–34", "35+"]
COLORS_X = dict(COLORS, **{"20–34": "#7f7f7f"})

# DHSC Table 3a, % of abortions with parity 1+ (2014 tables for 2004-2012, 2023 tables for 2013-2023).
EW = {2004: 47, 2005: 47, 2006: 47, 2007: 47, 2008: 48, 2009: 49, 2010: 50, 2011: 51, 2012: 52,
      2013: 53, 2014: 54, 2015: 54, 2016: 55, 2017: 55, 2018: 56, 2019: 55, 2020: 58, 2021: 57,
      2022: 54, 2023: 54}
# Destatis, Schwangerschaftsabbrüche nach vorangegangenen Lebendgeborenen: (none, total).
DE = {2021: (38686, 94596), 2022: (43828, 103927), 2023: (45127, 106218), 2024: (45440, 106455),
      2025: (46675, 105710)}
# IGJ Tabel F: % of women treated with no children (excludes "not filled in", 0.7%).
NL = {2022: 51.0, 2023: 51.5, 2024: 51.9}

US = "United States (40–45 areas)"
SHOWN = ["England & Wales", "Scotland", "Finland", "Spain", "Portugal", "Germany", "Italy",
         "Czechia", "Hungary", US]
CATS = ["0", "1", "2", "3", "4", "5", "GE6"]


def eurostat_parity():
    d = pd.read_csv(DATA / "demo_fabortord.csv")
    d = d[d.geo.isin(NAMES) & d.age.isin(list(EUROSTAT_AGE) + ["TOTAL"])]
    d["age"] = d.age.map(lambda a: "All ages" if a == "TOTAL" else EUROSTAT_AGE[a])
    p = d.pivot_table(index=["geo", "TIME_PERIOD", "age"], columns="ord_brth", values="OBS_VALUE",
                      aggfunc="sum")
    known = p[[c for c in CATS if c in p]].sum(axis=1, min_count=2)
    unk = p["UNK"].fillna(0) if "UNK" in p else 0
    out = pd.DataFrame({"none": p["0"], "known": known, "unknown_share": unk / (known + unk)})
    out = out[out["none"].notna() & (out.unknown_share < 0.15) & (out.known > 0)].reset_index()
    # Italy 2012 reads 50% against 59-61% either side, at every age: a recording break.
    out = out[~((out.geo == "IT") & (out.TIME_PERIOD == 2012))]
    out["share_with_child"] = 100 * (1 - out["none"] / out.known)
    out["country"] = out.geo.map(NAMES)
    return out.rename(columns={"TIME_PERIOD": "year"})


def load():
    e = eurostat_parity()
    e = e[e.age == "All ages"][["country", "year", "share_with_child", "known"]]
    e = e[~((e.country == "Germany") & (e.year >= 2021))]
    rows = [("England & Wales", y, v, None) for y, v in EW.items()]
    rows += [("Germany", y, 100 * (1 - n / t), t) for y, (n, t) in DE.items()]
    rows += [("Netherlands", y, 100 - v - 0.7, None) for y, v in NL.items()]
    s = pd.read_csv(_ROOT / "ONS" / "data" / "scotland" / "parity_2022.csv")
    s = s[s.HBR != "RA2704"]
    s["n"] = pd.to_numeric(s.NumberofTerminations, errors="coerce")
    for y, g in s.groupby("YearofTermination"):
        k = g[g.Parity != "Other"].groupby("Parity").n.sum()
        rows.append(("Scotland", int(y), 100 * (1 - k["0"] / k.sum()), k.sum()))
    # CDC single-year tables, 40-45 reporting areas (the set changes year to year).
    u = pd.read_csv(DATA / "national" / "us_cdc_parity.csv")
    u = u[u.table == "single-year"]
    rows += [(US, int(r.data_year), 100 - r.pct_0, r.total_known) for r in u.itertuples()]
    x = pd.DataFrame(rows, columns=["country", "year", "share_with_child", "known"])
    d = pd.concat([e, x], ignore_index=True).sort_values(["country", "year"])
    # Serbia's series breaks between 2020 and 2022 (72% to 38%); Albania and Croatia are too patchy.
    return d[~d.country.isin(["Serbia", "Albania", "Croatia"])]


def plot_trend(d):
    fig = go.Figure()
    order = SHOWN + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    for i, c in enumerate(order):
        x = d[d.country == c].sort_values("year")
        fig.add_trace(go.Scatter(
            x=x.year, y=x.share_with_child, mode="lines+markers", name=c, marker=dict(size=4),
            line=dict(color=colors[i % len(colors)], width=2.5 if c in ("England & Wales", "Scotland") else 1.5),
            visible=True if c in SHOWN else "legendonly",
            hovertemplate=c + " %{x}: %{y:.0f}%<extra></extra>"))
    fig.update_yaxes(title_text="% of abortions to women with a previous birth", ticksuffix="%",
                     range=[30, 80])
    fig.update_layout(template="plotly_white",
                      title="Share of abortions to women who already have a child (click names to add countries)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=150, t=60), hovermode="closest")
    return fig


def plot_by_age(cols=4):
    e = age_parity()
    e = e[e.age != "All ages"]
    n = e.groupby("country").year.nunique()
    countries = sorted(c for c in n[n >= 3].index if c not in ("Serbia", "Albania", "Croatia"))
    e = e[e.country.isin(countries)]
    rows = -(-len(countries) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=countries, shared_yaxes=True,
                        horizontal_spacing=0.04, vertical_spacing=0.3 / rows * 1.4)
    shown = set()
    for i, c in enumerate(countries):
        r, k = i // cols + 1, i % cols + 1
        x = e[e.country == c]
        for a in AGES_X:
            s = x[x.age == a].sort_values("year")
            if s.empty:
                continue
            fig.add_trace(go.Scatter(
                x=s.year, y=s.share_with_child, mode="lines", name=a, legendgroup=a,
                showlegend=a not in shown, line=dict(color=COLORS_X[a], width=1.8),
                hovertemplate=f"{c} {a} %{{x}}: %{{y:.0f}}%<extra></extra>"), row=r, col=k)
            shown.add(a)
    fig.update_xaxes(range=[2006.5, 2024.5], dtick=5, tickfont=dict(size=9))
    fig.update_yaxes(range=[0, 100], ticksuffix="%", tickfont=dict(size=9))
    fig.update_annotations(font_size=12)
    fig.update_layout(template="plotly_white", height=190 * rows + 120,
                      title=dict(text="Share of abortions to women who already have a child, by age, 2007–2024",
                                 y=0.995, yanchor="top"),
                      legend=dict(orientation="h", x=0, y=1.0 + 45 / (190 * rows), yanchor="bottom"),
                      margin=dict(t=120, l=45, r=15, b=30), hovermode="closest")
    return fig, e


# --- Abortions per 100 births of the same order ---------------------------------
HFD_BO = _ROOT / "HFD" / "data" / "HFD" / "birthsRRbo.txt"


def bad_age_years(e=None):
    """Country-years whose age-by-parity cells don't add up to the all-ages share."""
    e = eurostat_parity() if e is None else e
    tot = e[e.age == "All ages"].set_index(["country", "year"]).share_with_child
    g = e[e.age != "All ages"].groupby(["country", "year"])[["none", "known"]].sum()
    diff = (100 * (1 - g["none"] / g.known) - tot.reindex(g.index)).abs()
    return set(diff[diff > 3].index)


def age_parity():
    """Eurostat abortions by age and parity, dropping country-years whose age cells
    don't add up to the all-ages share (Germany 2019 has only ~60% in the age cells)."""
    e = eurostat_parity()
    bad = bad_age_years(e)
    e = e[[(c, y) not in bad for c, y in zip(e.country, e.year)]]
    return pd.concat([e, ew_age_parity()], ignore_index=True)


def ew_age_parity():
    """England & Wales, DHSC Table 2 by age group and parity, 2013-2023 (ONS/scripts/dhsc_parity_by_age.py)."""
    d = pd.read_csv(_ROOT / "ONS" / "outputs" / "dhsc_parity_by_age.csv")
    d = d[d.age != "All ages"].pivot_table(index=["year", "age"], columns="parity", values="abortions")
    d = d.reset_index().rename(columns={"0": "none"})
    d["known"] = d["none"] + d["1+"]
    d["share_with_child"] = 100 * d["1+"] / d.known
    return d.drop(columns="1+").assign(country="England & Wales", unknown_share=0.0)


def eurostat_births_by_order():
    d = pd.read_csv(DATA / "demo_fordagec.csv")
    d = d[d.geo.isin(NAMES) & d.age.isin(list(EUROSTAT_AGE) + ["TOTAL"])]
    d["age"] = d.age.map(lambda a: "All ages" if a == "TOTAL" else EUROSTAT_AGE[a])
    p = d.pivot_table(index=["geo", "TIME_PERIOD", "age"], columns="ord_brth", values="OBS_VALUE",
                      aggfunc="sum")
    known = p[["1", "2", "3", "GE4"]].sum(axis=1, min_count=4)
    total = known + (p["UNK"].fillna(0) if "UNK" in p else 0)
    out = pd.DataFrame({"first": p["1"] * total / known, "later": (known - p["1"]) * total / known})
    out = out.dropna().reset_index().rename(columns={"TIME_PERIOD": "year"})
    out["country"] = out.geo.map(NAMES)
    return out.drop(columns="geo")


def hfd_births_by_order(code, groups=None):
    """HFD births by order; all ages, or grouped by age with groups = [(label, lo, hi)]."""
    import re as _re
    rows = []
    with open(HFD_BO, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) == 9 and p[0] == code and p[1].isdigit():
                age = int(_re.sub(r"\D", "", p[2]))
                g = "All ages" if groups is None else next((l for l, lo, hi in groups if lo <= age <= hi), None)
                rows.append((int(p[1]), g, float(p[4]), float(p[3]) - float(p[4])))
    d = pd.DataFrame(rows, columns=["year", "age", "first", "later"])
    return d.dropna().groupby(["year", "age"], as_index=False).sum()


def order_ratios():
    """Abortions to women with no children per 100 first births, and abortions to
    mothers per 100 second-or-later births, by country, year and age."""
    import abortion_by_age_national as nat
    e = age_parity()
    scale = 1 / (1 - e.unknown_share)  # spread unknown parity in proportion
    ab = pd.DataFrame({"country": e.country, "year": e.year, "age": e.age,
                       "ab_none": e["none"] * scale, "ab_mother": (e.known - e["none"]) * scale})
    ab = ab[~((ab.country == "Germany") & (ab.year >= 2021))]
    # England & Wales: DHSC parity share x residents' abortions; HFD births by order.
    tot = nat.ew.abortions_total()
    rows = [("England & Wales", y, "All ages", tot[y] * (1 - v / 100), tot[y] * v / 100)
            for y, v in EW.items() if y in tot]
    rows += [("Germany", y, "All ages", n0, t - n0) for y, (n0, t) in DE.items()]
    s = pd.read_csv(_ROOT / "ONS" / "data" / "scotland" / "parity_2022.csv")
    s = s[s.HBR != "RA2704"]
    s["n"] = pd.to_numeric(s.NumberofTerminations, errors="coerce")
    for y, g in s.groupby("YearofTermination"):
        k = g[g.Parity != "Other"].groupby("Parity").n.sum()
        rows.append(("Scotland", int(y), "All ages", k["0"], k.sum() - k["0"]))
    ab = pd.concat([ab, pd.DataFrame(rows, columns=ab.columns)], ignore_index=True)

    b = pd.concat([eurostat_births_by_order(),
                   hfd_births_by_order("GBRTENW").assign(country="England & Wales"),
                   hfd_births_by_order("GBRTENW", [("Under 20", 0, 19), ("20–34", 20, 34), ("35+", 35, 99)])
                   .assign(country="England & Wales"),
                   hfd_births_by_order("GBR_SCO").assign(country="Scotland")], ignore_index=True)
    d = ab.merge(b, on=["country", "year", "age"])
    d["first_pregnancies"] = 100 * d.ab_none / d["first"]
    d["later_pregnancies"] = 100 * d.ab_mother / d.later
    return d[~d.country.isin(["Serbia", "Albania", "Croatia"])]


def _grid(countries, cols):
    rows = -(-len(countries) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=countries,
                        horizontal_spacing=0.05, vertical_spacing=0.3 / rows * 1.4)
    return fig, rows


def _finish(fig, rows, title, xr, dtick):
    fig.update_xaxes(range=xr, dtick=dtick, tickfont=dict(size=9))
    fig.update_yaxes(rangemode="tozero", tickfont=dict(size=9))
    fig.update_annotations(font_size=12)
    fig.update_layout(template="plotly_white", height=190 * rows + 120,
                      title=dict(text=title, y=0.995, yanchor="top"),
                      legend=dict(orientation="h", x=0, y=1.0 + 45 / (190 * rows), yanchor="bottom"),
                      margin=dict(t=120, l=45, r=15, b=30), hovermode="closest")
    return fig


def plot_order_all_ages(d, cols=4):
    d = d[(d.age == "All ages") & (d.year >= 2000)]
    n = d.groupby("country").year.nunique()
    countries = sorted(n[n >= 3].index)
    fig, rows = _grid(countries, cols)
    styles = {"first_pregnancies": ("First pregnancies", "#d62728"),
              "later_pregnancies": ("Later pregnancies", "#1f77b4")}
    for i, c in enumerate(countries):
        x = d[d.country == c].sort_values("year")
        for col, (name, color) in styles.items():
            fig.add_trace(go.Scatter(
                x=x.year, y=x[col], mode="lines+markers", marker=dict(size=3), name=name,
                legendgroup=name, showlegend=(i == 0), line=dict(color=color, width=1.8),
                hovertemplate=c + " " + name.lower() + " %{x}: %{y:.0f} per 100 births<extra></extra>"),
                row=i // cols + 1, col=i % cols + 1)
    return _finish(fig, rows, "Abortions per 100 births of the same order, all ages", [1999.5, 2025.5], 10)


def plot_by_age_lines(d, col, title, unit, cols=4, fmt=".0f"):
    """Small chart per country, a line per age group, for one column of d (Eurostat countries)."""
    d = d[(d.age != "All ages") & (d.year >= 2007)]
    n = d.groupby("country").year.nunique()
    countries = sorted(n[n >= 3].index)
    fig, rows = _grid(countries, cols)
    shown = set()
    for i, c in enumerate(countries):
        x = d[d.country == c]
        for a in AGES_X:
            s = x[x.age == a].sort_values("year")
            if s.empty:
                continue
            fig.add_trace(go.Scatter(
                x=s.year, y=s[col], mode="lines", name=a, legendgroup=a,
                showlegend=a not in shown, line=dict(color=COLORS_X[a], width=1.8),
                hovertemplate=c + " " + a + " %{x}: %{y:" + fmt + "}" + unit + "<extra></extra>"),
                row=i // cols + 1, col=i % cols + 1)
            shown.add(a)
    return _finish(fig, rows, title, [2006.5, 2024.5], 5)


def plot_order_first_by_age(d):
    return plot_by_age_lines(d, "first_pregnancies",
                             "Abortions to women with no children per 100 first births, by age",
                             " per 100 first births")


def plot_order_later_by_age(d):
    return plot_by_age_lines(d, "later_pregnancies",
                             "Abortions to mothers per 100 second-or-later births, by age",
                             " per 100 later births")


def plot_abs_by_age(cols=4):
    """Abortions by age, with buttons to switch between women with no children and mothers."""
    e = age_parity()
    e = e[(e.age != "All ages") & (e.year >= 2007)]
    scale = 1 / (1 - e.unknown_share)
    e = e.assign(ab_none=e["none"] * scale, ab_mother=(e.known - e["none"]) * scale)
    e = e[~e.country.isin(["Serbia", "Albania", "Croatia"])]
    n = e.groupby("country").year.nunique()
    countries = sorted(n[n >= 3].index)
    fig, rows = _grid(countries, cols)
    groups = {"ab_none": "No children", "ab_mother": "Already a mother"}
    tags, shown = [], set()
    for col, label in groups.items():
        for i, c in enumerate(countries):
            x = e[e.country == c]
            for a in AGES_X:
                s = x[x.age == a].sort_values("year")
                if s.empty:
                    continue
                fig.add_trace(go.Scatter(
                    x=s.year, y=s[col], mode="lines", name=a, legendgroup=a,
                    showlegend=(col, a) not in shown, visible=(col == "ab_none"),
                    line=dict(color=COLORS_X[a], width=1.8),
                    hovertemplate=c + " " + a + " (" + label.lower() + ") %{x}: %{y:,.0f}<extra></extra>"),
                    row=i // cols + 1, col=i % cols + 1)
                tags.append(col)
                shown.add((col, a))
    fig = _finish(fig, rows, "Abortions by age: women with no children", [2006.5, 2024.5], 5)
    fig.update_yaxes(tickformat="~s")
    buttons = [dict(label=label, method="update",
                    args=[{"visible": [t == col for t in tags]},
                          {"title.text": "Abortions by age: " + label.lower().replace("already a mother", "mothers")
                           .replace("no children", "women with no children")}])
               for col, label in groups.items()]
    fig.update_layout(updatemenus=[dict(type="buttons", direction="right", x=1.0, xanchor="right",
                                        y=1.0 + 45 / (190 * rows), yanchor="bottom", active=0,
                                        buttons=buttons)])
    return fig


def abs_counts():
    """Abortions to women with no children and to mothers, all ages (unknown parity spread)."""
    import abortion_by_age_national as nat
    e = eurostat_parity()
    e = e[(e.age == "All ages") & ~((e.country == "Germany") & (e.year >= 2021))]
    scale = 1 / (1 - e.unknown_share)
    d = pd.DataFrame({"country": e.country, "year": e.year,
                      "ab_none": e["none"] * scale, "ab_mother": (e.known - e["none"]) * scale})
    tot = nat.ew.abortions_total()
    rows = [("England & Wales", y, tot[y] * (1 - v / 100), tot[y] * v / 100)
            for y, v in EW.items() if y in tot]
    rows += [("Germany", y, n0, t - n0) for y, (n0, t) in DE.items()]
    rows += [("Netherlands", y, nat.NL_RESIDENT[y] * v / 100, nat.NL_RESIDENT[y] * (1 - v / 100))
             for y, v in NL.items()]
    s = pd.read_csv(_ROOT / "ONS" / "data" / "scotland" / "parity_2022.csv")
    s = s[s.HBR != "RA2704"]
    s["n"] = pd.to_numeric(s.NumberofTerminations, errors="coerce")
    for y, g in s.groupby("YearofTermination"):
        k = g[g.Parity != "Other"].groupby("Parity").n.sum()
        rows.append(("Scotland", int(y), k["0"], k.sum() - k["0"]))
    d = pd.concat([d, pd.DataFrame(rows, columns=d.columns)], ignore_index=True)
    return d[~d.country.isin(["Serbia", "Albania", "Croatia"])].sort_values(["country", "year"])


def plot_abs(d, cols=4):
    d = d[d.year >= 2000]
    n = d.groupby("country").year.nunique()
    countries = sorted(n[n >= 3].index)
    fig, rows = _grid(countries, cols)
    styles = {"ab_none": ("No children", "#d62728"), "ab_mother": ("Already a mother", "#1f77b4")}
    for i, c in enumerate(countries):
        x = d[d.country == c]
        for col, (name, color) in styles.items():
            fig.add_trace(go.Scatter(
                x=x.year, y=x[col], mode="lines+markers", marker=dict(size=3), name=name,
                legendgroup=name, showlegend=(i == 0), line=dict(color=color, width=1.8),
                hovertemplate=c + " " + name.lower() + " %{x}: %{y:,.0f}<extra></extra>"),
                row=i // cols + 1, col=i % cols + 1)
    fig = _finish(fig, rows, "Abortions to women with no children and to mothers, all ages",
                  [1999.5, 2025.5], 10)
    fig.update_yaxes(tickformat="~s")
    return fig


# --- Abortions per 100 births, by parity step ----------------------------------
# No children vs first births, one child vs second births, two or more vs third+ births.
STEPS = {"1st": ("No children → 1st birth", "#d62728"),
         "2nd": ("One child → 2nd birth", "#ff7f0e"),
         "3rd+": ("Two or more → 3rd+ birth", "#1f77b4")}
DE_PARITY = {  # Destatis: none, 1, 2, 3, 4, 5+ previous live births
    2021: (38686, 20542, 22254, 8772, 2896, 1446), 2022: (43828, 21785, 24009, 9604, 3043, 1658),
    2023: (45127, 21993, 23851, 9932, 3414, 1901), 2024: (45440, 21905, 24015, 9735, 3445, 1915),
}


def parity_step_ratios():
    # Abortions by parity step (unknown parity spread in proportion)
    d = pd.read_csv(DATA / "demo_fabortord.csv")
    d = d[d.geo.isin(NAMES) & d.age.isin(list(EUROSTAT_AGE) + ["TOTAL"])]
    d["age"] = d.age.map(lambda a: "All ages" if a == "TOTAL" else EUROSTAT_AGE[a])
    p = d.pivot_table(index=["geo", "TIME_PERIOD", "age"], columns="ord_brth", values="OBS_VALUE",
                      aggfunc="sum")
    hi = [c for c in ["2", "3", "4", "5", "GE6"] if c in p]
    known = p[["0", "1"] + hi].sum(axis=1, min_count=3)
    unk = p["UNK"].fillna(0) if "UNK" in p else 0
    ok = (unk / (known + unk) < 0.15) & p["0"].notna() & p["1"].notna()
    sc = (known + unk) / known
    ab = pd.DataFrame({"1st": p["0"] * sc, "2nd": p["1"] * sc, "3rd+": p[hi].sum(axis=1) * sc})[ok]
    ab = ab.reset_index().rename(columns={"TIME_PERIOD": "year"})
    ab["country"] = ab.geo.map(NAMES)
    ab = ab.drop(columns="geo")
    ab = ab[~((ab.country == "Italy") & (ab.year == 2012))]
    bad = bad_age_years()
    ab = ab[[a == "All ages" or (c, y) not in bad for c, y, a in zip(ab.country, ab.year, ab.age)]]

    # Births by order
    b = pd.read_csv(DATA / "demo_fordagec.csv")
    b = b[b.geo.isin(NAMES) & b.age.isin(list(EUROSTAT_AGE) + ["TOTAL"])]
    b["age"] = b.age.map(lambda a: "All ages" if a == "TOTAL" else EUROSTAT_AGE[a])
    q = b.pivot_table(index=["geo", "TIME_PERIOD", "age"], columns="ord_brth", values="OBS_VALUE",
                      aggfunc="sum")
    kn = q[["1", "2", "3", "GE4"]].sum(axis=1, min_count=4)
    s2 = (kn + (q["UNK"].fillna(0) if "UNK" in q else 0)) / kn
    br = pd.DataFrame({"b1": q["1"] * s2, "b2": q["2"] * s2, "b3": (q["3"] + q["GE4"]) * s2}).dropna()
    br = br.reset_index().rename(columns={"TIME_PERIOD": "year"})
    br["country"] = br.geo.map(NAMES)
    br = br.drop(columns="geo")

    # Germany 2021+ (all ages) from Destatis; Scotland from PHS + HFD
    ab = ab[~((ab.country == "Germany") & (ab.year >= 2021))]
    extra = [("Germany", y, "All ages", v[0], v[1], sum(v[2:])) for y, v in DE_PARITY.items()]
    s = pd.read_csv(_ROOT / "ONS" / "data" / "scotland" / "parity_2022.csv")
    s = s[s.HBR != "RA2704"]
    s["n"] = pd.to_numeric(s.NumberofTerminations, errors="coerce")
    for y, g in s.groupby("YearofTermination"):
        k = g[g.Parity != "Other"].groupby("Parity").n.sum()
        extra.append(("Scotland", int(y), "All ages", k["0"], k["1"], k.sum() - k["0"] - k["1"]))
    ab = pd.concat([ab, pd.DataFrame(extra, columns=["country", "year", "age", "1st", "2nd", "3rd+"])],
                   ignore_index=True)
    rows = []
    with open(HFD_BO, encoding="utf-8") as f:
        for line in f:
            t = line.split()
            if len(t) == 9 and t[0] == "GBR_SCO" and t[1].isdigit():
                rows.append((int(t[1]), float(t[4]), float(t[5]), float(t[6]) + float(t[7]) + float(t[8])))
    sb = pd.DataFrame(rows, columns=["year", "b1", "b2", "b3"]).groupby("year", as_index=False).sum()
    br = pd.concat([br, sb.assign(country="Scotland", age="All ages")], ignore_index=True)

    m = ab.merge(br, on=["country", "year", "age"])
    out = pd.DataFrame({"country": m.country, "year": m.year, "age": m.age,
                        "1st": 100 * m["1st"] / m.b1, "2nd": 100 * m["2nd"] / m.b2,
                        "3rd+": 100 * m["3rd+"] / m.b3})
    return out[~out.country.isin(["Serbia", "Albania", "Croatia"])]


def plot_order_second_by_age(d):
    return plot_by_age_lines(d, "2nd", "Abortions to women with one child per 100 second births, by age",
                             " per 100 second births")


if __name__ == "__main__":
    d = load()
    write_html(plot_trend(d), "abortion_parity_trend.html")
    fig, e = plot_by_age()
    write_html(fig, "abortion_parity_by_age.html")
    out = pd.concat([d.assign(age="All ages"), e[["country", "year", "age", "share_with_child", "known"]]])
    out["share_with_child"] = out.share_with_child.round(1)
    out.to_csv(OUTDIR / "abortion_parity.csv", index=False)
    print(d.pivot(index="country", columns="year", values="share_with_child").round(0)
          .loc[:, lambda t: [c for c in t.columns if c in (2004, 2010, 2013, 2016, 2019, 2021, 2023, 2024, 2025)]]
          .to_string())
    a = e[e.age.isin(["25–29", "30–34"])].pivot_table(index=["country", "age"], columns="year",
                                                    values="share_with_child").round(0)
    print(a[[c for c in a.columns if c in (2008, 2013, 2019, 2022, 2024)]].to_string())

    o = order_ratios()
    write_html(plot_order_all_ages(o), "abortion_order_ratio.html")
    write_html(plot_order_first_by_age(o), "abortion_order_ratio_first_by_age.html")
    write_html(plot_order_later_by_age(o), "abortion_order_ratio_later_by_age.html")
    write_html(plot_abs_by_age(), "abortion_parity_abs_by_age.html")
    lt = o[o.age.isin(["20–24", "25–29", "30–34", "35+"])].pivot_table(
        index=["country", "age"], columns="year", values="later_pregnancies").round(0)
    print("later by age")
    print(lt[[c for c in lt.columns if c in (2008, 2013, 2019, 2022, 2024)]].to_string())
    ag = age_parity()
    ag = ag[ag.age != "All ages"].assign(ab_none=lambda x: x["none"] / (1 - x.unknown_share),
                                         ab_mother=lambda x: (x.known - x["none"]) / (1 - x.unknown_share))
    for col in ("ab_none", "ab_mother"):
        q = ag[ag.country.isin(["Spain", "Italy", "Germany", "Finland", "Hungary", "Czechia", "Portugal"])]
        q = q.pivot_table(index=["country", "age"], columns="year", values=col).round(-1)
        print(col)
        print(q[[c for c in q.columns if c in (2008, 2013, 2019, 2022, 2024)]].to_string())
    o.round(1).to_csv(OUTDIR / "abortion_order_ratio.csv", index=False)
    t = o[o.age == "All ages"]
    for col in ("first_pregnancies", "later_pregnancies"):
        q = t.pivot_table(index="country", columns="year", values=col).round(0)
        print(col)
        print(q[[y for y in (2004, 2008, 2013, 2019, 2021, 2022, 2023, 2024) if y in q.columns]].to_string())
    f = o[o.age.isin(["20–24", "25–29", "30–34"])].pivot_table(
        index=["country", "age"], columns="year", values="first_pregnancies").round(0)
    print(f[[c for c in f.columns if c in (2008, 2013, 2019, 2022, 2024)]].to_string())
    a = abs_counts()
    write_html(plot_abs(a), "abortion_parity_abs.html")
    a.round(0).to_csv(OUTDIR / "abortion_parity_abs.csv", index=False)
    for col in ("ab_none", "ab_mother"):
        q = a.pivot_table(index="country", columns="year", values=col).round(-2)
        print(col)
        print(q[[y for y in (2004, 2008, 2013, 2019, 2021, 2022, 2023, 2024) if y in q.columns]].to_string())
    st = parity_step_ratios()
    write_html(plot_order_second_by_age(st), "abortion_order_ratio_second_by_age.html")
    st.round(1).to_csv(OUTDIR / "abortion_parity_step_ratio.csv", index=False)
    q = st[st.age.isin(["20–24", "25–29", "30–34", "35+"])].pivot_table(
        index=["country", "age"], columns="year", values="2nd").round(0)
    print("second by age")
    print(q[[c for c in q.columns if c in (2008, 2013, 2019, 2022, 2024)]].to_string())
    q = st[st.age == "All ages"].pivot_table(index="country", columns="year", values="2nd").round(0)
    print(q[[c for c in q.columns if c in (2008, 2013, 2019, 2021, 2022, 2024)]].to_string())
