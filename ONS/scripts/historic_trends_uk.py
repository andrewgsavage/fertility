"""Historic UK fertility trends by birth cohort, England & Wales — a single
Plotly figure consolidating the separate charts on the Later Births docs
page (plain ASFR from HFD, conditional and cumulative first/second-birth
rates reconstructed from ONS) into one row of panels, sharing y-axes where
the underlying scale matches (see PANEL_GROUPS).
"""

import datetime
import json
import pathlib
import sys

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
_HFD_SCRIPTS = _SCRIPT_DIR.parent.parent / "HFD" / "scripts"
if str(_HFD_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_HFD_SCRIPTS))

from asfr_uk import load_data as load_hfd_asfr  # noqa: E402

from cond_asfr_uk_ons import load_cohort_cumulative, load_cohort_rates  # noqa: E402

OUTPUT = "outputs/historic_trends_uk.html"

# Same cohort color axis as every other chart on Later Births, so the same
# color means the same cohort here too.
CAXIS_MIN, CAXIS_MAX = 1920, 2005

# (subplot title, y-axis group). Panels in the same group get linked
# y-axes (Plotly's "matches") and only the first panel in each group shows
# tick labels — the rest just show gridlines at the same scale.
PANELS = [
    ("ASFR", "pct25"),
    ("Cond. 1st", "pct25"),
    ("Cond. 2nd", "pct25"),
    ("Cum. ≥1", "pct100"),
    ("Cum. ≥2", "pct100"),
]
Y_GROUP_RANGE = {"pct25": (0, 25), "pct100": (0, 100)}
Y_GROUP_TITLE = {"pct25": "ASFR %", "pct100": "Cumulative %"}
# pct25 anchors its visible axis (title/ticks) on its first column, on the
# left edge of the whole row; pct100 anchors on its LAST column instead, on
# the right edge — so with horizontal_spacing=0 (panels flush against each
# other) the two labels bracket the merged row rather than one landing in
# the middle of it.
Y_GROUP_ANCHOR = {"pct25": "first", "pct100": "last"}
Y_GROUP_SIDE = {"pct25": "left", "pct100": "right"}


# Number of extra "context" cohorts prepended before each era's own start
# year, shown in black/grey instead of the turbo scale (see _line_color).
CONTEXT_YEARS = 5


def _cohort_color(cohort):
    t = (cohort - CAXIS_MIN) / (CAXIS_MAX - CAXIS_MIN)
    t = min(1.0, max(0.0, t))
    return pc.sample_colorscale("Turbo", [t])[0]


def _line_color(cohort, context_range):
    """Turbo-scale color by default; inside context_range (the CONTEXT_YEARS
    cohorts just before an era's start) a grey gradient — dark grey for the
    most recent of those, grading lighter the further back a cohort goes —
    so they read as context rather than competing with the era's own
    colored cohorts."""
    if context_range is not None:
        c_lo, c_hi = context_range
        if c_lo <= cohort <= c_hi:
            span = c_hi - c_lo
            t = (cohort - c_lo) / span if span > 0 else 1.0  # 0 = oldest (lightest), 1 = most recent (darkest)
            shade = round(190 - t * 130)  # 190 (light grey) .. 60 (dark grey)
            return f"#{shade:02x}{shade:02x}{shade:02x}"
    return _cohort_color(cohort)


def _peak(ages, idx):
    """(age, value) of the max non-None value at ages[age][idx]."""
    candidates = [(age, vals[idx]) for age, vals in ages.items() if vals[idx] is not None]
    age, val = max(candidates, key=lambda t: t[1])
    return age, val


def _threshold_age(ages, idx, threshold):
    """Age (linearly interpolated between the surrounding data points) at
    which ages[age][idx] first reaches threshold, ascending by age."""
    items = sorted(ages.items())
    prev_age, prev_val = None, None
    for age, vals in items:
        val = vals[idx]
        if val is None:
            continue
        if val >= threshold:
            if prev_val is None:
                return age
            frac = (threshold - prev_val) / (val - prev_val)
            return prev_age + frac * (age - prev_age)
        prev_age, prev_val = age, val
    return items[-1][0]


def _trend_word(v0, v1, up, down):
    return up if v1 > v0 else down


def _add_trend_arrows(fig, cond_rates, cumulative, lo, hi):
    """Data-driven arrows on the era's two boundary cohorts (lo, hi) showing
    how each panel's curve moves between them, with the direction word in
    each label (later/earlier, rising/falling, higher/lower) read off the
    real data each time rather than assumed — added only for specific era
    copies (see ERA_RANGES/__main__)."""
    cond_lo = cond_rates[lo]
    cum_lo = cumulative[lo]
    # hi is 9999 for the open-ended "1989-" era (no real cohort has that
    # birth year) — fall back to the latest cohort that actually has data
    # (the very latest cohorts are in the dict but empty/right-censored)
    # for any generic (non hand-tuned) comparison below.
    cond_hi = cond_rates[hi] if hi in cond_rates else cond_rates[max(c for c in cond_rates if cond_rates[c])]
    cum_hi = cumulative[hi] if hi in cumulative else cumulative[max(c for c in cumulative if cumulative[c])]

    MIN_ARROW_AGE_YEARS = 5
    MIN_ARROW_ASFR_PCT = 3

    def arrow(xref, yref, x0, y0, x1, y1, min_x=MIN_ARROW_AGE_YEARS, min_y=MIN_ARROW_ASFR_PCT):
        """Arrowhead at the real data point (x1, y1). The tail (x0, y0) is
        the real second data point too, EXCEPT where that makes the arrow
        too short to read: age deltas under min_x years, or value deltas
        under min_y percentage points, get padded out to that minimum
        (preserving direction) rather than rendering as a near-invisible
        sliver. Deltas already bigger than the minimum are left alone, so
        an arrow's length still reflects the real size of the trend once
        it's large enough to see.
        """
        dx, dy = x0 - x1, y0 - y1
        if dx != 0 and abs(dx) < min_x:
            dx = min_x if dx > 0 else -min_x
        if dy != 0 and abs(dy) < min_y:
            dy = min_y if dy > 0 else -min_y
        if dx == 0 and dy == 0:
            dy = -min_y  # degenerate (x0,y0) == (x1,y1): default to pointing up
        fig.add_annotation(
            xref=xref, yref=yref, x=x1, y=y1,
            axref=xref, ayref=yref, ax=x1 + dx, ay=y1 + dy,
            showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2, arrowcolor="black",
            text="",
        )

    def label(xref, yref, x, y, text, xanchor="center", yanchor="bottom"):
        fig.add_annotation(
            xref=xref, yref=yref, x=x, y=y, xanchor=xanchor, yanchor=yanchor,
            text=text, showarrow=False, font=dict(size=11, color="black"),
            bgcolor="rgba(255,255,255,0.75)",
        )

    def endpoint_arrow(xref, yref, x, y0, y1):
        """Vertical arrow from y0 to y1 — a thin wrapper now that arrow()
        itself guarantees a fixed minimum pixel length regardless of how
        close y0 and y1 are numerically."""
        arrow(xref, yref, x, y0, x, y1)

    # Cond. 1st (col 2): the eras with hand-picked call-outs below use a
    # plain vertical arrow at a specific age = the actual difference
    # between the two cohorts' rates there. Other eras keep the generic
    # peak-shift arrow in the final else branch.
    def vertical_callout(age, text, hi_cohort=None):
        hi_dict = cond_rates[hi_cohort] if hi_cohort is not None else cond_hi
        y0 = cond_lo[age][0] * 100
        y1 = hi_dict[age][0] * 100
        arrow("x2", "y2", age, y0, age, y1)
        label("x2", "y2", age, max(y0, y1), text, yanchor="bottom")
        return y0, y1

    if (lo, hi) == (1945, 1965):
        vertical_callout(24, "Significantly fewer<br>early births")
        vertical_callout(35, "Slightly more<br>late births")
    elif (lo, hi) == (1965, 1979):
        vertical_callout(25, "Fewer early<br>births")
        vertical_callout(32, "More late<br>births")
    elif (lo, hi) == (1989, 9999):
        # The 1989 cohort is right-censored (only ~36 observed years so
        # far), so no later cohort has caught up to it at any deep age —
        # each call-out here uses whichever is the latest cohort that still
        # has data at that specific age (2000 reaches age 25; 1993 is the
        # latest to reach age 32), rather than a single shared "hi" cohort.
        vertical_callout(25, "Fewer early<br>births", hi_cohort=2000)
        y0, y1 = cond_lo[32][0] * 100, cond_rates[1993][32][0] * 100
        late_word = _trend_word(y0, y1, "More", "Fewer")
        vertical_callout(32, f"{late_word} late<br>births", hi_cohort=1993)
    elif (lo, hi) == (1979, 1989):
        pass  # no Cond. 1st call-out for this era
    else:
        age0, val0 = _peak(cond_lo, 0)
        age1, val1 = _peak(cond_hi, 0)
        arrow("x2", "y2", age0, val0 * 100, age1, val1 * 100)
        shift_word = _trend_word(age0, age1, "later", "earlier")
        rate_word = _trend_word(val0, val1, "rising", "falling")
        label("x2", "y2", (age0 + age1) / 2, max(val0, val1) * 100, f"Peak {shift_word},<br>{rate_word}", yanchor="bottom")

    # Cond. 2nd (col 3): how the peak conditional second-birth rate's height
    # moves across cohorts.
    COND2_VERTICAL_AGE = {(1989, 9999): None, (1979, 1989): 28}  # None = lo's own peak age
    if (lo, hi) in COND2_VERTICAL_AGE:
        # The generic "hi" fallback (latest cohort with *any* data, possibly
        # right-censored to too few ages to have a real peak there) isn't
        # good enough for these eras — compare at a fixed age instead
        # (defaulting to lo's own peak age), against the latest cohort
        # *within this era's own range* that still has data at that age,
        # and keep the arrow vertical (same age) rather than connecting two
        # different peak ages.
        peak_age = COND2_VERTICAL_AGE[(lo, hi)]
        if peak_age is None:
            peak_age = _peak(cond_lo, 1)[0]
        cmp_hi_cohort = max(
            c for c in cond_rates if lo <= c <= hi and peak_age in cond_rates[c] and cond_rates[c][peak_age][1] is not None
        )
        val0 = cond_lo[peak_age][1]
        val1 = cond_rates[cmp_hi_cohort][peak_age][1]
        arrow("x3", "y3", peak_age, val0 * 100, peak_age, val1 * 100)
        label("x3", "y3", peak_age, max(val0, val1) * 100, f"{_trend_word(val0, val1, 'More', 'Fewer')}<br>births", yanchor="bottom")
    else:
        age0, val0 = _peak(cond_lo, 1)
        age1, val1 = _peak(cond_hi, 1)
        arrow("x3", "y3", age0, val0 * 100, age1, val1 * 100)
        # To the right of the arrow (not above it), and clamped below the
        # panel's 0-25 ceiling: peak values here can be high enough
        # (individually, or their midpoint) that a label placed at the raw
        # value gets clipped by the plot area and is never visible at all.
        label_y = min((val0 + val1) / 2 * 100, 23)
        label("x3", "y3", max(age0, age1) + 2, label_y, f"{_trend_word(val0, val1, 'More', 'Fewer')}<br>births", xanchor="left", yanchor="middle")

    if (lo, hi) == (1945, 1965):
        y0, y1 = cond_lo[35][1] * 100, cond_hi[35][1] * 100
        arrow("x3", "y3", 35, y0, 35, y1)
        label("x3", "y3", 35, max(y0, y1), f"{_trend_word(y0, y1, 'More', 'Fewer')}<br>late births", yanchor="bottom")

    # Cum. >=1/>=2 (cols 4-5): rising edge (age at which the cohort crosses
    # a threshold %) and the eventual/completed level (read near the right
    # edge, just before the curves flatten out). The 1989- era is
    # right-censored (see the cond_hi/cum_hi fallback above) — 1993 is the
    # latest cohort with data as deep as age 32, so it stands in for "hi"
    # here instead of the generic fallback, at that shallower endpoint age.
    # 1979-1989's own "hi" cohort (1989) is likewise right-censored (only
    # reaches age 36) but has no other call-out here — skip Cum. >=1/>=2
    # entirely for that era rather than crash on a missing age 43.
    if (lo, hi) == (1979, 1989):
        return

    if (lo, hi) == (1989, 9999):
        cum_hi_for_threshold, end_age = cumulative[1993], 32
    else:
        cum_hi_for_threshold, end_age = cum_hi, 43

    # The 1989- era's endpoint comparison would only reach age 32 (see
    # above) — too early in either curve to call a "completed" trend — so
    # skip the endpoint arrow there and keep just the rising-edge one.
    show_endpoint = (lo, hi) != (1989, 9999)

    # Rising-edge ("Later"/"Earlier") call-out kept only on Cum. >=1 for
    # 1965-1979 — removed everywhere else per explicit request.
    if (lo, hi) == (1965, 1979):
        a0 = _threshold_age(cum_lo, 0, 50)
        a1 = _threshold_age(cum_hi_for_threshold, 0, 50)
        arrow("x4", "y4", a0, 50, a1, 50)
        label("x4", "y4", (a0 + a1) / 2, 50, _trend_word(a0, a1, "Later", "Earlier"), yanchor="top")
    if show_endpoint:
        end0, end1 = cum_lo[end_age][0], cum_hi_for_threshold[end_age][0]
        endpoint_arrow("x4", "y4", end_age, end0, end1)
        label("x4", "y4", end_age, max(end0, end1), _trend_word(end0, end1, "More", "Fewer"), xanchor="right")

    # Cum. >=2 (col 5): same pattern as Cum. >=1, using the >=2-children curve.
    if show_endpoint:
        end0, end1 = cum_lo[end_age][1], cum_hi_for_threshold[end_age][1]
        endpoint_arrow("x5", "y5", end_age, end0, end1)
        label("x5", "y5", end_age, max(end0, end1), _trend_word(end0, end1, "More", "Fewer"), xanchor="right")


def build_figure(cohort_range=None, trend_arrows=False):
    """cohort_range: optional (lo, hi) to restrict which birth cohorts get
    plotted at all (used for the fixed-era copies below) — the color axis
    stays fixed at CAXIS_MIN/CAXIS_MAX regardless, so colors stay comparable
    across the full-range chart and every era copy. When set, the
    CONTEXT_YEARS cohorts immediately before lo are also included, colored
    dark grey (most recent)/light grey (older) instead of by the turbo
    scale. trend_arrows: when True (and cohort_range is set), adds
    data-driven arrows comparing the lo vs hi boundary cohorts on each
    panel — see _add_trend_arrows()."""
    hfd_df = load_hfd_asfr()
    cond_rates = load_cohort_rates()
    cumulative = load_cohort_cumulative()

    context_range = None
    if cohort_range is not None:
        lo, hi = cohort_range
        context_range = (lo - CONTEXT_YEARS, lo - 1)
        plot_lo = context_range[0]
        hfd_df = hfd_df[(hfd_df["cohort"] >= plot_lo) & (hfd_df["cohort"] <= hi)]
        cond_rates = {c: v for c, v in cond_rates.items() if plot_lo <= c <= hi}
        cumulative = {c: v for c, v in cumulative.items() if plot_lo <= c <= hi}

    fig = make_subplots(
        rows=1, cols=len(PANELS), subplot_titles=[p[0] for p in PANELS], horizontal_spacing=0
    )
    trace_groups = []

    # Panel 1: plain ASFR (HFD, already *100 in load_hfd_asfr's own units —
    # asfr_uk.py multiplies by 100 when plotting, so do the same here).
    for cohort, rows in hfd_df.groupby("cohort"):
        rows = rows.sort_values("age")
        fig.add_trace(
            go.Scatter(
                x=rows["age"], y=rows["asfr"] * 100,
                mode="lines", line=dict(width=1, color=_line_color(cohort, context_range)),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"ASFR<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=1,
        )
        trace_groups.append(cohort)

    # Panels 2-3: conditional first/second birth (ONS reconstruction).
    for cohort, ages in cond_rates.items():
        color = _line_color(cohort, context_range)
        sorted_ages = sorted(ages)
        c1 = [ages[a][0] for a in sorted_ages]
        c2 = [ages[a][1] for a in sorted_ages]
        fig.add_trace(
            go.Scatter(
                x=sorted_ages, y=[v * 100 if v is not None else None for v in c1],
                mode="lines", line=dict(width=1, color=color),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"Conditional 1st birth<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=2,
        )
        fig.add_trace(
            go.Scatter(
                x=sorted_ages, y=[v * 100 if v is not None else None for v in c2],
                mode="lines", line=dict(width=1, color=color),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"Conditional 2nd birth<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=3,
        )
        trace_groups.extend([cohort, cohort])

    # Panels 4-5: cumulative % with >=1 / >=2 children (ONS reconstruction,
    # already 0-100 percentages, no *100 needed).
    for cohort, ages in cumulative.items():
        color = _line_color(cohort, context_range)
        sorted_ages = sorted(ages)
        p1 = [ages[a][0] for a in sorted_ages]
        p2 = [ages[a][1] for a in sorted_ages]
        fig.add_trace(
            go.Scatter(
                x=sorted_ages, y=p1,
                mode="lines", line=dict(width=1, color=color),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"Cumulative ≥ 1 child<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=4,
        )
        fig.add_trace(
            go.Scatter(
                x=sorted_ages, y=p2,
                mode="lines", line=dict(width=1, color=color),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"Cumulative ≥ 2 children<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=5,
        )
        trace_groups.extend([cohort, cohort])

    # One shared colorbar (dummy trace), horizontal and above the chart —
    # a vertical one on the right competed for space with the "Cum. >=2"
    # panel's own right-side axis (see Y_GROUP_SIDE).
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=CAXIS_MIN, cmax=CAXIS_MAX,
                color=[CAXIS_MIN], showscale=True,
                # Inset into the chart itself, vertical, centered on age=40
                # on the Cond. 1st panel — an empty region of that panel's
                # curve. Colorbar x/y is whole-figure "paper" fraction, not
                # data-relative, so this converts data coords -> paper
                # coords by hand using that panel's own xaxis domain/range
                # (domain 0.2-0.4, range 20-45, so age=40 -> paper x =
                # 0.2 + (40-20)/(45-20)*0.2 = 0.36) and the shared yaxis
                # (domain 0-1, range 0-25).
                colorbar=dict(
                    title=dict(text="Cohort"),
                    orientation="v",
                    x=0.36, xanchor="center",
                    y=1.0, yanchor="top",
                    len=0.28, thickness=10,
                ),
            ),
            showlegend=False,
        ),
        row=1, col=1,
    )
    trace_groups.append(None)

    # Link y-axes within each PANELS group (see Y_GROUP_RANGE): the anchor
    # column (Y_GROUP_ANCHOR) carries the visible title/ticks on the side
    # given by Y_GROUP_SIDE, every other column in the group just links to
    # it ("matches") with its own ticks hidden — one continuous shared
    # scale per group instead of duplicated axes.
    group_cols = {}
    for col, (_, group) in enumerate(PANELS, start=1):
        group_cols.setdefault(group, []).append(col)
    anchor_col_for_group = {
        group: (cols[0] if Y_GROUP_ANCHOR[group] == "first" else cols[-1])
        for group, cols in group_cols.items()
    }

    for col, (_, group) in enumerate(PANELS, start=1):
        # Matches each source chart's own age range: the plain-ASFR panel
        # (HFD/scripts/asfr_uk.py) starts at 15, the conditional/cumulative
        # panels (ONS/scripts/cond_asfr_uk_ons.py) start at 20.
        age_min = 15 if col == 1 else 20
        fig.update_xaxes(title_text="Age", range=[age_min, 45], row=1, col=col)
        anchor_col = anchor_col_for_group[group]
        if col == anchor_col:
            fig.update_yaxes(
                title_text=Y_GROUP_TITLE[group], range=list(Y_GROUP_RANGE[group]),
                side=Y_GROUP_SIDE[group],
                row=1, col=col,
            )
        else:
            anchor_axis = "y" if anchor_col == 1 else f"y{anchor_col}"
            fig.update_yaxes(matches=anchor_axis, showticklabels=False, row=1, col=col)

    # Era copies have no external slider/label to show which cohorts are
    # plotted, so stamp it into the plot itself instead — top-left corner of
    # the first panel, clear of the colorbar (which sits on panel 2). A
    # second line gives the age those cohorts are today, since "born
    # 1945-1965" is less immediately meaningful than "aged 61-81 now".
    if cohort_range is not None:
        lo, hi = cohort_range
        label_hi = hi
        if hi >= 9999:
            # Open-ended era: report the actual most recent cohort that has
            # real (non-empty) data anywhere in this chart, rather than a
            # vague "1989-" with no real upper bound — cohorts right up
            # against CAXIS_MAX are right-censored and often present as
            # empty entries (see the cond_hi/cum_hi fallback in
            # _add_trend_arrows), so "last with data" != "last key". Only
            # this label's own display uses label_hi — hi itself stays the
            # 9999 sentinel below, since _add_trend_arrows keys its
            # right-censoring logic off that exact value.
            label_hi = max(
                max((c for c in cond_rates if cond_rates.get(c)), default=lo),
                max((c for c in cumulative if cumulative.get(c)), default=lo),
            )
        range_text = f"Cohorts {lo}–{label_hi}"
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.01, y=0.97, xanchor="left", yanchor="top",
            text=range_text, showarrow=False,
            font=dict(size=14),
        )
        current_year = datetime.date.today().year
        age_old = current_year - lo
        age_young = current_year - label_hi
        age_text = f"Ages in {current_year}: {age_old}-{age_young}"
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.01, y=0.88, xanchor="left", yanchor="top",
            text=age_text, showarrow=False,
            font=dict(size=14),
        )

    if trend_arrows and cohort_range is not None:
        _add_trend_arrows(fig, cond_rates, cumulative, lo, hi)

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin=dict(t=30, r=60, l=50, b=40),
    )
    return fig, trace_groups


RANGE_POST_SCRIPT = """
var gd = document.getElementById('{plot_id}');
var traceGroups = __TRACE_GROUPS__;
window.setRange = function (lo, hi) {
    var visible = traceGroups.map(function (g) { return g === null ? true : (g >= lo && g <= hi); });
    Plotly.restyle(gd, {visible: visible});
};
"""


# Fixed-era copies of the same chart (e.g. for side-by-side generational
# comparison) — each pre-filtered to its own cohort range, no range control
# needed since there's nothing left to slide. "1989-" has no upper bound of
# its own, so it just keeps every cohort from 1989 up to whatever each
# source's data actually goes to.
ERA_RANGES = {
    "1945_1965": (1945, 1965),
    "1965_1979": (1965, 1979),
    "1979_1989": (1979, 1989),
    "1989_": (1989, 9999),
}


def _write(fig, trace_groups, output_path):
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
    html = open(output_path, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(output_path, "w", encoding="utf-8").write(html)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    fig, trace_groups = build_figure()
    _write(fig, trace_groups, OUTPUT)

    ARROW_ERAS = {"1945_1965", "1965_1979", "1979_1989", "1989_"}
    for suffix, era in ERA_RANGES.items():
        era_fig, era_trace_groups = build_figure(cohort_range=era, trend_arrows=(suffix in ARROW_ERAS))
        era_output = OUTPUT.replace(".html", f"_{suffix}.html")
        _write(era_fig, era_trace_groups, era_output)
