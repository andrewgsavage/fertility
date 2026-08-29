"""Overlay HFD-derived expected-children-by-age-of-first-birth curves
against Beaujouan, Zeman & Nathan (2023, Demographic Research) -- "mothers'
completed fertility conditional on age at first birth" (their CFMx), for
the seven of their ten countries HFD has cohort parity-progression data
for (France, Italy and Switzerland aren't in HFD's cft.txt at all).

Unlike the Finland (Roustaei) comparison, the paper's own grouping here
*is* by birth-cohort decade (1940-49/1950-59/1960-69), the same unit HFD's
cft.txt is indexed by -- so each decade's HFD cohorts are averaged
together into one solid line, colored to match that decade's paper line
(dashed), instead of showing the full per-cohort spaghetti. Faceted one
country per row, one decade per column, with the country's other two
decades shown in light grey for context in each panel.

The paper's own values are exact, not digitized: it supplies an Excel
supplement (one sheet per country) with the CFMx figures underlying its
own Figure 3, grouped into 1940-49/1950-59/1960-69 birth-cohort decades
and 5-year age-at-first-birth bins (15-19 .. 40-44). Age bins are plotted
at their midpoint (17, 22, 27, 32, 37, 42).
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from births_per_mother_region_grid import X_LIM, Y_LIM, load_data
from country_names import COUNTRY_NAMES

OUTPUT = "outputs/beaujouan_paper_comparison.html"

# GBR isn't an HFD code (paper's own label, compared against UK_ONS below).
COUNTRY_TITLES = {**COUNTRY_NAMES, "GBR": "Great Britain"}

# Paper's own age bins, plotted at their midpoint.
BIN_MIDPOINTS = [17, 22, 27, 32, 37, 42]

# Extracted from the paper's supplementary Excel file (48-15_supplement.xlsx,
# one sheet per country, "CFMx" block), not digitized from the figure.
PAPER_CFMX = {
    "AUT": {
        "1940-49": [2.551, 2.294, 2.016, 1.608, 1.422, 1.174],
        "1950-59": [2.443, 2.254, 1.984, 1.649, 1.424, 1.670],
        "1960-69": [2.488, 2.198, 1.953, 1.780, 1.402, 1.148],
    },
    "NLD": {
        "1940-49": [3.018, 2.389, 2.103, 1.828, 1.155, 1.552],
        "1950-59": [2.588, 2.368, 2.332, 2.092, 1.731, 1.000],
        "1960-69": [2.728, 2.544, 2.295, 2.106, 1.628, 1.497],
    },
    "NOR": {
        "1940-49": [2.834, 2.619, 2.250, 1.839, 1.442, 1.372],
        "1950-59": [2.534, 2.428, 2.257, 1.902, 1.622, 1.219],
        "1960-69": [2.788, 2.576, 2.324, 1.948, 1.542, 1.223],
    },
    "POL": {
        "1940-49": [3.018, 2.538, 2.163, 1.651, 1.174, 1.000],
        "1950-59": [2.923, 2.495, 2.035, 1.645, 1.488, 1.000],
        "1960-69": [2.822, 2.534, 2.043, 1.743, 1.286, 1.222],
    },
    "SWE": {
        "1940-49": [2.591, 2.366, 2.105, 1.655, 1.593, 1.000],
        "1950-59": [2.656, 2.407, 2.250, 1.978, 1.625, 1.273],
        "1960-69": [3.140, 2.594, 2.251, 2.082, 1.793, 1.400],
    },
    "USA": {
        "1940-49": [3.290, 2.704, 2.201, 1.872, 1.619, 1.933],
        "1950-59": [2.795, 2.482, 2.177, 1.872, 1.510, 1.514],
        "1960-69": [3.094, 2.632, 2.312, 1.994, 1.687, 1.426],
    },
    "GBR": {
        "1940-49": [3.230, 2.560, 2.170, 1.830, 1.440, 1.000],
        "1950-59": [2.950, 2.530, 2.200, 1.910, 1.500, 1.000],
        "1960-69": [3.130, 2.570, 2.220, 1.920, 1.520, 1.000],
    },
}

# Which HFD code each paper country is compared against.
HFD_CODE = {
    "AUT": "AUT",
    "NLD": "NLD",
    "NOR": "NOR",
    "POL": "POL",
    "SWE": "SWE",
    "USA": "USA",
    "GBR": "UK_ONS",
}

# Inclusive birth-cohort range for each decade bin, used to average HFD's
# cohort curves within it.
DECADE_RANGES = {
    "1940-49": (1940, 1949),
    "1950-59": (1950, 1959),
    "1960-69": (1960, 1969),
}
DECADE_COLORS = {
    "1940-49": "#1b1b1b",
    "1950-59": "#4c78a8",
    "1960-69": "#e45756",
}

LABEL_FONT = dict(size=12, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")
ROW_HEIGHT = 170


def hfd_decade_average(df, code, start, end):
    subset = df[(df["code"] == code) & (df["cohort"] >= start) & (df["cohort"] <= end)]
    return subset.groupby("age")["expected_children"].mean().sort_index()


def plot(df):
    countries = list(PAPER_CFMX.keys())
    decades = list(DECADE_RANGES.keys())
    nrows, ncols = len(countries), len(decades)

    # Precompute every (country, decade) HFD average up front, once, so
    # each panel can also draw its country's *other* two decades as light
    # grey context lines without recomputing them.
    hfd_avg = {
        country: {
            decade: hfd_decade_average(df, HFD_CODE[country], start, end)
            for decade, (start, end) in DECADE_RANGES.items()
        }
        for country in countries
    }

    # Decade labels head the top row only, like column labels in a faceted
    # grid; country names are placed inside each row's first panel instead
    # (see the annotation loop below), matching cond_asfr_facet.py's
    # first-vs-second-birth convention.
    subplot_titles = [f"<b>{d}</b>" for d in decades] + ["" for _ in range(ncols * (nrows - 1))]

    fig = make_subplots(
        rows=nrows, cols=ncols, subplot_titles=subplot_titles,
        horizontal_spacing=0.03, vertical_spacing=0.02,
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT

    for row, country in enumerate(countries, start=1):
        fig.add_annotation(
            text=f"<b>{COUNTRY_TITLES.get(country, country)}</b>", x=0.04, y=0.92,
            xref="x domain", yref="y domain", xanchor="left", yanchor="top", showarrow=False,
            font=LABEL_FONT, row=row, col=1,
        )
        for col, decade in enumerate(decades, start=1):
            # Every other decade's pair, in light grey, for context --
            # drawn first so the highlighted decade's colored pair sits on
            # top.
            for other in decades:
                if other == decade:
                    continue
                other_avg = hfd_avg[country][other]
                fig.add_trace(
                    go.Scatter(
                        x=other_avg.index, y=other_avg.values, mode="lines",
                        line=dict(width=1, color="lightgrey"), showlegend=False, hoverinfo="skip",
                    ),
                    row=row, col=col,
                )
                fig.add_trace(
                    go.Scatter(
                        x=BIN_MIDPOINTS, y=PAPER_CFMX[country][other], mode="lines",
                        line=dict(width=1, color="lightgrey", dash="dash"), showlegend=False, hoverinfo="skip",
                    ),
                    row=row, col=col,
                )

            color = DECADE_COLORS[decade]
            avg = hfd_avg[country][decade]
            fig.add_trace(
                go.Scatter(
                    x=avg.index, y=avg.values, mode="lines",
                    line=dict(width=2, color=color), showlegend=False,
                    hovertemplate=f"{COUNTRY_TITLES.get(country, country)}, HFD {decade}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
                ),
                row=row, col=col,
            )
            fig.add_trace(
                go.Scatter(
                    x=BIN_MIDPOINTS, y=PAPER_CFMX[country][decade], mode="lines",
                    line=dict(width=2, color=color, dash="dash"), showlegend=False,
                    hovertemplate=f"{COUNTRY_TITLES.get(country, country)}, Beaujouan et al. {decade}<br>Age %{{x}}<br>%{{y:.2f}} children<extra></extra>",
                ),
                row=row, col=col,
            )
            fig.update_xaxes(range=list(X_LIM), showticklabels=(row == nrows), row=row, col=col)
            fig.update_yaxes(range=list(Y_LIM), showticklabels=(col == 1), row=row, col=col)

    # Dummy traces, style only -- a legend describing what solid vs dashed
    # means, independent of the per-decade color coding.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2, color="black"), name="Probabilistic estimation using HFD cohort data",
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", line=dict(width=2, color="black", dash="dash"), name="Beaujouan et al. 2023",
    ))

    fig.update_layout(
        title=dict(text="HFD birth cohorts vs Beaujouan, Zeman & Nathan 2023", y=0.985, yanchor="top"),
        template="plotly_white",
        height=ROW_HEIGHT * nrows + 160,
        margin=dict(t=160, b=40, l=50, r=20),
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.05, yanchor="bottom", font=dict(size=10)),
    )
    return fig


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)

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
    print(f"Saved {OUTPUT}")
