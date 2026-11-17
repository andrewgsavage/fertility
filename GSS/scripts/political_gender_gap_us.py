"""Gender gap in political views by age group, US.

General Social Survey cumulative file 1972-2024 (NORC), variable polviews (1-3 liberal,
4 moderate, 5-7 conservative), age, sex, wtssps weight. Pooled into 4-year windows.
Gap = share of women minus share of men.

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
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "political_gender_gap_us.html"

EDGES = [1972, 1976, 1980, 1984, 1988, 1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]
GROUPS = {"18-29": (18, 29), "30-49": (30, 49), "50+": (50, 120)}


def window(y):
    for lo, hi in zip(EDGES[:-1], EDGES[1:]):
        if lo < y <= hi or (lo == 1972 and y == 1972):
            return f"{lo + 1 if lo != 1972 else 1972}-{hi}"


def liberal_share(g):
    return 100 * g[g.polviews <= 3].wtssps.sum() / g.wtssps.sum()


def load():
    d = pd.read_stata(DATA, convert_categoricals=False, columns=["year", "age", "sex", "polviews", "wtssps"])
    d = d[d.polviews.notna() & d.age.notna() & d.wtssps.notna()].copy()
    d["window"] = d.year.map(window)
    d["gender"] = d.sex.map({1: "Men", 2: "Women"})
    rows = []
    for gname, (lo, hi) in GROUPS.items():
        for (w, s), g in d[d.age.between(lo, hi)].groupby(["window", "gender"]):
            rows.append(dict(age=gname, window=w, gender=s, n=len(g), liberal=liberal_share(g),
                             conservative=100 * g[g.polviews >= 5].wtssps.sum() / g.wtssps.sum()))
    return pd.DataFrame(rows)


def plot(d):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.1, subplot_titles=(
        "Aged 18-29: % liberal", "Women minus men, % liberal (points)"))
    for s, col in [("Men", "#1f77b4"), ("Women", "#d62728")]:
        x = d[(d.age == "18-29") & (d.gender == s)]
        fig.add_trace(go.Scatter(x=x.window, y=x.liberal, mode="lines+markers", name=s,
                                 line=dict(color=col), customdata=x.n,
                                 hovertemplate=s + " %{x}: %{y:.1f}% (n=%{customdata})<extra></extra>"),
                      row=1, col=1)
    cols = {"18-29": "#d62728", "30-49": "#ff7f0e", "50+": "#7f7f7f"}
    for a in GROUPS:
        w = d[d.age == a].pivot(index="window", columns="gender", values="liberal")
        gap = (w.Women - w.Men).dropna()
        fig.add_trace(go.Scatter(x=gap.index, y=gap, mode="lines+markers", name=f"Aged {a}",
                                 line=dict(color=cols[a]),
                                 hovertemplate=f"Aged {a}" + " %{x}: %{y:+.1f} pts<extra></extra>"),
                      row=1, col=2)
    fig.add_hline(y=0, line_color="#999", row=1, col=2)
    fig.update_yaxes(ticksuffix="%", rangemode="tozero", row=1, col=1)
    fig.update_yaxes(title_text="points", row=1, col=2)
    fig.update_layout(template="plotly_white", title="US gender gap in political views by age (GSS)",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=110, t=90), hovermode="closest")
    return fig


if __name__ == "__main__":
    fig = plot(load())
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
