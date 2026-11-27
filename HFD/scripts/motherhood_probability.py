"""Probability that a childless woman of a given age becomes a mother before
age 45 if that calendar year's conditional first-birth rates held.

HFD's m1x (mi.txt) is first births per person-year lived childless at age x
(completed age), so for a woman childless at exact age a the chance she stays
childless to exact age 45 is exp(-sum_{x=a}^{44} m1x), and

    P(mother before 45 | childless at a) = 1 - exp(-sum_{x=a}^{44} m1x).

The upper age is 45 rather than HFD's 55+ because many countries have m1x
missing at ages 45+ for a ten-year stretch; first births after 45 add well under
one percentage point.

The UK reconstruction (common.ons_table3) gives discrete yearly hazards
(the share of still-childless women who have a first birth within the year of
age) for ages 21-45, so for it the survival is prod_{x=a}^{44} (1 - h_x).

Greece and Mauritius are not in HFD. Their m1x come from cohort-cumulated order-specific rates
(HFD/scripts/cond_asfr_facet.py, MAX_BACKFILL_SHARE rule), so a probability is drawn only for years
where every age from the starting age to 44 passes that rule: Greece from 1984 at 25, Mauritius not
at all, since its rates start in 2005.

One panel per country, x = year, a line per starting age (AGES).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.country_names import COUNTRY_REGIONS, country_title
from common.hfd import age_to_int, read_hfd
from common.ons_table3 import load_period_rates
from common.paths import outputs_dir
from common.plotting import write_html

OUTPUT = outputs_dir("HFD") / "motherhood_probability.html"
OUTPUT_CSV = outputs_dir("HFD") / "motherhood_probability.csv"

AGES = [25, 30, 35]
END_AGE = 45  # exclusive: probability of a first birth before this age
# Categorical slots 1-3 of the dataviz reference palette (blue, orange, aqua).
AGE_COLORS = {25: "#2a78d6", 30: "#eb6834", 35: "#1baf7a"}
COLS = 3
ROW_HEIGHT = 200
TOP_MARGIN = 120
X_RANGE = (1950, 2026)
LABEL_FONT = dict(size=13, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")


def hfd_probabilities():
    df = read_hfd("mi.txt", ["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"])
    df["age"] = age_to_int(df["age"])
    rows = []
    for (code, year), group in df.groupby(["code", "year"]):
        m = group.set_index("age")["m1x"]
        for age in AGES:
            tail = m[(m.index >= age) & (m.index < END_AGE)]
            if tail.empty or tail.isna().any():
                continue
            rows.append({"code": code, "year": year, "age": age, "p": 1 - np.exp(-tail.sum())})
    return pd.DataFrame(rows)


def uk_probabilities():
    rows = []
    for year, ages in load_period_rates().items():
        hazards = pd.Series({age: c1 for age, (c1, _) in ages.items()}).sort_index()
        for age in AGES:
            tail = hazards[(hazards.index >= age) & (hazards.index < END_AGE)]
            # Need every year of age from `age` to END_AGE - 1 for the product to mean anything.
            if tail.isna().any() or len(tail) != END_AGE - age:
                continue
            rows.append({"code": "UK_ONS", "year": year, "age": age, "p": 1 - (1 - tail).prod()})
    return pd.DataFrame(rows)


def cumulated_probabilities():
    from cond_asfr_facet import GRC_CODE, MUS_CODE, MAX_BACKFILL_SHARE, CUMULATED_CSV
    rows = []
    for code in (GRC_CODE, MUS_CODE):
        d = pd.read_csv(CUMULATED_CSV[code])
        d["m1x"] = d.m1x.where(d.backfill_share1 <= MAX_BACKFILL_SHARE)
        for year, group in d.groupby("year"):
            m = group.set_index("age")["m1x"]
            for age in AGES:
                tail = m.reindex(range(age, END_AGE))
                if tail.isna().any():
                    continue
                rows.append({"code": code, "year": year, "age": age, "p": 1 - np.exp(-tail.sum())})
    return pd.DataFrame(rows, columns=["code", "year", "age", "p"])


def load():
    return pd.concat([hfd_probabilities(), uk_probabilities(), cumulated_probabilities()], ignore_index=True)


def make_facet(df, countries):
    nrows = -(-len(countries) // COLS)
    fig = make_subplots(
        rows=nrows, cols=COLS, shared_xaxes=True, shared_yaxes=True,
        horizontal_spacing=0.03, vertical_spacing=0.03,
        subplot_titles=[f"<b>{country_title(code)}</b>" for code in countries],
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT
    for i, code in enumerate(countries):
        row, col = i // COLS + 1, i % COLS + 1
        subset = df[df["code"] == code]
        name = country_title(code)
        for age in AGES:
            line = subset[subset["age"] == age].sort_values("year")
            fig.add_trace(
                go.Scatter(
                    x=line["year"], y=line["p"], mode="lines",
                    line=dict(width=2, color=AGE_COLORS[age]),
                    name=f"Childless at {age}", legendgroup=str(age), showlegend=(i == 0),
                    hovertemplate=f"Childless at {age}: %{{y:.0%}}<extra></extra>",
                ),
                row=row, col=col,
            )
        # Unified hover header: country and year once, then one row per age.
        fig.update_xaxes(unifiedhovertitle=dict(text=f"<b>{name}</b>, %{{x}}"), row=row, col=col)
    # Interior ticks only, so labels at adjacent panels' edges don't collide.
    # fixedrange: no zoom/pan, so no axis drag zones; those sat over the
    # previous panel's last years and grabbed the cursor instead of hover.
    fig.update_xaxes(range=list(X_RANGE), tickvals=[1960, 1980, 2000, 2020], fixedrange=True)
    fig.update_yaxes(range=[0, 1], tickformat=".0%", dtick=0.25, fixedrange=True)
    for col in range(1, COLS + 1):
        # Bottom row may be short: put x tick labels on the lowest panel in each column.
        last_row = max(r for r in range(1, nrows + 1) if (r - 1) * COLS + col <= len(countries))
        fig.update_xaxes(showticklabels=True, row=last_row, col=col)
    fig.update_layout(
        title=dict(text="Chance a childless woman becomes a mother before 45<br><sup>at that year's first-birth rates</sup>", y=1, yref="container", yanchor="top", pad=dict(t=10)),
        template="plotly_white",
        height=ROW_HEIGHT * nrows + TOP_MARGIN + 40,
        # Legend in its own row under the title, above the first row's country names.
        legend=dict(orientation="h", x=0, xanchor="left", yref="container", y=1 - 62 / (ROW_HEIGHT * nrows + TOP_MARGIN + 40), yanchor="top"),
        hovermode="x unified",
        margin=dict(t=TOP_MARGIN, l=50, r=20),
    )
    return fig


if __name__ == "__main__":
    df = load()
    countries = [code for codes in COUNTRY_REGIONS.values() for code in codes]
    from cond_asfr_facet import GRC_CODE, MUS_CODE
    for code, after in ((GRC_CODE, "PRT"), (MUS_CODE, "TWN")):
        if (df["code"] == code).any():
            countries.insert(countries.index(after) + 1, code)
    df = df[df["code"].isin(countries)]
    df.assign(p=df["p"].round(4)).sort_values(["code", "age", "year"]).to_csv(OUTPUT_CSV, index=False)
    fig = make_facet(df, countries)
    write_html(fig, OUTPUT, height=f"{fig.layout.height}px")
