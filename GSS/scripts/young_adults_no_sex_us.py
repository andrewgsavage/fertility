"""US adults aged 18-29 with no sex in the past year, and aged 25-29 never married, by sex.

General Social Survey cumulative file 1972-2024 (NORC), variables sexfreq (0 = not at all in
the last 12 months; asked from 1989), marital (5 = never married), age, sex, wtssps weight.
Pooled into 4-year windows because the yearly samples of young adults are small.

Input (download into GSS/data/ and unzip - not tracked in git):
  https://gss.norc.org/content/dam/gss/get-the-data/documents/stata/GSS_stata.zip
  -> GSS/data/GSS_stata/gss7224_r3a.dta
"""

import pathlib
import warnings

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.simplefilter("ignore")
_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data" / "GSS_stata" / "gss7224_r3a.dta"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "young_adults_no_sex_us.html"

EDGES = [1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]


def window(y):
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        if lo < y <= hi:
            return f"{lo + 1}-{hi}"


def share(g, cond):
    ok = g[cond(g)].wtssps.sum()
    return 100 * ok / g.wtssps.sum()


def load():
    d = pd.read_stata(DATA, convert_categoricals=False,
                      columns=["year", "age", "sex", "sexfreq", "marital", "wtssps"])
    d = d[d.year > 1988].assign(window=lambda x: x.year.map(window))
    d["gender"] = d.sex.map({1: "Men", 2: "Women"})
    rows = []
    for (w, s), g in d.groupby(["window", "gender"]):
        a = g[(g.age.between(18, 29)) & g.sexfreq.notna()]
        m = g[(g.age.between(25, 29)) & g.marital.notna()]
        rows.append(dict(window=w, gender=s, n_sex=len(a), no_sex=share(a, lambda x: x.sexfreq == 0),
                         n_mar=len(m), never=share(m, lambda x: x.marital == 5)))
    return pd.DataFrame(rows)


def plot(d):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.1, subplot_titles=(
        "Aged 18-29, no sex in past year", "Aged 25-29, never married"))
    for s, col in [("Men", "#1f77b4"), ("Women", "#d62728")]:
        x = d[d.gender == s]
        fig.add_trace(go.Scatter(x=x.window, y=x.no_sex, mode="lines+markers", name=s,
                                 legendgroup=s, line=dict(color=col), customdata=x.n_sex,
                                 hovertemplate=s + " %{x}: %{y:.1f}% (n=%{customdata})<extra></extra>"),
                      row=1, col=1)
        fig.add_trace(go.Scatter(x=x.window, y=x.never, mode="lines+markers", name=s,
                                 legendgroup=s, showlegend=False, line=dict(color=col),
                                 customdata=x.n_mar,
                                 hovertemplate=s + " %{x}: %{y:.1f}% (n=%{customdata})<extra></extra>"),
                      row=1, col=2)
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_layout(template="plotly_white", title="US young adults: no recent sex and never married (GSS)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=100, t=90), hovermode="closest")
    return fig


if __name__ == "__main__":
    fig = plot(load())
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
