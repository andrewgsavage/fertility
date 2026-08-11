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
cohort + age). The standalone HTML output is unfiltered — a pair of
min/max range-slider inputs in the page let the viewer restrict which
years are shown client-side, via Plotly.restyle on trace visibility.
load_period_rates()'s own MIN_PERIOD_YEAR default (used by callers like
HFD/scripts/cond_asfr_region_grid.py) is unchanged.
"""

import json
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
COHORT_OUTPUT = "outputs/cond_asfr_uk_ons_cohort.html"
CUMULATIVE_OUTPUT = "outputs/cond_asfr_uk_ons_cumulative.html"
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


def plot(
    by_period,
    group_label="Year",
    title="Conditional (parity-progression) ASFR, England & Wales — derived from ONS cohort table 3",
    subplot_titles=("First birth", "Second birth"),
    y_title="Conditional ASFR (%)",
    y_range=(0, 25),
    value_scale=100,
):
    """Returns (fig, trace_groups): trace_groups[i] is the group key (period
    year, or cohort — see plot_cohort()) of fig.data[i], or None for traces
    (e.g. the colorbar dummy) that should stay visible regardless of any
    range filter applied to the figure. value_scale multiplies the raw
    values before plotting — 100 for the hazard rates (stored as 0-1
    fractions), 1 for the cumulative P1/P2 values (already 0-100 percentages
    in ONS's table).
    """
    groups = sorted(by_period)
    cmap_min, cmap_max = min(groups), max(groups)
    trace_groups = []

    fig = make_subplots(rows=1, cols=2, subplot_titles=subplot_titles)

    for group in groups:
        ages = sorted(by_period[group])
        v1 = [by_period[group][a][0] for a in ages]
        v2 = [by_period[group][a][1] for a in ages]
        color = _year_color(group, cmap_min, cmap_max)
        fig.add_trace(
            go.Scatter(
                x=ages, y=[v * value_scale if v is not None else None for v in v1],
                mode="lines", line=dict(width=1, color=color),
                name=str(group), legendgroup=str(group), showlegend=False,
                hovertemplate=f"{group_label} {group}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=ages, y=[v * value_scale if v is not None else None for v in v2],
                mode="lines", line=dict(width=1, color=color),
                name=str(group), legendgroup=str(group), showlegend=False,
                hovertemplate=f"{group_label} {group}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=2,
        )
        trace_groups.extend([group, group])

    # Dummy trace to show a colorbar for the group axis.
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=cmap_min, cmax=cmap_max,
                color=[cmap_min], showscale=True,
                colorbar=dict(title=group_label),
            ),
            showlegend=False,
        ),
        row=1, col=2,
    )
    trace_groups.append(None)

    fig.update_xaxes(title_text="Age", range=[20, 45])
    fig.update_yaxes(title_text=y_title, range=list(y_range))
    fig.update_layout(title=title, template="plotly_white", autosize=True)
    return fig, trace_groups


def plot_cohort(by_cohort_rates):
    """Same chart as plot(), colored/grouped by birth cohort instead of
    period year — uses conditional_rates()'s cohort-indexed output
    directly (no to_period() reslicing), since the hazard is naturally
    computed along each cohort in the first place."""
    return plot(
        by_cohort_rates,
        group_label="Cohort",
        title="Conditional (parity-progression) ASFR, England & Wales — by birth cohort, derived from ONS cohort table 3",
    )


def plot_cumulative_cohort(by_cohort_cumulative):
    """Cumulative % of the cohort with >=1 / >=2 children by age (P1/P2 —
    the raw ONS table values, before differencing into the conditional
    hazard that plot_cohort() shows) — colored by birth cohort, using
    load_table3()'s cohort-indexed output directly (no reslicing needed,
    same as plot_cohort())."""
    return plot(
        by_cohort_cumulative,
        group_label="Cohort",
        title="Cumulative % with 1+ / 2+ children by age, England & Wales — by birth cohort, ONS cohort table 3",
        subplot_titles=("Cumulative first births", "Cumulative second births"),
        y_title="Cumulative %",
        y_range=(0, 100),
        value_scale=1,
    )


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


def load_cohort_cumulative():
    """{cohort: {age: (P1, P2)}} — the cumulative % of the cohort with
    >=1 / >=2 children, i.e. load_table3()'s raw values directly (already
    cohort-indexed, like load_cohort_rates()). For plot_cumulative_cohort().
    """
    return load_table3()


def load_cohort_rates():
    """{cohort: {age: (cond1, cond2)}} — the cohort-indexed counterpart to
    load_period_rates(), for plot_cohort()."""
    by_cohort = load_table3()
    return conditional_rates(by_cohort)


# No in-iframe UI — the range control lives in the containing docs page
# (outside the iframe, see docs/uk/cond-asfr.md / later-births.md) so one
# control can drive several of these charts at once. This just exposes the
# filtering itself as window.setRange(lo, hi) for that external control to
# call via each iframe's contentWindow.
RANGE_POST_SCRIPT = """
var gd = document.getElementById('{plot_id}');
var traceGroups = __TRACE_GROUPS__;
window.setRange = function (lo, hi) {
    var visible = traceGroups.map(function (g) { return g === null ? true : (g >= lo && g <= hi); });
    Plotly.restyle(gd, {visible: visible});
};
"""


def _write_range_chart(fig, trace_groups, output_path):
    post_script = RANGE_POST_SCRIPT.replace("__TRACE_GROUPS__", json.dumps(trace_groups))
    fig.write_html(
        output_path,
        include_plotlyjs="cdn",
        full_html=True,
        post_script=post_script,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    # write_html's own template doesn't stretch <html>/<body> to fill the
    # iframe — without an external UI panel pushing content down (unlike
    # before), height:100% now works the same way build_plotly_map.py uses
    # it. See that script for the fuller explanation.
    html = open(output_path, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(output_path, "w", encoding="utf-8").write(html)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    by_period = load_period_rates(min_period_year=0)
    fig, trace_groups = plot(by_period)
    _write_range_chart(fig, trace_groups, OUTPUT)

    by_cohort = load_cohort_rates()
    fig_cohort, trace_groups_cohort = plot_cohort(by_cohort)
    _write_range_chart(fig_cohort, trace_groups_cohort, COHORT_OUTPUT)

    by_cohort_cumulative = load_cohort_cumulative()
    fig_cumulative, trace_groups_cumulative = plot_cumulative_cohort(by_cohort_cumulative)
    _write_range_chart(fig_cumulative, trace_groups_cumulative, CUMULATIVE_OUTPUT)
