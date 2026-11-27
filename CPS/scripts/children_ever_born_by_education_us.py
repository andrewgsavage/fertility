"""Children ever born and childlessness by age and education, US women, from the Current
Population Survey June Fertility Supplement (Census Bureau published tables).

Inputs (CPS/data/, not tracked in git): Table 3c "Children Ever Born per 1,000 Women and Percent
Childless by Age, Marital Status, and Educational Attainment" for each June supplement:
  https://www2.census.gov/programs-surveys/demo/tables/fertility/<year>/am-women-fertility/t3c.xlsx
  saved as t3c_<year>.xlsx, for 2016, 2018, 2020, 2022, 2024 (earlier years are not at this path).

The tables give, for each age group and education level, women (thousands), children ever born
per 1,000 women and percent childless. Education is combined into four groups as in the ACS
charts (some college includes associate degrees; bachelor's or more includes graduate degrees),
weighting by women.

Writes CPS/outputs/children_ever_born_by_education_us.{csv,html}.
"""

import re

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

YEARS = [2016, 2018, 2020, 2022, 2024]
AGES = ["20-29", "30-39", "40-50"]
EDU = [
    ("Less than high school", "#eb6834", ["not a high school graduate"]),
    ("High school", "#eda100", ["high school graduate"]),
    ("Some college", "#1baf7a", ["some college, no degree", "associate's degree"]),
    ("Bachelor's or more", "#2a78d6", ["bachelor's degree", "graduate or professional degree"]),
]


def parse(year):
    x = pd.read_excel(data_dir("CPS") / f"t3c_{year}.xlsx", header=None, dtype=str)
    cols = {}
    for i in range(min(12, len(x))):
        for j, v in enumerate(x.iloc[i]):
            m = re.search(r"Women (\d+) to (\d+) years", str(v))
            if m:
                cols[f"{m.group(1)}-{m.group(2)}"] = j
    labels = x[0].fillna("").str.strip().str.lstrip(".").str.strip().str.lower()
    start = labels[labels.str.startswith("educational attainment")].index[0]
    rows = []
    for i in range(start + 2, start + 8):  # the "All Marital Statuses" block
        lab = labels[i]
        for age, j in cols.items():
            vals = pd.to_numeric(x.iloc[i, j:j + 3], errors="coerce").tolist()
            rows.append(dict(year=year, label=lab, age=age, women=vals[0], ceb=vals[1], childless=vals[2]))
    return pd.DataFrame(rows)


def combine(d):
    out = []
    for name, _, parts in EDU:
        g = d[d.label.isin(parts)].copy()
        g["ceb_n"] = g.women * g.ceb / 1000
        g["childless_n"] = g.women * g.childless / 100
        s = g.groupby(["year", "age"])[["women", "ceb_n", "childless_n"]].sum()
        s["children_per_woman"] = s.ceb_n / s.women
        s["childless_pct"] = s.childless_n / s.women * 100
        s["education"] = name
        out.append(s.reset_index())
    return pd.concat(out)[["year", "age", "education", "women", "children_per_woman", "childless_pct"]]


def chart(c):
    fig = make_subplots(rows=2, cols=3, shared_xaxes=True, vertical_spacing=0.12, horizontal_spacing=0.06,
                        subplot_titles=[f"Children per woman, {a}" for a in AGES] + [f"% childless, {a}" for a in AGES])
    for r, (col, fmt) in enumerate([("children_per_woman", ".2f"), ("childless_pct", ".0f")]):
        for k, age in enumerate(AGES):
            for name, color, _ in EDU:
                s = c[(c.age == age) & (c.education == name)]
                fig.add_trace(go.Scatter(
                    x=s.year, y=s[col], name=name, legendgroup=name, showlegend=r == 0 and k == 0,
                    mode="lines+markers", marker=dict(size=7), line=dict(color=color, width=2),
                    hovertemplate=f"{name}, %{{x}}: %{{y:{fmt}}}<extra></extra>",
                ), row=r + 1, col=k + 1)
    fig.update_layout(template="plotly_white", height=620,
                      title="US women's children ever born and childlessness by age and education",
                      title_y=0.98, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1.07, xanchor="left", yanchor="bottom"),
                      margin=dict(l=50, r=20, t=120, b=40))
    fig.update_xaxes(tickvals=YEARS)
    return fig


def main():
    d = pd.concat([parse(y) for y in YEARS])
    c = combine(d)
    out = outputs_dir("CPS")
    out.mkdir(parents=True, exist_ok=True)
    c.round(3).to_csv(out / "children_ever_born_by_education_us.csv", index=False)
    pd.set_option("display.width", 200)
    print(c[c.age.isin(AGES)].pivot_table(index=["age", "education"], columns="year",
                                         values=["children_per_woman", "childless_pct"]).round(2).to_string())
    write_html(chart(c[c.age.isin(AGES)]), out / "children_ever_born_by_education_us.html")


if __name__ == "__main__":
    main()
