"""US ideal number of children by birth cohort and age, women and men, GSS 1972-2024.

General Social Survey cumulative file (NORC): chldidel ("What do you think is the ideal number of
children for a family to have?"; 7 = seven or more; 8 = "as many as you want", dropped), wtssps
weight, age 18-49. Birth cohort = survey year - age, in 5-year groups 1965-69 to 2000-06. Cells
with fewer than 40 respondents are dropped.

Input (not tracked in git): GSS/data/GSS_stata/gss7224_r3a.dta
Outputs: GSS/outputs/ideal_by_cohort_us.html, ideal_by_cohort_us.csv, and ideal_matrix_us.csv (US rows
for eurostat/scripts/change_matrix.py: women 18-29 and 30-39, survey years pooled around 2005,
2010 and 2018)
"""

import warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plot_colors import COHORT_COLORSCALE, cohort_axis, sample_color
from common.plotting import write_html

warnings.simplefilter("ignore")
DATA = data_dir("GSS") / "GSS_stata" / "gss7224_r3a.dta"
OUT = outputs_dir("GSS")
COHORTS = [(1965, 1969), (1970, 1974), (1975, 1979), (1980, 1984), (1985, 1989), (1990, 1994),
           (1995, 1999), (2000, 2006)]
AGES = [(18, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49)]
MIN_N = 40


def load():
    d = pd.read_stata(DATA, convert_categoricals=False,
                      columns=["year", "age", "sex", "chldidel", "wtssps"])
    d = d[d.chldidel.between(0, 7) & d.wtssps.notna() & d.age.between(18, 49)]
    d["cohort"] = d.year - d.age
    rows = []
    for sex, name in [(2, "Women"), (1, "Men")]:
        for clo, chi in COHORTS:
            for alo, ahi in AGES:
                g = d[(d.sex == sex) & d.cohort.between(clo, chi) & d.age.between(alo, ahi)]
                if len(g) >= MIN_N:
                    rows.append(dict(sex=name, cohort=f"{clo}-{chi}", cohort_mid=(clo + chi) / 2,
                                     age=f"{alo}-{ahi}", years=f"{int(g.year.min())}-{int(g.year.max())}",
                                     ideal=round(np.average(g.chldidel, weights=g.wtssps), 2), n=len(g)))
    return pd.DataFrame(rows)


# Pooled survey years for the country comparison matrix, labelled by the year they stand for.
MATRIX_POINTS = {2005: (2004, 2006), 2010: (2008, 2010, 2012), 2018: (2016, 2018, 2021)}
MATRIX_AGES = {"ideal_young": (18, 29), "ideal_30s": (30, 39)}


def matrix_series():
    d = pd.read_stata(DATA, convert_categoricals=False, columns=["year", "age", "sex", "chldidel", "wtssps"])
    d = d[(d.sex == 2) & d.chldidel.between(0, 7) & d.wtssps.notna()]
    rows = []
    for key, (lo, hi) in MATRIX_AGES.items():
        for point, years in MATRIX_POINTS.items():
            g = d[d.age.between(lo, hi) & d.year.isin(years)]
            rows.append(dict(key=key, iso="USA", year=point, value=round(np.average(g.chldidel, weights=g.wtssps), 2),
                             n=len(g), source=f"GSS, ideal for a family, women {lo}–{hi}, "
                                              f"{'/'.join(str(y) for y in years)} pooled"))
    return pd.DataFrame(rows)


def plot(d):
    axis = cohort_axis(COHORTS[0][0], COHORTS[-1][1])
    ages = [f"{a}-{b}" for a, b in AGES]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=["Women", "Men"])
    for col, sex in enumerate(["Women", "Men"], start=1):
        for cohort, g in d[d.sex == sex].groupby("cohort", sort=True):
            color = sample_color(COHORT_COLORSCALE, g.cohort_mid.iloc[0], axis)
            fig.add_trace(go.Scatter(
                x=g.age, y=g.ideal, mode="lines+markers", name=f"Born {cohort}", legendgroup=cohort,
                showlegend=col == 1, line=dict(color=color), customdata=g[["years", "n"]],
                hovertemplate=f"Born {cohort}, aged " + "%{x}: %{y:.2f}<br>Surveyed %{customdata[0]}, "
                              "n=%{customdata[1]}<extra></extra>"), row=1, col=col)
    fig.update_xaxes(categoryorder="array", categoryarray=ages, title_text="Age")
    fig.update_yaxes(range=[2.0, 3.1], title_text="Mean ideal number of children", col=1)
    fig.update_layout(template="plotly_white", title="US ideal number of children by birth cohort and age",
                      legend=dict(x=1.02, y=1, xanchor="left"), margin=dict(t=80, r=140),
                      hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "ideal_by_cohort_us.csv", index=False)
    print(d.pivot_table(index=["sex", "cohort"], columns="age", values="ideal").to_string())
    write_html(plot(d), OUT / "ideal_by_cohort_us.html")
    m = matrix_series()
    print(m.to_string(index=False))
    m.to_csv(OUT / "ideal_matrix_us.csv", index=False)
