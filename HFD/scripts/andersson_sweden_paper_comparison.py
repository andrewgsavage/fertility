"""Reproduce the completed-fertility-by-age-at-first-birth curves for
Swedish women born 1935-39 and 1950-54, from Andersson (2008: 49, Table
12d), as reprinted in Schmidt, Sobotka, Bentzen & Nyboe Andersen (2012,
Hum Reprod Update 18(1):29-43, Fig. 4) -- digitized by eye from that
figure. Faceted one panel per cohort group, same convention as the
Finland and Beaujouan comparisons: each panel highlights its own group
in color, with the other group shown in light grey for context.

HFD's own Swedish parity-progression data (cft.txt) only starts at the
1955 birth cohort -- too late for the 1935-39 panel, but close enough to
the paper's own 1950-54 group to plot alongside it as the closest
available real HFD cohort.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from births_per_mother_region_grid import load_data

OUTPUT = "outputs/andersson_sweden_paper_comparison.html"

# Digitized by eye, one point per age year, from Fig. 4 of Schmidt et al.
# 2012 (originally Andersson 2008, Table 12d).
AGES = list(range(15, 45))
PAPER_CURVES = {
    "1935-39": [3.65, 3.22, 3.08, 2.92, 2.76, 2.62, 2.55, 2.44, 2.38, 2.32,
                2.20, 2.15, 2.06, 2.00, 1.92, 1.86, 1.78, 1.70, 1.62, 1.58,
                1.49, 1.46, 1.33, 1.28, 1.22, 1.16, 1.13, 1.11, 1.08, 1.00],
    "1950-54": [2.80, 2.78, 2.67, 2.64, 2.58, 2.47, 2.45, 2.39, 2.36, 2.33,
                2.30, 2.26, 2.20, 2.17, 2.12, 2.06, 2.02, 1.95, 1.89, 1.80,
                1.75, 1.60, 1.56, 1.47, 1.35, 1.28, 1.20, 1.15, 1.12, 1.02],
}
GROUP_COLORS = {"1935-39": "navy", "1950-54": "black"}

# HFD's earliest tracked Swedish cohort, added to whichever paper group
# it's closest to -- there's no HFD data anywhere near 1935-39.
HFD_COHORT = 1955
HFD_GROUP = "1950-54"

X_LIM = (15, 44)
Y_LIM = (1.0, 4.0)


def plot(df):
    groups = list(PAPER_CURVES.keys())
    hfd_1955 = df[(df["code"] == "SWE") & (df["cohort"] == HFD_COHORT)].sort_values("age")

    fig = make_subplots(
        rows=1, cols=len(groups),
        subplot_titles=[f"<b>Cohorts {g}</b>" for g in groups],
        horizontal_spacing=0.06,
    )
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")

    for col, group in enumerate(groups, start=1):
        # The other group's paper curve, in light grey, for context.
        for other in groups:
            if other == group:
                continue
            fig.add_trace(
                go.Scatter(
                    x=AGES, y=PAPER_CURVES[other], mode="lines",
                    line=dict(width=1, color="lightgrey", dash="dash"), showlegend=False, hoverinfo="skip",
                ),
                row=1, col=col,
            )

        color = GROUP_COLORS[group]
        fig.add_trace(
            go.Scatter(
                x=AGES, y=PAPER_CURVES[group], mode="lines",
                line=dict(width=2.5, color=color, dash="dash"), showlegend=False,
                hovertemplate=f"Andersson 2008, cohorts {group}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
            ),
            row=1, col=col,
        )
        if group == HFD_GROUP:
            fig.add_trace(
                go.Scatter(
                    x=hfd_1955["age"], y=hfd_1955["expected_children"], mode="lines",
                    line=dict(width=2.5, color=color), showlegend=False,
                    hovertemplate=f"HFD, cohort {HFD_COHORT}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
                ),
                row=1, col=col,
            )
        fig.update_xaxes(range=list(X_LIM), row=1, col=col)
        fig.update_yaxes(range=list(Y_LIM), showticklabels=(col == 1), row=1, col=col)

    # Dummy traces, style only -- a legend describing what solid vs dashed
    # means, independent of the per-group color coding.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2.5, color="black"),
        name=f"HFD (cohort {HFD_COHORT})",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2.5, color="black", dash="dash"),
        name="Andersson 2008",
    ))

    fig.update_layout(
        title=dict(text="Sweden: Andersson (2008) via Schmidt et al. 2012", y=0.97, yanchor="top"),
        template="plotly_white",
        height=430,
        margin=dict(t=110, b=40, l=50, r=20),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.1, yanchor="bottom", font=dict(size=10)),
    )
    fig.update_xaxes(title="Age at first birth")
    fig.update_yaxes(title="Completed fertility rate", col=1)
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
