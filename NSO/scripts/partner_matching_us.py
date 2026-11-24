"""Who partners with whom in the US, and how many single men there are per single woman by
education, ages 25-39, from American Community Survey microdata (2008, 2013, 2018, 2024).

(a) Couples: householder plus spouse or unmarried partner of the opposite sex, woman aged
    25-39. Woman's education compared with the man's on three levels (high school or less;
    some college or associate degree; bachelor's or more): she has more (hypogamy), the
    same (homogamy) or less (hypergamy). Plus the man's age minus the woman's.
(b) Singles: people aged 25-39 in households (group quarters excluded) who are not married
    and not the householder's cohabiting partner or a householder living with one.
    Men per woman by education: tertiary = associate degree or more (ISCED 5-8, to match
    Eurostat), bachelor's or more, and below high school diploma (ISCED 0-2).

The ACS records relationships to the householder only, so couples in which neither partner
is the householder (e.g. living with parents) are missed in (a), and if unmarried, are
counted as single in (b). Married people whose spouse lives elsewhere count as partnered.

Inputs (not tracked in git), the 1-year PUMS person files from the Census Bureau:
  https://www2.census.gov/programs-surveys/acs/data/pums/<year>/1-Year/csv_pus.zip
  saved as NSO/data/acs_pums/csv_pus_<year>.zip for year in YEARS.
Variables: SERIALNO, SPORDER, REL (2008) / RELP (2013, 2018) / RELSHIPP (2024), SEX, AGEP, MAR, SCHL,
PWGTP (person weight).

Writes NSO/outputs/partner_matching_us_{pairing,age_gap,singles}.csv and
partner_matching_us_{pairing,singles}.html.
"""

import zipfile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

YEARS = [2008, 2013, 2018, 2024]
DATA = data_dir("NSO") / "acs_pums"
OUTDIR = outputs_dir("NSO")
COLS = ["SERIALNO", "SPORDER", "SEX", "AGEP", "MAR", "SCHL", "PWGTP"]


def read_year(year):
    frames = []
    with zipfile.ZipFile(DATA / f"csv_pus_{year}.zip") as z:
        for name in z.namelist():
            if not name.lower().endswith(".csv"):
                continue
            with z.open(name) as f:
                header = f.readline().decode().strip().split(",")
            # 2008-09 call it REL, 2010-18 RELP (same codes); 2019+ RELSHIPP (new codes).
            rel = next(r for r in ("RELSHIPP", "RELP", "REL") if r in header)
            with z.open(name) as f:
                d = pd.read_csv(f, usecols=COLS + [rel], dtype={"SERIALNO": str})
            frames.append(d.rename(columns={rel: "REL"}).assign(relvar=rel))
    d = pd.concat(frames, ignore_index=True)
    if (d.relvar == "RELSHIPP").all():
        d["role"] = d.REL.map({20: "head", 21: "spouse", 22: "partner", 23: "spouse", 24: "partner",
                               37: "gq", 38: "gq"}).fillna("other")
    else:
        d["role"] = d.REL.map({0: "head", 1: "spouse", 13: "partner", 16: "gq", 17: "gq"}).fillna("other")
    d["SCHL"] = pd.to_numeric(d.SCHL, errors="coerce")
    assert d.SCHL.max() == 24, "expects the 24-category SCHL coding used from 2008"
    return d.drop(columns=["REL", "relvar"])


def edu3(schl):
    return np.select([schl <= 17, schl <= 20], [0, 1], 2)


def couples(d):
    heads = d[d.role == "head"].set_index("SERIALNO")
    mates = d[d.role.isin(["spouse", "partner"])].drop_duplicates("SERIALNO").set_index("SERIALNO")
    c = heads.join(mates, how="inner", lsuffix="_h", rsuffix="_p")
    c = c[c.SEX_h != c.SEX_p]
    woman_is_head = c.SEX_h == 2
    pick = lambda v: np.where(woman_is_head, c[f"{v}_h"], c[f"{v}_p"])
    other = lambda v: np.where(woman_is_head, c[f"{v}_p"], c[f"{v}_h"])
    out = pd.DataFrame({"w_age": pick("AGEP"), "w_schl": pick("SCHL"), "w_wt": pick("PWGTP"),
                        "m_age": other("AGEP"), "m_schl": other("SCHL"),
                        "married": c.role_p.values == "spouse"})
    out = out[(out.w_age >= 25) & (out.w_age <= 39)].dropna(subset=["w_schl", "m_schl"])
    out["diff"] = np.sign(edu3(out.w_schl) - edu3(out.m_schl))
    out["gap"] = out.m_age - out.w_age
    return out


def wmedian(x, w):
    o = np.argsort(x.values)
    cw = np.cumsum(w.values[o])
    return float(x.values[o][np.searchsorted(cw, cw[-1] / 2)])


def summarise_couples(c, year):
    rows, gaps = [], []
    for group, g in [("All couples", c), ("Married", c[c.married]), ("Cohabiting", c[~c.married])]:
        w = g.w_wt.sum()
        rows.append(dict(year=year, couples=group, n=len(g),
                         woman_more=g.w_wt[g["diff"] > 0].sum() / w,
                         same=g.w_wt[g["diff"] == 0].sum() / w,
                         woman_less=g.w_wt[g["diff"] < 0].sum() / w))
        gaps.append(dict(year=year, couples=group, n=len(g),
                         mean_gap=np.average(g.gap, weights=g.w_wt), median_gap=wmedian(g.gap, g.w_wt),
                         man_5plus_older=g.w_wt[g.gap >= 5].sum() / w,
                         woman_older=g.w_wt[g.gap < 0].sum() / w))
    return rows, gaps


def singles(d, year):
    p = d[(d.AGEP >= 25) & (d.AGEP <= 39) & (d.role != "gq")].dropna(subset=["SCHL"])
    heads_with_mate = set(d.SERIALNO[d.role.isin(["spouse", "partner"])])
    partnered = (p.MAR == 1) | p.role.isin(["spouse", "partner"]) | ((p.role == "head") & p.SERIALNO.isin(heads_with_mate))
    s = p[~partnered]
    tot = lambda sex, mask: s.PWGTP[(s.SEX == sex) & mask(s.SCHL)].sum()
    m, f = 1, 2
    tert = lambda x: x >= 20
    nont = lambda x: x < 20
    ba = lambda x: x >= 21
    noba = lambda x: x < 21
    lths = lambda x: x <= 15
    every = lambda x: x > 0
    return dict(
        year=year,
        nontertiary_men_per_tertiary_woman=tot(m, nont) / tot(f, tert),
        tertiary_men_per_tertiary_woman=tot(m, tert) / tot(f, tert),
        below_hs_men_per_tertiary_woman=tot(m, lths) / tot(f, tert),
        nontertiary_men_per_nontertiary_woman=tot(m, nont) / tot(f, nont),
        no_ba_men_per_ba_woman=tot(m, noba) / tot(f, ba),
        ba_men_per_ba_woman=tot(m, ba) / tot(f, ba),
        all_men_per_woman=tot(m, every) / tot(f, every),
        single_share_men=s.PWGTP[s.SEX == m].sum() / p.PWGTP[p.SEX == m].sum(),
        single_share_women=s.PWGTP[s.SEX == f].sum() / p.PWGTP[p.SEX == f].sum(),
        single_tertiary_women=tot(f, tert),
        single_nontertiary_men=tot(m, nont),
    )


def plot_pairing(pair, gaps):
    a = pair[pair.couples == "All couples"].set_index("year")
    g = gaps[gaps.couples == "All couples"].set_index("year")
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4], horizontal_spacing=0.12,
                        subplot_titles=("Woman's education vs her partner's (% of couples)",
                                        "Man's age minus woman's (years)"))
    for col, label, color in [("woman_more", "Woman more educated", "#d62728"),
                              ("same", "Same level", "#7f7f7f"),
                              ("woman_less", "Woman less educated", "#1f77b4")]:
        fig.add_trace(go.Bar(x=a.index.astype(str), y=100 * a[col], name=label, marker_color=color,
                             hovertemplate=label + " %{x}: %{y:.1f}%<extra></extra>"), row=1, col=1)
    for col, label, color in [("mean_gap", "Mean age gap", "#2ca02c"), ("median_gap", "Median age gap", "#9467bd")]:
        fig.add_trace(go.Scatter(x=g.index.astype(str), y=g[col], name=label, mode="lines+markers",
                                 line=dict(color=color), hovertemplate=label + " %{x}: %{y:.1f}<extra></extra>"),
                      row=1, col=2)
    fig.update_layout(template="plotly_white", barmode="stack",
                      title="US couples with the woman aged 25-39",
                      legend=dict(orientation="h", x=0, y=-0.12), margin=dict(t=90))
    fig.update_yaxes(range=[0, 100], row=1, col=1)
    fig.update_yaxes(rangemode="tozero", row=1, col=2)
    return fig


def plot_singles(s):
    fig = go.Figure()
    for col, label, color in [("nontertiary_men_per_tertiary_woman", "Non-tertiary men per tertiary woman", "#ff7f0e"),
                              ("no_ba_men_per_ba_woman", "Men without a bachelor's per woman with one", "#8c564b"),
                              ("tertiary_men_per_tertiary_woman", "Tertiary men per tertiary woman", "#1f77b4"),
                              ("ba_men_per_ba_woman", "Bachelor's men per bachelor's woman", "#17becf"),
                              ("below_hs_men_per_tertiary_woman", "Men below high school per tertiary woman", "#d62728")]:
        fig.add_trace(go.Scatter(x=s.year, y=s[col], name=label, mode="lines+markers", line=dict(color=color),
                                 hovertemplate=label + " %{x}: %{y:.2f}<extra></extra>"))
    fig.add_hline(y=1, line=dict(color="grey", dash="dot"))
    fig.update_layout(template="plotly_white", title="US single men per single woman by education, ages 25-39",
                      yaxis_title="Single men per single woman", yaxis_rangemode="tozero",
                      legend=dict(orientation="h", x=0, y=-0.15), margin=dict(t=70))
    return fig


def main():
    pair, gaps, sing = [], [], []
    for year in YEARS:
        d = read_year(year)
        r, g = summarise_couples(couples(d), year)
        pair += r
        gaps += g
        sing.append(singles(d, year))
        print(year, "done")
    pair, gaps, sing = pd.DataFrame(pair), pd.DataFrame(gaps), pd.DataFrame(sing)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    pair.round(4).to_csv(OUTDIR / "partner_matching_us_pairing.csv", index=False)
    gaps.round(3).to_csv(OUTDIR / "partner_matching_us_age_gap.csv", index=False)
    sing.round(4).to_csv(OUTDIR / "partner_matching_us_singles.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 20):
        print(pair.round(3), gaps.round(2), sing.round(3), sep="\n")
    write_html(plot_pairing(pair, gaps), OUTDIR / "partner_matching_us_pairing.html")
    write_html(plot_singles(sing), OUTDIR / "partner_matching_us_singles.html")


if __name__ == "__main__":
    main()
