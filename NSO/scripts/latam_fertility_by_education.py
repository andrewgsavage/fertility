"""Chart of birth rates by mother's education for Mexico (2015-2024) and Brazil (2010, 2022).

Reads NSO/outputs/{mexico,brazil}_fertility_by_education.csv (from mexico_births_by_education.py
and brazil_births_by_education.py) and writes NSO/outputs/latam_fertility_by_education.{csv,html}:
births per woman at 25-44 and births per 1,000 women at 20-24, by country, year and education.
Also writes latam_fertility_by_education_curves.html: birth rate by age, a row of small multiples per
country (common.education_curves), for docs/factors/education-age-curves.md.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import outputs_dir
from common.education_curves import curves_grid
from common.plotting import write_html

COUNTRIES = [("mexico", "Mexico"), ("brazil", "Brazil")]
OLD = ["25-29", "30-34", "35-39", "40-44"]
SERIES = {
    "mexico": [("low", "Primary or less", "#eb6834"), ("medium", "Secondary or preparatoria", "#eda100"),
               ("tertiary", "Some university", "#2a78d6")],
    "brazil": [("low", "Below secondary complete", "#eb6834"), ("medium", "Secondary complete", "#eda100"),
               ("tertiary", "Tertiary complete", "#2a78d6")],
}


def summary():
    frames = []
    for code, name in COUNTRIES:
        d = pd.read_csv(outputs_dir("NSO") / f"{code}_fertility_by_education.csv")
        t = (d[d.age.isin(OLD)].groupby(["year", "ed"]).rate.sum() * 5).rename("tfr_25_44")
        y = (d[d.age == "20-24"].set_index(["year", "ed"]).rate * 1000).rename("per_1000_20_24")
        frames.append(pd.concat([t, y], axis=1).reset_index().assign(country=name))
    return pd.concat(frames)[["country", "year", "ed", "tfr_25_44", "per_1000_20_24"]]


def chart(s):
    fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.09, vertical_spacing=0.16,
                        subplot_titles=[f"{n}: {t}" for _, n in COUNTRIES
                                        for t in ["births per woman, 25-44", "per 1,000 women, 20-24"]])
    for r, (code, name) in enumerate(COUNTRIES):
        c = s[s.country == name]
        for k, (col, fmt) in enumerate([("tfr_25_44", ".2f"), ("per_1000_20_24", ".0f")]):
            for e, lab, color in SERIES[code] + [("all", "All women", "#6b6b6b")]:
                g = c[c.ed == e].sort_values("year")
                fig.add_trace(go.Scatter(
                    x=g.year, y=g[col], name=lab, legendgroup=f"{code}-{e}", showlegend=k == 0,
                    legendgrouptitle_text=name if (k == 0 and e == "low") else None, legend="legend" if r == 0 else "legend2",
                    mode="lines+markers", marker=dict(size=7),
                    line=dict(color=color, width=2, dash="dash" if e == "all" else "solid"),
                    hovertemplate=f"{name}, {lab}, %{{x}}: %{{y:{fmt}}}<extra></extra>",
                ), row=r + 1, col=k + 1)
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(
        template="plotly_white", height=760, title="Birth rates by mother's education, Mexico and Brazil",
        title_y=0.98, title_yanchor="top",
        legend=dict(orientation="h", x=0, y=1.07, xanchor="left", yanchor="bottom"),
        legend2=dict(orientation="h", x=0, y=0.47, xanchor="left", yanchor="bottom"),
        margin=dict(l=50, r=20, t=120, b=40))
    return fig


def curves_chart():
    rows = []
    for code, name in COUNTRIES:
        d = pd.read_csv(outputs_dir("NSO") / f"{code}_fertility_by_education.csv")
        d = d.assign(band=d.age, x=d.age.str[:2].astype(int) + 2, rate=d.rate * 1000)
        rows.append((name, [d[d.ed == e][["year", "x", "band", "rate"]] for e, _, _ in SERIES[code]]))
    return curves_grid(rows, ["Lowest education", "Middle", "Highest"],
                       "Birth rate by age and education, Mexico and Brazil")


def main():
    s = summary()
    out = outputs_dir("NSO")
    s.round(3).to_csv(out / "latam_fertility_by_education.csv", index=False)
    print(s.pivot_table(index=["country", "ed"], columns="year", values="tfr_25_44").round(2).to_string())
    print(s.pivot_table(index=["country", "ed"], columns="year", values="per_1000_20_24").round(0).to_string())
    write_html(chart(s), out / "latam_fertility_by_education.html")
    write_html(curves_chart(), out / "latam_fertility_by_education_curves.html")


if __name__ == "__main__":
    main()
