"""Mauritius's period TFR by birth order, 1972-2024, from the Human Fertility Collection.

HFD has no Mauritian series. HFC holds order-specific rates (orders 1-6+) by 5-year age group from
the Ministry of Health demographic yearbooks (to 2012) and Statistics Mauritius digests, split by
HFC into single ages 15-49 (age in completed years). Years present: 1972, 1983-85, 1990 and
1994-2024. From 2015 the series excludes Agalega and St Brandon (HFC note 28).

The order split breaks in 2005, inside one source table (2005 yearbook, reference MUS_08): TFR1
goes from 0.83 to 0.98 and TFR2 from 0.64 to 0.52 while TFR barely moves. BREAK marks the first
year of the consistent series; earlier years are drawn dotted. Order-specific rates per woman, not
conditional on parity.

First- and second-birth rates per woman at risk (cond_asfr_mus.csv) come from cumulating each
cohort's order-specific rates from BREAK, as for Brazil (NSO/scripts/births_by_order_rates.cond_asfr):
years before BREAK take BREAK's rates, and backfill_share1/2 say how much of a cohort's births that is.

Input: https://www.fertilitydata.org/ MUS_ASFRstand_BO.txt, cached in HFC/data/.
Outputs (HFC/outputs/): mus_tfr_by_order.csv, mus_asfr_by_order.csv, mus_tfr_by_order.html, cond_asfr_mus.csv.
"""

import sys

import pandas as pd
import plotly.graph_objects as go
import requests

from common.paths import REPO, data_dir, outputs_dir
from common.plotting import write_html

URL = "https://www.fertilitydata.org/File/GetFile/Country/MUS%5CMUS_ASFRstand_BO.txt"
RAW = data_dir("HFC") / "MUS_ASFRstand_BO.txt"
OUT = outputs_dir("HFC")
BREAK = 2005  # first year of the consistent order coding
ORDERS = {"ASFR1": "f1", "ASFR2": "f2", "ASFR3": "f3", "ASFR4": "f4", "ASFR5P": "f5p"}
SHOWN = {"TFR1": "First", "TFR2": "Second", "TFR3P": "Third+"}  # as the Korea, Uruguay and Mexico charts
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]


def load():
    """Single-age order-specific rates: year, age, f1, f2, f3, f4, f5p."""
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, timeout=60, headers={"User-Agent": "curl/8.0"})
        r.raise_for_status()
        RAW.write_bytes(r.content)
    d = pd.read_csv(RAW, skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    d = d[(d.Year1 == d.Year2) & (d.AgeDef.str.strip() == "ACY") & (d.AgeInt == 1)]
    if d.duplicated(["Year1", "Age"]).any():
        raise ValueError("repeated HFC years for MUS")
    d = d.rename(columns={"Year1": "year", "Age": "age", **ORDERS})[["year", "age", *ORDERS.values()]]
    return d.fillna({c: 0.0 for c in ORDERS.values()}).sort_values(["year", "age"])


def summary(a):
    g = a.groupby("year")
    t = pd.DataFrame({"TFR1": g.f1.sum(), "TFR2": g.f2.sum(), "TFR3P": g[["f3", "f4", "f5p"]].sum().sum(axis=1)})
    t["TFR"] = t.sum(axis=1)
    t["MAB1"] = a.assign(w=a.f1 * (a.age + 0.5)).groupby("year").w.sum() / t.TFR1
    t["consistent"] = t.index >= BREAK
    return t[["TFR", "TFR1", "TFR2", "TFR3P", "MAB1", "consistent"]].reset_index()


def cond(a):
    """First- and second-birth rates per woman at risk, from cohort-cumulated rates since BREAK."""
    sys.path.insert(0, str(REPO / "NSO" / "scripts"))
    from births_by_order_rates import AGES as ALL_AGES, cond_asfr
    a = a[a.year >= BREAK]
    pad = pd.MultiIndex.from_product([a.year.unique(), ALL_AGES], names=["year", "age"])
    return cond_asfr(a.set_index(["year", "age"]).reindex(pad, fill_value=0.0).reset_index())


def chart(t, path):
    # Gaps between years show as gaps: reindex to every year.
    s = t.set_index("year").reindex(range(t.year.min(), t.year.max() + 1))
    fig = go.Figure()
    for (col, label), c in zip(SHOWN.items(), COLORS):
        fig.add_trace(go.Scatter(x=s.index, y=s[col].where(s.index >= BREAK), mode="lines+markers", name=label,
                                 legendgroup=label, line=dict(color=c, width=2), marker=dict(size=4),
                                 hovertemplate=f"{label}: %{{y:.2f}}<extra></extra>"))
        fig.add_trace(go.Scatter(x=s.index, y=s[col].where(s.index < BREAK), mode="lines+markers", name=label,
                                 legendgroup=label, showlegend=False, line=dict(color=c, width=2, dash="dot"),
                                 marker=dict(size=4), hovertemplate=f"{label}: %{{y:.2f}} (before {BREAK} break)<extra></extra>"))
    fig.add_vline(x=BREAK - 0.5, line=dict(color="#888", width=1, dash="dot"))
    fig.add_annotation(x=BREAK - 0.5, y=1.0, yref="paper", text="order coding changes", showarrow=False,
                       yanchor="bottom", font=dict(size=11, color="#666"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title=f"Mauritius: period TFR by birth order, {t.year.min()}–{t.year.max()}",
                      yaxis=dict(title="Births per woman", rangemode="tozero"), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.15))
    write_html(fig, path)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a = load()
    a.round(6).to_csv(OUT / "mus_asfr_by_order.csv", index=False)
    t = summary(a)
    t.round(4).to_csv(OUT / "mus_tfr_by_order.csv", index=False)
    cond(a).round(6).to_csv(OUT / "cond_asfr_mus.csv", index=False)
    print(t.round(3).to_string(index=False))
    chart(t, OUT / "mus_tfr_by_order.html")


if __name__ == "__main__":
    main()
