"""US: share of 25-34s and 35-44s living with a spouse or partner, by employment status and
earnings, with a shift-share of the change, from American Community Survey (ACS) 1-year
Public Use Microdata Sample (PUMS) person files, 2008, 2013, 2018 and 2023.

Couple: the person is the householder's spouse or unmarried partner, or is the householder
and the household contains a spouse or unmarried partner. ACS records relationships only to
the householder, so a couple living in someone else's home (e.g. with the parents of one of
them) is counted only when the couple includes the householder; young couples in a parent's
home are missed. Married + cohabiting, same-sex couples included. Group-quarters residents
(prisons, barracks, dorms, care homes) are excluded.

Employment status (ESR; WKHP usual weekly hours, SCH school enrolment):
  Employed full-time   at work or with a job (incl. armed forces), usual hours >= 35
  Employed part-time   usual hours < 35
  Unemployed           looking for and available for work
  Not in labour force, in education   enrolled in school or college in the last 3 months
  Not in labour force, not in education
Earnings: PERNP (wages plus self-employment income over the previous 12 months), ranked into
quintiles within each year, sex and age band (zero earnings included in the bottom quintile).

Shift-share (symmetric, exact): dC = sum_g ds_g * mean(r_g) [employment mix]
                                     + sum_g mean(s_g) * dr_g [within groups].

Inputs (download into NSO/data/acs_pums/ - not tracked in git; ~600 MB each):
  pus_2008.zip  https://www2.census.gov/programs-surveys/acs/data/pums/2008/1-Year/csv_pus.zip
  pus_2013.zip  https://www2.census.gov/programs-surveys/acs/data/pums/2013/1-Year/csv_pus.zip
  pus_2018.zip  https://www2.census.gov/programs-surveys/acs/data/pums/2018/1-Year/csv_pus.zip
  pus_2023.zip  https://www2.census.gov/programs-surveys/acs/data/pums/2023/1-Year/csv_pus.zip
(The Census Data API's PUMS endpoint now needs a key, so the bulk CSV files are used.)

Outputs (NSO/outputs/):
  coupling_by_employment_us_cells.csv   weighted persons and couple share per year x sex x
                                        age band x employment group x earnings quintile
  coupling_by_employment_us.csv         couple share and population share by employment group
  coupling_by_employment_us_shift_share.csv   2008 -> 2023 change split into mix vs within
  coupling_by_employment_us.html        couple share by employment group, 2008-2023
  coupling_by_earnings_us.html          couple share by earnings quintile, 2008-2023
"""

import zipfile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("NSO") / "acs_pums"
OUT = outputs_dir("NSO")
YEARS = [2008, 2013, 2018, 2023]
BANDS = {"25-34": (25, 34), "35-44": (35, 44)}
SEXES = {1: "Men", 2: "Women"}
GROUPS = ["Employed full-time", "Employed part-time", "Unemployed",
          "Not in labour force, in education", "Not in labour force, not in education"]
COLORS = dict(zip(GROUPS, ["#1f77b4", "#2ca02c", "#d62728", "#9467bd", "#ff7f0e"]))


def read_year(year):
    rel = "RELSHIPP" if year >= 2019 else "RELP" if year >= 2010 else "REL"  # same codes in REL and RELP
    cols = ["SERIALNO", "PWGTP", "AGEP", "SEX", rel, "ESR", "WKHP", "SCH", "PERNP"]
    parts = []
    with zipfile.ZipFile(DATA / f"pus_{year}.zip") as z:
        for name in sorted(n for n in z.namelist() if n.lower().endswith(".csv")):
            with z.open(name) as f:
                parts.append(pd.read_csv(f, usecols=cols, dtype={"SERIALNO": str}))
    p = pd.concat(parts, ignore_index=True).rename(columns={rel: "REL"})
    if year >= 2019:
        head, partner, gq = 20, {21, 22, 23, 24}, {37, 38}
    else:
        head, partner, gq = 0, {1, 13}, {16, 17}
    p = p[~p.REL.isin(gq)]
    has_partner = p.REL.isin(partner).groupby(p.SERIALNO).transform("any")
    p["couple"] = p.REL.isin(partner) | ((p.REL == head) & has_partner)
    return p


def classify(p):
    p = p[(p.AGEP >= 25) & (p.AGEP <= 44)].copy()
    p["band"] = np.where(p.AGEP <= 34, "25-34", "35-44")
    emp = p.ESR.isin([1, 2, 4, 5])
    enrolled = p.SCH.isin([2, 3])
    p["group"] = np.select(
        [emp & (p.WKHP >= 35), emp, p.ESR == 3, enrolled],
        GROUPS[:4], default=GROUPS[4])
    p["earn_q"] = 0
    for _, idx in p.groupby(["SEX", "band"]).groups.items():
        x = p.loc[idx].sort_values("PERNP", kind="mergesort")
        cum = x.PWGTP.cumsum() / x.PWGTP.sum()
        p.loc[x.index, "earn_q"] = np.minimum(5, np.floor(cum.values * 5 - 1e-9).astype(int) + 1)
    return p


def cells():
    out = []
    for y in YEARS:
        p = classify(read_year(y))
        p["w_cpl"] = p.PWGTP * p.couple
        c = p.groupby(["SEX", "band", "group", "earn_q"]).agg(
            persons=("PWGTP", "sum"), couples=("w_cpl", "sum"), n=("PWGTP", "size")).reset_index()
        c.insert(0, "year", y)
        out.append(c)
        print(y, f"{len(p):,} persons aged 25-44")
    c = pd.concat(out)
    c["sex"] = c.SEX.map(SEXES)
    return c.drop(columns="SEX")


def by_group(c, col):
    g = c.groupby(["year", "sex", "band", col])[["persons", "couples", "n"]].sum().reset_index()
    tot = g.groupby(["year", "sex", "band"]).persons.transform("sum")
    g["share"] = 100 * g.persons / tot
    g["couple_rate"] = 100 * g.couples / g.persons
    return g


def shift_share(g, y0=YEARS[0], y1=YEARS[-1]):
    rows = []
    for (sex, band), x in g.groupby(["sex", "band"]):
        a = x[x.year == y0].set_index("group")
        b = x[x.year == y1].set_index("group")
        ds, dr = b.share - a.share, b.couple_rate - a.couple_rate
        comp = (ds / 100 * (a.couple_rate + b.couple_rate) / 2).sum()
        within = ((a.share + b.share) / 200 * dr).sum()
        c0 = (a.share * a.couple_rate).sum() / 100
        c1 = (b.share * b.couple_rate).sum() / 100
        rows.append(dict(sex=sex, band=band, year0=y0, year1=y1, couple_0=c0, couple_1=c1,
                         change=c1 - c0, composition=comp, within=within,
                         **{f"within: {k}": v for k, v in ((a.share + b.share) / 200 * dr).items()}))
    return pd.DataFrame(rows).round(2)


def plot(g, col, order, colors, title, ytitle):
    fig = make_subplots(rows=2, cols=2, shared_yaxes=True, vertical_spacing=0.14, horizontal_spacing=0.05,
                        subplot_titles=[f"{s}, {b}" for b in BANDS for s in SEXES.values()])
    for i, band in enumerate(BANDS):
        for j, sex in enumerate(SEXES.values()):
            for k in order:
                x = g[(g.sex == sex) & (g.band == band) & (g[col] == k)].sort_values("year")
                name = k if isinstance(k, str) else f"Quintile {k}"
                fig.add_trace(go.Scatter(
                    x=x.year, y=x.couple_rate, mode="lines+markers", name=name, legendgroup=name,
                    showlegend=(i == 0 and j == 0), line=dict(color=colors[k], width=2),
                    customdata=x[["share"]],
                    hovertemplate=f"{sex} {band}, {name.lower()} %{{x}}: %{{y:.1f}}% in a couple"
                                  " (%{customdata[0]:.1f}% of age group)<extra></extra>",
                ), row=i + 1, col=j + 1)
    fig.update_yaxes(ticksuffix="%", range=[0, 90])
    fig.update_yaxes(title_text=ytitle, col=1)
    fig.update_xaxes(tickvals=YEARS)
    fig.update_layout(template="plotly_white", title=title, height=720,
                      legend=dict(orientation="h", y=-0.1), margin=dict(t=90), hovermode="closest")
    return fig


if __name__ == "__main__":
    c = cells()
    c.to_csv(OUT / "coupling_by_employment_us_cells.csv", index=False)
    g = by_group(c, "group")
    ss = shift_share(g)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    tab = g.pivot_table(index=["sex", "band", "group"], columns="year", values=["share", "couple_rate"]).round(1)
    print(tab.to_string())
    print(ss.to_string())
    tot = g.groupby(["year", "sex", "band"]).apply(lambda x: 100 * x.couples.sum() / x.persons.sum(),
                                                   include_groups=False)
    print(tot.round(1).unstack("year").to_string())
    q = by_group(c, "earn_q")
    print(q.pivot_table(index=["sex", "band", "earn_q"], columns="year", values="couple_rate").round(1).to_string())
    g.round(2).to_csv(OUT / "coupling_by_employment_us.csv", index=False)
    ss.to_csv(OUT / "coupling_by_employment_us_shift_share.csv", index=False)
    write_html(plot(g, "group", GROUPS, COLORS, "US: living with a spouse or partner, by employment status",
                    "% in a couple"), OUT / "coupling_by_employment_us.html")
    qcol = dict(zip(range(1, 6), ["#d62728", "#ff7f0e", "#bcbd22", "#2ca02c", "#1f77b4"]))
    write_html(plot(q, "earn_q", list(range(1, 6)), qcol,
                    "US: living with a spouse or partner, by earnings quintile (1 = lowest, within year, sex and age)",
                    "% in a couple"), OUT / "coupling_by_earnings_us.html")
