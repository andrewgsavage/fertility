"""US birth rates by women's education, from ACS/outputs/acs_births_by_education.csv
(written by acs_births_by_education.py).

Rates are weighted births in the past 12 months per woman, by single year of age. "Births per
woman, ages 25-44" is the sum of the single-year rates over 25-44 (a partial TFR). Ages under 25
are shown for all women only, since many are still in education.

Writes ACS/outputs/:
  fertility_by_education_us_trend.html    births per woman 25-44 by education, by year
  fertility_by_education_us_age.html      % change in rate by 5-year age group, first vs last year
  fertility_by_education_us_share.html    share of women 25-44 by education, by year
  fertility_by_education_us_ages.html     births per woman at 15-24 and 25-44, all women, by year
  fertility_by_education_us_curves.html   birth rate by single year of age (3-year moving average),
                                          women not enrolled in school, one panel per education
  fertility_by_education_us_20_24.html     birth rate at 20-24 by education (not enrolled) and for
                                          enrolled women, by year
  fertility_by_education_us.csv           the numbers behind them
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plot_colors import PERIOD_COLORSCALE, period_axis, sample_color

from common.paths import outputs_dir
from common.plotting import write_html

OUT = outputs_dir("ACS")
EDU = [  # low to high, fixed colors
    ("Less than high school", "#eb6834"),
    ("High school", "#eda100"),
    ("Some college", "#1baf7a"),
    ("Bachelor's or more", "#2a78d6"),
]
ALL = ("All women", "#6b6b6b")
AGE_GROUPS = [(25, 29), (30, 34), (35, 39), (40, 44)]
LAYOUT = dict(
    template="plotly_white",
    legend=dict(orientation="h", x=0, y=1.02, xanchor="left", yanchor="bottom"),
    margin=dict(l=60, r=20, t=125, b=50),
    title_y=0.98, title_yanchor="top",
    hovermode="x unified",
)


def load():
    d = pd.read_csv(OUT / "acs_births_by_education.csv")
    return d


def partial_tfr(d, lo, hi, by):
    """Sum of single-year rates over ages lo..hi, by `by` (plus year)."""
    q = d[d.age.between(lo, hi)].groupby(["year", "age"] + by)[["births", "women"]].sum()
    return (q.births / q.women).groupby(["year"] + by).sum()


def tables(d):
    by_edu = partial_tfr(d, 25, 44, ["education"]).unstack()[[e for e, _ in EDU]]
    by_edu["All women"] = partial_tfr(d, 25, 44, [])
    ages = pd.DataFrame({"15-24": partial_tfr(d, 15, 24, []), "25-44": partial_tfr(d, 25, 44, [])})
    w = d[d.age.between(25, 44)].groupby(["year", "education"]).women.sum().unstack()
    share = w.div(w.sum(axis=1), axis=0)[[e for e, _ in EDU]] * 100
    first, last = d.year.min(), d.year.max()
    rows = []
    for lo, hi in AGE_GROUPS:
        g = d[d.age.between(lo, hi)].groupby(["year", "education"])[["births", "women"]].sum()
        r = (g.births / g.women).unstack()
        for e, _ in EDU:
            rows.append(dict(age=f"{lo}-{hi}", education=e, rate_first=r.loc[first, e] * 1000,
                             rate_last=r.loc[last, e] * 1000,
                             change=(r.loc[last, e] / r.loc[first, e] - 1) * 100))
    by_age = pd.DataFrame(rows)
    return by_edu, ages, share, by_age, first, last


def decompose(d, first, last):
    """Change in births per woman 25-44 split into within-group rate change and composition,
    by 5-year age group (average-weights / Kitagawa)."""
    within = comp = 0.0
    for lo, hi in [(a, a) for a in range(25, 45)]:
        g = d[d.age == lo].groupby(["year", "education"])[["births", "women"]].sum()
        r = (g.births / g.women).unstack()
        s = g.women.unstack()
        s = s.div(s.sum(axis=1), axis=0)
        within += ((r.loc[last] - r.loc[first]) * (s.loc[last] + s.loc[first]) / 2).sum()
        comp += ((s.loc[last] - s.loc[first]) * (r.loc[last] + r.loc[first]) / 2).sum()
    return within, comp


def line_chart(table, series, title, ytitle, fmt, dash_last=False):
    fig = go.Figure()
    for name, color in series:
        dash = "dash" if dash_last and name == series[-1][0] else "solid"
        fig.add_trace(go.Scatter(
            x=table.index, y=table[name], name=name, mode="lines+markers",
            line=dict(color=color, width=2, dash=dash), marker=dict(size=8),
            hovertemplate=f"{name}: %{{y:{fmt}}}<extra></extra>",
        ))
    fig.update_layout(title=title, yaxis_title=ytitle, xaxis_title=None, **LAYOUT)
    fig.update_xaxes(tickmode="array", tickvals=list(table.index))
    return fig


def age_chart(by_age, first, last):
    fig = go.Figure()
    for e, color in EDU:
        s = by_age[by_age.education == e]
        fig.add_trace(go.Bar(
            x=s.age, y=s.change, name=e, marker_color=color,
            customdata=s[["rate_first", "rate_last"]],
            hovertemplate=(f"{e}: %{{y:+.0f}}%<br>%{{customdata[0]:.0f}} → %{{customdata[1]:.0f}} "
                           "births per 1,000 women<extra></extra>"),
        ))
    fig.add_hline(y=0, line=dict(color="#6b6b6b", width=1))
    lay = {k: v for k, v in LAYOUT.items() if k != "hovermode"}
    fig.update_layout(title=f"Change in US birth rate by age and education, {first} to {last}",
                      yaxis_title="Change in birth rate (%)", xaxis_title="Age",
                      barmode="group", bargap=0.25, bargroupgap=0.08, **lay)
    fig.update_yaxes(ticksuffix="%")
    return fig


def curves(d):
    """Births per 1,000 women not enrolled in school, by single year of age 18-44, 3-year
    centred moving average of births and women."""
    q = d[~d.enrolled & d.age.between(17, 45)].groupby(["year", "education", "age"])[["births", "women"]].sum()
    out = []
    for (y, e), g in q.groupby(level=[0, 1]):
        g = g.droplevel([0, 1]).reindex(range(17, 46)).fillna(0)
        r = g.births.rolling(3, center=True).sum() / g.women.rolling(3, center=True).sum() * 1000
        out.append(pd.DataFrame({"year": y, "education": e, "age": r.index, "rate": r.values}))
    c = pd.concat(out)
    return c[c.age.between(18, 44)]


def curves_chart(c):
    years = sorted(c.year.unique())
    axis = period_axis(min(years), max(years))
    fig = make_subplots(rows=2, cols=2, subplot_titles=[e for e, _ in EDU], shared_yaxes=True,
                        shared_xaxes=True, vertical_spacing=0.1, horizontal_spacing=0.05)
    for i, (e, _) in enumerate(EDU):
        row, col = i // 2 + 1, i % 2 + 1
        for y in years:
            s = c[(c.education == e) & (c.year == y)]
            if e == "Bachelor's or more":
                s = s[s.age >= 21]
            fig.add_trace(go.Scatter(
                x=s.age, y=s.rate, name=str(y), legendgroup=str(y), showlegend=i == 0,
                mode="lines", line=dict(color=sample_color(PERIOD_COLORSCALE, y, axis), width=2),
                hovertemplate=f"{y}, age %{{x}}: %{{y:.0f}}<extra></extra>",
            ), row=row, col=col)
    fig.update_layout(template="plotly_white", title="US birth rate by age and education, women not in school",
                      title_y=0.98, title_yanchor="top", height=640,
                      legend=dict(orientation="h", x=0, y=1.06, xanchor="left", yanchor="bottom"),
                      margin=dict(l=60, r=20, t=120, b=50))
    fig.update_yaxes(title_text="Births per 1,000 women", col=1)
    fig.update_xaxes(title_text="Age", row=2)
    return fig


def young(d):
    """Births per 1,000 women aged 20-24: not enrolled by education, and all enrolled women."""
    q = d[d.age.between(20, 24)]
    g = q[~q.enrolled].groupby(["year", "education"])[["births", "women"]].sum()
    t = (g.births / g.women * 1000).unstack()[[e for e, _ in EDU]]
    en = q[q.enrolled].groupby("year")[["births", "women"]].sum()
    t["Enrolled in school"] = en.births / en.women * 1000
    al = q.groupby("year")[["births", "women"]].sum()
    t["All women"] = al.births / al.women * 1000
    share = q.groupby(["year", "enrolled"]).women.sum().unstack()
    t["Share enrolled (%)"] = share[True] / share.sum(axis=1) * 100
    return t


def main():
    d = load()
    by_edu, ages, share, by_age, first, last = tables(d)
    within, comp = decompose(d, first, last)
    total = by_edu.loc[last, "All women"] - by_edu.loc[first, "All women"]
    print(by_edu.round(3).to_string())
    print(ages.round(3).to_string())
    print(share.round(1).to_string())
    print(by_age.round(1).to_string())
    print(f"25-44 change {first}-{last}: {total:+.3f} = within {within:+.3f} + composition {comp:+.3f}")

    out = by_edu.round(3).join(share.round(1).add_prefix("share_")).join(ages.round(3).add_prefix("all_"))
    out.to_csv(OUT / "fertility_by_education_us.csv")
    by_age.round(2).to_csv(OUT / "fertility_by_education_us_age.csv", index=False)

    write_html(line_chart(by_edu, EDU + [ALL], "US births per woman at ages 25-44, by education",
                          "Births per woman, ages 25-44", ".2f", dash_last=True),
               OUT / "fertility_by_education_us_trend.html")
    write_html(age_chart(by_age, first, last), OUT / "fertility_by_education_us_age.html")
    write_html(line_chart(share, EDU, "Education of US women aged 25-44",
                          "Share of women 25-44 (%)", ".1f"),
               OUT / "fertility_by_education_us_share.html")
    c = curves(d)
    c.round(1).to_csv(OUT / "fertility_by_education_us_curves.csv", index=False)
    write_html(curves_chart(c), OUT / "fertility_by_education_us_curves.html")
    y = young(d)
    print(y.round(1).to_string())
    y.round(1).to_csv(OUT / "fertility_by_education_us_20_24.csv")
    write_html(line_chart(y, EDU + [("Enrolled in school", "#9b59b6"), ALL],
                          "US births per 1,000 women aged 20-24, by education (not in school) and enrolment",
                          "Births per 1,000 women aged 20-24", ".0f", dash_last=True),
               OUT / "fertility_by_education_us_20_24.html")
    write_html(line_chart(ages, [("15-24", "#eb6834"), ("25-44", "#2a78d6")],
                          "US births per woman under and over 25, all women",
                          "Births per woman in the age range", ".2f"),
               OUT / "fertility_by_education_us_ages.html")


if __name__ == "__main__":
    main()
