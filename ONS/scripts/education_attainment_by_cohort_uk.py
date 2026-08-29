"""Educational attainment distribution by birth cohort, England & Wales /
Scotland / Northern Ireland -- reproducing Kuang, Berrington & Falkingham
(2025) Figure 2 as an interactive stacked-bar chart.

Kuang, X., Berrington, A. & Falkingham, J. (2025), "Educational trends in
cohort fertility by birth order: A comparison of England and Wales,
Scotland, and Northern Ireland", Demographic Research 51(36):1121-1168.
https://www.demographic-research.org/volumes/vol51/36/51-36.pdf
Source (per the paper): ONS Longitudinal Study, Scottish Longitudinal
Study, Northern Ireland Longitudinal Study (NILS' earliest data point is
the 1966-1969 birth cohort, binned into "1965-1969" here as in the source).

Figure 2 is a raster image embedded in the PDF (a stacked bar chart, not
the line-and-marker style of Figures 3-5 in this paper), digitized
differently as a result: at each cohort's bar column, the pixel rows where
the fill colour changes give the Low/Medium boundary and the Medium/High
boundary directly (cumulative proportions), with the segment colours
(~51/153/204 on a 0-255 scale -- ggplot's grey20/grey60/grey80, not the
Figures 3-5 line-chart palette) picked out by directly sampling one bar's
full-height colour profile rather than assumed. y-axis calibration
(top=1.00, bottom=0.00) cross-checked against the axis tick label text's
own row positions, the same safeguard used in
mean_age_first_birth_by_education_uk.py after an earlier off-by-one
gridline error there. Segment proportions are approximate to roughly
+/-0.01 each.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUTPUT = "outputs/education_attainment_by_cohort_uk.html"

COUNTRIES = ["England & Wales", "Scotland", "Northern Ireland"]
LEVELS = ["Low", "Medium", "High"]
LEVEL_COLOR = {"Low": "#1a1a1a", "Medium": "#969696", "High": "#cccccc"}

# {country: [(cohort_label, low_proportion, medium_proportion, high_proportion), ...]}
# -- see module docstring for how these were digitized. Proportions sum to
# ~1.0 per cohort (rounding). Northern Ireland has no 1956-1959/1960-1964
# bars (NILS doesn't cover them).
EDUCATION_ATTAINMENT = {
    "England & Wales": [
        ("1956-1959", 0.674, 0.133, 0.193),
        ("1960-1964", 0.688, 0.121, 0.191),
        ("1965-1969", 0.677, 0.135, 0.188),
        ("1970-1974", 0.525, 0.183, 0.292),
        ("1975-1978", 0.381, 0.241, 0.378),
    ],
    "Scotland": [
        ("1956-1959", 0.566, 0.134, 0.300),
        ("1960-1964", 0.566, 0.144, 0.290),
        ("1965-1969", 0.535, 0.186, 0.279),
        ("1970-1974", 0.408, 0.172, 0.420),
        ("1975-1978", 0.319, 0.139, 0.542),
    ],
    "Northern Ireland": [
        ("1965-1969", 0.715, 0.097, 0.188),
        ("1970-1974", 0.620, 0.115, 0.265),
        ("1975-1978", 0.418, 0.176, 0.406),
    ],
}


def plot():
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.02, column_titles=COUNTRIES)

    for col, country in enumerate(COUNTRIES, start=1):
        rows = EDUCATION_ATTAINMENT[country]
        cohorts = [r[0] for r in rows]
        for i, level in enumerate(LEVELS):
            values = [r[i + 1] for r in rows]
            fig.add_trace(
                go.Bar(
                    x=cohorts, y=values, name=level, legendgroup=level, showlegend=(col == 1),
                    marker=dict(color=LEVEL_COLOR[level]),
                    hovertemplate=f"{country}, {level} education<br>%{{x}}<br>%{{y:.1%}}<extra></extra>",
                ),
                row=1, col=col,
            )
        fig.update_xaxes(
            categoryorder="array", categoryarray=[c for c, *_ in EDUCATION_ATTAINMENT["England & Wales"]],
            tickangle=-45, row=1, col=col,
        )
        fig.update_yaxes(range=[0, 1], tickformat=".0%", showticklabels=(col == 1), row=1, col=col)

    fig.update_layout(
        title="Educational attainment distribution by birth cohort",
        template="plotly_white", autosize=True, barmode="stack",
        legend=dict(title="Education level", x=1.02, y=1, xanchor="left", yanchor="top"),
        margin=dict(r=140, t=90),
    )
    return fig


if __name__ == "__main__":
    fig = plot()
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
