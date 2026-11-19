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
The Table 3 loaders and hazard calculation live in common/ons_table3.py,
shared with HFD/scripts/cond_asfr_facet.py and the coupling charts.
"""

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.ons_table3 import load_cohort_cumulative, load_cohort_rates, load_period_rates
from common.paths import outputs_dir
from common.plot_colors import COHORT_COLORSCALE, PERIOD_COLORSCALE, cohort_axis, period_axis
from common.plotting import range_post_script, write_html

OUTDIR = outputs_dir("ONS")
OUTPUT = OUTDIR / "cond_asfr_uk_ons.html"
COHORT_OUTPUT = OUTDIR / "cond_asfr_uk_ons_cohort.html"
CUMULATIVE_OUTPUT = OUTDIR / "cond_asfr_uk_ons_cumulative.html"


def plot(
    by_period,
    group_label="Year",
    title="Conditional (parity-progression) ASFR, England & Wales — derived from ONS cohort table 3",
    subplot_titles=("First birth", "Second birth"),
    y_title="Conditional ASFR (%)",
    y_range=(0, 25),
    value_scale=100,
    colorscale=PERIOD_COLORSCALE,
    caxis=None,
):
    """Returns (fig, trace_groups): trace_groups[i] is the group key (period
    year, or cohort — see plot_cohort()) of fig.data[i], or None for traces
    (e.g. the colorbar dummy) that should stay visible regardless of any
    range filter applied to the figure. value_scale multiplies the raw
    values before plotting — 100 for the hazard rates (stored as 0-1
    fractions), 1 for the cumulative P1/P2 values (already 0-100 percentages
    in ONS's table). caxis is the (min, max) color axis range — the
    period axis for the data by default, cohort_axis() for plot_cohort()/
    plot_cumulative_cohort() (see plot_colors.py).
    """
    groups = sorted(by_period)
    cmap_min, cmap_max = caxis if caxis is not None else period_axis(min(groups), max(groups))
    trace_groups = []

    fig = make_subplots(rows=1, cols=2, subplot_titles=subplot_titles)

    for group in groups:
        ages = sorted(by_period[group])
        v1 = [by_period[group][a][0] for a in ages]
        v2 = [by_period[group][a][1] for a in ages]
        color = _year_color(group, cmap_min, cmap_max, colorscale)
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
                colorscale=colorscale, cmin=cmap_min, cmax=cmap_max,
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
        colorscale=COHORT_COLORSCALE,
        caxis=cohort_axis(min(by_cohort_rates), max(by_cohort_rates)),
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
        colorscale=COHORT_COLORSCALE,
        caxis=cohort_axis(min(by_cohort_cumulative), max(by_cohort_cumulative)),
    )


def _year_color(year, ymin, ymax, colorscale):
    t = 0.0 if ymax == ymin else (year - ymin) / (ymax - ymin)
    t = min(1.0, max(0.0, t))  # clip: groups outside [ymin, ymax] clamp to the end color
    return pc.sample_colorscale(colorscale, [t])[0]


def _write_range_chart(fig, trace_groups, output_path):
    write_html(fig, output_path, post_script=range_post_script(trace_groups))


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
