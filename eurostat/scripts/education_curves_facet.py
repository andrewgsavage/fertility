"""Birth rate by age and mother's education, every country in one facet grid, in the layout of the
first vs second birth chart (HFD/scripts/cond_asfr_facet.py): a group of education panels per
country (three levels; four for the US), three countries per row, a thin line per year coloured on
the period scale, the country name inside its first panel.

Reads the curves the per-source scripts write:
  eurostat/outputs/fertility_by_education_nordic_by_age.csv   (fertility_by_education_nordic.py)
  eurostat/outputs/fertility_by_education_europe_curves.csv   (fertility_by_education_europe_curves.py)
  NSO/outputs/{mexico,brazil}_fertility_by_education.csv      (mexico/brazil_births_by_education.py)
  ACS/outputs/fertility_by_education_us_curves.csv            (ACS fertility_by_education_us.py)
Rates by 5-year age group are drawn at the band's middle; the US has single years of age.

Writes eurostat/outputs/education_curves_facet.html (births per 1,000 women) and
education_curves_facet_change.html (each rate over the same country's mean in its first three
years at that age, on a log axis; cells with a base under 5 per 1,000 dropped).
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
NORDIC = ["FI", "SE", "DK", "NO"]
EUROPE_ORDER = ["EE"]  # the one register series first, then alphabetical


def mid(band):
    lo, hi = band.str.split("-").str[0].astype(int), band.str.split("-").str[1].astype(int)
    return (lo + hi) / 2


def load():
    """Rows of (country, sublabel, level labels, long frame with level, year, x, rate)."""
    out = []
    n = pd.read_csv(outputs_dir("eurostat") / "fertility_by_education_nordic_by_age.csv")
    cols = ["Lower secondary or less", "Upper secondary", "Tertiary"]
    for g in NORDIC:
        d = n[n.geo == g].melt(["year", "age"], cols, "level", "rate").assign(x=lambda t: mid(t.age))
        d["level"] = d.level.map(dict(zip(cols, LEVELS3)))
        out.append((NAMES[g], "register", LEVELS3, d))
    e = pd.read_csv(outputs_dir("eurostat") / "fertility_by_education_europe_curves.csv")
    geos = EUROPE_ORDER + sorted(set(e.geo) - set(EUROPE_ORDER), key=lambda g: NAMES[g])
    for g in geos:
        d = e[e.geo == g].melt(["year", "age"], ["low", "medium", "tertiary"], "level", "rate")
        d["level"] = d.level.map(dict(zip(["low", "medium", "tertiary"], LEVELS3)))
        out.append((NAMES[g], "register" if g == "EE" else "births / LFS women", LEVELS3, d.assign(x=mid(d.age))))
    for code, name in [("mexico", "Mexico"), ("brazil", "Brazil")]:
        d = pd.read_csv(outputs_dir("NSO") / f"{code}_fertility_by_education.csv")
        d = d[d.ed != "all"].assign(rate=lambda t: t.rate * 1000, x=lambda t: mid(t.age))
        d["level"] = d.ed.map(dict(zip(["low", "medium", "tertiary"], LEVELS3)))
        out.append((name, "births / survey women", LEVELS3, d))
    u = pd.read_csv(outputs_dir("ACS") / "fertility_by_education_us_curves.csv")
    u = u[~((u.education == "Bachelor's or more") & (u.age < 21))]
    u = u.assign(level=u.education.map(dict(US_LEVELS)), x=u.age)
    out.insert(0, ("United States", "ACS, not in school", [s for _, s in US_LEVELS], u))
    return [(c, s, lv, d[["level", "year", "x", "rate"]].dropna()) for c, s, lv, d in out]


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


def group_domains(k):
    """x domains of the k panels of each of the GROUPS_PER_ROW country groups in a row."""
    gw = (1 - (GROUPS_PER_ROW - 1) * BETWEEN_GAP) / GROUPS_PER_ROW
    pw = (gw - (k - 1) * WITHIN_GAP) / k
    return [[(g * (gw + BETWEEN_GAP) + p * (pw + WITHIN_GAP), g * (gw + BETWEEN_GAP) + p * (pw + WITHIN_GAP) + pw)
             for p in range(k)] for g in range(GROUPS_PER_ROW)]


def facet(rows, change=False):
    years = [int(y) for _, _, _, d in rows for y in d.year]
    axis = period_axis(min(years), max(years))
    grid = [rows[i:i + GROUPS_PER_ROW] for i in range(0, len(rows), GROUPS_PER_ROW)]
    nrows = len(grid)
    fig = make_subplots(rows=nrows, cols=GROUPS_PER_ROW * SLOTS, horizontal_spacing=0.001,
                        vertical_spacing=min(0.012, 1 / max(nrows - 1, 1)))
    for r, line in enumerate(grid, start=1):
        for g, (country, sub, levels, d) in enumerate(line):
            if change:
                d, base_years = add_change(d)
            doms = group_domains(len(levels))[g]
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
                        hovertemplate=f"{country}, {lv}<br>{int(y)}, age %{{x}}<br>{val}<extra></extra>",
                    ), row=r, col=col)
                if p == 0:
                    fig.add_annotation(text=f"<b>{country}</b>", x=0.05, y=0.97, xref="x domain", yref="y domain",
                                       xanchor="left", yanchor="top", showarrow=False, font=LABEL_FONT, row=r, col=col)
                    fig.add_annotation(text=sub + (f", vs {base_years}" if change else ""), x=0.05, y=0.8,
                                       xref="x domain", yref="y domain", xanchor="left", yanchor="top",
                                       showarrow=False, font=dict(LABEL_FONT, size=10, color="#666"), row=r, col=col)
                if levels is not LEVELS3 or r == 1:  # level names: top row, and on the US's own panels
                    fig.add_annotation(text=lv, x=0.5, y=1.0, xref="x domain", yref="y domain", yanchor="bottom",
                                       showarrow=False, font=dict(LABEL_FONT, size=12 if levels is LEVELS3 else 10), row=r, col=col)
                fig.update_xaxes(range=[18, 44], tickvals=[25, 40], tickangle=0, showticklabels=r == nrows or r == nrows - 1 and g >= len(grid[-1]),
                                 row=r, col=col)
                if change:
                    fig.update_yaxes(type="log", range=[math.log10(v) for v in CHANGE_RANGE], tickvals=CHANGE_TICKS,
                                     ticktext=[f"{t - 1:+.0%}" if t != 1 else "0%" for t in CHANGE_TICKS],
                                     showticklabels=col == 1, row=r, col=col)
                else:
                    fig.update_yaxes(range=list(RATE_RANGE), dtick=100, showticklabels=col == 1, row=r, col=col)
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", showlegend=False,
                             marker=dict(colorscale=PERIOD_COLORSCALE, cmin=axis[0], cmax=axis[1], color=[axis[0]],
                                         showscale=True, colorbar=dict(title="Year", len=min(1, 600 / (ROW_HEIGHT * nrows)),
                                                                       y=1, yanchor="top"))), row=1, col=1)
    title = ("Change in birth rate by age and education since each country's first three years (log scale)" if change
             else "Birth rate by age and education, births per 1,000 women")
    fig.update_layout(template="plotly_white", title=title, height=ROW_HEIGHT * nrows + 130, showlegend=False,
                      margin=dict(l=50, r=80, t=90, b=40))
    return fig


def main():
    rows = load()
    out = outputs_dir("eurostat")
    for path, change in [(out / "education_curves_facet.html", False), (out / "education_curves_facet_change.html", True)]:
        fig = facet(rows, change)
        write_html(fig, path, height=f"{fig.layout.height}px")
    print(f"{len(rows)} countries")


if __name__ == "__main__":
    main()
