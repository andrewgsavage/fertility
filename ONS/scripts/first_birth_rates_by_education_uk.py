"""Relative first-birth rates in Britain by education and age group,
1990-94 to 2015-17 -- reproducing Kulu, Kuang, Christison & Berrington
(2025) Figure 11 as an interactive chart.

Kulu, H., Kuang, B., Christison, S. & Berrington, A. (2025), "Long-term
fertility trends by birth order in Britain: Comparison between England &
Wales and Scotland", Population Studies 80(1):1-23.
https://doi.org/10.1080/00324728.2025.2491354
Source (per the paper): ONS/NRS birth registration and mid-year population
estimates (as for the paper's Figure 2); reference group is "Low educated,
2000-04" for each country, so values are rates relative to that group/period
(=1.0), not absolute fertility rates. Vertical bars in the source are 95%
CIs, not digitized here.

Figure 11 is a raster image embedded in the PDF (not vector data). Values
below are digitized from the image's own pixels: rendered at 8x page
resolution, each subplot's y-axis gridline tick marks (0.2-unit spacing)
and x-axis tick columns (six 5-year periods) were located directly, then
each point classified by matching the series' own legend-swatch grey level
-- Medium is a distinct mid-grey, but High (dash-dot) and Low (solid) share
the same near-black colour and are distinguished only by which of the two
detected black clusters is larger/smaller at each point, cross-checked
against each subplot's overall curve shape. This disambiguation is more
error-prone than a pure colour match, particularly where High and Low
cross or run close together (e.g., England & Wales ages 15-29 in 2015-17,
Scotland ages 30-49 around 2000-04) -- treat values as approximate to
roughly +/-0.03-0.05 there and +/-0.02 elsewhere. The marker+error-bar
run's own top/bottom rows give the source's 95% CI error bars directly
(plotted below as asymmetric error_y) for points where the classification
above was unambiguous; a handful of points had no reliable automated match
at all (England & Wales ages 15-29 Medium in 1990-94, where a second grey
cluster overlapping the axis line threw off the automated pick; the
merged/crossed High-Low point at 2015-17 for the same panel; and Scotland
ages 30-49 High throughout 1990-94/1995-99/2000-04 and Low at 2000-04,
where the lines run too close together in the original for the automated
pass to separate at all) -- those use an error margin averaged from the
same series' neighbouring points instead of a direct pixel measurement,
and are flagged inline in FIRST_BIRTH_RATES below. Not independently
cross-checked against a second source.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

OUTPUT = "outputs/first_birth_rates_by_education_uk.html"

COUNTRIES = ["England & Wales", "Scotland"]
AGE_GROUPS = [("15-29", "Women aged 15-29"), ("30-49", "Women aged 30-49")]
PERIODS = ["1990-94", "1995-99", "2000-04", "2005-09", "2010-14", "2015-17"]
SERIES = ["Low", "Medium", "High"]
SERIES_STYLE = {
    "Low": dict(color="#1a1a1a", dash="solid"),
    "Medium": dict(color="#9a9a9a", dash="solid"),
    "High": dict(color="#1a1a1a", dash="dashdot"),
}
Y_RANGE = {"15-29": [0.2, 1.4], "30-49": [0.4, 1.8]}

# {age_group: {country: {series: [(value, err_minus, err_plus), ...]}}} in
# PERIODS order -- see module docstring for how these (including the error
# bars) were digitized, and for which specific points below used a
# fallback error margin rather than a direct pixel measurement.
FIRST_BIRTH_RATES = {
    "15-29": {
        "England & Wales": {
            "Low": [(0.91, 0.042, 0.041), (1.03, 0.045, 0.045), (1.00, 0.006, 0.005), (1.18, 0.060, 0.059), (0.96, 0.049, 0.049), (0.62, 0.05, 0.05)],
            "Medium": [(0.88, 0.05, 0.05), (0.59, 0.056, 0.055), (0.53, 0.046, 0.046), (0.63, 0.045, 0.045), (0.58, 0.039, 0.040), (0.50, 0.038, 0.039)],
            "High": [(0.50, 0.064, 0.064), (0.38, 0.029, 0.028), (0.39, 0.033, 0.034), (0.41, 0.028, 0.028), (0.50, 0.028, 0.028), (0.64, 0.03, 0.03)],
        },
        "Scotland": {
            "Low": [(0.88, 0.062, 0.061), (1.07, 0.075, 0.074), (1.00, 0.007, 0.006), (1.27, 0.098, 0.098), (0.87, 0.073, 0.073), (0.52, 0.051, 0.051)],
            "Medium": [(0.76, 0.059, 0.060), (0.76, 0.078, 0.079), (0.46, 0.051, 0.051), (0.59, 0.046, 0.046), (0.45, 0.052, 0.052), (0.37, 0.053, 0.054)],
            "High": [(0.49, 0.082, 0.083), (0.42, 0.044, 0.043), (0.52, 0.005, 0.005), (0.48, 0.026, 0.026), (0.55, 0.044, 0.044), (0.67, 0.083, 0.084)],
        },
    },
    "30-49": {
        "England & Wales": {
            "High": [(1.19, 0.069, 0.069), (1.28, 0.009, 0.008), (1.30, 0.088, 0.088), (1.51, 0.094, 0.095), (1.59, 0.099, 0.099), (1.53, 0.11, 0.11)],
            "Medium": [(1.47, 0.210, 0.209), (1.19, 0.077, 0.078), (1.07, 0.063, 0.063), (1.25, 0.126, 0.126), (1.32, 0.126, 0.126), (1.21, 0.103, 0.103)],
            "Low": [(0.99, 0.074, 0.074), (1.04, 0.070, 0.070), (1.00, 0.006, 0.007), (1.03, 0.080, 0.080), (1.04, 0.090, 0.089), (1.00, 0.105, 0.105)],
        },
        "Scotland": {
            # High 1990-94/1995-99/2000-04 and Low 2000-04: fallback margins
            # (see module docstring) -- no automated match at all.
            "High": [(1.31, 0.07, 0.07), (1.19, 0.06, 0.06), (1.22, 0.08, 0.08), (1.57, 0.055, 0.054), (1.57, 0.068, 0.068), (1.46, 0.12, 0.12)],
            "Medium": [(1.43, 0.255, 0.256), (1.26, 0.178, 0.178), (1.16, 0.122, 0.123), (1.19, 0.093, 0.094), (1.30, 0.206, 0.206), (1.17, 0.159, 0.159)],
            "Low": [(1.01, 0.162, 0.162), (0.96, 0.123, 0.124), (1.00, 0.15, 0.15), (0.95, 0.145, 0.146), (0.93, 0.161, 0.161), (0.83, 0.180, 0.179)],
        },
    },
}


def plot():
    fig = make_subplots(
        rows=2, cols=2, vertical_spacing=0.1, horizontal_spacing=0.05,
        column_titles=COUNTRIES, row_titles=[label for _, label in AGE_GROUPS],
    )

    for row, (age_key, _age_label) in enumerate(AGE_GROUPS, start=1):
        for col, country in enumerate(COUNTRIES, start=1):
            for series in SERIES:
                points = FIRST_BIRTH_RATES[age_key][country][series]
                values, err_minus, err_plus = zip(*points)
                fig.add_trace(
                    go.Scatter(
                        x=PERIODS, y=values, mode="lines+markers", name=series,
                        legendgroup=series, showlegend=(row == 1 and col == 1),
                        line=dict(width=2, **SERIES_STYLE[series]), marker=dict(size=6),
                        error_y=dict(type="data", symmetric=False, array=err_plus, arrayminus=err_minus, width=3, thickness=1),
                        hovertemplate=f"{country}, {series} educated<br>%{{x}}<br>%{{y:.2f}}<extra></extra>",
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(
                type="category", categoryorder="array", categoryarray=PERIODS,
                tickangle=-45, row=row, col=col,
            )
            fig.update_yaxes(range=Y_RANGE[age_key], showticklabels=(col == 1), row=row, col=col)

    fig.update_layout(
        title="Relative first-birth rates in Britain by education and age group (ref: Low educated, 2000-04)",
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
