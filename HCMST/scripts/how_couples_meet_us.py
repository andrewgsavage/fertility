"""How US couples met, by period in which they first met.

How Couples Meet and Stay Together (HCMST) 2017-2022 combined public file, v2.2 (Rosenfeld,
Thomas & Hausen, Stanford). Uses wave 1 (2017) respondents with a partner, weighted by
w1_weight_combo, grouped by year they first met (w1_q21a_year). Retrospective: couples that
broke up before 2017 are not in the sample.

Input (download into HCMST/data/hcmst_2017_2022.dta - not tracked in git):
  https://stacks.stanford.edu/file/druid:hg921sg6829/HCMST%202017%20to%202022%20small%20public%20version%202.2.dta
  (landing page: https://data.stanford.edu/hcmst2017)
"""

import pathlib
import warnings

import pandas as pd
import plotly.graph_objects as go

warnings.simplefilter("ignore")
_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA = _SCRIPT_DIR.parent / "data" / "hcmst_2017_2022.dta"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "how_couples_meet_us.html"

BINS = [1939, 1959, 1969, 1979, 1989, 1999, 2004, 2009, 2014, 2017]
LABELS = ["<1960", "1960-69", "1970-79", "1980-89", "1990-99", "2000-04", "2005-09", "2010-14", "2015-17"]
SERIES = {
    "Online (all kinds)": "w1_q24_met_online",
    "Dating site or app": "w1_q24_internet_dating",
    "Through friends": "w1_q24_met_through_friend",
    "Through family": "w1_q24_met_through_family",
    "Work": "w1_q24_met_as_through_cowork",
    "Bar or restaurant": "w1_q24_bar_restaurant",
    "College": "w1_q24_college",
    "Church": "w1_q24_church",
}


def load():
    d = pd.read_stata(DATA, convert_categoricals=False)
    d = d[d.w1_q21a_year.notna() & d.w1_weight_combo.notna() & d.w1_q24_met_online.notna()].copy()
    d["period"] = pd.cut(d.w1_q21a_year, BINS, labels=LABELS)
    rows = []
    for p, g in d.groupby("period", observed=True):
        for name, c in SERIES.items():
            rows.append(dict(period=p, series=name, n=len(g),
                             share=100 * (g[c].fillna(0) * g.w1_weight_combo).sum() / g.w1_weight_combo.sum()))
    return pd.DataFrame(rows)


def plot(d):
    fig = go.Figure()
    for s in d.series.unique():
        x = d[d.series == s]
        fig.add_trace(go.Scatter(
            x=x.period, y=x.share, mode="lines+markers", name=s, customdata=x.n,
            line=dict(width=3 if s == "Online (all kinds)" else 1.8),
            hovertemplate=s + " %{x}: %{y:.1f}% (n=%{customdata})<extra></extra>",
        ))
    fig.update_yaxes(title_text="% of couples", ticksuffix="%", rangemode="tozero")
    fig.update_xaxes(title_text="Period couple first met")
    fig.update_layout(
        template="plotly_white", title="How US couples met, by period first met (HCMST 2017)",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"), margin=dict(r=150, t=60),
        hovermode="closest",
    )
    return fig


if __name__ == "__main__":
    fig = plot(load())
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
