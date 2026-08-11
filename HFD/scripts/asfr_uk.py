"""Cohort age-specific fertility rate (ASFR, all birth orders combined) for
England & Wales, from HFD's asfrRR.txt — unlike the conditional/parity-
progression ASFR on the Conditional ASFR page (see ONS/scripts/
cond_asfr_uk_ons.py), HFD does publish plain ASFR directly for the UK, so
no reconstruction is needed here.

asfrRR.txt is period data (calendar year x age); each row is resliced onto
its birth cohort (cohort = year - age) rather than grouped by calendar
year, so each line traces one cohort's fertility across its own lifetime
instead of one calendar year's snapshot across all ages.
"""

import json

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from country_names import COUNTRY_NAMES

INPUT = "data/HFD/asfrRR.txt"
OUTPUT = "outputs/asfr_uk.html"
CODES = ["GBRTENW"]

# Fixed to match the color axis of the ONS-derived conditional/cumulative
# charts this one sits alongside on docs/uk/later-births.md (their cohort
# coverage is 1920-2005), so the same color means the same cohort across
# all three charts even though this one's own data (and the external range
# control) covers a wider span.
CAXIS_MIN, CAXIS_MAX = 1920, 2005

# No in-iframe UI — matches ONS/scripts/cond_asfr_uk_ons.py's RANGE_POST_SCRIPT,
# so the same external cohort-range control on docs/uk/later-births.md can
# drive this chart too via its own window.setRange(lo, hi).
RANGE_POST_SCRIPT = """
var gd = document.getElementById('{plot_id}');
var traceGroups = __TRACE_GROUPS__;
window.setRange = function (lo, hi) {
    var visible = traceGroups.map(function (g) { return g === null ? true : (g >= lo && g <= hi); });
    Plotly.restyle(gd, {visible: visible});
};
"""


def load_data():
    df = pd.read_csv(
        INPUT,
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "asfr"],
        na_values=".",
    )
    df["age"] = df["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
    df["cohort"] = df["year"] - df["age"]
    df = df[df["code"].isin(CODES)]
    return df


def plot(df):
    """Returns (fig, trace_groups): trace_groups[i] is the birth cohort of
    fig.data[i], or None for the colorbar dummy trace — same convention as
    ONS/scripts/cond_asfr_uk_ons.py's plot(), for the shared external
    range-control pattern."""
    cohorts = sorted(df["cohort"].unique())
    cmap_min, cmap_max = CAXIS_MIN, CAXIS_MAX
    trace_groups = []

    fig = make_subplots(rows=1, cols=len(CODES), subplot_titles=[COUNTRY_NAMES[c] for c in CODES])

    for col, code in enumerate(CODES, start=1):
        subset = df[df["code"] == code]
        for cohort, rows in subset.groupby("cohort"):
            rows = rows.sort_values("age")
            color = _cohort_color(cohort, cmap_min, cmap_max)
            fig.add_trace(
                go.Scatter(
                    x=rows["age"], y=rows["asfr"] * 100,
                    mode="lines", line=dict(width=1, color=color),
                    name=str(cohort), legendgroup=str(cohort), showlegend=False,
                    hovertemplate=f"{COUNTRY_NAMES[code]}<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
                ),
                row=1, col=col,
            )
            trace_groups.append(cohort)

    # Dummy trace to show a colorbar for cohort.
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=cmap_min, cmax=cmap_max,
                color=[cmap_min], showscale=True,
                colorbar=dict(title="Cohort"),
            ),
            showlegend=False,
        ),
        row=1, col=len(CODES),
    )
    trace_groups.append(None)

    fig.update_xaxes(title_text="Age", range=[15, 45])
    fig.update_yaxes(title_text="ASFR (%)", range=[0, 15], col=1)
    fig.update_layout(
        title=f"Cohort ASFR, England & Wales ({min(cohorts)}–{max(cohorts)} birth cohorts) — HFD",
        template="plotly_white",
        autosize=True,
    )
    return fig, trace_groups


def _cohort_color(cohort, cmin, cmax):
    t = 0.0 if cmax == cmin else (cohort - cmin) / (cmax - cmin)
    t = min(1.0, max(0.0, t))  # clip: cohorts outside [cmin, cmax] clamp to the end color
    return pc.sample_colorscale("Turbo", [t])[0]


if __name__ == "__main__":
    df = load_data()
    fig, trace_groups = plot(df)
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
