"""Same expected-children-given-first-birth-age recursion as
births_per_mother_facet.py, run on HFD's period fertility tables (pft.txt)
instead of cohort tables (cft.txt) -- one line per calendar year instead of
one line per birth cohort, for every country in COUNTRY_REGIONS. A
period-basis cross-check of the same estimation method against the main
(cohort-based) chart, covering every country rather than just the handful
with register-measured parity data.

UK_ONS is skipped: it has no HFD period table to run this on (the main
chart's UK column comes from ONS Table 3 instead, which is inherently
cohort-based).
"""

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from births_per_mother_period_grid import load_data
from births_per_mother_region_grid import X_LIM, Y_LIM
from common.country_names import COUNTRY_REGIONS, country_title
from common.plot_colors import PERIOD_CAXIS, PERIOD_COLORSCALE
from common.paths import outputs_dir
from common.plotting import write_html

OUTPUT = outputs_dir("HFD") / "births_per_mother_estimated_facet.html"

COUNTRIES_PER_ROW = 6
ROW_HEIGHT = 190
LABEL_FONT = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")


def _year_color(year, ymin, ymax, alpha=0.6):
    t = 0.0 if ymax == ymin else (year - ymin) / (ymax - ymin)
    t = min(1.0, max(0.0, t))  # clip: years outside [ymin, ymax] clamp to the end color
    r, g, b = pc.sample_colorscale(PERIOD_COLORSCALE, [t])[0][4:-1].split(",")
    return f"rgba({r},{g},{b},{alpha})"


def make_facet(df, countries):
    ymin, ymax = PERIOD_CAXIS
    rows_of_countries = [
        countries[i : i + COUNTRIES_PER_ROW] for i in range(0, len(countries), COUNTRIES_PER_ROW)
    ]
    nrows = len(rows_of_countries)
    ncols = COUNTRIES_PER_ROW

    subplot_titles = []
    for row_countries in rows_of_countries:
        for code in row_countries:
            subplot_titles.append(f"<b>{country_title(code)}</b>")
        subplot_titles += [""] * (ncols - len(row_countries))

    fig = make_subplots(
        rows=nrows, cols=ncols, subplot_titles=subplot_titles,
        horizontal_spacing=0.015, vertical_spacing=min(0.05, 1 / max(nrows - 1, 1)),
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT

    for row, row_countries in enumerate(rows_of_countries, start=1):
        for col, code in enumerate(row_countries, start=1):
            subset = df[df["code"] == code]
            name = country_title(code, subset["year"].min(), subset["year"].max())
            for year, year_rows in subset.groupby("year"):
                year_rows = year_rows.sort_values("age")
                fig.add_trace(
                    go.Scatter(
                        x=year_rows["age"], y=year_rows["expected_children"], mode="lines",
                        line=dict(width=0.8, color=_year_color(year, ymin, ymax)),
                        name=str(year), legendgroup=str(year), showlegend=False,
                        hovertemplate=f"{name}<br>Year {year}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(range=list(X_LIM), showticklabels=(row == nrows), row=row, col=col)
            fig.update_yaxes(range=list(Y_LIM), showticklabels=(col == 1), row=row, col=col)

    last_row_countries = rows_of_countries[-1]
    if len(last_row_countries) < ncols:
        cb_row, cb_col = nrows, len(last_row_countries) + 1
    else:
        cb_row, cb_col = 1, ncols
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale=PERIOD_COLORSCALE, cmin=ymin, cmax=ymax,
                color=[ymin], showscale=True,
                colorbar=dict(title="Year"),
            ),
            showlegend=False,
        ),
        row=cb_row, col=cb_col,
    )
    fig.update_xaxes(visible=False, row=cb_row, col=cb_col)
    fig.update_yaxes(visible=False, row=cb_row, col=cb_col)

    fig.update_layout(
        title="Estimated expected total children given first birth at that age (period basis), by country",
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 90,
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    all_codes = [code for codes in COUNTRY_REGIONS.values() for code in codes if code != "UK_ONS"]
    present = set(df["code"].unique())
    countries = [code for code in all_codes if code in present]
    fig = make_facet(df, countries)

    write_html(fig, OUTPUT, height=f"{fig.layout.height}px", log=False)
    print(f"Saved {OUTPUT} (height={fig.layout.height}px)")
