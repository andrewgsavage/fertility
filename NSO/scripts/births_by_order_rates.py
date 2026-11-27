"""Period TFR by birth order and mean age at first birth for Mexico and Brazil, from birth
records (births_by_order_download.py) over UN WPP 2024 female population by single age.

Births with mother's age or birth order not stated are spread pro rata: unknown order over the
order mix at the same age, then unknown age over the age pattern of the same order. Ages
10-11 count at 12 and 56+ at 55. Rates are order-specific (births of order i per woman, as
HFD's asfrRRbo), not conditional on parity. Total TFR is compared with WPP's estimate.

Mexico's recent years miss births not yet registered. Each year's rates are raised by the share of
births registered by the same lag among births of BASE_YEARS (registered over 10+ years): a year
seen for 2 registration years after the birth year is about 96% complete. Years needing more
than MAX_COMPLETION are dropped, and completed years are drawn dotted. Brazil's SINASC counts
births by year of birth, so it needs no completion.

Inputs: NSO/intermediate/births_by_order_{mex,bra}.csv, births_by_file_{mex,bra}.csv; UN/data/WPP2024_PopulationBySingleAgeSex
_Medium_{1950-2023,2024-2100}.csv.gz and WPP2024_Demographic_Indicators_Medium.csv.gz
(https://population.un.org/wpp/downloads, CSV files).
Outputs (NSO/outputs/): tfr_by_order_mex_bra.csv, {mex,bra}_tfr_by_order.html,
asfr_by_order_{mex,bra}.csv (rates by age and order) and cond_asfr_{mex,bra}.csv (first- and
second-birth rates per woman at risk, see cond_asfr).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from common.paths import data_dir, intermediate_dir, outputs_dir
from common.plotting import write_html

COUNTRIES = {"mex": ("MEX", "Mexico", 1990), "bra": ("BRA", "Brazil", 2000)}  # 1996-99: previous children blank for 15-47%
AGES = range(12, 56)
ORDERS = {1: "TFR1", 2: "TFR2", 3: "TFR3", 4: "TFR4p"}
SHOWN = {"TFR1": "First", "TFR2": "Second", "TFR3p": "Third+"}  # as the Korea and Uruguay charts
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c"]
WPP = data_dir("UN")
BASE_YEARS = range(2010, 2015)  # birth years whose registration is complete, for the lag pattern
MAX_COMPLETION = 1.10  # drop years with more than 10% of births still to be registered


def completion(code):
    """Factor by year of birth: final births / births in the files so far."""
    f = pd.read_csv(intermediate_dir("NSO") / f"births_by_file_{code}.csv")
    f["lag"] = f.file - f.year
    if (f.lag == 0).all():  # files by year of birth (Brazil)
        return pd.Series(1.0, index=f.year.unique())
    base = f[f.year.isin(BASE_YEARS)].groupby("lag").births.sum()
    seen = base.cumsum() / base.sum()  # share registered within each lag
    last_lag = f.file.max() - f.groupby("year").file.min().index.to_series()
    return last_lag.map(lambda lag: 1 / seen.loc[min(lag, seen.index.max())])


def women(iso3):
    cols = ["ISO3_code", "Time", "AgeGrpStart", "PopFemale"]
    parts = [pd.read_csv(WPP / f"WPP2024_PopulationBySingleAgeSex_Medium_{span}.csv.gz", usecols=cols,
                         dtype={"ISO3_code": str})
             for span in ("1950-2023", "2024-2100")]
    p = pd.concat(parts)
    p = p[p.ISO3_code == iso3]
    return p.set_index(["Time", "AgeGrpStart"]).PopFemale * 1000  # thousands


def wpp_tfr(iso3):
    d = pd.read_csv(WPP / "WPP2024_Demographic_Indicators_Medium.csv.gz",
                    usecols=["ISO3_code", "Time", "TFR"], dtype={"ISO3_code": str})
    return d[d.ISO3_code == iso3].set_index("Time").TFR


def spread(b):
    """Births for one year as an age x order matrix, with not-stated age or order spread pro rata."""
    b = b.assign(age=b.age.where(b.age < 0, b.age.clip(AGES[0], AGES[-1])),
                 order=b.order.where(b.order < 0, b.order.clip(upper=4)))
    m = b.pivot_table(index="age", columns="order", values="births", aggfunc="sum", fill_value=0)
    m = m.reindex(index=[-1, *AGES], columns=[-1, *ORDERS], fill_value=0).astype(float)
    known = m.loc[list(AGES), list(ORDERS)]
    # unknown order, known age -> order mix at that age
    share = known.div(known.sum(axis=1), axis=0).fillna(0)
    known = known + share.mul(m.loc[list(AGES), -1], axis=0)
    # unknown age (any order) -> age pattern of that order
    unk_age = m.loc[-1, list(ORDERS)] + m.loc[-1, -1] * known.sum() / known.values.sum()
    known = known + known.div(known.sum(), axis=1) * unk_age
    return known


def rates(code):
    iso3, name, first_year = COUNTRIES[code]
    births = pd.read_csv(intermediate_dir("NSO") / f"births_by_order_{code}.csv")
    pop = women(iso3)
    factor = completion(code)
    rows, by_age = [], []
    for year, b in births[births.year >= first_year].groupby("year"):
        m = spread(b)
        w = pop.loc[year].reindex(list(AGES))
        asfr = m.div(w, axis=0) * factor.get(year, 1.0)
        row = {"country": name, "year": year, "births": b.births.sum(), "completion": factor.get(year, 1.0),
               "age_unknown": b.loc[b.age < 0, "births"].sum() / b.births.sum(),
               "order_unknown": b.loc[b.order < 0, "births"].sum() / b.births.sum()}
        for o, col in ORDERS.items():
            row[col] = asfr[o].sum()
        row["TFR3p"] = row["TFR3"] + row["TFR4p"]
        row["TFR"] = asfr.values.sum()
        by_age.append(asfr.set_axis([f"f{o}" for o in ORDERS], axis=1).rename_axis("age")
                      .reset_index().assign(year=year))
        f1 = asfr[1]
        row["MAB1"] = (f1 * (np.array(AGES) + 0.5)).sum() / f1.sum()
        rows.append(row)
    out = pd.DataFrame(rows)
    out = out[out.completion <= MAX_COMPLETION]
    out["TFR_registered"] = out.TFR / out.completion
    out["TFR_wpp"] = out.year.map(wpp_tfr(iso3))
    out["TFR_vs_wpp"] = out.TFR / out.TFR_wpp
    asfr = pd.concat(by_age)
    return out, asfr[asfr.year.isin(out.year)]


def cond_asfr(asfr):
    """First- and second-birth rates per woman at risk (m1x, m2x, as HFD's mi.txt).

    Women by parity come from cumulating each cohort's order-specific rates (as HFD does where
    it has no census parity), ignoring differences in mortality and migration by parity:
    the share with i+ children at age x in year t is the sum of f_i over the cohort's earlier
    ages plus half the rate at age x. Years before the first data year take that year's rates;
    backfilled is how many, and backfill_share1/2 the share of the cumulated first/second
    births that came from them.
    """
    f = asfr.set_index(["year", "age"]).sort_index()
    first = f.index.get_level_values("year").min()
    rows = []
    for (year, age), r in f.iterrows():
        if not 15 <= age <= 49:
            continue
        past = [f.loc[(max(year - age + a, first), a)] for a in range(AGES[0], age)]
        filled = [p for a, p in zip(range(AGES[0], age), past) if year - age + a < first]
        cum = (sum(past) if past else 0 * r) + 0.5 * r
        cum_filled = sum(filled) if filled else 0 * r
        p0, p1 = 1 - cum.f1, cum.f1 - cum.f2
        rows.append({"year": year, "age": age, "p0": p0, "p1": p1,
                     "m1x": r.f1 / p0 if p0 > 0 else np.nan, "m2x": r.f2 / p1 if p1 > 0 else np.nan,
                     "backfilled": len(filled),
                     "backfill_share1": cum_filled.f1 / cum.f1, "backfill_share2": cum_filled.f2 / cum.f2})
    return pd.DataFrame(rows)


def chart(d, path):
    """One country: period TFR by order, years completed for late registration dotted."""
    name = d.country.iloc[0]
    fig = go.Figure()
    # Dotted: Mexico's years raised by over 1% for late registration; for records by year of birth
    # (Brazil), years over 5% below WPP (SINASC's early coverage). Mexico's gap to WPP is the finding.
    by_birth_year = (d.completion == 1).all()
    full = (d.completion <= 1.01) & ((d.TFR_vs_wpp >= 0.95) | (not by_birth_year))
    for (col, label), c in zip(SHOWN.items(), COLORS):
        fig.add_trace(go.Scatter(x=d.year, y=d[col].where(full), mode="lines+markers", name=label,
                                 legendgroup=label, line=dict(color=c, width=2), marker=dict(size=4),
                                 hovertemplate=f"{label}: %{{y:.2f}}<extra></extra>"))
        part = d[col].where(~full | ~full.shift(-1, fill_value=True) | ~full.shift(1, fill_value=True))
        fig.add_trace(go.Scatter(x=d.year, y=part, mode="lines", name=label, legendgroup=label,
                                 showlegend=False, line=dict(color=c, width=2, dash="dot"),
                                 hoverinfo="skip"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title=f"{name}: period TFR by birth order, {d.year.min()}–{d.year.max()}",
                      yaxis=dict(title="Births per woman", rangemode="tozero"), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.15))
    write_html(fig, path)


if __name__ == "__main__":
    out = outputs_dir("NSO")
    parts = []
    for code in COUNTRIES:
        if not (intermediate_dir("NSO") / f"births_by_order_{code}.csv").exists():
            continue
        summary, asfr = rates(code)
        parts.append(summary)
        asfr.round(6).to_csv(out / f"asfr_by_order_{code}.csv", index=False)
        cond_asfr(asfr).round(6).to_csv(out / f"cond_asfr_{code}.csv", index=False)
    df = pd.concat(parts)
    df.round(4).to_csv(out / "tfr_by_order_mex_bra.csv", index=False)
    print(df[["country", "year", "TFR", "TFR_registered", "completion", "TFR_wpp", "TFR1", "TFR2", "TFR3p", "MAB1",
              "age_unknown", "order_unknown"]].round(3).to_string(index=False))
    for code in COUNTRIES:
        d = df[df.country == COUNTRIES[code][1]]
        if len(d):
            chart(d, out / f"{code}_tfr_by_order.html")
