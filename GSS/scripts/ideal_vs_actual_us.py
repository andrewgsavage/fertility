"""US women aged 40-54: ideal number of children vs children ever born, 1972-2024.

General Social Survey cumulative file 1972-2024 (NORC): chldidel ("What do you think is the
ideal number of children for a family to have?"; 7 = seven or more, 8 = "as many as you want",
dropped), childs (8 = eight or more), women (sex 2) aged 40-54, wtssps weight. Pooled into
4-year windows. Compared with Human Fertility Database cumulative cohort fertility (ccfrVH.txt,
USA) for women aged 40-54, averaged over the years in each window.

Inputs (not tracked in git):
  GSS/data/GSS_stata/gss7224_r3a.dta  (https://gss.norc.org/content/dam/gss/get-the-data/documents/stata/GSS_stata.zip)
  HFD/data/HFD/ccfrVH.txt
Outputs: GSS/outputs/ideal_vs_actual_us.html, ideal_vs_actual_us.csv
"""

import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from common.hfd import age_to_int, read_hfd
from common.paths import data_dir, outputs_dir
from common.plotting import write_html

warnings.simplefilter("ignore")
DATA = data_dir("GSS") / "GSS_stata" / "gss7224_r3a.dta"
OUT = outputs_dir("GSS")
EDGES = [1971, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]


def window(y):
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        if lo < y <= hi:
            return lo + 1, hi


def wmean(v, w):
    ok = v.notna() & w.notna()
    return np.average(v[ok], weights=w[ok]), int(ok.sum())


def hfd_us():
    c = read_hfd("ccfrVH.txt")
    c = c[c.Code == "USA"].dropna(subset=["CCFR"])
    c["Age"] = age_to_int(c.Age)
    out = {}
    for year in range(1972, 2025):
        vals = []
        for cohort in range(year - 54, year - 39):
            s = c[(c.Cohort == cohort) & (c.Age <= year - cohort) & (c.Age >= 40)]
            if len(s):
                vals.append(s.sort_values("Age").CCFR.iloc[-1])
        if len(vals) == 15:
            out[year] = sum(vals) / 15
    return out


def load():
    d = pd.read_stata(DATA, convert_categoricals=False,
                      columns=["year", "age", "sex", "chldidel", "childs", "wtssps"])
    d = d[(d.sex == 2) & d.age.between(40, 54)].copy()
    d.loc[d.chldidel == 8, "chldidel"] = np.nan
    d["window"] = d.year.map(window)
    hfd = hfd_us()
    rows = []
    for (lo, hi), g in d.groupby("window"):
        ideal, n_ideal = wmean(g.chldidel, g.wtssps)
        actual, n_actual = wmean(g.childs, g.wtssps)
        h = [hfd[y] for y in range(lo, hi + 1) if y in hfd]
        rows.append(dict(window=f"{lo}-{hi}", ideal=round(ideal, 2), gss_actual=round(actual, 2),
                         hfd_actual=round(sum(h) / len(h), 2) if h else None,
                         n_ideal=n_ideal, n_actual=n_actual))
    return pd.DataFrame(rows)


def plot(d):
    fig = go.Figure()
    for col, name, color, dash in [("ideal", "Ideal (GSS)", "#c00000", "solid"),
                                   ("gss_actual", "Actual (GSS)", "#9e9e9e", "solid"),
                                   ("hfd_actual", "Actual (HFD)", "#1f2937", "dot")]:
        fig.add_trace(go.Scatter(x=d.window, y=d[col], mode="lines+markers", name=name,
                                 line=dict(color=color, dash=dash),
                                 hovertemplate=name + " %{x}: %{y:.2f}<extra></extra>"))
    fig.update_yaxes(range=[1.5, 3.5], title_text="Children per woman aged 40-54")
    fig.update_layout(template="plotly_white",
                      title="US women aged 40-54: ideal and actual number of children",
                      legend=dict(orientation="h", x=0, y=-0.2), margin=dict(t=70, b=110),
                      hovermode="x unified")
    return fig


if __name__ == "__main__":
    d = load()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "ideal_vs_actual_us.csv", index=False)
    print(d.to_string(index=False))
    write_html(plot(d), OUT / "ideal_vs_actual_us.html")
