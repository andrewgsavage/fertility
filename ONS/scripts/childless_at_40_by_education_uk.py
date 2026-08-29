"""Proportion of women without children at age 40, by birth cohort and
educational attainment, England & Wales / Scotland / Northern Ireland --
reproducing Kuang, Berrington & Falkingham (2025) Figure 5 as an
interactive chart.

Kuang, X., Berrington, A. & Falkingham, J. (2025), "Educational trends in
cohort fertility by birth order: A comparison of England and Wales,
Scotland, and Northern Ireland", Demographic Research 51(36):1121-1168.
https://www.demographic-research.org/volumes/vol51/36/51-36.pdf
Source (per the paper): ONS Longitudinal Study, Scottish Longitudinal
Study, Northern Ireland Longitudinal Study (NILS' earliest data point is
the 1966-1969 birth cohort, binned into "1965-1969" here as in the source).

Unlike Figures 3 and 4 in this paper (family_size_by_education_uk.py /
mean_age_first_birth_by_education_uk.py), Figure 5 has no exact published
table behind it -- the paper's appendix covers average family size
(Appendix 2), mean age at first birth (Appendix 3) and parity progression
ratios (Appendix 4), but not proportion childless as such. Table A-7
(Appendix 4, transition from childless to first birth) is a related but
distinct measure -- 1 minus that ratio tracks these values closely but
not exactly, likely a different age cutoff or estimation method, so it
isn't used as a substitute here. CHILDLESS_AT_40 below is therefore fully
pixel-digitized, same method as this repo's
mean_age_first_birth_by_education_uk.py / family_size_by_education_uk.py
(see either module's docstring), with y-axis calibration cross-checked
against the axis tick label text's own row positions rather than trusting
gridline-band detection alone; the marker+error-bar run's own top/bottom
rows give the source's 95% CI error bars directly (plotted below as
asymmetric error_y). Values are approximate to roughly +/-0.005
(i.e. +/-0.5pp), not independently cross-checked against a second source.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUTPUT = "outputs/childless_at_40_by_education_uk.html"

COUNTRIES = ["England & Wales", "Scotland", "Northern Ireland"]
SERIES = ["Low", "Medium", "High", "All"]
SERIES_STYLE = {
    "Low": dict(color="#1a1a1a", dash="solid"),
    "Medium": dict(color="#707070", dash="solid"),
    "High": dict(color="#b0b0b0", dash="solid"),
    "All": dict(color="#b0b0b0", dash="dot"),
}
Y_RANGE = [0.08, 0.37]

# {country: {series: [(cohort_label, value, err_minus, err_plus), ...]}} --
# see module docstring for how these were digitized, including the error
# bars. Northern Ireland has no 1956-1959/1960-1964 points (NILS doesn't
# cover them).
CHILDLESS_AT_40 = {
    "England & Wales": {
        "Low": [("1956-1959", 0.156, 0.007, 0.007), ("1960-1964", 0.173, 0.008, 0.007), ("1965-1969", 0.171, 0.007, 0.007), ("1970-1974", 0.180, 0.009, 0.009), ("1975-1978", 0.159, 0.013, 0.013)],
        "Medium": [("1956-1959", 0.200, 0.009, 0.009), ("1960-1964", 0.228, 0.019, 0.019), ("1965-1969", 0.243, 0.023, 0.023), ("1970-1974", 0.209, 0.012, 0.012), ("1975-1978", 0.189, 0.015, 0.014)],
        "High": [("1956-1959", 0.240, 0.017, 0.018), ("1960-1964", 0.265, 0.016, 0.015), ("1965-1969", 0.286, 0.017, 0.017), ("1970-1974", 0.279, 0.014, 0.014), ("1975-1978", 0.257, 0.015, 0.015)],
        "All": [("1956-1959", 0.182, 0.003, 0.002), ("1960-1964", 0.204, 0.005, 0.005), ("1965-1969", 0.209, 0.005, 0.005), ("1970-1974", 0.227, 0.005, 0.005), ("1975-1978", 0.217, 0.006, 0.006)],
    },
    "Scotland": {
        "Low": [("1956-1959", 0.143, 0.012, 0.012), ("1960-1964", 0.147, 0.011, 0.011), ("1965-1969", 0.150, 0.012, 0.012), ("1970-1974", 0.179, 0.016, 0.017), ("1975-1978", 0.150, 0.022, 0.022)],
        "Medium": [("1956-1959", 0.186, 0.007, 0.007), ("1960-1964", 0.200, 0.012, 0.012), ("1965-1969", 0.226, 0.019, 0.019), ("1970-1974", 0.241, 0.006, 0.006), ("1975-1978", 0.192, 0.007, 0.007)],
        "High": [("1956-1959", 0.213, 0.019, 0.019), ("1960-1964", 0.230, 0.017, 0.017), ("1965-1969", 0.270, 0.020, 0.020), ("1970-1974", 0.267, 0.019, 0.019), ("1975-1978", 0.248, 0.021, 0.021)],
        "All": [("1956-1959", 0.172, 0.006, 0.006), ("1960-1964", 0.181, 0.006, 0.006), ("1965-1969", 0.200, 0.006, 0.006), ("1970-1974", 0.218, 0.007, 0.007), ("1975-1978", 0.211, 0.005, 0.005)],
    },
    "Northern Ireland": {
        "Low": [("1965-1969", 0.156, 0.009, 0.009), ("1970-1974", 0.165, 0.009, 0.009), ("1975-1978", 0.155, 0.008, 0.008)],
        "Medium": [("1965-1969", 0.212, 0.022, 0.022), ("1970-1974", 0.215, 0.015, 0.015), ("1975-1978", 0.175, 0.012, 0.012)],
        "High": [("1965-1969", 0.256, 0.021, 0.021), ("1970-1974", 0.246, 0.016, 0.016), ("1975-1978", 0.227, 0.014, 0.014)],
        "All": [("1965-1969", 0.183, 0.006, 0.006), ("1970-1974", 0.194, 0.005, 0.005), ("1975-1978", 0.193, 0.006, 0.006)],
    },
}


def plot():
    fig = make_subplots(rows=1, cols=3, shared_yaxes=True, horizontal_spacing=0.02, column_titles=COUNTRIES)

    for col, country in enumerate(COUNTRIES, start=1):
        for series in SERIES:
            points = CHILDLESS_AT_40[country][series]
            cohorts, values, err_minus, err_plus = zip(*points)
            fig.add_trace(
                go.Scatter(
                    x=cohorts, y=values, mode="lines+markers", name=series,
                    legendgroup=series, showlegend=(col == 1),
                    line=dict(width=2, **SERIES_STYLE[series]), marker=dict(size=6),
                    error_y=dict(type="data", symmetric=False, array=err_plus, arrayminus=err_minus, width=3, thickness=1),
                    hovertemplate=f"{country}, {series} education<br>%{{x}}<br>%{{y:.1%}} childless<extra></extra>",
                ),
                row=1, col=col,
            )
        fig.update_xaxes(
            categoryorder="array", categoryarray=[c for c, *_ in CHILDLESS_AT_40["England & Wales"]["Low"]],
            tickangle=-45, row=1, col=col,
        )
        fig.update_yaxes(range=Y_RANGE, tickformat=".0%", showticklabels=(col == 1), row=1, col=col)

    fig.update_layout(
        title="Proportion of women without children at age 40, by birth cohort and educational attainment",
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
