"""Cohort age-specific fertility rate (ASFR, all birth orders combined) for
the UK's constituent countries, from HFD's asfrRR.txt — unlike the
conditional/parity-progression ASFR on the Conditional ASFR page (see
ONS/scripts/cond_asfr_uk_ons.py), HFD does publish plain ASFR directly for
the UK, so no reconstruction is needed here.

asfrRR.txt is period data (calendar year x age); each row is resliced onto
its birth cohort (cohort = year - age) rather than grouped by calendar
year, so each line traces one cohort's fertility across its own lifetime
instead of one calendar year's snapshot across all ages.
"""

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from country_names import COUNTRY_NAMES

INPUT = "data/HFD/asfrRR.txt"
OUTPUT = "outputs/asfr_uk.html"
DISPLAY_MIN_COHORT = 1970
CODES = ["GBRTENW", "GBR_SCO", "GBR_NIR", "GBR_NP"]


def load_data():
    df = pd.read_csv(
        INPUT,
        sep=r"\s+",
        skiprows=3,
        names=["code", "year", "age", "asfr"],
        na_values=".",
    )
    df["age"] = df["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
    df["cohort"] = df["year"] - df["age"]
    df = df[df["code"].isin(CODES) & (df["cohort"] >= DISPLAY_MIN_COHORT)]
    return df


def plot(df):
    cohorts = sorted(df["cohort"].unique())
    cmap_min, cmap_max = min(cohorts), max(cohorts)

    fig = make_subplots(rows=1, cols=len(CODES), subplot_titles=[COUNTRY_NAMES[c] for c in CODES])

    for col, code in enumerate(CODES, start=1):
        subset = df[df["code"] == code]
        for cohort, rows in subset.groupby("cohort"):
            rows = rows.sort_values("age")
            color = _cohort_color(cohort, cmap_min, cmap_max)
            fig.add_trace(
                go.Scatter(
                    x=rows["age"], y=rows["asfr"] * 100,
                    mode="lines", line=dict(width=1, color=color),
                    name=str(cohort), legendgroup=str(cohort), showlegend=False,
                    hovertemplate=f"{COUNTRY_NAMES[code]}<br>Cohort {cohort}<br>Age %{{x}}<br>%{{y:.1f}}%<extra></extra>",
                ),
                row=1, col=col,
            )

    # Dummy trace to show a colorbar for cohort.
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale="Turbo", cmin=cmap_min, cmax=cmap_max,
                color=[cmap_min], showscale=True,
                colorbar=dict(title="Cohort"),
            ),
            showlegend=False,
        ),
        row=1, col=len(CODES),
    )

    fig.update_xaxes(title_text="Age", range=[15, 45])
    fig.update_yaxes(title_text="ASFR (%)", range=[0, 15], col=1)
    fig.update_layout(
        title=f"Cohort ASFR, UK constituent countries ({min(cohorts)}–{max(cohorts)} birth cohorts) — HFD",
        template="plotly_white",
        height=450,
    )
    return fig


def _cohort_color(cohort, cmin, cmax):
    t = 0.0 if cmax == cmin else (cohort - cmin) / (cmax - cmin)
    return pc.sample_colorscale("Turbo", [t])[0]


if __name__ == "__main__":
    df = load_data()
    fig = plot(df)
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%")
    print(f"Saved {OUTPUT}")
