"""Mean age at first birth, by educational attainment and birth cohort,
England & Wales / Scotland / Northern Ireland -- reproducing Kuang,
Berrington & Falkingham (2025) Figure 4 as an interactive chart.

Kuang, X., Berrington, A. & Falkingham, J. (2025), "Educational trends in
cohort fertility by birth order: A comparison of England and Wales,
Scotland, and Northern Ireland", Demographic Research 51(36):1121-1168.
https://www.demographic-research.org/volumes/vol51/36/51-36.pdf
Source (per the paper): ONS Longitudinal Study, Scottish Longitudinal
Study, Northern Ireland Longitudinal Study (NILS' earliest data point is
the 1966-1969 birth cohort, binned into "1965-1969" here as in the source).

Figure 4 is a raster image embedded in the PDF, digitized the same way as
this repo's family_size_by_education_uk.py (see that module's docstring for
the general method) -- rendered at 8x page resolution, with one difference
worth flagging: the first pass at the y-axis calibration here used the
gridline rows directly and was off by exactly one gridline (roughly +1
year), silently reading the topmost *unlabelled* minor gridline as the
labelled "30" tick. Caught by cross-checking against the y-axis tick
*label* text's own row positions (which reliably identify only the four
labelled rows, 24/26/28/30) rather than trusting gridline-band detection
alone -- that cross-check is now the calibration this module (and
family_size_by_education_uk.py, checked retrospectively and found
correct) relies on. Point estimate is the vertical midpoint of each
matched marker+error-bar run, per series' own legend-swatch grey level
(17/111/158/190 on a 0-255 scale, same palette as Figure 3/5 in this
paper); the run's own top/bottom rows give the source's 95% CI error bars
directly (plotted below as asymmetric error_y). Values are approximate to
roughly +/-0.05 years, not independently cross-checked against a second
source.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUTPUT = "outputs/mean_age_first_birth_by_education_uk.html"

COUNTRIES = ["England & Wales", "Scotland", "Northern Ireland"]
SERIES = ["Low", "Medium", "High", "All"]
SERIES_STYLE = {
    "Low": dict(color="#1a1a1a", dash="solid"),
    "Medium": dict(color="#707070", dash="solid"),
    "High": dict(color="#b0b0b0", dash="solid"),
    "All": dict(color="#b0b0b0", dash="dot"),
}
Y_RANGE = [23, 31.5]

# {country: {series: [(cohort_label, value, err_minus, err_plus), ...]}} --
# see module docstring for how these were digitized, including the error
# bars. Northern Ireland has no 1956-1959/1960-1964 points (NILS doesn't
# cover them).
MEAN_AGE_FIRST_BIRTH = {
    "England & Wales": {
        "Low": [("1956-1959", 24.66, 0.13, 0.13), ("1960-1964", 25.45, 0.12, 0.11), ("1965-1969", 25.49, 0.12, 0.12), ("1970-1974", 25.38, 0.16, 0.15), ("1975-1978", 24.42, 0.22, 0.22)],
        "Medium": [("1956-1959", 25.77, 0.22, 0.22), ("1960-1964", 26.67, 0.31, 0.31), ("1965-1969", 26.97, 0.31, 0.31), ("1970-1974", 26.96, 0.24, 0.24), ("1975-1978", 26.80, 0.30, 0.30)],
        "High": [("1956-1959", 28.24, 0.25, 0.25), ("1960-1964", 29.28, 0.22, 0.22), ("1965-1969", 30.45, 0.23, 0.23), ("1970-1974", 30.82, 0.19, 0.19), ("1975-1978", 30.77, 0.20, 0.20)],
        "All": [("1956-1959", 25.45, 0.08, 0.08), ("1960-1964", 26.25, 0.09, 0.09), ("1965-1969", 26.54, 0.10, 0.10), ("1970-1974", 27.32, 0.10, 0.10), ("1975-1978", 27.46, 0.12, 0.12)],
    },
    "Scotland": {
        "Low": [("1956-1959", 23.97, 0.18, 0.18), ("1960-1964", 24.54, 0.17, 0.17), ("1965-1969", 24.65, 0.19, 0.19), ("1970-1974", 24.84, 0.26, 0.26), ("1975-1978", 24.14, 0.37, 0.36)],
        "Medium": [("1956-1959", 26.09, 0.39, 0.39), ("1960-1964", 26.94, 0.34, 0.34), ("1965-1969", 27.47, 0.34, 0.34), ("1970-1974", 27.83, 0.38, 0.38), ("1975-1978", 26.46, 0.56, 0.56)],
        "High": [("1956-1959", 27.30, 0.26, 0.26), ("1960-1964", 27.87, 0.25, 0.25), ("1965-1969", 28.86, 0.32, 0.32), ("1970-1974", 29.98, 0.27, 0.27), ("1975-1978", 29.29, 0.30, 0.30)],
        "All": [("1956-1959", 25.17, 0.11, 0.11), ("1960-1964", 25.76, 0.11, 0.11), ("1965-1969", 26.21, 0.12, 0.12), ("1970-1974", 27.35, 0.08, 0.08), ("1975-1978", 27.21, 0.16, 0.16)],
    },
    "Northern Ireland": {
        "Low": [("1965-1969", 24.91, 0.14, 0.14), ("1970-1974", 24.92, 0.15, 0.15), ("1975-1978", 24.04, 0.19, 0.19)],
        "Medium": [("1965-1969", 26.27, 0.32, 0.32), ("1970-1974", 27.07, 0.33, 0.32), ("1975-1978", 26.01, 0.21, 0.21)],
        "High": [("1965-1969", 29.29, 0.28, 0.28), ("1970-1974", 30.21, 0.21, 0.21), ("1975-1978", 29.35, 0.20, 0.20)],
        "All": [("1965-1969", 25.80, 0.14, 0.14), ("1970-1974", 26.48, 0.13, 0.13), ("1975-1978", 26.44, 0.12, 0.12)],
    },
}


def plot():
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.02, column_titles=COUNTRIES)

    for col, country in enumerate(COUNTRIES, start=1):
        for series in SERIES:
            points = MEAN_AGE_FIRST_BIRTH[country][series]
            cohorts, values, err_minus, err_plus = zip(*points)
            fig.add_trace(
                go.Scatter(
                    x=cohorts, y=values, mode="lines+markers", name=series,
                    legendgroup=series, showlegend=(col == 1),
                    line=dict(width=2, **SERIES_STYLE[series]), marker=dict(size=6),
                    error_y=dict(type="data", symmetric=False, array=err_plus, arrayminus=err_minus, width=3, thickness=1),
                    hovertemplate=f"{country}, {series} education<br>%{{x}}<br>%{{y:.1f}} years<extra></extra>",
                ),
                row=1, col=col,
            )
        fig.update_xaxes(
            categoryorder="array", categoryarray=[c for c, *_ in MEAN_AGE_FIRST_BIRTH["England & Wales"]["Low"]],
            tickangle=-45, row=1, col=col,
        )
        fig.update_yaxes(range=Y_RANGE, showticklabels=(col == 1), row=1, col=col)

    fig.update_layout(
        title="Mean age at first birth, by educational attainment and birth cohort",
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
