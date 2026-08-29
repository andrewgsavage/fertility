"""Childlessness by exact age, England & Wales (ONS cohort table 3), plotted
against year of birth, stacked above the staying-on/HE-participation panel
from pupils_leaving_age_uk.py on a shared x-axis (both use estimated birth
year), so the education expansion and the childlessness trends it may
explain can be read off the same cohort scale.
"""

import bisect
import pathlib

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import pupils_leaving_age_uk as staying_on
from cond_asfr_uk_ons import load_table3

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT = "outputs/childlessness_by_age_uk.html"

AGES = [20, 25, 30, 35, 40, 45]

AGE_COLORS = pc.qualitative.Safe
X_RANGE = [1932, 2009]


def childlessness_by_age():
    """{age: [(birth_year, pct_childless), ...]} for AGES, from ONS Table 3
    (already cohort-indexed, so no calendar-year reslicing needed)."""
    by_cohort = load_table3()
    result = {age: [] for age in AGES}
    for birth_year, ages in by_cohort.items():
        for age in AGES:
            if age in ages:
                p1, _p2 = ages[age]
                result[age].append((birth_year, 100 - p1))
    for age in AGES:
        result[age].sort()
    return result


ARROW_YEARS = (1968, 1975)


def _interp(series, x):
    """Linearly interpolate y at x from a sorted [(x, y), ...] series --
    the digitized API series is only at ~2-year resolution, so ARROW_YEARS
    won't always land on an exact digitized point."""
    exact = dict(series)
    if x in exact:
        return exact[x]
    xs = [px for px, _ in series]
    i = bisect.bisect_left(xs, x)
    (x0, y0), (x1, y1) = series[i - 1], series[i]
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def _add_trend_arrow(fig, series, x0, x1, color, label, y_offset=0, label_before=True, label_dx=0, label_dy=0):
    """Annotation arrow from (x0, y at x0) to (x1, y at x1) on a single
    trace's data in the top (childlessness) panel -- xref/yref are hardcoded
    to that panel's own axes ("x"/"y", i.e. row 1 of the shared-x subplot
    grid) since every call site here targets it. y_offset shifts both ends
    vertically by the same amount, to keep overlapping arrows (e.g. the
    childless-at-N series) visually separated; color matches the underlying
    trace's line color rather than a flat black, so each arrow reads as
    belonging to its trace. label is a format string taking the real
    (un-offset) percentage-point change as {pp}. label_before puts the
    label to the left of the arrow (right-anchored text ending at the
    arrow's tail) when True, or to the right (left-anchored text starting
    at the arrow's head) when False -- so the label sits clear of the
    arrow rather than straddling it. label_dx/label_dy nudge just the text
    (not the arrow itself) further, in data units."""
    y0_real, y1_real = _interp(series, x0), _interp(series, x1)
    y0, y1 = y0_real + y_offset, y1_real + y_offset
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2, arrowcolor=color,
        text="",
    )
    label_x, label_y, xanchor = (x0, y0, "right") if label_before else (x1, y1, "left")
    fig.add_annotation(
        x=label_x + label_dx, y=label_y + label_dy, xref="x", yref="y", xanchor=xanchor, yanchor="bottom",
        showarrow=False, text=label.format(pp=y1_real - y0_real),
        font=dict(size=11, color=color), bgcolor="rgba(255,255,255,0.75)",
    )


def plot(childless_by_age):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0,
        row_heights=[0.55, 0.45],
    )

    for i, age in enumerate(AGES):
        years, pct = zip(*childless_by_age[age])
        observed_years = [y + age for y in years]
        fig.add_trace(
            go.Scatter(
                x=years, y=pct, mode="lines", name=f"Childless at {age}",
                legend="legend", customdata=observed_years,
                line=dict(width=2, color=AGE_COLORS[i % len(AGE_COLORS)]),
                hovertemplate=f"Age {age}<br>Born %{{x}}, observed %{{customdata}}<br>%{{y:.1f}}% childless<extra></extra>",
            ),
            row=1, col=1,
        )

    staying_on.add_staying_on_traces(fig, row=2, col=1, legend="legend2")
    staying_on.add_he_traces(fig, row=2, col=1, legend="legend2")
    staying_on.add_staying_on_style_legend(fig, legend="legend3")

    for year in ARROW_YEARS:
        for row in (1, 2):
            fig.add_vline(x=year, line=dict(width=1, color="#999999", dash="dash"), row=row, col=1)
    for year in (1987, 1998):
        for row in (1, 2):
            fig.add_vline(x=year, line=dict(width=1, color="#999999", dash="dash"), row=row, col=1)

    CHILDLESS_ARROWS = {
        20: ("Static ({pp:.1f}pp) in Childless at 20", 3),
        25: ("Rise ({pp:.1f}pp) in Childless at 25", 3),
        30: ("Rise ({pp:.1f}pp) in Childless at 30", 3),
        35: ("Small rise ({pp:.1f}pp) in Childless at 35", 3),
        40: ("Static ({pp:.1f}pp) in Childless at 40", 3),
    }
    for age, (label, y_offset) in CHILDLESS_ARROWS.items():
        color = AGE_COLORS[AGES.index(age) % len(AGE_COLORS)]
        _add_trend_arrow(fig, childless_by_age[age], *ARROW_YEARS, color=color, label=label, y_offset=y_offset)

    # Flush against row 2 (vertical_spacing=0), so row 1 shows no x-axis of
    # its own -- ticks/labels only appear once, on the shared bottom axis.
    fig.update_xaxes(range=X_RANGE, showticklabels=False, row=1, col=1)
    fig.update_xaxes(title_text="Estimated year of birth", range=X_RANGE, row=2, col=1)
    fig.update_yaxes(title_text="% childless", range=[0, 100], row=1, col=1)
    fig.update_yaxes(title_text="% of age group in education", range=[0, 100], row=2, col=1)
    fig.update_layout(
        title="Childlessness by age, and staying-on/HE participation, by birth cohort",
        template="plotly_white", autosize=True,
        legend=dict(title="Childlessness", x=1.02, y=1, xanchor="left", yanchor="top"),
        # tracegroupgap=0: legend2's entries are split across several
        # legendgroups (one per age, so each age's extra period/DfE traces
        # can stay hidden -- see add_staying_on_traces), which otherwise
        # get Plotly's default gap between them, showing as blank rows.
        legend2=dict(
            title="Staying-on / HE participation", x=1.02, y=0.43, xanchor="left", yanchor="top",
            tracegroupgap=0,
        ),
        # Same right-hand column as legend2, stacked directly below it.
        legend3=dict(title="Staying-on methodology", x=1.02, y=0.12, xanchor="left", yanchor="top"),
        margin=dict(r=170, t=50),
    )
    return fig


if __name__ == "__main__":
    fig = plot(childlessness_by_age())
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
