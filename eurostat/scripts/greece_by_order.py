"""Greece's period TFR by birth order, 1960-2024: Human Fertility Collection to 1991, Eurostat from 1992.

HFD has no Greek series. Eurostat demo_fordagec gives live births by mother's age (single years,
age reached in the year) and birth order 1, 2, 3, 4+ from 1992 (earlier years have order totals
only); births of unknown age are spread over ages pro rata within each order. demo_pjan gives women
by single age on 1 January. Rates are births over women exposed (mean of 1 January this year and
next; the last year uses 1 January only), ages 15-49, with births under 15 counted at 15 and 50+ at
49. Order-specific rates per woman, as HFD's asfrRRbo, not conditional on parity. Before 1992 the
series is the Human Fertility Collection's European Demographic Observatory (ODE) estimates
(1960-2008, age in completed years); where both exist they are compared.

First- and second-birth rates per woman at risk (cond_asfr_grc.csv) come from cumulating each
cohort's order-specific rates from 1960, as for Brazil (NSO/scripts/births_by_order_rates.cond_asfr):
years before 1960 take 1960's rates, and backfill_share1/2 say how much of a cohort's births that is.

Inputs (eurostat/data/greece_by_order/, fetched on first run): demo_fordagec and demo_pjan for EL;
HFC GRC_ASFRstand_BO.txt.
Outputs (eurostat/outputs/): grc_tfr_by_order.csv, grc_tfr_by_order_vs_hfc.csv, grc_tfr_by_order.html,
grc_asfr_by_order.csv (year, age, f1, f2, f3p) and cond_asfr_grc.csv.
"""

import sys
import urllib.request

import pandas as pd
import plotly.graph_objects as go

from common.paths import REPO, data_dir, outputs_dir
from common.plotting import write_html

CACHE = data_dir("eurostat") / "greece_by_order"
OUT = outputs_dir("eurostat")
API = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
URLS = {
    "demo_fordagec_EL.csv": API + "demo_fordagec/A.NR...EL?format=SDMX-CSV",
    "demo_pjan_EL.csv": API + "demo_pjan/A.NR..F.EL?format=SDMX-CSV",
    "GRC_ASFRstand_BO.txt": "https://www.fertilitydata.org/File/GetFile/Country/GRC%5CGRC_ASFRstand_BO.txt",
}
AGES = range(15, 50)
ORDERS = {"1": "TFR1", "2": "TFR2", "3": "TFR3", "GE4": "TFR4P"}
SHOWN = {"TFR1": "First", "TFR2": "Second", "TFR3P": "Third+"}  # as the Korea, Uruguay and Mexico charts
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]
SPLICE = 1992  # first year from Eurostat


def fetch(name):
    path = CACHE / name
    if not path.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(URLS[name], headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    return path


def rates():
    """Eurostat rates by single age and order, 1992 onward (earlier years have order totals only)."""
    b = pd.read_csv(fetch("demo_fordagec_EL.csv"))
    b = b[b.ord_brth.isin(ORDERS)].assign(year=b.TIME_PERIOD.astype(int))
    by_age = b[b.age.str.fullmatch(r"Y\d+") | b.age.isin(["Y10-14", "Y_GE50"])]
    by_age = by_age.assign(a=by_age.age.map({"Y10-14": 15, "Y_GE50": 49}).fillna(by_age.age.str[1:]).astype(int)
                           .clip(AGES[0], AGES[-1]))
    births = by_age.groupby(["year", "a", "ord_brth"]).OBS_VALUE.sum().unstack("ord_brth")
    # Births of unknown age: spread over ages in proportion, per order (the TOTAL-age row includes them).
    total = b[b.age == "TOTAL"].pivot(index="year", columns="ord_brth", values="OBS_VALUE")
    scale = (total / births.groupby("year").sum()).reindex(births.index, level="year")
    births = births * scale
    w = pd.read_csv(fetch("demo_pjan_EL.csv"))
    w = w[w.age.str.fullmatch(r"Y\d+")].assign(a=lambda f: f.age.str[1:].astype(int), year=lambda f: f.TIME_PERIOD.astype(int))
    w = w[w.a.isin(AGES)].set_index(["year", "a"]).OBS_VALUE
    nxt = w.rename(index=lambda y: y - 1, level="year")
    exposure = pd.concat([w, nxt], axis=1).mean(axis=1)
    asfr = births.div(exposure, axis=0).dropna(how="all")
    t = asfr.groupby("year").sum(min_count=len(AGES)).rename(columns=ORDERS).dropna()
    t["TFR3P"] = t.TFR3 + t.TFR4P
    t["TFR"] = t[list(ORDERS.values())].sum(axis=1)
    f1 = asfr["1"].unstack("a")
    t["MAB1"] = (f1 * (f1.columns.to_numpy() + 0.5)).sum(axis=1) / f1.sum(axis=1)
    long = pd.DataFrame({"f1": asfr["1"], "f2": asfr["2"], "f3p": asfr["3"] + asfr["GE4"]})
    long = long.rename_axis(["year", "age"]).reset_index()
    return t.reset_index().assign(source="Eurostat"), long[long.year.isin(t.index)]


def hfc():
    d = pd.read_csv(fetch("GRC_ASFRstand_BO.txt"), skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    d = d[(d.Year1 == d.Year2) & (d.AgeDef.str.strip() == "ACY") & (d.AgeInt == 1)]
    t = d.groupby("Year1")[["ASFR", "ASFR1", "ASFR2", "ASFR3P"]].sum()
    t = t.set_axis(["TFR", "TFR1", "TFR2", "TFR3P"], axis=1).rename_axis("year")
    t["MAB1"] = d.assign(w=d.ASFR1 * (d.Age + 0.5)).groupby("Year1").w.sum() / t.TFR1
    long = d.rename(columns={"Year1": "year", "Age": "age", "ASFR1": "f1", "ASFR2": "f2", "ASFR3P": "f3p"})
    return t, long[["year", "age", "f1", "f2", "f3p"]]


def cond(asfr):
    """First- and second-birth rates per woman at risk, from cohort-cumulated order-specific rates."""
    sys.path.insert(0, str(REPO / "NSO" / "scripts"))
    from births_by_order_rates import AGES as ALL_AGES, cond_asfr
    # cond_asfr cumulates from its first age (12): no births are recorded under 15 here.
    pad = pd.MultiIndex.from_product([asfr.year.unique(), ALL_AGES], names=["year", "age"])
    full = asfr.set_index(["year", "age"]).reindex(pad, fill_value=0.0).reset_index()
    return cond_asfr(full)


def chart(t, path):
    fig = go.Figure()
    fig.add_vline(x=SPLICE - 0.5, line=dict(color="#888", width=1, dash="dot"))
    fig.add_annotation(x=SPLICE - 0.5, y=1.0, yref="paper", text="HFC (ODE) | Eurostat", showarrow=False,
                       yanchor="bottom", font=dict(size=11, color="#666"))
    for (col, label), c in zip(SHOWN.items(), COLORS):
        fig.add_trace(go.Scatter(x=t.year, y=t[col], mode="lines", name=label, line=dict(color=c, width=2),
                                 customdata=t.source,
                                 hovertemplate=f"{label}: %{{y:.2f}} (%{{customdata}})<extra></extra>"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title=f"Greece: period TFR by birth order, {t.year.min()}–{t.year.max()}",
                      yaxis=dict(title="Births per woman", rangemode="tozero"), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.15))
    write_html(fig, path)


if __name__ == "__main__":
    e, e_asfr = rates()
    h, h_asfr = hfc()
    cmp = e.set_index("year")[["TFR", "TFR1", "TFR2", "TFR3P"]].join(h, rsuffix="_hfc", how="inner")
    for c in ("TFR", "TFR1", "TFR2", "TFR3P"):
        cmp[f"{c}_gap"] = cmp[c] - cmp[f"{c}_hfc"]
    cmp.round(4).to_csv(OUT / "grc_tfr_by_order_vs_hfc.csv")
    t = pd.concat([h[h.index < SPLICE].reset_index().assign(source="HFC (ODE)"), e])
    t = t[["year", "TFR", "TFR1", "TFR2", "TFR3P", "MAB1", "source"]]
    t.round(4).to_csv(OUT / "grc_tfr_by_order.csv", index=False)
    asfr = pd.concat([h_asfr[h_asfr.year < SPLICE], e_asfr]).sort_values(["year", "age"])
    asfr.round(6).to_csv(OUT / "grc_asfr_by_order.csv", index=False)
    cond(asfr).round(6).to_csv(OUT / "cond_asfr_grc.csv", index=False)
    print(t.round(3).to_string(index=False))
    print(cmp.filter(like="_gap").describe().round(3))
    chart(t, OUT / "grc_tfr_by_order.html")
