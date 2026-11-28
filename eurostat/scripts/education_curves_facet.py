"""Birth rate by age and mother's education: facet grids in the layout of the first vs second birth
chart (HFD/scripts/cond_asfr_facet.py), and line charts by year.

Reads the curves the per-source scripts write:
  eurostat/outputs/fertility_by_education_nordic_by_age.csv   (fertility_by_education_nordic.py)
  eurostat/outputs/fertility_by_education_europe_curves.csv   (fertility_by_education_europe_curves.py)
  NSO/outputs/{mexico,brazil}_fertility_by_education.csv      (mexico/brazil_births_by_education.py)
  ACS/outputs/fertility_by_education_us_curves.csv            (ACS fertility_by_education_us.py)
Rates by 5-year age group are drawn at the band's middle; the US has single years of age, averaged
within each band for the by-year charts.

Writes to eurostat/outputs/:
  education_curves_facet.html         every country but the US: a group of three education panels
                                      per country, three countries per row, a thin line per year
  education_curves_facet_change.html  the same, each rate over the country's mean in its first three
                                      years at that age, log axis; bases under 5 per 1,000 dropped
  education_by_year_facet.html        every country, the US first: rate by year, a panel per age band
                                      20-24 ... 35-39 per country, a line per education level
  education_curves_us.html            the US age curves, four education panels
"""

import math

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from _common import NAMES
from common.paths import outputs_dir
from common.plot_colors import PERIOD_COLORSCALE, period_axis
from common.plotting import write_html

GROUPS_PER_ROW = 3
SLOTS = 4  # panel slots per country group; three-level countries widen theirs to fill the group
ROW_HEIGHT = 150
WITHIN_GAP = 0.004
BETWEEN_GAP = 0.03
RATE_RANGE = (0, 300)
CHANGE_RANGE = (0.22, 3.3)
CHANGE_TICKS = [0.25, 0.5, 0.75, 1, 1.5, 2, 3]
MIN_BASE = 5
LABEL_FONT = dict(size=14, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")
LEVELS3 = ["Low", "Middle", "High"]
US_LEVELS = [("Less than high school", "No HS"), ("High school", "HS"),
             ("Some college", "Some coll."), ("Bachelor's or more", "BA+")]
US_FULL = {short: full for full, short in US_LEVELS}  # full names where the US has a chart to itself
NORDIC = ["FI", "SE", "DK", "NO"]
EUROPE_ORDER = ["EE"]  # the one register series first, then alphabetical

BANDS = ["20-24", "25-29", "30-34", "35-39"]  # 40-44 left out: rates near zero everywhere
BAND_SLOT = {**{b: i for i, b in enumerate(BANDS)}, "30-39": 2}  # Norway's population has a 30-39 band
BAND_COLORS = dict(zip(BANDS, pc.sample_colorscale("Viridis", [0.0, 0.33, 0.62, 0.88])))
BAND_COLORS["30-39"] = BAND_COLORS["30-34"]
LEVEL_COLORS = {"Low": "#d95f02", "Middle": "#7570b3", "High": "#1b9e77",
                "No HS": "#d95f02", "HS": "#e6ab02", "Some coll.": "#7570b3", "BA+": "#1b9e77"}


def mid(band):
    lo, hi = band.str.split("-").str[0].astype(int), band.str.split("-").str[1].astype(int)
    return (lo + hi) / 2


def load():
    """Rows of (country, sublabel, level labels, long frame with level, year, x, band, rate); the US first."""
    out = []
    n = pd.read_csv(outputs_dir("eurostat") / "fertility_by_education_nordic_by_age.csv")
    cols = ["Lower secondary or less", "Upper secondary", "Tertiary"]
    for g in NORDIC:
        d = n[n.geo == g].melt(["year", "age"], cols, "level", "rate")
        d["level"] = d.level.map(dict(zip(cols, LEVELS3)))
        out.append((NAMES[g], "register", LEVELS3, d.assign(x=mid(d.age), band=d.age)))
    e = pd.read_csv(outputs_dir("eurostat") / "fertility_by_education_europe_curves.csv")
    geos = EUROPE_ORDER + sorted(set(e.geo) - set(EUROPE_ORDER), key=lambda g: NAMES[g])
    for g in geos:
        d = e[e.geo == g].melt(["year", "age"], ["low", "medium", "tertiary"], "level", "rate")
        d["level"] = d.level.map(dict(zip(["low", "medium", "tertiary"], LEVELS3)))
        out.append((NAMES[g], "register" if g == "EE" else "births / LFS women", LEVELS3,
                    d.assign(x=mid(d.age), band=d.age)))
    for code, name in [("mexico", "Mexico"), ("brazil", "Brazil")]:
        d = pd.read_csv(outputs_dir("NSO") / f"{code}_fertility_by_education.csv")
        d = d[d.ed != "all"].assign(rate=lambda t: t.rate * 1000)
        d["level"] = d.ed.map(dict(zip(["low", "medium", "tertiary"], LEVELS3)))
        out.append((name, "births / survey women", LEVELS3, d.assign(x=mid(d.age), band=d.age)))
    u = pd.read_csv(outputs_dir("ACS") / "fertility_by_education_us_curves.csv")
    u = u[~((u.education == "Bachelor's or more") & (u.age < 21))]
    lo = (u.age // 5) * 5
    u = u.assign(level=u.education.map(dict(US_LEVELS)), x=u.age, band=lo.astype(str) + "-" + (lo + 4).astype(str))
    out.insert(0, ("United States", "ACS, not in school", [s for _, s in US_LEVELS], u))
    return [(c, s, lv, d[["level", "year", "x", "band", "rate"]].dropna()) for c, s, lv, d in out]


def add_change(d):
    first = sorted(d.year.unique())[:3]
    base = d[d.year.isin(first)].groupby(["level", "x"]).rate.mean().rename("base")
    d = d.join(base, on=["level", "x"])
    return d.assign(rate=(d.rate / d.base).where(d.base >= MIN_BASE)).dropna(), f"{first[0]}–{first[-1]}"


def color(year, axis, alpha=0.7):
    lo, hi = axis
    t = min(1.0, max(0.0, (year - lo) / (hi - lo)))
    r, g, b = pc.sample_colorscale(PERIOD_COLORSCALE, [t])[0][4:-1].split(",")
    return f"rgba({r},{g},{b},{alpha})"


def group_domains(k, per_row):
    """x domains of the k panels of each of the per_row country groups in a row."""
    gw = (1 - (per_row - 1) * BETWEEN_GAP) / per_row
    pw = (gw - (k - 1) * WITHIN_GAP) / k
    return [[(g * (gw + BETWEEN_GAP) + p * (pw + WITHIN_GAP), g * (gw + BETWEEN_GAP) + p * (pw + WITHIN_GAP) + pw)
             for p in range(k)] for g in range(per_row)]


def facet(rows, change=False, per_row=GROUPS_PER_ROW, row_height=ROW_HEIGHT, title=None):
    years = [int(y) for _, _, _, d in rows for y in d.year]
    axis = period_axis(min(years), max(years))
    grid = [rows[i:i + per_row] for i in range(0, len(rows), per_row)]
    nrows = len(grid)
    fig = make_subplots(rows=nrows, cols=per_row * SLOTS, horizontal_spacing=0.001,
                        vertical_spacing=min(0.012, 1 / max(nrows - 1, 1)))
    for r, line in enumerate(grid, start=1):
        for g, (country, _, levels, d) in enumerate(line):
            if change:
                d, base_years = add_change(d)
            doms = group_domains(len(levels), per_row)[g]
            for p in range(SLOTS):
                col = g * SLOTS + p + 1
                if p >= len(levels):
                    fig.update_xaxes(visible=False, row=r, col=col)
                    fig.update_yaxes(visible=False, row=r, col=col)
                    continue
                fig.update_xaxes(domain=list(doms[p]), row=r, col=col)
                lv = levels[p]
                for y, s in d[d.level == lv].groupby("year"):
                    s = s.sort_values("x")
                    val = "%{customdata:+.0%} vs " + base_years if change else "%{y:.0f} per 1,000"
                    fig.add_trace(go.Scatter(
                        x=s.x, y=s.rate, mode="lines", line=dict(width=1, color=color(int(y), axis)),
                        customdata=s.rate - 1 if change else None, showlegend=False,
                        hovertemplate=f"{country}, {US_FULL.get(lv, lv)}<br>{int(y)}, age %{{x}}<br>{val}<extra></extra>",
                    ), row=r, col=col)
                if p == 0 and per_row > 1:
                    fig.add_annotation(text=f"<b>{country}</b>", x=0.05, y=0.97, xref="x domain", yref="y domain",
                                       xanchor="left", yanchor="top", showarrow=False, font=LABEL_FONT, row=r, col=col)
                if r == 1:  # level names head the top row
                    fig.add_annotation(text=US_FULL.get(lv, lv) if per_row == 1 else lv, x=0.5, y=1.0, xref="x domain", yref="y domain", yanchor="bottom",
                                       showarrow=False, font=dict(LABEL_FONT, size=12), row=r, col=col)
                last = r == nrows or (r == nrows - 1 and g >= len(grid[-1]))
                fig.update_xaxes(range=[18, 44], tickvals=[25, 40] if per_row > 1 else [20, 30, 40], tickangle=0,
                                 showticklabels=last, title_text="Age" if per_row == 1 else None, row=r, col=col)
                if change:
                    fig.update_yaxes(type="log", range=[math.log10(v) for v in CHANGE_RANGE], tickvals=CHANGE_TICKS,
                                     ticktext=[f"{t - 1:+.0%}" if t != 1 else "0%" for t in CHANGE_TICKS],
                                     showticklabels=col == 1, row=r, col=col)
                else:
                    fig.update_yaxes(range=list(RATE_RANGE), dtick=100, showticklabels=col == 1, row=r, col=col)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", showlegend=False,
                             marker=dict(colorscale=PERIOD_COLORSCALE, cmin=axis[0], cmax=axis[1], color=[axis[0]],
                                         showscale=True, colorbar=dict(title="Year", len=min(1, 600 / (row_height * nrows)),
                                                                       y=1, yanchor="top"))), row=1, col=1)
    title = title or ("Change in birth rate by age and education since each country's first three years (log scale)"
                      if change else "Birth rate by age and education, births per 1,000 women")
    fig.update_layout(template="plotly_white", title=title, height=row_height * nrows + 130, showlegend=False,
                      margin=dict(l=50, r=80, t=90, b=50 if per_row == 1 else 40))
    return fig


def by_band(d):
    """Rates by 5-year age band; single years of age (US) averaged within the band."""
    return d[d.band.isin(BAND_SLOT)].groupby(["level", "band", "year"]).rate.mean().reset_index()


LEGEND = [("Low (US less than high school)", "Low"), ("US high school", "HS"),
          ("Middle (US some college)", "Middle"), ("High (US bachelor's or more)", "High")]


def year_facet(rows, per_row=GROUPS_PER_ROW, row_height=ROW_HEIGHT):
    """Birth rate by year: a group of panels per country, one per age band, a line per education level."""
    years = [int(y) for _, _, _, d in rows for y in d.year]
    grid = [rows[i:i + per_row] for i in range(0, len(rows), per_row)]
    nrows = len(grid)
    fig = make_subplots(rows=nrows, cols=per_row * SLOTS, horizontal_spacing=0.001,
                        vertical_spacing=min(0.012, 1 / max(nrows - 1, 1)))
    for lab, lv in LEGEND:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", name=lab,
                                 line=dict(color=LEVEL_COLORS[lv], width=2)), row=1, col=1)
    for r, line in enumerate(grid, start=1):
        for g, (country, _, levels, d) in enumerate(line):
            b = by_band(d)
            doms = group_domains(len(BANDS), per_row)[g]
            for p in range(SLOTS):
                col = g * SLOTS + p + 1
                fig.update_xaxes(domain=list(doms[p]), row=r, col=col)
                sel = b[b.band.map(BAND_SLOT) == p]
                for lv in levels:
                    s = sel[sel.level == lv].sort_values("year")
                    if s.empty:
                        continue
                    band = s.band.iloc[0].replace("-", "–")
                    fig.add_trace(go.Scatter(
                        x=s.year, y=s.rate, mode="lines", showlegend=False,
                        line=dict(width=1.5, color=LEVEL_COLORS[lv]),
                        hovertemplate=f"{country}, {US_FULL.get(lv, lv)}, age {band}"
                                      "<br>%{x}: %{y:.0f} per 1,000<extra></extra>",
                    ), row=r, col=col)
                if p == 2 and (b.band == "30-39").any():
                    fig.add_annotation(text="30–39", x=0.95, y=0.97, xref="x domain", yref="y domain",
                                       xanchor="right", yanchor="top", showarrow=False,
                                       font=dict(LABEL_FONT, size=11), row=r, col=col)
                if p == 0:
                    fig.add_annotation(text=f"<b>{country}</b>", x=0.05, y=0.97, xref="x domain", yref="y domain",
                                       xanchor="left", yanchor="top", showarrow=False, font=LABEL_FONT, row=r, col=col)
                if r == 1:
                    fig.add_annotation(text=BANDS[p].replace("-", "–"), x=0.5, y=1.0, xref="x domain",
                                       yref="y domain", yanchor="bottom", showarrow=False,
                                       font=dict(LABEL_FONT, size=12), row=r, col=col)
                last = r == nrows or (r == nrows - 1 and g >= len(grid[-1]))
                fig.update_xaxes(range=[min(years) - 0.5, max(years) + 0.5], tickvals=[2010, 2015, 2020],
                                 tickangle=-90, showticklabels=last, row=r, col=col)
                fig.update_yaxes(range=list(RATE_RANGE), dtick=100, showticklabels=col == 1, row=r, col=col)
    height = row_height * nrows + 170
    fig.update_layout(template="plotly_white", height=height,
                      title=dict(text="Birth rate by year, age and education, births per 1,000 women",
                                 y=1 - 25 / height, yref="container"),
                      legend=dict(orientation="h", x=0, xanchor="left", y=1 - 50 / height, yref="container",
                                  yanchor="top"),
                      margin=dict(l=50, r=30, t=110, b=60))
    return fig


def main():
    rows = load()
    us, rest = rows[0], rows[1:]
    us_title = "United States, births per 1,000 women not in school"
    figs = {
        "education_curves_facet.html": facet(rest),
        "education_curves_facet_change.html": facet(rest, change=True),
        "education_by_year_facet.html": year_facet(rows),
        "education_curves_us.html": facet([us], per_row=1, row_height=300,
                                          title=f"Birth rate by age and education, {us_title}"),
    }
    out = outputs_dir("eurostat")
    for name, fig in figs.items():
        write_html(fig, out / name, height=f"{fig.layout.height}px")
    print(f"{len(rest)} countries plus the US")


if __name__ == "__main__":
    main()
