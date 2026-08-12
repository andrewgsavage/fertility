"""Historic UK fertility trends by birth cohort, England & Wales — a single
Plotly figure consolidating the separate charts on the Later Births docs
page (plain ASFR from HFD, conditional and cumulative first/second-birth
rates reconstructed from ONS) into one row of panels, sharing y-axes where
the underlying scale matches (see PANEL_GROUPS).
"""

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


def _cohort_color(cohort):
    t = (cohort - CAXIS_MIN) / (CAXIS_MAX - CAXIS_MIN)
    t = min(1.0, max(0.0, t))
    return pc.sample_colorscale("Turbo", [t])[0]


def build_figure():
    hfd_df = load_hfd_asfr()
    cond_rates = load_cohort_rates()
    cumulative = load_cohort_cumulative()

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
                mode="lines", line=dict(width=1, color=_cohort_color(cohort)),
                name=str(cohort), legendgroup=str(cohort), showlegend=False,
                hovertemplate=f"ASFR<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=1,
        )
        trace_groups.append(cohort)

    # Panels 2-3: conditional first/second birth (ONS reconstruction).
    for cohort, ages in cond_rates.items():
        color = _cohort_color(cohort)
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
        color = _cohort_color(cohort)
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
                colorbar=dict(
                    title=dict(text="Cohort", side="top"),
                    orientation="h",
                    x=0.5, xanchor="center",
                    y=1.2, yanchor="bottom",
                    len=0.4, thickness=12,
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

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin=dict(t=90, r=60, l=50, b=40),
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


if __name__ == "__main__":
    fig, trace_groups = build_figure()
    post_script = RANGE_POST_SCRIPT.replace("__TRACE_GROUPS__", json.dumps(trace_groups))
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        post_script=post_script,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
