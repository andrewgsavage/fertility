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

Figure 4 itself is a raster image embedded in the PDF, but its data is
also published as an exact 1-decimal-place table -- Appendix 3, Table
A-6 -- which is what the point estimates in MEAN_AGE_FIRST_BIRTH below
actually come from, not pixel digitization (Table A-6 covers all three
countries in one table, unlike Figure 3's per-country appendix tables).

The error bars are still pixel-digitized, the same way as this repo's
family_size_by_education_uk.py (see that module's docstring for the
general method and the same re-centring/fallback approach used here),
rendered at 8x page resolution -- with one difference worth flagging: the
first pass at the y-axis calibration here used the gridline rows directly
and was off by exactly one gridline (roughly +1 year), silently reading
the topmost *unlabelled* minor gridline as the labelled "30" tick. Caught
by cross-checking against the y-axis tick *label* text's own row
positions (which reliably identify only the four labelled rows,
24/26/28/30) rather than trusting gridline-band detection alone -- that
cross-check is what the error-bar calibration here relies on (and what
confirmed family_size_by_education_uk.py's own calibration was correct,
checked retrospectively). Every exact table value fell within its own
pixel-detected error-bar run here (unlike Figure 3, where about 20 of 104
points needed the fallback margin), so no fallback cases to flag. Only
the error-bar widths are approximate; the plotted values themselves are
exact as published.
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
# values are exact, from Appendix 3 (Table A-6); err_minus/plus are
# pixel-digitized (see module docstring). Northern Ireland has no
# 1956-1959/1960-1964 points (NILS doesn't cover them).
MEAN_AGE_FIRST_BIRTH = {
    "England & Wales": {
        "Low": [("1956-1959", 24.7, 0.17, 0.10), ("1960-1964", 25.4, 0.07, 0.16), ("1965-1969", 25.5, 0.13, 0.11), ("1970-1974", 25.4, 0.17, 0.14), ("1975-1978", 24.4, 0.20, 0.24)],
        "Medium": [("1956-1959", 25.6, 0.06, 0.39), ("1960-1964", 26.7, 0.34, 0.28), ("1965-1969", 26.9, 0.24, 0.38), ("1970-1974", 27.0, 0.28, 0.19), ("1975-1978", 26.8, 0.30, 0.30)],
        "High": [("1956-1959", 28.2, 0.21, 0.29), ("1960-1964", 29.3, 0.24, 0.20), ("1965-1969", 30.5, 0.28, 0.18), ("1970-1974", 30.8, 0.16, 0.21), ("1975-1978", 30.8, 0.22, 0.17)],
        "All": [("1956-1959", 25.5, 0.13, 0.02), ("1960-1964", 26.3, 0.14, 0.04), ("1965-1969", 26.6, 0.16, 0.04), ("1970-1974", 27.3, 0.08, 0.11), ("1975-1978", 27.4, 0.06, 0.18)],
    },
    "Scotland": {
        "Low": [("1956-1959", 24.0, 0.21, 0.15), ("1960-1964", 24.5, 0.13, 0.20), ("1965-1969", 24.7, 0.24, 0.14), ("1970-1974", 24.8, 0.22, 0.29), ("1975-1978", 24.1, 0.33, 0.40)],
        "Medium": [("1956-1959", 26.1, 0.40, 0.38), ("1960-1964", 26.9, 0.30, 0.37), ("1965-1969", 27.5, 0.37, 0.30), ("1970-1974", 27.8, 0.35, 0.40), ("1975-1978", 26.5, 0.60, 0.52)],
        "High": [("1956-1959", 27.3, 0.26, 0.25), ("1960-1964", 27.9, 0.28, 0.22), ("1965-1969", 28.9, 0.36, 0.28), ("1970-1974", 30.0, 0.30, 0.25), ("1975-1978", 29.3, 0.31, 0.29)],
        "All": [("1956-1959", 25.1, 0.04, 0.18), ("1960-1964", 25.7, 0.04, 0.17), ("1965-1969", 26.2, 0.11, 0.13), ("1970-1974", 27.4, 0.13, 0.03), ("1975-1978", 27.1, 0.06, 0.27)],
    },
    "Northern Ireland": {
        "Low": [("1965-1969", 24.9, 0.13, 0.16), ("1970-1974", 24.9, 0.13, 0.16), ("1975-1978", 24.0, 0.15, 0.23)],
        "Medium": [("1965-1969", 26.2, 0.25, 0.39), ("1970-1974", 27.1, 0.36, 0.29), ("1975-1978", 26.1, 0.30, 0.12)],
        "High": [("1965-1969", 29.3, 0.29, 0.26), ("1970-1974", 30.2, 0.19, 0.22), ("1975-1978", 29.4, 0.25, 0.15)],
        "All": [("1965-1969", 25.8, 0.14, 0.14), ("1970-1974", 26.5, 0.15, 0.12), ("1975-1978", 26.4, 0.08, 0.16)],
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
