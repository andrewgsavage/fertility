"""Average family size at age 40, by educational attainment and birth
cohort, England & Wales / Scotland / Northern Ireland -- reproducing Kuang,
Berrington & Falkingham (2025) Figure 3 as an interactive chart.

Kuang, X., Berrington, A. & Falkingham, J. (2025), "Educational trends in
cohort fertility by birth order: A comparison of England and Wales,
Scotland, and Northern Ireland", Demographic Research 51(36):1121-1168.
https://www.demographic-research.org/volumes/vol51/36/51-36.pdf
Source (per the paper): ONS Longitudinal Study, Scottish Longitudinal
Study, Northern Ireland Longitudinal Study (NILS' earliest data point is
the 1966-1969 birth cohort, binned into "1965-1969" here as in the source).

Figure 3 is a raster image embedded in the PDF (not vector data, unlike
this repo's own text-sourced tables), so FAMILY_SIZE below is digitized
from the image's own pixels rather than read off any published table:
rendered at 8x page resolution, the panel's five labelled gridlines
(2.50/2.25/2.00/1.75/1.50) are 828px apart and evenly spaced, giving a
linear pixel-to-value calibration; each facet's five birth-cohort tick
columns were located from the small tick-mark ticks below the bottom
panel's axis border. At each (panel, facet, cohort) column, pixels were
classified into Low/Medium/High/All by matching the exact grey level of
each series' own legend swatch (17/111/158/190 on a 0-255 scale, sampled
directly from the legend rather than assumed), and the point estimate
taken as the vertical midpoint of the matched marker+error-bar run (valid
since the source's error bars are symmetric about the point estimate).
Values are therefore approximate to roughly +/-0.02 children, and -- unlike
this repo's ONS-derived series -- aren't cross-checked against a second,
independent source.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUTPUT = "outputs/family_size_by_education_uk.html"

COUNTRIES = ["England & Wales", "Scotland", "Northern Ireland"]
PANELS = [("all_women", "All women"), ("excl_childless", "Excluding childless women")]
SERIES = ["Low", "Medium", "High", "All"]
SERIES_STYLE = {
    "Low": dict(color="#1a1a1a", dash="solid"),
    "Medium": dict(color="#707070", dash="solid"),
    "High": dict(color="#b0b0b0", dash="solid"),
    "All": dict(color="#b0b0b0", dash="dot"),
}
Y_RANGE = [1.35, 2.55]

# {panel: {country: {series: [(cohort_label, value), ...]}}} -- see module
# docstring for how these were digitized. Northern Ireland has no
# 1956-1959/1960-1964 points (NILS doesn't cover them).
FAMILY_SIZE = {
    "all_women": {
        "England & Wales": {
            "Low": [("1956-1959", 1.91), ("1960-1964", 1.85), ("1965-1969", 1.86), ("1970-1974", 1.87), ("1975-1978", 2.03)],
            "Medium": [("1956-1959", 1.76), ("1960-1964", 1.64), ("1965-1969", 1.59), ("1970-1974", 1.63), ("1975-1978", 1.65)],
            "High": [("1956-1959", 1.65), ("1960-1964", 1.54), ("1965-1969", 1.42), ("1970-1974", 1.42), ("1975-1978", 1.47)],
            "All": [("1956-1959", 1.83), ("1960-1964", 1.75), ("1965-1969", 1.73), ("1970-1974", 1.68), ("1975-1978", 1.72)],
        },
        "Scotland": {
            "Low": [("1956-1959", 1.91), ("1960-1964", 1.88), ("1965-1969", 1.83), ("1970-1974", 1.77), ("1975-1978", 1.88)],
            "Medium": [("1956-1959", 1.77), ("1960-1964", 1.71), ("1965-1969", 1.58), ("1970-1974", 1.52), ("1975-1978", 1.55)],
            "High": [("1956-1959", 1.69), ("1960-1964", 1.63), ("1965-1969", 1.46), ("1970-1974", 1.43), ("1975-1978", 1.48)],
            "All": [("1956-1959", 1.84), ("1960-1964", 1.79), ("1965-1969", 1.70), ("1970-1974", 1.62), ("1975-1978", 1.64)],
        },
        "Northern Ireland": {
            "Low": [("1965-1969", 2.01), ("1970-1974", 1.97), ("1975-1978", 2.05)],
            "Medium": [("1965-1969", 1.87), ("1970-1974", 1.84), ("1975-1978", 1.97)],
            "High": [("1965-1969", 1.75), ("1970-1974", 1.76), ("1975-1978", 1.78)],
            "All": [("1965-1969", 1.96), ("1970-1974", 1.91), ("1975-1978", 1.94)],
        },
    },
    "excl_childless": {
        "England & Wales": {
            "Low": [("1956-1959", 2.28), ("1960-1964", 2.24), ("1965-1969", 2.24), ("1970-1974", 2.28), ("1975-1978", 2.42)],
            "Medium": [("1956-1959", 2.12), ("1960-1964", 2.14), ("1965-1969", 2.10), ("1970-1974", 2.12), ("1975-1978", 2.09)],
            "High": [("1956-1959", 2.17), ("1960-1964", 2.09), ("1965-1969", 1.99), ("1970-1974", 1.97), ("1975-1978", 1.98)],
            "All": [("1956-1959", 2.25), ("1960-1964", 2.20), ("1965-1969", 2.18), ("1970-1974", 2.17), ("1975-1978", 2.19)],
        },
        "Scotland": {
            "Low": [("1956-1959", 2.25), ("1960-1964", 2.22), ("1965-1969", 2.16), ("1970-1974", 2.16), ("1975-1978", 2.21)],
            "Medium": [("1956-1959", 2.08), ("1960-1964", 2.06), ("1965-1969", 2.06), ("1970-1974", 2.01), ("1975-1978", 2.04)],
            "High": [("1956-1959", 2.13), ("1960-1964", 2.11), ("1965-1969", 2.00), ("1970-1974", 1.95), ("1975-1978", 1.97)],
            "All": [("1956-1959", 2.21), ("1960-1964", 2.15), ("1965-1969", 2.11), ("1970-1974", 2.07), ("1975-1978", 2.08)],
        },
        "Northern Ireland": {
            "Low": [("1965-1969", 2.40), ("1970-1974", 2.37), ("1975-1978", 2.44)],
            "Medium": [("1965-1969", 2.40), ("1970-1974", 2.36), ("1975-1978", 2.40)],
            "High": [("1965-1969", 2.29), ("1970-1974", 2.26), ("1975-1978", 2.29)],
            "All": [("1965-1969", 2.36), ("1970-1974", 2.32), ("1975-1978", 2.37)],
        },
    },
}


def plot():
    fig = make_subplots(
        rows=2, cols=3, shared_xaxes=True, vertical_spacing=0.08, horizontal_spacing=0.03,
        column_titles=COUNTRIES, row_titles=[label for _, label in PANELS],
    )

    for row, (panel_key, _panel_label) in enumerate(PANELS, start=1):
        for col, country in enumerate(COUNTRIES, start=1):
            for series in SERIES:
                points = FAMILY_SIZE[panel_key][country][series]
                if not points:
                    continue
                cohorts, values = zip(*points)
                fig.add_trace(
                    go.Scatter(
                        x=cohorts, y=values, mode="lines+markers", name=series,
                        legendgroup=series, showlegend=(row == 1 and col == 1),
                        line=dict(width=2, **SERIES_STYLE[series]), marker=dict(size=6),
                        hovertemplate=f"{country}, {series} education<br>%{{x}}<br>%{{y:.2f}} children<extra></extra>",
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(
                categoryorder="array", categoryarray=[c for c, _ in FAMILY_SIZE["all_women"]["England & Wales"]["Low"]],
                showticklabels=(row == 2), tickangle=-45, row=row, col=col,
            )
            fig.update_yaxes(range=Y_RANGE, showticklabels=(col == 1), row=row, col=col)

    fig.update_layout(
        title="Average family size at age 40, by educational attainment and birth cohort",
        template="plotly_white", autosize=True,
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
