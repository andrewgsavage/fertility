"""Ideal vs actual number of children, women aged 40-54: Resolution Foundation Figure 2 against
Human Fertility Database cohort fertility for the same women.

Figure 2 of C McCurdy, "Bye bye baby", Resolution Foundation, April 2026 (p. 9):
  https://www.resolutionfoundation.org/app/uploads/2026/03/Bye-bye-baby.pdf
The bar ends are read from the PDF's vector paths (pdftocairo -svg, page 9): x-axis 0 at
133.57pt (left panel) / 371.86pt (right panel), 52.548pt per child. They round to the gap labels
printed on the chart.

HFD comparison: mean cumulative cohort fertility (ccfrVH.txt) of the 15 one-year cohorts aged
40-54 in the survey year, each at its age that year (latest observed age if the year is past the
end of the series). 2020/2023 survey waves are compared with 2022.

Inputs: HFD/data/HFD/ccfrVH.txt (not tracked in git).
Outputs: resolution/outputs/ideal_vs_actual_rf.html, ideal_gap_rf.html, ideal_vs_actual_rf.csv
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.hfd import age_to_int, read_hfd
from common.paths import outputs_dir
from common.plotting import write_html

OUT = outputs_dir("resolution")

# country: HFD code, (2011 actual, 2011 ideal), (2020/23 actual, 2020/23 ideal)
RF_FIG2 = {
    "Germany": ("DEUTNP", (1.95, 2.30), (1.45, 2.14)),
    "Denmark": ("DNK", (1.88, 2.47), (1.73, 2.37)),
    "United Kingdom": ("GBR_NP", (2.10, 2.36), (1.66, 2.32)),
    "Netherlands": ("NLD", (1.91, 2.38), (1.69, 2.26)),
    "France": ("FRATNP", (2.07, 2.51), (1.92, 2.50)),
    "Finland": ("FIN", (2.10, 2.64), (1.82, 2.36)),
    "Estonia": ("EST", (2.04, 2.58), (1.95, 2.55)),
    "Czech Republic": ("CZE", (1.90, 2.13), (1.83, 2.31)),
}
WAVES = [("2011", 2011), ("2020/23", 2022)]

GREY, RED, DARK = "#9e9e9e", "#c00000", "#1f2937"


def hfd_mean_children(ccfr, code, year, lo=40, hi=54):
    """Mean children ever born of women aged lo-hi in `year` (cohorts year-hi..year-lo)."""
    c = ccfr[ccfr.Code == code]
    vals = []
    for cohort in range(year - hi, year - lo + 1):
        s = c[(c.Cohort == cohort) & (c.Age <= year - cohort) & (c.Age >= lo)].dropna(subset=["CCFR"])
        if len(s):
            vals.append(s.sort_values("Age").CCFR.iloc[-1])
    return sum(vals) / len(vals) if vals else None


def load():
    ccfr = read_hfd("ccfrVH.txt")
    ccfr["Age"] = age_to_int(ccfr.Age)
    rows = []
    for country, (code, w1, w2) in RF_FIG2.items():
        for (wave, hfd_year), (actual, ideal) in zip(WAVES, (w1, w2)):
            hfd = hfd_mean_children(ccfr, code, hfd_year)
            rows.append(dict(country=country, wave=wave, survey_actual=actual, ideal=ideal,
                             hfd_actual=round(hfd, 2), gap_survey=round(ideal - actual, 2),
                             gap_hfd=round(ideal - hfd, 2)))
    return pd.DataFrame(rows)


def plot_levels(d):
    order = list(RF_FIG2)[::-1]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=[w for w, _ in WAVES])
    for col, (wave, _) in enumerate(WAVES, start=1):
        x = d[d.wave == wave].set_index("country").loc[order].reset_index()
        for _, r in x.iterrows():
            fig.add_trace(go.Scatter(x=[r.survey_actual, r.ideal], y=[r.country] * 2, mode="lines",
                                     line=dict(color=RED, width=6), opacity=0.35, showlegend=False,
                                     hoverinfo="skip"), row=1, col=col)
        for name, colname, color, symbol in [
            ("Actual (survey, as in Figure 2)", "survey_actual", GREY, "circle"),
            ("Actual (HFD, same ages and year)", "hfd_actual", DARK, "circle-open"),
            ("Ideal (survey)", "ideal", RED, "diamond"),
        ]:
            fig.add_trace(go.Scatter(
                x=x[colname], y=x.country, mode="markers", name=name, legendgroup=name,
                showlegend=col == 1, marker=dict(color=color, size=11, symbol=symbol,
                                                 line=dict(width=2, color=color)),
                hovertemplate="%{y} " + wave + ": %{x:.2f}<extra>" + name + "</extra>"),
                row=1, col=col)
    fig.update_xaxes(range=[1.3, 2.8], title_text="Children per woman aged 40-54")
    fig.update_layout(template="plotly_white", title="Actual and ideal number of children, women aged 40-54",
                      legend=dict(orientation="h", x=0, y=-0.18), margin=dict(t=90, b=110),
                      hovermode="closest")
    return fig


def plot_gap(d):
    order = list(RF_FIG2)[::-1]
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=["Ideal minus survey actual (Figure 2)",
                                        "Ideal minus HFD actual"])
    for col, gap in enumerate(["gap_survey", "gap_hfd"], start=1):
        w = d.pivot(index="country", columns="wave", values=gap).loc[order]
        for country, r in w.iterrows():
            fig.add_trace(go.Scatter(x=[r["2011"], r["2020/23"]], y=[country] * 2, mode="lines",
                                     line=dict(color=GREY, width=2), showlegend=False,
                                     hoverinfo="skip"), row=1, col=col)
        for wave, color in [("2011", "#93c5fd"), ("2020/23", "#1d4ed8")]:
            fig.add_trace(go.Scatter(x=w[wave], y=w.index, mode="markers", name=wave, legendgroup=wave,
                                     showlegend=col == 1, marker=dict(color=color, size=11),
                                     hovertemplate="%{y} " + wave + ": %{x:.2f}<extra></extra>"),
                          row=1, col=col)
    fig.update_xaxes(range=[0, 0.9], title_text="Ideal minus actual (children)")
    fig.update_layout(template="plotly_white", title="Gap between ideal and actual number of children, women aged 40-54",
                      legend=dict(orientation="h", x=0, y=-0.18), margin=dict(t=90, b=110),
                      hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "ideal_vs_actual_rf.csv", index=False)
    print(d.to_string(index=False))
    write_html(plot_levels(d), OUT / "ideal_vs_actual_rf.html")
    write_html(plot_gap(d), OUT / "ideal_gap_rf.html")
