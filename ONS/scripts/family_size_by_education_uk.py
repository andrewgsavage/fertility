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

Figure 3 itself is a raster image embedded in the PDF, but its data is
also published as exact 2-decimal-place tables -- Appendix 2, Tables
A-3/A-4/A-5 (England & Wales / Scotland / Northern Ireland) -- which is
what the point estimates in FAMILY_SIZE below actually come from, not
pixel digitization. The error bars are still pixel-digitized, since the
appendix tables give point estimates only, no CIs: rendered at 8x page
resolution, the panel's five labelled gridlines (2.50/2.25/2.00/1.75/1.50)
are 828px apart and evenly spaced, giving a linear pixel-to-value
calibration; each facet's five birth-cohort tick columns were located
from the small tick-mark ticks below the bottom panel's axis border. At
each (panel, facet, cohort) column, pixels were classified into
Low/Medium/High/All by matching the exact grey level of each series' own
legend swatch (17/111/158/190 on a 0-255 scale), and the matched
marker+error-bar run's own top/bottom rows re-centred on the exact table
value (rather than the pixel-estimated midpoint, which was occasionally
off by more than the run's own width -- about 20 of the 104 points here,
usually where two series' lines run close together) give the 95% CI error
bars plotted below as asymmetric error_y. Where the exact value fell
outside the pixel-detected run entirely, the run's half-width is used as
a symmetric fallback margin instead of a directly re-centred one. Only the
error-bar widths are therefore approximate; the plotted values themselves
are exact as published.
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

# {panel: {country: {series: [(cohort_label, value, err_minus, err_plus), ...]}}}
# -- values are exact, from Appendix 2 (Tables A-3/A-4/A-5); err_minus/plus
# are pixel-digitized (see module docstring). Northern Ireland has no
# 1956-1959/1960-1964 points (NILS doesn't cover them).
FAMILY_SIZE = {
    "all_women": {
        "England & Wales": {
            "Low": [("1956-1959", 1.91, 0.032, 0.031), ("1960-1964", 1.85, 0.023, 0.021), ("1965-1969", 1.86, 0.023, 0.020), ("1970-1974", 1.87, 0.033, 0.032), ("1975-1978", 2.03, 0.053, 0.051)],
            "Medium": [("1956-1959", 1.78, 0.072, 0.023), ("1960-1964", 1.63, 0.045, 0.061), ("1965-1969", 1.60, 0.072, 0.059), ("1970-1974", 1.68, 0.018, 0.018), ("1975-1978", 1.69, 0.028, 0.028)],
            "High": [("1956-1959", 1.65, 0.052, 0.057), ("1960-1964", 1.53, 0.042, 0.053), ("1965-1969", 1.42, 0.043, 0.041), ("1970-1974", 1.43, 0.042, 0.031), ("1975-1978", 1.47, 0.032, 0.041)],
            "All": [("1956-1959", 1.83, 0.023, 0.023), ("1960-1964", 1.75, 0.023, 0.022), ("1965-1969", 1.73, 0.025, 0.022), ("1970-1974", 1.68, 0.013, 0.022), ("1975-1978", 1.71, 0.005, 0.032)],
        },
        "Scotland": {
            "Low": [("1956-1959", 1.91, 0.042, 0.039), ("1960-1964", 1.88, 0.037, 0.035), ("1965-1969", 1.83, 0.041, 0.038), ("1970-1974", 1.77, 0.055, 0.052), ("1975-1978", 1.88, 0.078, 0.077)],
            "Medium": [("1956-1959", 1.74, 0.024, 0.024), ("1960-1964", 1.67, 0.026, 0.026), ("1965-1969", 1.58, 0.064, 0.064), ("1970-1974", 1.56, 0.077, 0.000), ("1975-1978", 1.57, 0.034, 0.004)],
            "High": [("1956-1959", 1.69, 0.055, 0.055), ("1960-1964", 1.63, 0.049, 0.051), ("1965-1969", 1.46, 0.053, 0.054), ("1970-1974", 1.43, 0.046, 0.045), ("1975-1978", 1.48, 0.051, 0.055)],
            "All": [("1956-1959", 1.83, 0.008, 0.030), ("1960-1964", 1.78, 0.013, 0.027), ("1965-1969", 1.69, 0.011, 0.029), ("1970-1974", 1.60, 0.002, 0.039), ("1975-1978", 1.62, 0.018, 0.018)],
        },
        "Northern Ireland": {
            "Low": [("1965-1969", 2.01, 0.029, 0.036), ("1970-1974", 1.97, 0.032, 0.035), ("1975-1978", 2.05, 0.042, 0.048)],
            "Medium": [("1965-1969", 1.85, 0.034, 0.064), ("1970-1974", 1.84, 0.028, 0.028), ("1975-1978", 1.93, 0.017, 0.017)],
            "High": [("1965-1969", 1.75, 0.066, 0.065), ("1970-1974", 1.76, 0.049, 0.050), ("1975-1978", 1.78, 0.041, 0.049)],
            "All": [("1965-1969", 1.95, 0.009, 0.026), ("1970-1974", 1.90, 0.010, 0.025), ("1975-1978", 1.92, 0.002, 0.034)],
        },
    },
    "excl_childless": {
        "England & Wales": {
            "Low": [("1956-1959", 2.27, 0.003, 0.021), ("1960-1964", 2.24, 0.020, 0.022), ("1965-1969", 2.24, 0.020, 0.022), ("1970-1974", 2.28, 0.032, 0.033), ("1975-1978", 2.41, 0.040, 0.054)],
            "Medium": [("1956-1959", 2.18, 0.003, 0.003), ("1960-1964", 2.10, 0.012, 0.012), ("1965-1969", 2.11, 0.063, 0.051), ("1970-1974", 2.14, 0.052, 0.004), ("1975-1978", 2.09, 0.053, 0.051)],
            "High": [("1956-1959", 2.17, 0.044, 0.046), ("1960-1964", 2.09, 0.044, 0.036), ("1965-1969", 1.99, 0.032, 0.032), ("1970-1974", 1.98, 0.032, 0.020), ("1975-1978", 1.98, 0.032, 0.030)],
            "All": [("1956-1959", 2.24, 0.009, 0.009), ("1960-1964", 2.20, 0.024, 0.016), ("1965-1969", 2.18, 0.015, 0.022), ("1970-1974", 2.17, 0.023, 0.023), ("1975-1978", 2.18, 0.012, 0.023)],
        },
        "Scotland": {
            "Low": [("1956-1959", 2.23, 0.017, 0.017), ("1960-1964", 2.20, 0.001, 0.034), ("1965-1969", 2.16, 0.030, 0.036), ("1970-1974", 2.16, 0.049, 0.050), ("1975-1978", 2.21, 0.071, 0.071)],
            "Medium": [("1956-1959", 2.13, 0.016, 0.016), ("1960-1964", 2.10, 0.014, 0.014), ("1965-1969", 2.03, 0.011, 0.011), ("1970-1974", 2.03, 0.015, 0.015), ("1975-1978", 2.01, 0.014, 0.014)],
            "High": [("1956-1959", 2.14, 0.045, 0.030), ("1960-1964", 2.12, 0.044, 0.021), ("1965-1969", 2.00, 0.046, 0.047), ("1970-1974", 1.95, 0.041, 0.043), ("1975-1978", 1.97, 0.053, 0.051)],
            "All": [("1956-1959", 2.20, 0.009, 0.027), ("1960-1964", 2.17, 0.011, 0.011), ("1965-1969", 2.10, 0.009, 0.026), ("1970-1974", 2.06, 0.006, 0.031), ("1975-1978", 2.06, 0.018, 0.018)],
        },
        "Northern Ireland": {
            "Low": [("1965-1969", 2.38, 0.003, 0.003), ("1970-1974", 2.35, 0.005, 0.005), ("1975-1978", 2.43, 0.016, 0.043)],
            "Medium": [("1965-1969", 2.33, 0.004, 0.004), ("1970-1974", 2.30, 0.006, 0.006), ("1975-1978", 2.35, 0.009, 0.009)],
            "High": [("1965-1969", 2.30, 0.049, 0.033), ("1970-1974", 2.28, 0.046, 0.015), ("1975-1978", 2.29, 0.039, 0.039)],
            "All": [("1965-1969", 2.36, 0.025, 0.028), ("1970-1974", 2.32, 0.024, 0.030), ("1975-1978", 2.36, 0.004, 0.031)],
        },
    },
}


def plot():
    fig = make_subplots(
        rows=2, cols=3, shared_xaxes=True, vertical_spacing=0.08, horizontal_spacing=0.03,
        column_titles=COUNTRIES,
    )

    for row, (panel_key, panel_label) in enumerate(PANELS, start=1):
        for col, country in enumerate(COUNTRIES, start=1):
            for series in SERIES:
                points = FAMILY_SIZE[panel_key][country][series]
                if not points:
                    continue
                cohorts, values, err_minus, err_plus = zip(*points)
                fig.add_trace(
                    go.Scatter(
                        x=cohorts, y=values, mode="lines+markers", name=series,
                        legendgroup=series, showlegend=(row == 1 and col == 1),
                        line=dict(width=2, **SERIES_STYLE[series]), marker=dict(size=6),
                        error_y=dict(type="data", symmetric=False, array=err_plus, arrayminus=err_minus, width=3, thickness=1),
                        hovertemplate=f"{country}, {series} education<br>%{{x}}<br>%{{y:.2f}} children<extra></extra>",
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(
                categoryorder="array", categoryarray=[c for c, *_ in FAMILY_SIZE["all_women"]["England & Wales"]["Low"]],
                showticklabels=(row == 2), tickangle=-45, row=row, col=col,
            )
            fig.update_yaxes(
                range=Y_RANGE, showticklabels=(col == 1),
                title_text=panel_label if col == 1 else None, title_standoff=10, automargin=True,
                row=row, col=col,
            )

    fig.update_layout(
        title="Average family size at age 40, by educational attainment and birth cohort",
        template="plotly_white", autosize=True,
        legend=dict(title="Education level", x=1.02, y=1, xanchor="left", yanchor="top"),
        margin=dict(l=90, r=140, t=90),
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
