"""Women's leaving age vs TFR and vs mean age of mothers at first birth, all
years on one static chart per y metric, by European country (alternatives to
the year-slider scatters in leaving_home_vs_tfr.py).

Every country-year is a faint point. Each country gets one arrow along its
straight-line trend in both variables from START_YEAR to its latest year:
leaving age and the y metric are each regressed on year, and the arrow
joins the fitted values at the first and last year. Hovering an arrow
highlights the country-years it was fitted to; clicking a region in the legend
hides its arrows. Built with common/trend_arrows.py.

Inputs: as leaving_home_vs_tfr.py (eurostat/data/).
Outputs: outputs/leaving_home_tfr_fitted.html, outputs/leaving_home_mab1_fitted.html
"""

from common.paths import outputs_dir
from common.trend_arrows import write_trend_arrows
from leaving_home_vs_tfr import CODE_REGION, NAMES, REGION_COLOR, load

START_YEAR = 2010
XTITLE = "Women's average age at leaving the parental home"

# y metric -> (axis title, hover format, output file)
METRICS = {
    "tfr": ("Total fertility rate", ".2f", outputs_dir("eurostat") / "leaving_home_tfr_fitted.html"),
    "mab1": ("Mean age of mothers at first birth", ".1f", outputs_dir("eurostat") / "leaving_home_mab1_fitted.html"),
}


def fitted(df, ycol):
    ytitle, yfmt, output = METRICS[ycol]
    df = df.dropna(subset=[ycol, "age"])
    regions = list(REGION_COLOR)
    series = []
    # Sorted by region so the legend lists regions in REGION_COLOR order.
    for geo, g in sorted(df.groupby("geo"), key=lambda kv: regions.index(CODE_REGION[kv[0]])):
        g = g.sort_values("year")
        region = CODE_REGION[geo]
        series.append({"name": NAMES[geo], "label": geo, "group": region, "color": REGION_COLOR[region],
                       "years": g["year"].tolist(), "x": {"age": g["age"].tolist()},
                       "y": {ycol: g[ycol].tolist()}})
    write_trend_arrows(
        output, series, {"age": XTITLE}, {ycol: ytitle},
        title=f"Each country's linear trend, {START_YEAR} to latest year (points: every country-year)",
        start_year=START_YEAR, y_fmt=yfmt, full_page=False, log=False,
        layout=dict(legend=dict(orientation="h", y=-0.15)))


if __name__ == "__main__":
    _, df = load()
    for ycol in METRICS:
        fitted(df, ycol)
