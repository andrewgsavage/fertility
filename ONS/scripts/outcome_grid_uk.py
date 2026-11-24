"""Outcome grid for England & Wales: which of the nine stage x channel cells
(couple / first child / second+ child  x  desire / age / ability) moved
between 2010 and 2022.

Measured series:
- Coupling: share of women living in a couple by age group (ONS
  population estimates by marital status and living arrangements, LFS).
- First child and second+: synthetic-cohort summaries from period
  parity-progression hazards, rebuilt from ONS cohort Table 3 the same way
  as mdf_uk_ons.py, but starting each synthetic cohort from the parity mix
  at age 20 of the cohort turning 20 that year (so births under 21 count).

Desire cells come from published surveys and are typed into the docs page;
there is no annual series to compute here.

Run with cwd = ONS/.
"""

import csv
import pathlib
import sys

import openpyxl
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import ons_mdf as m  # noqa: E402
from common.ons_table3 import load_table3_shares  # noqa: E402

LIVING = pathlib.Path("data/families/maritalstatuslivingarrangements2002to2025englandandwales.xlsx")
OUT_HTML = "outputs/outcome_grid_uk.html"
OUT_CSV = "outputs/outcome_grid_uk.csv"
YEARS = range(2005, 2025)
BASE, END = 2010, 2022
COUPLE_AGES = ["16 to 29", "30 to 34", "35 to 39", "40 to 44"]

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, GRID = "#1f2328", "#6b7280", "#e5e7eb"


def couple_shares():
    """{age_group: {year: share of women living in a couple}} from Table 6."""
    wb = openpyxl.load_workbook(LIVING, read_only=True, data_only=True)
    rows = list(wb["6"].iter_rows(values_only=True))
    header = rows[9]
    year_col = {int(h.split()[0]): i for i, h in enumerate(header) if h and str(h).endswith("Estimate")}
    totals, couple = {}, {}
    for r in rows[10:]:
        cat, age = r[0], r[1]
        if cat is None or age not in COUPLE_AGES:
            continue
        for year, col in year_col.items():
            v = r[col]
            if not isinstance(v, (int, float)):
                continue
            totals.setdefault(age, {}).setdefault(year, 0)
            totals[age][year] += v
            if cat.startswith("Living in a couple"):
                couple.setdefault(age, {}).setdefault(year, 0)
                couple[age][year] += v
    return {a: {y: couple[a][y] / totals[a][y] for y in couple[a]} for a in couple}


def parity_metrics(by_ages=()):
    """{year: dict} synthetic-cohort summaries for each period year; by_ages adds first_by_<age>."""
    shares = load_table3_shares()
    hazards = m._reslice_to_period({c: m._hazards(s) for c, s in shares.items()})
    out = {}
    for year, age_h in hazards.items():
        start = shares.get(year - 20, {}).get(20)
        if start is None or any(a not in age_h for a in range(m.MIN_AGE, m.MAX_AGE + 1)):
            continue
        p0, p1, p2, p3, p4 = (x / 100 for x in start)
        s = [p0, p1, p2, p3, p4]
        # births before 21 are placed at age 19 for the mean-age calculations
        first_age_sum, second_age_sum = 19 * (1 - p0), 19 * (p2 + p3 + p4)
        first_by_30 = None
        first_by = {}
        for age in range(m.MIN_AGE, m.MAX_AGE + 1):
            q1, q2, q3, q4 = age_h[age]
            new1, new2 = s[0] * q1, s[1] * q2
            first_age_sum += age * new1
            second_age_sum += age * new2
            s = [s[0] - new1, s[1] - new2 + new1, s[2] * (1 - q3) + new2, s[3] * (1 - q4) + s[2] * q3, s[4] + s[3] * q4]
            if age == 30:
                first_by_30 = 1 - s[0]
            if age in by_ages:
                first_by[f"first_by_{age}"] = 1 - s[0]
        tmr = 1 - s[0]
        two_plus = s[2] + s[3] + s[4]
        tfr = s[1] + 2 * s[2] + 3 * s[3] + m.VALUE_4PLUS * s[4]
        out[year] = {
            "first_by_30": first_by_30,
            "ever_mother_by_45": tmr,
            "mean_age_first": first_age_sum / tmr,
            "mothers_with_2plus": two_plus / tmr,
            "mean_age_second": second_age_sum / two_plus,
            "children_per_mother": tfr / tmr,
            "tfr_synthetic": tfr,
            **first_by,
        }
    return out


def main():
    couples = couple_shares()
    parity = parity_metrics()

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["series", "year", "value"])
        for age, by_year in couples.items():
            for y in sorted(by_year):
                w.writerow([f"women in a couple, {age}", y, round(by_year[y], 4)])
        for y in sorted(parity):
            for k, v in parity[y].items():
                w.writerow([k, y, round(v, 4)])

    for label, a, b in [
        ("in couple 16-29", couples["16 to 29"].get(BASE), couples["16 to 29"].get(END)),
        ("in couple 30-34", couples["30 to 34"].get(BASE), couples["30 to 34"].get(END)),
        ("in couple 35-39", couples["35 to 39"].get(BASE), couples["35 to 39"].get(END)),
        ("in couple 40-44", couples["40 to 44"].get(BASE), couples["40 to 44"].get(END)),
    ] + [(k, parity[BASE][k], parity[END][k]) for k in parity[BASE]]:
        print(f"{label:22s} {BASE}: {a:.3f}  {END}: {b:.3f}  change: {b - a:+.3f}")

    titles = [
        "Couple: desire", "Couple: age", "Couple: in a couple at 35–44 (desire + ability)",
        "First child: desire", "First child: age", "First child: ever (desire + ability)",
        "Second+: desire", "Second+: age", "Second+: mothers with 2+ (desire + ability)",
    ]
    fig = make_subplots(rows=3, cols=3, subplot_titles=titles, horizontal_spacing=0.07, vertical_spacing=0.11)
    yrs = [y for y in YEARS]

    def line(row, col, ys, name, color, fmt, label=True):
        xs = [y for y in yrs if ys.get(y) is not None]
        vals = [ys[y] for y in xs]
        fig.add_trace(go.Scatter(
            x=xs, y=vals, mode="lines", name=name, line=dict(color=color, width=2),
            hovertemplate=f"{name}<br>%{{x}}: %{{y:{fmt}}}<extra></extra>", showlegend=False,
        ), row=row, col=col)
        if label and xs:
            fig.add_annotation(x=xs[-1], y=vals[-1], text=name, showarrow=False, xanchor="left", xshift=4,
                               font=dict(size=10, color=INK), row=row, col=col)

    # Coupling age: share in a couple at 16-29 and 30-34
    line(1, 2, couples["16 to 29"], "16–29", BLUE, ".1%")
    line(1, 2, couples["30 to 34"], "30–34", ORANGE, ".1%")
    # Coupling final: 40-44
    line(1, 3, couples["35 to 39"], "35–39", BLUE, ".1%")
    line(1, 3, couples["40 to 44"], "40–44", ORANGE, ".1%")
    # First child
    line(2, 2, {y: parity[y]["mean_age_first"] for y in parity}, "Mean age", BLUE, ".1f", label=False)
    line(2, 3, {y: parity[y]["first_by_30"] for y in parity}, "By 30", BLUE, ".1%")
    line(2, 3, {y: parity[y]["ever_mother_by_45"] for y in parity}, "By 45", ORANGE, ".1%")
    # Second+
    line(3, 2, {y: parity[y]["mean_age_second"] for y in parity}, "Mean age", BLUE, ".1f", label=False)
    line(3, 3, {y: parity[y]["mothers_with_2plus"] for y in parity}, "Share of mothers", BLUE, ".1%", label=False)

    # Desire for a first child: survey points (childless 18-25, "definitely not")
    fig.add_trace(go.Scatter(
        x=[2006, 2022.5], y=[0.075, 0.15], mode="markers",
        marker=dict(size=9, color=BLUE),
        error_y=dict(type="data", array=[0.025, 0], color=BLUE, thickness=1.5, width=4),
        hovertemplate="%{x}: %{y:.0%} definitely not intending a child<extra></extra>", showlegend=False,
    ), row=2, col=1)
    fig.add_annotation(x=2014, y=0.13, text="Childless 18–25 saying<br>“definitely not”", showarrow=False,
                       font=dict(size=10, color=INK), row=2, col=1)

    for r in (1, 3):
        # invisible trace so the empty panel keeps its axes
        fig.add_trace(go.Scatter(x=[2005, 2025], y=[0, 1], mode="markers", marker=dict(opacity=0),
                                 hoverinfo="skip", showlegend=False), row=r, col=1)
        fig.add_annotation(x=2015, y=0.5, text="No UK trend series", showarrow=False,
                           font=dict(size=11, color=MUTED), row=r, col=1)

    pct_axes = {(1, 2), (1, 3), (2, 1), (2, 3), (3, 3)}
    for r in range(1, 4):
        for c in range(1, 4):
            fig.add_vrect(x0=BASE, x1=END, fillcolor="#9ca3af", opacity=0.12, line_width=0, row=r, col=c)
            fig.update_xaxes(range=[2004.5, 2026.5], showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED, size=10),
                             dtick=5, row=r, col=c)
            fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED, size=10),
                             tickformat=".0%" if (r, c) in pct_axes else None, row=r, col=c)
    fig.update_yaxes(range=[0, 0.25], row=2, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=3, col=1)
    fig.update_annotations(font_size=11)
    fig.update_layout(
        height=760, margin=dict(l=40, r=60, t=40, b=30), plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="system-ui, sans-serif", color=INK), hovermode="closest",
    )
    fig.write_html(OUT_HTML, include_plotlyjs="cdn", full_html=True)


if __name__ == "__main__":
    main()
