"""Expected total children given first birth at that age, one interactive
Plotly facet grid across every HFD country with a complete-enough cohort
(see births_per_mother_region_grid.load_data) -- replaces the old
per-region tab-set of static matplotlib grids with a single page, faceted
six countries per row, in the same style as cond_asfr_facet.py's
first-vs-second-birth grid.
"""

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from births_per_mother_region_grid import X_LIM, Y_LIM, load_data
from country_names import COUNTRY_REGIONS, country_title

OUTPUT = "outputs/births_per_mother_facet.html"

COUNTRIES_PER_ROW = 6
ROW_HEIGHT = 190
# Matches plotly_white's default axis-title font (size/family/color), so the
# per-panel country titles read as part of the same system as the
# first-vs-second-birth facet grid.
LABEL_FONT = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")


def _cohort_color(cohort, cmin, cmax, alpha=0.6):
    t = 0.0 if cmax == cmin else (cohort - cmin) / (cmax - cmin)
    r, g, b = pc.sample_colorscale("Turbo", [t])[0][4:-1].split(",")
    return f"rgba({r},{g},{b},{alpha})"


def make_facet(df, countries):
    """One Plotly figure with one subplot per country, COUNTRIES_PER_ROW
    countries per row, continuing onto further rows rather than behind
    per-region tabs -- same continuous-grid convention as
    cond_asfr_facet.py's first-vs-second-birth page."""
    cmin, cmax = df["cohort"].min(), df["cohort"].max()
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
            name = country_title(code, subset["cohort"].min(), subset["cohort"].max())
            for cohort, cohort_rows in subset.groupby("cohort"):
                cohort_rows = cohort_rows.sort_values("age")
                fig.add_trace(
                    go.Scatter(
                        x=cohort_rows["age"], y=cohort_rows["expected_children"], mode="lines",
                        line=dict(width=0.8, color=_cohort_color(cohort, cmin, cmax)),
                        name=str(cohort), legendgroup=str(cohort), showlegend=False,
                        hovertemplate=f"{name}<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
                    ),
                    row=row, col=col,
                )
            fig.update_xaxes(range=list(X_LIM), showticklabels=(row == nrows), row=row, col=col)
            fig.update_yaxes(range=list(Y_LIM), showticklabels=(col == 1), row=row, col=col)

    # Dummy trace to show a colorbar for the cohort axis, placed next to the
    # last country's subplot when that row has empty columns to spare
    # (country count isn't always a multiple of COUNTRIES_PER_ROW);
    # otherwise fall back to the top-right corner.
    last_row_countries = rows_of_countries[-1]
    if len(last_row_countries) < ncols:
        cb_row, cb_col = nrows, len(last_row_countries) + 1
    else:
        cb_row, cb_col = 1, ncols
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=cmin, cmax=cmax,
                color=[cmin], showscale=True,
                colorbar=dict(title="Birth cohort"),
            ),
            showlegend=False,
        ),
        row=cb_row, col=cb_col,
    )
    fig.update_xaxes(visible=False, row=cb_row, col=cb_col)
    fig.update_yaxes(visible=False, row=cb_row, col=cb_col)

    fig.update_layout(
        title="Expected total children given first birth at that age, by country",
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 90,
        showlegend=False,
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    all_codes = [code for codes in COUNTRY_REGIONS.values() for code in codes]
    present = set(df["code"].unique())
    countries = [code for code in all_codes if code in present]
    fig = make_facet(df, countries)

    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height=f"{fig.layout.height}px",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT} (height={fig.layout.height}px)")
