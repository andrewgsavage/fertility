"""Abortions and live births by mother's age, by country, and abortions per 100 births.

Abortions: Eurostat demo_fabort (legally induced abortions by age of woman),
replaced by national series where they exist (Sweden, Norway, Germany, the
Netherlands; see abortion_by_age_national.py). Births: Eurostat demo_fasec (live
births by mother's age, 2007 onward), with HFD birthsRR filling earlier years.
England & Wales (DHSC + ONS births), Scotland (PHS + NRS births), the US (CDC)
and Japan (MHLW + HFD births) come entirely from abortion_by_age_national.py.

Abortions and births with unknown age are spread across the known age groups in
proportion, so the age groups add up to the reported total.

Inputs (not tracked in git):
  eurostat/data/demo_fabort_age.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_fabort/A.NR..?format=SDMX-CSV
  eurostat/data/demo_fasec.csv       https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_fasec/A.NR...?format=SDMX-CSV
  HFD/data/HFD/birthsRR.txt          Human Fertility Database, all-countries zip
  plus the national files listed in abortion_by_age_national.py

Outputs:
  eurostat/outputs/abortion_by_age.csv   country, year, age, abortions, births, abortions_per_100_births
  eurostat/outputs/abortion_by_age.html  chart with a country dropdown
"""

import pathlib
import re
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parent.parent
DATA = _SCRIPT_DIR.parent / "data"
OUTDIR = _SCRIPT_DIR.parent / "outputs"
HFD_BIRTHS = _ROOT / "HFD" / "data" / "HFD" / "birthsRR.txt"

sys.path.insert(0, str(_SCRIPT_DIR))
import abortion_by_age_national as nat_src  # noqa: E402

NAMES = {
    "AL": "Albania", "AM": "Armenia", "AZ": "Azerbaijan", "BE": "Belgium", "BG": "Bulgaria",
    "BY": "Belarus", "CH": "Switzerland", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark",
    "EE": "Estonia", "EL": "Greece", "ES": "Spain", "FI": "Finland", "FR": "France",
    "GE": "Georgia", "HR": "Croatia", "HU": "Hungary", "IS": "Iceland", "IT": "Italy",
    "LT": "Lithuania", "LV": "Latvia", "MD": "Moldova", "ME": "Montenegro", "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RS": "Serbia", "RU": "Russia",
    "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "UA": "Ukraine",
}
# HFD codes used for births before Eurostat's 2007 start.
HFD = {
    "BE": "BEL", "BG": "BGR", "BY": "BLR", "CH": "CHE", "CZ": "CZE", "DE": "DEUTNP", "DK": "DNK",
    "EE": "EST", "ES": "ESP", "FI": "FIN", "FR": "FRATNP", "HR": "HRV", "HU": "HUN", "IS": "ISL",
    "IT": "ITA", "LT": "LTU", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT", "RU": "RUS", "SE": "SWE",
    "SI": "SVN", "SK": "SVK", "UA": "UKR",
}
AGES = ["Under 20", "20–24", "25–29", "30–34", "35+"]
EUROSTAT_AGE = {
    "Y_LT15": "Under 20", "Y10-14": "Under 20", "Y15-19": "Under 20", "Y20-24": "20–24",
    "Y25-29": "25–29", "Y30-34": "30–34", "Y35-39": "35+", "Y40-44": "35+", "Y45-49": "35+",
    "Y_GE50": "35+",
}


def age_group(a):
    for g, lo in zip(reversed(AGES), [35, 30, 25, 20, 0]):
        if a >= lo:
            return g


def eurostat(path, value, sex=None):
    x = pd.read_csv(DATA / path)
    if sex:
        x = x[x.sex == sex]
    x = x[x.geo.isin(NAMES)].rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": value})
    known = x[x.age.isin(EUROSTAT_AGE)].assign(age=lambda d: d.age.map(EUROSTAT_AGE))
    known = known.groupby(["geo", "year", "age"], as_index=False)[value].sum()
    total = x[x.age == "TOTAL"].set_index(["geo", "year"])[value]
    # Spread unknown age in proportion: scale known groups up to the total.
    s = known.groupby(["geo", "year"])[value].transform("sum")
    t = known.set_index(["geo", "year"]).index.map(total)
    known["unknown_share"] = 1 - s / t
    known[value] = known[value] * (t / s)
    return known


def hfd_births(codes=None):
    codes = set(codes or HFD.values())
    rows = []
    with open(HFD_BIRTHS, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) == 4 and p[0] in codes and p[1].isdigit():
                rows.append((p[0], int(p[1]), age_group(int(re.sub(r"\D", "", p[2]))), float(p[3])))
    d = pd.DataFrame(rows, columns=["hfd", "year", "age", "births"])
    d = d.groupby(["hfd", "year", "age"], as_index=False).births.sum()
    d["geo"] = d.hfd.map({v: k for k, v in HFD.items()})
    return d.drop(columns="hfd")


def load():
    ab = eurostat("demo_fabort_age.csv", "abortions")
    ab = ab.rename(columns={"unknown_share": "abortions_unknown_age"})
    ab["country"] = ab.geo.map(NAMES)
    # National series replace Eurostat's for the country-years they cover.
    nat = nat_src.national_abortions()
    nat["geo"] = nat.country.map({v: k for k, v in NAMES.items()})
    covered = set(zip(nat.country, nat.year))
    ab = ab[[(c, y) not in covered for c, y in zip(ab.country, ab.year)]]
    ab = pd.concat([ab, nat], ignore_index=True)

    bE = eurostat("demo_fasec.csv", "births", sex="T").drop(columns="unknown_share")
    bH = hfd_births()
    bH = bH.merge(bE[["geo", "year"]].drop_duplicates(), how="left", indicator=True)
    bH = bH[bH._merge == "left_only"].drop(columns="_merge")
    b = pd.concat([bE, bH])
    d = ab.merge(b, on=["geo", "year", "age"])

    cols = ["country", "year", "age", "abortions", "births", "abortions_unknown_age"]
    # England & Wales (DHSC + ONS births) and Scotland (PHS + NRS births).
    e = nat_src.england_wales_abortions().merge(nat_src.england_wales_births(), on=["country", "year", "age"])
    s = nat_src.scotland_abortions().merge(nat_src.scotland_births(), on=["country", "year", "age"])

    # United States (CDC, 43 reporting areas) and Japan (MHLW + HFD births).
    u = pd.DataFrame(nat_src.us(), columns=["year", "age", "abortions", "births"])
    u["country"] = "United States (43 areas)"
    jb = hfd_births(["JPN"]).set_index(["year", "age"]).births
    j = pd.DataFrame([(y, g, n, jb.get((y, g))) for (y, g), n in nat_src.japan().items()],
                     columns=["year", "age", "abortions", "births"]).dropna()
    j["country"] = "Japan"
    x = pd.concat([u, j]).assign(abortions_unknown_age=0.0)

    d = pd.concat([d[cols], e[cols], s[cols], x[cols]], ignore_index=True)
    d = d[d.births > 0]
    # Keep country-years with all five age groups and under 10% of abortions of
    # unknown age, so the proportional spread of unknowns stays small.
    n = d.groupby(["country", "year"]).age.transform("count")
    d = d[(n == len(AGES)) & (d.abortions_unknown_age < 0.10)]
    d["abortions_per_100_births"] = 100 * d.abortions / d.births
    return d.sort_values(["country", "year", "age"])


COLORS = dict(zip(AGES, ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"]))


def plot(d):
    countries = sorted(d.country.unique())
    first = "England & Wales"
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        subplot_titles=("Abortions", "Live births", "Abortions per 100 live births"))
    traces = []
    for c in countries:
        x = d[d.country == c]
        for row, col, fmt in [(1, "abortions", ",.0f"), (2, "births", ",.0f"),
                              (3, "abortions_per_100_births", ".1f")]:
            for a in AGES:
                s = x[x.age == a].sort_values("year")
                fig.add_trace(go.Scatter(
                    x=s.year, y=s[col], mode="lines+markers", marker=dict(size=4),
                    name=a, legendgroup=a, showlegend=(row == 1),
                    line=dict(color=COLORS[a]), visible=(c == first),
                    hovertemplate=f"{c} {a} %{{x}}: %{{y:{fmt}}}<extra></extra>"), row=row, col=1)
                traces.append(c)
    buttons = [dict(label=c, method="update",
                    args=[{"visible": [t == c for t in traces]}, {"title.text": f"{c}: abortions and births by age"}])
               for c in countries]
    fig.update_layout(
        template="plotly_white", title=f"{first}: abortions and births by age",
        updatemenus=[dict(buttons=buttons, active=countries.index(first), x=1.0, xanchor="right",
                          y=1.07, yanchor="bottom")],
        legend=dict(orientation="h", x=0, y=-0.06), margin=dict(t=90, l=60, r=20, b=40),
        hovermode="closest")
    for r in (1, 2, 3):
        fig.update_yaxes(rangemode="tozero", row=r, col=1)
    return fig


def plot_small_multiples(d, start=2005, end=2025, cols=4):
    """One small chart per country: abortions per 100 births by age, start-end."""
    d = d[d.year.between(start, end)]
    n = d.groupby("country").year.nunique()
    countries = sorted(n[n >= 3].index)
    rows = -(-len(countries) // cols)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=countries,
                        horizontal_spacing=0.05, vertical_spacing=0.25 / rows * 1.6)
    for i, c in enumerate(countries):
        r, k = i // cols + 1, i % cols + 1
        x = d[d.country == c]
        for a in AGES:
            s = x[x.age == a].sort_values("year")
            fig.add_trace(go.Scatter(
                x=s.year, y=s.abortions_per_100_births, mode="lines", name=a, legendgroup=a,
                showlegend=(i == 0), line=dict(color=COLORS[a], width=1.8),
                hovertemplate=f"{c} {a} %{{x}}: %{{y:.0f}}%<extra></extra>"), row=r, col=k)
    fig.update_xaxes(range=[start, end], dtick=10, tickfont=dict(size=9))
    fig.update_yaxes(rangemode="tozero", ticksuffix="%", tickfont=dict(size=9))
    fig.update_annotations(font_size=12)
    # Buttons: each chart on its own y scale, or all on one shared scale.
    ynames = [f"yaxis{i + 1 if i else ''}" for i in range(len(countries))]  # skip empty slots
    top = 1.05 * d[d.country.isin(countries)].abortions_per_100_births.max()
    own = {f"{y}.autorange": True for y in ynames}
    shared = {f"{y}.range": [0, top] for y in ynames} | {f"{y}.autorange": False for y in ynames}
    fig.update_layout(
        template="plotly_white", height=170 * rows + 140,
        title=dict(text=f"Abortions per 100 live births, by age, {start}–{end}", y=0.995, yanchor="top"),
        legend=dict(orientation="h", x=0, xanchor="left", y=1.0 + 60 / (170 * rows), yanchor="bottom"),
        updatemenus=[dict(type="buttons", direction="right", x=1.0, xanchor="right",
                          y=1.0 + 60 / (170 * rows), yanchor="bottom", showactive=True, active=0,
                          buttons=[dict(label="Own y-axis", method="relayout", args=[own]),
                                   dict(label="Shared y-axis", method="relayout", args=[shared])])],
        margin=dict(t=110, l=45, r=15, b=30), hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    out = d.copy()
    out[["abortions", "births"]] = out[["abortions", "births"]].round(0).astype(int)
    out["abortions_per_100_births"] = out.abortions_per_100_births.round(1)
    out["abortions_unknown_age"] = (100 * out.abortions_unknown_age).round(1)
    out = out.rename(columns={"abortions_unknown_age": "abortions_unknown_age_pct"})
    out.to_csv(OUTDIR / "abortion_by_age.csv", index=False)
    sys.path.insert(0, str(_SCRIPT_DIR))
    from _common import write_html
    write_html(plot(d), "abortion_by_age.html")
    write_html(plot_small_multiples(d), "abortion_by_age_small_multiples.html")

    latest = d[d.year == d.groupby("country").year.transform("max")]
    p = latest.pivot_table(index=["country", "year"], columns="age",
                           values="abortions_per_100_births")[AGES].round(1)
    tot = latest.groupby(["country", "year"])[["abortions", "births"]].sum()
    p["Abortions"] = tot.abortions.round(-2).astype(int)
    p["Births"] = tot.births.round(-2).astype(int)
    p["All"] = (100 * tot.abortions / tot.births).round(1)
    unk = latest.groupby(["country", "year"]).abortions_unknown_age.first().mul(100).round(1)
    p["Unk%"] = unk
    print(p.to_markdown())
