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
directly from the legend rather than assumed). The point estimate is the
vertical midpoint of the matched marker+error-bar run, and the run's own
top/bottom rows give the source's 95% CI error bars directly (plotted
below as asymmetric error_y, since the marker's own radius makes the two
sides not perfectly equal in pixel terms even though the underlying CI is
symmetric). Values are therefore approximate to roughly +/-0.02 children,
and -- unlike this repo's ONS-derived series -- aren't cross-checked
against a second, independent source.
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
# -- see module docstring for how these were digitized, including the
# error bars. Northern Ireland has no 1956-1959/1960-1964 points (NILS
# doesn't cover them).
FAMILY_SIZE = {
    "all_women": {
        "England & Wales": {
            "Low": [("1956-1959", 1.909, 0.031, 0.032), ("1960-1964", 1.849, 0.022, 0.022), ("1965-1969", 1.859, 0.022, 0.021), ("1970-1974", 1.870, 0.033, 0.032), ("1975-1978", 2.029, 0.052, 0.052)],
            "Medium": [("1956-1959", 1.755, 0.047, 0.048), ("1960-1964", 1.638, 0.053, 0.053), ("1965-1969", 1.594, 0.066, 0.065), ("1970-1974", 1.635, 0.019, 0.018), ("1975-1978", 1.653, 0.027, 0.028)],
            "High": [("1956-1959", 1.652, 0.054, 0.055), ("1960-1964", 1.536, 0.048, 0.047), ("1965-1969", 1.419, 0.042, 0.042), ("1970-1974", 1.425, 0.037, 0.036), ("1975-1978", 1.475, 0.037, 0.036)],
            "All": [("1956-1959", 1.830, 0.023, 0.023), ("1960-1964", 1.749, 0.022, 0.023), ("1965-1969", 1.729, 0.024, 0.023), ("1970-1974", 1.684, 0.017, 0.018), ("1975-1978", 1.723, 0.018, 0.019)],
        },
        "Scotland": {
            "Low": [("1956-1959", 1.909, 0.041, 0.040), ("1960-1964", 1.879, 0.036, 0.036), ("1965-1969", 1.829, 0.040, 0.039), ("1970-1974", 1.769, 0.054, 0.053), ("1975-1978", 1.879, 0.077, 0.078)],
            "Medium": [("1956-1959", 1.771, 0.025, 0.024), ("1960-1964", 1.708, 0.026, 0.025), ("1965-1969", 1.580, 0.064, 0.064), ("1970-1974", 1.522, 0.039, 0.038), ("1975-1978", 1.555, 0.019, 0.019)],
            "High": [("1956-1959", 1.690, 0.055, 0.055), ("1960-1964", 1.631, 0.050, 0.050), ("1965-1969", 1.461, 0.054, 0.053), ("1970-1974", 1.429, 0.045, 0.046), ("1975-1978", 1.482, 0.053, 0.053)],
            "All": [("1956-1959", 1.841, 0.019, 0.019), ("1960-1964", 1.787, 0.020, 0.020), ("1965-1969", 1.699, 0.020, 0.020), ("1970-1974", 1.618, 0.020, 0.021), ("1975-1978", 1.643, 0.017, 0.018)],
        },
        "Northern Ireland": {
            "Low": [("1965-1969", 2.013, 0.032, 0.033), ("1970-1974", 1.972, 0.034, 0.033), ("1975-1978", 2.053, 0.045, 0.045)],
            "Medium": [("1965-1969", 1.865, 0.049, 0.049), ("1970-1974", 1.840, 0.028, 0.028), ("1975-1978", 1.975, 0.017, 0.017)],
            "High": [("1965-1969", 1.749, 0.065, 0.066), ("1970-1974", 1.761, 0.050, 0.049), ("1975-1978", 1.784, 0.045, 0.045)],
            "All": [("1965-1969", 1.958, 0.017, 0.018), ("1970-1974", 1.908, 0.018, 0.017), ("1975-1978", 1.936, 0.018, 0.018)],
        },
    },
    "excl_childless": {
        "England & Wales": {
            "Low": [("1956-1959", 2.279, 0.012, 0.012), ("1960-1964", 2.241, 0.021, 0.021), ("1965-1969", 2.241, 0.021, 0.021), ("1970-1974", 2.280, 0.032, 0.033), ("1975-1978", 2.417, 0.047, 0.047)],
            "Medium": [("1956-1959", 2.121, 0.003, 0.003), ("1960-1964", 2.139, 0.012, 0.012), ("1965-1969", 2.104, 0.057, 0.057), ("1970-1974", 2.116, 0.028, 0.028), ("1975-1978", 2.089, 0.052, 0.052)],
            "High": [("1956-1959", 2.171, 0.045, 0.045), ("1960-1964", 2.086, 0.040, 0.040), ("1965-1969", 1.990, 0.032, 0.032), ("1970-1974", 1.974, 0.026, 0.026), ("1975-1978", 1.979, 0.031, 0.031)],
            "All": [("1956-1959", 2.254, 0.009, 0.009), ("1960-1964", 2.196, 0.020, 0.020), ("1965-1969", 2.184, 0.019, 0.018), ("1970-1974", 2.170, 0.023, 0.023), ("1975-1978", 2.185, 0.017, 0.018)],
        },
        "Scotland": {
            "Low": [("1956-1959", 2.249, 0.017, 0.017), ("1960-1964", 2.217, 0.018, 0.017), ("1965-1969", 2.163, 0.033, 0.033), ("1970-1974", 2.161, 0.050, 0.049), ("1975-1978", 2.210, 0.071, 0.071)],
            "Medium": [("1956-1959", 2.078, 0.016, 0.016), ("1960-1964", 2.061, 0.014, 0.014), ("1965-1969", 2.059, 0.011, 0.011), ("1970-1974", 2.010, 0.016, 0.015), ("1975-1978", 2.044, 0.014, 0.014)],
            "High": [("1956-1959", 2.133, 0.038, 0.037), ("1960-1964", 2.109, 0.033, 0.032), ("1965-1969", 2.001, 0.047, 0.046), ("1970-1974", 1.951, 0.042, 0.042), ("1975-1978", 1.969, 0.052, 0.052)],
            "All": [("1956-1959", 2.209, 0.018, 0.018), ("1960-1964", 2.153, 0.010, 0.011), ("1965-1969", 2.108, 0.017, 0.018), ("1970-1974", 2.072, 0.018, 0.019), ("1975-1978", 2.080, 0.018, 0.018)],
        },
        "Northern Ireland": {
            # 1965-1969 Low/Medium error bars come out unusually narrow --
            # all four series are tightly bunched (~2.29-2.40) at this
            # point, so the marker+error-bar runs partially overlap and
            # the pixel classification likely clips them; treat as a
            # lower-confidence point (see module docstring's general
            # +/-0.02 caveat, which does not fully cover this case).
            "Low": [("1965-1969", 2.404, 0.003, 0.003), ("1970-1974", 2.373, 0.005, 0.005), ("1975-1978", 2.444, 0.030, 0.029)],
            "Medium": [("1965-1969", 2.396, 0.005, 0.004), ("1970-1974", 2.361, 0.007, 0.006), ("1975-1978", 2.403, 0.009, 0.010)],
            "High": [("1965-1969", 2.292, 0.041, 0.041), ("1970-1974", 2.264, 0.030, 0.031), ("1975-1978", 2.290, 0.039, 0.039)],
            "All": [("1965-1969", 2.361, 0.026, 0.027), ("1970-1974", 2.323, 0.027, 0.027), ("1975-1978", 2.374, 0.018, 0.017)],
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
