"""Time from forming a couple to a first birth, for docs/factors/union-to-first-birth.md, from
published tables transcribed into research/data/:

- ffs_union_to_first_birth.csv: % of childless couples with a first child by years since the union
  began, 17 FFS populations around 1990 (Andersson & Philipov 2002, Table 17).
- ffs_union_birth_ages.csv: women's median age at first union and at first becoming a parent
  (same paper, Tables 6 and 8).
- jpn_kor_union_to_first_birth.csv: mean years to a first birth from starting to live together
  (Japan 1975-2019, MHLW) or from the start of married life (S Korea 2000-2024, Statistics Korea),
  from birth registrations.
- cohab_first_births.csv: % of women's first births within cohabitation, marriage or to single
  women, by period of the birth (Perelli-Harris et al. 2010; US NSFG 2006-2010).

Outputs: NSO/outputs/union_first_births_cohab.html, union_to_first_birth_ffs.html,
union_birth_ages_ffs.html, union_to_first_birth_jpn_kor.html.
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import REPO, outputs_dir
from common.plotting import write_html

DATA = REPO / "research" / "data"
OUTDIR = outputs_dir("NSO")
REGIONS = {
    "North & West": ["Sweden", "Norway", "Finland", "France", "Flanders", "Austria", "West Germany", "USA"],
    "South": ["Italy", "Spain"],
    "Central & East": ["East Germany", "Hungary", "Czech Republic", "Slovenia", "Poland", "Latvia", "Lithuania"],
}
REGION_COLORS = dict(zip(REGIONS, [pc.qualitative.D3[1], pc.qualitative.D3[3], pc.qualitative.D3[4]]))
DURS = [0, 1, 2, 3, 4, 5, 7, 10, 15]


def ffs_curves():
    d = pd.read_csv(DATA / "ffs_union_to_first_birth.csv", comment="#").set_index("country")
    fig = go.Figure()
    for region, countries in REGIONS.items():
        for i, c in enumerate(countries):
            r = d.loc[c]
            y = [0] + [r[f"d{k}"] for k in DURS[1:]]
            fig.add_trace(go.Scatter(
                x=DURS, y=y, mode="lines+markers", name=f"{c} ({r.period})", legendgroup=region,
                legendgrouptitle_text=region if i == 0 else None, line=dict(color=REGION_COLORS[region], width=1.6),
                marker=dict(size=4), connectgaps=False,
                hovertemplate=f"<b>{c}</b> ({r.period})<br>%{{y}}% with a first child %{{x}} years after the union began"
                              f"<br>median {r.median_years:.0f} years<extra></extra>"))
    for k in (3, 5, 10):
        fig.add_vline(x=k, line=dict(color="#bbbbbb", width=1, dash="dot"))
    fig.update_layout(
        template="plotly_white", hovermode="closest",
        title=dict(text="% of childless couples with a first child, by years since moving in together or marrying "
                        "(FFS, around 1990)", x=0.01, font=dict(size=14)),
        xaxis=dict(title="Years since the union began", tickvals=DURS),
        yaxis=dict(title="% with a first child", ticksuffix="%", range=[0, 100]),
        legend=dict(x=1.02, y=1, xanchor="left", groupclick="toggleitem"), margin=dict(r=200, t=60))
    return fig


def ffs_ages():
    d = pd.read_csv(DATA / "ffs_union_birth_ages.csv", comment="#")
    order = [c for cs in REGIONS.values() for c in cs]
    d = d.set_index("country").loc[order[::-1]].reset_index()
    region = {c: r for r, cs in REGIONS.items() for c in cs}
    fig = go.Figure()
    for _, r in d.iterrows():
        col = REGION_COLORS[region[r.country]]
        fig.add_trace(go.Scatter(x=[r.median_age_union, r.median_age_parent], y=[r.country] * 2, mode="lines",
                                 line=dict(color=col, width=3), showlegend=False, hoverinfo="skip"))
    for key, sym, lab in (("median_age_union", "circle-open", "first union"),
                          ("median_age_parent", "circle", "first child")):
        fig.add_trace(go.Scatter(
            x=d[key], y=d.country, mode="markers", name=f"Median age at {lab}",
            marker=dict(symbol=sym, size=10, color=[REGION_COLORS[region[c]] for c in d.country],
                        line=dict(width=2)),
            customdata=d.median_age_parent - d.median_age_union,
            hovertemplate="<b>%{y}</b><br>" + lab + ": %{x}<br>gap %{customdata} years<extra></extra>"))
    fig.update_layout(
        template="plotly_white", hovermode="closest",
        title=dict(text="Women's median age at first union (open) and at first child (filled), FFS, around 1990",
                   x=0.01, font=dict(size=14)),
        xaxis=dict(title="Median age (whole years)", dtick=1), yaxis=dict(title=None),
        legend=dict(orientation="h", y=-0.12), margin=dict(t=60, l=120), height=600)
    return fig


def _gaps(g):
    """Korea: rows for every year in the range, so lines break where years are missing (Japan's
    series is 5-yearly before 1990 and annual after, with no missing years, so it stays joined)."""
    if g.empty or g.country.iloc[0] != "S Korea":
        return g
    return g.set_index("year").reindex(range(int(g.year.min()), int(g.year.max()) + 1)).reset_index()


def jpn_kor():
    d = pd.read_csv(DATA / "jpn_kor_union_to_first_birth.csv", comment="#")
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.1,
                        subplot_titles=["Mean years to a first birth, from moving in together (Japan)<br>"
                                        "or start of married life (Korea)",
                                        "% of first births: within 2 years (Korea),<br>conceived before marriage (Japan)"])
    cols = {"Japan": pc.qualitative.D3[0], "S Korea": pc.qualitative.D3[2]}
    for c, g in d.groupby("country"):
        m = _gaps(g.dropna(subset=["mean_years"]))
        fig.add_trace(go.Scatter(x=m.year, y=m.mean_years, mode="lines+markers", name=c, legendgroup=c,
                                 line=dict(color=cols[c]), marker=dict(size=5),
                                 hovertemplate=f"<b>{c}</b> %{{x}}: %{{y:.2f}} years<extra></extra>"), row=1, col=1)
        w = _gaps(g.dropna(subset=["within_2y_pct"]))
        if len(w):
            fig.add_trace(go.Scatter(
                x=w.year, y=w.within_2y_pct, mode="lines+markers", name=f"{c}: within 2 years", legendgroup=c,
                line=dict(color=cols[c]), marker=dict(size=5, symbol=["circle-open" if f == "derived" else "circle"
                                                                      for f in w.flag.fillna("")]),
                customdata=["<br><i>derived from the printed change</i>" if f == "derived" else ""
                            for f in w.flag.fillna("")],
                hovertemplate=f"<b>{c}</b> %{{x}}: %{{y:.1f}}% within 2 years%{{customdata}}<extra></extra>"),
                row=1, col=2)
        p = g.dropna(subset=["premarital_conception_pct"])
        if len(p):
            fig.add_trace(go.Scatter(
                x=p.year, y=p.premarital_conception_pct, mode="lines+markers", legendgroup=c,
                name=f"{c}: conceived before marriage", line=dict(color=cols[c], dash="dot"), marker=dict(size=4),
                hovertemplate=f"<b>{c}</b> %{{x}}: %{{y:.1f}}% of marital first births conceived before "
                              f"marriage<extra></extra>"), row=1, col=2)
    fig.update_yaxes(title_text="Years", rangemode="tozero", row=1, col=1)
    fig.update_yaxes(title_text="% of first births", ticksuffix="%", rangemode="tozero", row=1, col=2)
    fig.update_layout(template="plotly_white", hovermode="closest", legend=dict(orientation="h", y=-0.15),
                      title=dict(text="Japan and S Korea, birth registrations", x=0.01, font=dict(size=14)),
                      margin=dict(t=80))
    return fig


def cohab_births():
    d = pd.read_csv(DATA / "cohab_first_births.csv", comment="#").dropna(subset=["mid_year"])
    order = ["Norway", "France", "UK", "Netherlands", "US", "Russia", "Italy"]
    fig = go.Figure()
    for i, c in enumerate(order):
        g = d[d.country == c]
        fig.add_trace(go.Scatter(
            x=g.mid_year, y=g.cohab_pct, mode="lines+markers", name=c, line=dict(color=pc.qualitative.D3[i]),
            marker=dict(size=6), customdata=g[["period", "married_pct", "single_pct"]],
            hovertemplate=f"<b>{c}</b> %{{customdata[0]}}<br>within cohabitation: %{{y}}%"
                          f"<br>married: %{{customdata[1]}}%<br>single: %{{customdata[2]}}%<extra></extra>"))
    fig.update_layout(
        template="plotly_white", hovermode="closest",
        title=dict(text="% of women's first births within cohabitation, by period of the birth", x=0.01,
                   font=dict(size=14)),
        xaxis=dict(title="Period of first birth (middle year)", dtick=5),
        yaxis=dict(title="% of first births", ticksuffix="%", rangemode="tozero"),
        legend=dict(x=1.02, y=1, xanchor="left"), margin=dict(r=140, t=60))
    return fig


def _mid(period):
    a, b = period.split("-")
    b = int(a[:2] + b) if len(b) == 2 else int(b)
    return (int(a) + b) / 2


def _timing_series():
    """Age at first cohabitation/union and at first birth, one dict per series."""
    c = pd.read_csv(DATA / "cohab_age_vs_first_birth.csv", comment="#")
    j = pd.read_csv(DATA / "jpn_kor_union_to_first_birth.csv", comment="#")
    j = j[j.country == "Japan"].dropna(subset=["wife_first_marriage_age", "mab1"])
    f = pd.read_csv(DATA / "ffs_union_birth_ages.csv", comment="#")
    us = c[c.country == "US"]
    out = []
    for s, dash, col in (("first cohabitation", "solid", pc.qualitative.D3[0]),
                         ("first union", "dot", pc.qualitative.D3[0])):
        g = us[us.series == s]
        out.append(dict(name=f"US, {s} (NSFG)", x=g.age_first_union, y=g.age_first_birth, year=g.mid_year,
                        label=g.period, dash=dash, color=col, mode="lines+markers"))
    uk = c[c.country == "UK"]
    out.append(dict(name="UK, first cohabitation (Understanding Society)", x=uk.age_first_union,
                    y=uk.age_first_birth, year=uk.mid_year, label=uk.period, dash="solid",
                    color=pc.qualitative.D3[6], mode="lines+markers"))
    out.append(dict(name="Japan, wedding or moving in (registrations)", x=j.wife_first_marriage_age, y=j.mab1,
                    year=j.year, label=j.year.astype(str), dash="solid", color=pc.qualitative.D3[2],
                    mode="lines+markers"))
    region = {c: r for r, cs in REGIONS.items() for c in cs}
    for r in REGIONS:
        g = f[f.country.map(region) == r]
        out.append(dict(name=f"FFS around 1990: {r}", x=g.median_age_union, y=g.median_age_parent,
                        year=g.period_union.map(_mid), label=g.country + " " + g.period_union, dash="solid",
                        color=REGION_COLORS[r], mode="markers"))
    fr = c[c.country == "France"]
    return out, fr


def cohab_ages():
    series, _ = _timing_series()
    fig = go.Figure()
    lo, hi = 20, 32
    for k, dash in ((0, "dot"), (2, "dash"), (4, "dash")):
        fig.add_trace(go.Scatter(x=[lo, hi - k], y=[lo + k, hi], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#bbbbbb", width=1, dash=dash)))
        fig.add_annotation(x=hi - k - 0.6, y=hi - 0.6, text="same age" if k == 0 else f"+{k} years",
                           showarrow=False, textangle=-45, yshift=10, font=dict(size=10, color="#999999"))
    for s in series:
        last = len(s["x"]) - 1
        fig.add_trace(go.Scatter(
            x=s["x"], y=s["y"], mode=s["mode"], name=s["name"], line=dict(color=s["color"], dash=s["dash"]),
            marker=dict(size=[7 if s["mode"] == "markers" else (10 if i == last else 5) for i in range(last + 1)],
                        symbol=["circle" if s["mode"] == "markers" or i < last else "arrow" for i in range(last + 1)],
                        angleref="previous", color=s["color"]),
            customdata=list(zip(s["label"], [y - x for x, y in zip(s["x"], s["y"])])),
            hovertemplate=f"<b>{s['name']}</b><br>%{{customdata[0]}}<br>first union/cohabitation: %{{x:.1f}}"
                          f"<br>first birth: %{{y:.1f}}<br>gap: %{{customdata[1]:.1f}} years<extra></extra>"))
    fig.update_layout(
        template="plotly_white", hovermode="closest",
        title=dict(text="Women's age at first birth against age at first cohabitation or union", x=0.01,
                   font=dict(size=14)),
        xaxis=dict(title="Age at first cohabitation or union", range=[lo, hi], constrain="domain", dtick=2),
        yaxis=dict(title="Age at first birth", range=[lo, hi], scaleanchor="x", scaleratio=1, constrain="domain",
                   dtick=2),
        legend=dict(x=1.02, y=1, xanchor="left"), margin=dict(r=260, t=60), height=620)
    return fig


def cohab_gap():
    series, fr = _timing_series()
    fig = go.Figure()
    for s in series:
        gap = [y - x for x, y in zip(s["x"], s["y"])]
        fig.add_trace(go.Scatter(
            x=s["year"], y=gap, mode=s["mode"], name=s["name"], line=dict(color=s["color"], dash=s["dash"]),
            marker=dict(size=7 if s["mode"] == "markers" else 5, color=s["color"]), customdata=s["label"],
            hovertemplate=f"<b>{s['name']}</b><br>%{{customdata}}: %{{y:.1f}} years<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=fr.mid_year, y=fr.gap_years, mode="lines+markers", name="France, first cohabitation before 30 (EPIC)",
        line=dict(color=pc.qualitative.D3[5]), marker=dict(size=7), customdata=fr.period,
        hovertemplate="<b>France</b>, first cohabitations begun %{customdata}: %{y:.1f} years<extra></extra>"))
    fig.update_layout(
        template="plotly_white", hovermode="closest",
        title=dict(text="Years from age at first cohabitation or union to age at first birth", x=0.01,
                   font=dict(size=14)),
        xaxis=dict(title="Year (middle of period)", dtick=5),
        yaxis=dict(title="Years", rangemode="tozero", ticksuffix=" yrs"),
        legend=dict(x=1.02, y=1, xanchor="left"), margin=dict(r=260, t=60), height=520)
    return fig


if __name__ == "__main__":
    write_html(cohab_ages(), OUTDIR / "cohab_age_vs_first_birth.html")
    write_html(cohab_gap(), OUTDIR / "cohab_age_vs_first_birth_gap.html")
    write_html(cohab_births(), OUTDIR / "union_first_births_cohab.html")
    write_html(ffs_curves(), OUTDIR / "union_to_first_birth_ffs.html")
    write_html(ffs_ages(), OUTDIR / "union_birth_ages_ffs.html")
    write_html(jpn_kor(), OUTDIR / "union_to_first_birth_jpn_kor.html")
