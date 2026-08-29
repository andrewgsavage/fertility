"""Overlay HFD-derived expected-children-by-age-of-first-birth curves for
Finland against Roustaei et al. (2019, BMJ Open) -- "completed fertility
rate by age at first birth" for Finnish women whose first birth occurred
in one of four 5-year periods from 1987-2006, digitized by eye from the
paper's online supplementary figure (panel B of
https://pmc.ncbi.nlm.nih.gov/articles/instance/6340426/bin/bmjopen-2018-026336supp001.pdf),
which extends the main text's Figure 2B (1987-91 and 1992-96 only) with
two further periods. The supplementary PDF has no caption identifying
what its three panels (A/B/C) each represent; panel B was picked because
its 1.0-3.5 children-per-woman scale and 1987-91/1992-96 curves match
Figure 2B exactly, so it's presumed to be the same measure extended to
later periods rather than a different subgroup.

The paper groups by first-birth *calendar period*, not birth cohort, so
it's compared against HFD's own period-basis recursion
(births_per_mother_period_grid.py, pft.txt) rather than the cohort-basis
one -- averaged over each paper period's calendar years -- instead of
against a birth-cohort grouping that has no real correspondence to it.

These are still two different kinds of measurement, not two samples of
the same thing. HFD's curve is a modeled expected value: it chains each
calendar year's own age-specific parity-progression hazards together,
assuming a woman's chance of a 2nd, 3rd, etc. birth can be treated as an
independent probability at each age. The paper's curve, from Finland's
individually-linked Medical Birth Register, is presumably a direct
empirical average -- the actual completed number of children real women
had, tracked via personal identifiers, with no chaining of rates
required. That a rate-chained model and a direct headcount land on the
same curve shape is itself a check on the independence assumption the
recursion relies on -- not a claim that the two datasets are identical.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from births_per_mother_period_grid import load_data
from births_per_mother_region_grid import X_LIM, Y_LIM

OUTPUT = "outputs/finland_paper_comparison.html"
LABEL_FONT = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")

# Digitized at gridline resolution (every 2 years / 0.5 children) from
# panel B of the supplementary PDF, which plots four curves: 1987-91,
# 1992-96, 1997-01, 2002-06. The first two match Figure 2B in the main
# text; the latter two are new here.
PAPER_AGES = [15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45]
PAPER_CURVES = {
    "1987-91": [3.15, 3.15, 3.20, 2.80, 2.65, 2.40, 2.20, 2.00,
                1.90, 1.75, 1.60, 1.45, 1.30, 1.20, 1.05, 1.00],
    "1992-96": [3.30, 3.35, 3.35, 2.85, 2.70, 2.45, 2.25, 2.05,
                1.95, 1.80, 1.65, 1.50, 1.35, 1.25, 1.10, 1.25],
    "1997-01": [3.30, 3.40, 3.45, 2.90, 2.72, 2.47, 2.27, 2.07,
                1.97, 1.82, 1.67, 1.52, 1.37, 1.27, 1.12, 1.20],
    "2002-06": [3.30, 3.40, 3.45, 2.90, 2.72, 2.47, 2.27, 2.07,
                1.97, 1.82, 1.67, 1.52, 1.37, 1.27, 1.12, 1.35],
}
PAPER_COLORS = {
    "1987-91": "#1b1b1b",
    "1992-96": "#4c78a8",
    "1997-01": "#59a14f",
    "2002-06": "#e45756",
}
# Inclusive calendar-year range each paper period covers, used to average
# HFD's period-basis curve over the matching years.
PAPER_PERIODS = {
    "1987-91": (1987, 1991),
    "1992-96": (1992, 1996),
    "1997-01": (1997, 2001),
    "2002-06": (2002, 2006),
}


def hfd_period_average(df, start, end):
    """Mean HFD expected-children curve over calendar years [start, end]."""
    subset = df[(df["year"] >= start) & (df["year"] <= end)]
    return subset.groupby("age")["expected_children"].mean().sort_index()


def plot(df):
    subset = df[df["code"] == "FIN"]
    labels = list(PAPER_PERIODS.keys())
    hfd_averages = {
        label: hfd_period_average(subset, *PAPER_PERIODS[label]) for label in labels
    }

    fig = make_subplots(
        rows=1, cols=len(labels),
        subplot_titles=[f"First birth {label}" for label in labels],
        horizontal_spacing=0.04,
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT

    for col, label in enumerate(labels, start=1):
        # Every other period's pair, in light grey, for context -- drawn
        # first so the highlighted period's colored pair sits on top.
        for other in labels:
            if other == label:
                continue
            fig.add_trace(
                go.Scatter(
                    x=hfd_averages[other].index, y=hfd_averages[other].values, mode="lines",
                    line=dict(width=1, color="lightgrey"), showlegend=False, hoverinfo="skip",
                ),
                row=1, col=col,
            )
            fig.add_trace(
                go.Scatter(
                    x=PAPER_AGES, y=PAPER_CURVES[other], mode="lines",
                    line=dict(width=1, color="lightgrey", dash="dash"), showlegend=False, hoverinfo="skip",
                ),
                row=1, col=col,
            )

        start, end = PAPER_PERIODS[label]
        color = PAPER_COLORS[label]
        avg = hfd_averages[label]
        fig.add_trace(
            go.Scatter(
                x=avg.index, y=avg.values, mode="lines",
                line=dict(width=2.5, color=color), showlegend=False,
                hovertemplate=f"HFD, first birth {label}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
            ),
            row=1, col=col,
        )
        fig.add_trace(
            go.Scatter(
                x=PAPER_AGES, y=PAPER_CURVES[label], mode="lines",
                line=dict(width=2, color=color, dash="dash"), showlegend=False,
                hovertemplate=f"Roustaei et al., first birth {label}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
            ),
            row=1, col=col,
        )
        fig.update_xaxes(range=list(X_LIM), showticklabels=True, row=1, col=col)
        fig.update_yaxes(range=list(Y_LIM), showticklabels=(col == 1), row=1, col=col)

    # Dummy traces, style only -- a legend describing what solid vs dashed
    # means, independent of the per-period color coding.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2.5, color="black"), name="HFD (period basis)",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2, color="black", dash="dash"), name="Roustaei et al. 2019",
    ))

    fig.update_layout(
        title="Finland: HFD vs Roustaei et al. 2019, by first-birth period",
        template="plotly_white",
        height=420,
        margin=dict(t=90, b=40, l=50, r=20),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.22, yanchor="bottom", font=dict(size=10)),
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)

    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height=f"{fig.layout.height}px",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
