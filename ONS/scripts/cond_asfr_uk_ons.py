"""Approximate conditional (parity-progression) ASFR for first and second
births in England & Wales, derived from ONS Table 3 (percentage
distribution of women by number of live-born children, by age and
year of birth). HFD has no conditional-ASFR tables for the UK, so this
reconstructs the equivalent from ONS's cohort parity-stock data.

At each exact age, the conditional rate is estimated as a discrete hazard:
  cond1(age) = (P1(age) - P1(age-1)) / (100 - P1(age-1))
  cond2(age) = (P2(age) - P2(age-1)) / (P1(age-1) - P2(age-1))
where P1/P2 are cumulative % of the cohort with >=1 / >=2 children.

Plotted lines are period years (calendar year the transition occurred:
cohort + age), filtered to MIN_PERIOD_YEAR onwards, matching HFD's chart
convention even though the hazard itself is computed along each cohort.
"""

import pathlib

import openpyxl
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Resolved relative to this file (not cwd) so load_table3()/load_period_rates()
# work whether this module is run directly (cwd=ONS/) or imported from
# elsewhere (e.g. HFD/scripts/cond_asfr_region_grid.py, cwd=HFD/) to fold the
# UK into the Western Europe region grid as an extra column.
_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SOURCE = _SCRIPT_DIR.parent / "data" / "finalisingcohorttables2024finalforupload.xlsx"
OUTPUT = "outputs/cond_asfr_uk_ons.html"
MIN_PERIOD_YEAR = 2005


def load_table3():
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    ws = wb["Table 3"]
    rows = list(ws.iter_rows(values_only=True))[9:]

    by_cohort = {}
    for year, age, pct0, pct1, pct2, pct3, pct4plus, *_ in rows:
        if year is None or age == "Final":
            continue
        p1 = 100 - pct0
        p2 = pct2 + pct3 + pct4plus
        by_cohort.setdefault(year, {})[age] = (p1, p2)
    return by_cohort


def conditional_rates(by_cohort):
    """cohort -> {age: (cond1, cond2)}, skipping the first age each cohort has."""
    result = {}
    for cohort, ages in by_cohort.items():
        sorted_ages = sorted(ages)
        cohort_rates = {}
        for prev_age, age in zip(sorted_ages, sorted_ages[1:]):
            if age != prev_age + 1:
                continue
            p1_prev, p2_prev = ages[prev_age]
            p1, p2 = ages[age]
            childless_prev = 100 - p1_prev
            one_child_prev = p1_prev - p2_prev
            c1 = max(0.0, (p1 - p1_prev) / childless_prev) if childless_prev > 0 else None
            c2 = max(0.0, (p2 - p2_prev) / one_child_prev) if one_child_prev > 0 else None
            cohort_rates[age] = (c1, c2)
        result[cohort] = cohort_rates
    return result


def to_period(rates, min_period_year):
    """Reslice the cohort-hazard Lexis diagram into period-year lines: for
    period year Y and age A, the transition happened to cohort (Y - A).
    Gives one age-profile line per calendar year, like HFD's period charts,
    even though the underlying hazard is still computed along each cohort.
    """
    by_period = {}
    for cohort, ages in rates.items():
        for age, (c1, c2) in ages.items():
            period_year = cohort + age
            if period_year < min_period_year:
                continue
            by_period.setdefault(period_year, {})[age] = (c1, c2)
    return by_period


def plot(by_period):
    period_years = sorted(by_period)
    cmap_min, cmap_max = min(period_years), max(period_years)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("First birth", "Second birth"))

    for period_year in period_years:
        ages = sorted(by_period[period_year])
        cond1 = [by_period[period_year][a][0] for a in ages]
        cond2 = [by_period[period_year][a][1] for a in ages]
        color = _year_color(period_year, cmap_min, cmap_max)
        fig.add_trace(
            go.Scatter(
                x=ages, y=[c * 100 if c is not None else None for c in cond1],
                mode="lines", line=dict(width=1, color=color),
                name=str(period_year), legendgroup=str(period_year), showlegend=False,
                hovertemplate=f"Year {period_year}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=ages, y=[c * 100 if c is not None else None for c in cond2],
                mode="lines", line=dict(width=1, color=color),
                name=str(period_year), legendgroup=str(period_year), showlegend=False,
                hovertemplate=f"Year {period_year}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=2,
        )

    # Dummy trace to show a colorbar for period year.
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=cmap_min, cmax=cmap_max,
                color=[cmap_min], showscale=True,
                colorbar=dict(title="Year"),
            ),
            showlegend=False,
        ),
        row=1, col=2,
    )

    fig.update_xaxes(title_text="Age", range=[20, 45])
    fig.update_yaxes(title_text="Conditional ASFR (%)", range=[0, 25])
    fig.update_layout(
        title="Conditional (parity-progression) ASFR, England & Wales — derived from ONS cohort table 3",
        template="plotly_white",
        width=1100, height=550,
    )
    return fig


def _year_color(year, ymin, ymax):
    t = 0.0 if ymax == ymin else (year - ymin) / (ymax - ymin)
    return pc.sample_colorscale("Turbo", [t])[0]


def load_period_rates(min_period_year=MIN_PERIOD_YEAR):
    """{period_year: {age: (cond1, cond2)}} — the reusable entry point for
    other scripts (see HFD/scripts/cond_asfr_region_grid.py, which folds
    this into the Western Europe region grid as a "UK_ONS" column)."""
    by_cohort = load_table3()
    rates = conditional_rates(by_cohort)
    return to_period(rates, min_period_year)


if __name__ == "__main__":
    by_period = load_period_rates()
    fig = plot(by_period)
    fig.write_html(OUTPUT, include_plotlyjs="cdn")
    print(f"Saved {OUTPUT}")
