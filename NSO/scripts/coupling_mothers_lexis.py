"""Women living with a spouse or partner against women with a child (Denmark, Finland,
the Netherlands: the national registers with single years of age, see coupling_nso.py).

Quantile ages, per country: the age by which 20%, 40% and 60% of women live with a
partner (top panel) and have had a child (bottom panel), on a shared x axis. Drawn twice:
by calendar year, and by birth cohort (cohort = year - age, so a point follows the same
women as they age). A cohort's quantile age needs the share observed below the level at
some age and reaching it later; cohorts too old (first observed above the level) or too
young (not reached it yet) are left out. Dotted guides mark the other time dimension:
calendar years by cohort, cohorts by year.

Trend arrows (common/trend_arrows.py): % in a couple (x) against % with a child (y), one
arrow per country and age: ages 25, 30 and 35 for Denmark, Finland and the Netherlands
(coloured by country), and a separate US chart for 18-24 and 25-34 (the only CPS ages).

% with a child: 100 - childless women's share of all female exposure at that age and year
(HFD exposRRpa.txt), as in common/coupling_hfd.py.

Outputs: NSO/outputs/coupling_mothers_ages_<country>.html (by year),
coupling_mothers_ages_cohort_<country>.html (by birth cohort), coupling_mothers_trends.html
and coupling_mothers_trends_us.html (trend arrows).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.coupling_hfd import _read_hfd
from common.plotting import write_html
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows
from coupling_nso import COLORS, OUTDIR, denmark, finland, netherlands, us

COUNTRIES = {"Denmark": ("DNK", denmark), "Finland": ("FIN", finland), "Netherlands": ("NLD", netherlands)}
AGES = list(range(18, 46))
QUANTILES = [20, 40, 60]
Q_COLORS = {20: "#e66101", 40: "#1b9e77", 60: "#5e3c99"}


def mothers(code):
    e = _read_hfd("exposRRpa.txt", ["code", "year", "age", "E0x", "E1x", "E2x", "E3x", "E4px"])
    e = e[(e.code == code) & e.age.isin(AGES)]
    e["mother"] = 100 - 100 * e.E0x / e[["E0x", "E1x", "E2x", "E3x", "E4px"]].sum(axis=1)
    return e.pivot(index="age", columns="year", values="mother")


def couples(load):
    d = load()
    d = d[(d.sex == "Women") & d.age.isin(AGES)]
    return (100 * d.couple / d["pop"]).set_axis(pd.MultiIndex.from_frame(d[["age", "year"]])).unstack("year")


def to_cohort(grid):
    """age x year -> age x birth cohort (year - age)."""
    d = grid.stack().rename("v").reset_index()
    d["cohort"] = (d.year - d.age).astype(int)
    return d.pivot(index="age", columns="cohort", values="v")


def age_at(grid, q):
    """Per column (year or cohort), the age at which the share first reaches q, linearly interpolated
    between single ages; None where it never does."""
    out = []
    for y in grid.columns:
        s = grid[y].dropna()
        hit = s[s >= q]
        if hit.empty or hit.index[0] == s.index[0]:
            out.append(None)
            continue
        a1 = hit.index[0]
        a0 = s.index[s.index.get_loc(a1) - 1]
        v0, v1 = s[a0], s[a1]
        out.append(float(a0 + (q - v0) / (v1 - v0) * (a1 - a0)))
    return out


def quantile_lines(cp, mo):
    """[(grid label, q, ages per column)] for both grids and every level."""
    mo = mo.reindex(columns=cp.columns)
    return [(label, q, age_at(grid, q)) for grid, label in [(cp, "in a couple"), (mo, "with a child")]
            for q in QUANTILES]


def box(cols, lines):
    """Axis ranges around every plotted point."""
    pts = [(x, y) for _, _, ys in lines for x, y in zip(cols, ys) if y is not None]
    return (min(p[0] for p in pts) - 1, max(p[0] for p in pts) + 1,
            int(min(p[1] for p in pts)) - 1, int(max(p[1] for p in pts)) + 2)


def diagonals(fig, cp, xlab, rng, rows):
    """Dotted guides for the other time dimension, every 5 years, within the data's range.
    x = cohort: calendar years, age = year - cohort. x = year: cohorts, age = year - cohort."""
    x0, x1, y0, y1 = rng
    obs = cp.stack().reset_index()
    age, col = obs.iloc[:, 0], obs.iloc[:, 1]
    by_cohort = xlab != "Year"
    ks = (age + col) if by_cohort else (col - age)
    for k in range(5 * ((int(ks.min()) + 4) // 5), int(ks.max()) + 1, 5):
        if by_cohort:  # age = k - x, falling
            xa, xb = max(x0, k - y1), min(x1, k - y0)
            ya, yb, label = k - xa, k - xb, str(k)
        else:  # age = x - k, rising
            xa, xb = max(x0, k + y0), min(x1, k + y1)
            ya, yb, label = xa - k, xb - k, f"born {k}"
        if xa >= xb:
            continue
        for row in rows:
            kw = dict(row=row, col=1) if len(rows) > 1 else {}
            fig.add_trace(go.Scatter(x=[xa, xb], y=[ya, yb], mode="lines", showlegend=False, hoverinfo="skip",
                                     line=dict(color="#bbbbbb", width=1, dash="dot")), **kw)
            # Label the upper end of each guide.
            lx, ly = (xa, ya) if by_cohort else (xb, yb)
            fig.add_annotation(x=lx, y=ly, text=label, showarrow=False, yanchor="bottom",
                               xanchor="left" if by_cohort else "right", font=dict(size=10, color="#999999"), **kw)
    fig.update_xaxes(range=[x0, x1])
    fig.update_yaxes(range=[y0, y1])


def _hover(xlab, q, label):
    return ("Born " if xlab != "Year" else "") + f"%{{x}}: {q}% of women {label} by age %{{y:.1f}}<extra></extra>"


def ages_chart(name, cp, mo, xlab="Year"):
    """In a couple above, with a child below; shared x axis and the same age scale, so a
    level's line can be compared straight down."""
    cols = list(cp.columns)
    lines = quantile_lines(cp, mo)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=("In a couple", "With a child"))
    for label, q, ys in lines:
        row = 1 if label == "in a couple" else 2
        fig.add_trace(go.Scatter(
            x=cols, y=ys, mode="lines", name=f"{q}% of women", legendgroup=str(q),
            showlegend=row == 1, line=dict(color=Q_COLORS[q], width=2.5),
            hovertemplate=_hover(xlab, q, label)), row=row, col=1)
    diagonals(fig, cp, xlab, box(cols, lines), rows=(1, 2))
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        title=dict(text=f"{name}: age by which 20%, 40% and 60% of women are in a couple, and have a child",
                   x=0.01, font=dict(size=14)),
        margin=dict(t=60, r=20, l=60, b=50))
    fig.update_yaxes(title_text="Age", matches="y")
    fig.update_xaxes(title_text=xlab, row=2, col=1)
    return fig


SCATTER_AGES = [25, 30, 35]
AGE_COLORS = {25: "#e66101", 30: "#1b9e77", 35: "#5e3c99", "18-24": "#e7298a", "25-34": "#666666"}
US_BANDS = {"18-24": (18, 24), "25-34": (25, 34)}


def us_series():
    """US: CPS couple shares for 18-24 and 25-34 (no single ages), and HFD % with a child
    pooled over the same ages."""
    c = us()
    c = c[c.sex == "Women"].pivot(index="age", columns="year", values="share")
    e = _read_hfd("exposRRpa.txt", ["code", "year", "age", "E0x", "E1x", "E2x", "E3x", "E4px"])
    e = e[e.code == "USA"]
    e["all"] = e[["E0x", "E1x", "E2x", "E3x", "E4px"]].sum(axis=1)
    m = {}
    for band, (lo, hi) in US_BANDS.items():
        g = e[e.age.between(lo, hi)].groupby("year")[["E0x", "all"]].sum()
        m[band] = 100 - 100 * g.E0x / g["all"]
    return c, pd.DataFrame(m).T


CODES = {"Denmark": "DK", "Finland": "FI", "Netherlands": "NL", "US": "US"}
COUNTRY_COLORS = {name: COLORS[name] for name in ("Denmark", "Finland", "Netherlands")}


def arrow_series(name, cp, mo, ages):
    """Trend-arrow series (common/trend_arrows.py) for one country: one per age. Single
    ages are coloured and grouped by country (age goes in an annotation by each cluster);
    the US age groups are coloured and grouped by age group."""
    out = []
    for a in ages:
        if a not in cp.index or a not in mo.index:
            continue
        x, y = cp.loc[a], mo.loc[a]
        yrs = sorted(set(x.dropna().index) & set(y.dropna().index))
        if len(yrs) < 3:
            continue
        band = isinstance(a, str)
        age = f"aged {a}" if band else f"age {a}"
        out.append({"name": f"{name}, {age}", "label": a if band else CODES[name],
                    "group": f"Aged {a} (US)" if band else name, "age": a,
                    "color": AGE_COLORS[a] if band else COUNTRY_COLORS[name], "years": [int(t) for t in yrs],
                    "x": {"couple": [float(x[t]) for t in yrs]}, "y": {"mother": [float(y[t]) for t in yrs]}})
    return out


if __name__ == "__main__":
    arrows = []
    for name, (code, load) in COUNTRIES.items():
        cp, mo = couples(load), mothers(code)
        slug = name.lower()
        write_html(ages_chart(name, cp, mo), OUTDIR / f"coupling_mothers_ages_{slug}.html")
        arrows += arrow_series(name, cp, mo, SCATTER_AGES)
        # Cohorts: every cohort with a couple share at some age in 18-45.
        cc, mc = to_cohort(cp), to_cohort(mo)
        mc = mc.reindex(columns=cc.columns)
        write_html(ages_chart(name, cc, mc, "Birth cohort"), OUTDIR / f"coupling_mothers_ages_cohort_{slug}.html")
        print(name, "cohorts", {q: [(c, round(a, 1)) for c, a in zip(cc.columns, age_at(cc, q)) if a is not None][::8]
                                for q in QUANTILES})
        y0, y1 = cp.columns[0], cp.columns[-1]
        print(name, y0, y1, {q: (age_at(cp[[y0, y1]], q), age_at(mo.reindex(columns=[y0, y1]), q)) for q in QUANTILES})
    uc, um = us_series()
    # Both axes are % of women: one percentage point is the same length on each.
    kw = dict(x_suffix="%", y_suffix="%", layout=dict(yaxis=dict(scaleanchor="x", scaleratio=1)))
    # Age labels: left of each age's cluster of points, at its mean height.
    age_notes = []
    for a in SCATTER_AGES:
        xs = [v for s in arrows if s["age"] == a for v in s["x"]["couple"]]
        ys = [v for s in arrows if s["age"] == a for v in s["y"]["mother"]]
        age_notes.append(dict(x=min(xs) - 2, y=sum(ys) / len(ys), text=f"<b>Age {a}</b>", showarrow=False,
                              xanchor="right", font=dict(size=13, color="#444444")))
    write_trend_arrows(
        OUTDIR / "coupling_mothers_trends.html", arrows,
        {"couple": "% of women in a couple"}, {"mother": "% of women with a child"},
        title="Each country's linear trend at each age, first to latest year (points: every year)",
        **{**kw, "layout": {**kw["layout"], "annotations": age_notes}})
    # US: CPS age groups, not single ages, so a chart of its own.
    write_trend_arrows(
        OUTDIR / "coupling_mothers_trends_us.html", arrow_series("US", uc, um, list(US_BANDS)),
        {"couple": "% of women in a couple"}, {"mother": "% of women with a child"},
        title="US linear trend by age group, first to latest year (points: every year)", **kw)
    # Ratio over time: one panel per age (Denmark, Finland, Netherlands) and per US age group.
    us_arrows = [a | {"label": "US", "color": COLORS["US"]} for a in arrow_series("US", uc, um, list(US_BANDS))]
    write_ratio_lines(
        OUTDIR / "coupling_mothers_trends_ratio.html", arrows,
        [{"x": "couple", "y": "mother", "title": f"Age {a}", "series": [s for s in arrows if s["age"] == a]}
         for a in SCATTER_AGES]
        + [{"x": "couple", "y": "mother", "title": f"US, aged {b}", "series": [s for s in us_arrows if s["age"] == b]}
           for b in US_BANDS],
        title="% of women with a child ÷ % in a couple, by year", cols=3, height=750)
