"""ART infants as a share of national births, European HFD countries.

ESHRE "ART in Europe" reports (open-access years 2007, 2015-2019; ART infants per national
births, only given for countries with complete clinic coverage), plus Goisis et al. (2024)
Figure 1 for Denmark, France, Spain and the UK in other years (that figure plots the same
ESHRE series). Run from the HFD directory.
"""

import pathlib

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
EIM = _REPO_ROOT / "research" / "data" / "eim_art_infants_by_country.csv"
GOISIS = _REPO_ROOT / "research" / "data" / "goisis2024_fig1_art_share_births.csv"
OUTPUT = "outputs/eshre_art_share_by_country.html"

# ESHRE country name -> display name, HFD countries only
NAMES = {
    "Austria": "Austria", "Belgium": "Belgium", "Bulgaria": "Bulgaria", "Czech Republic": "Czechia",
    "Denmark": "Denmark", "Estonia": "Estonia", "Finland": "Finland", "France": "France",
    "Hungary": "Hungary", "Ireland": "Ireland", "Lithuania": "Lithuania", "The Netherlands": "Netherlands",
    "Portugal": "Portugal", "Slovenia": "Slovenia", "Spain": "Spain", "Sweden": "Sweden",
    "Switzerland": "Switzerland", "UK": "UK", "United Kingdom": "UK",
}
COLS = 6
ESHRE_COLOR = "#2a78d6"
GOISIS_COLOR = "#86b6ef"
LABEL_FONT = dict(size=13, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")


def load():
    e = pd.read_csv(EIM)
    e = e[e["country"].isin(NAMES)].assign(country=lambda d: d["country"].map(NAMES), source="ESHRE")
    e = e.rename(columns={"pct_national_births": "pct"})[["country", "year", "pct", "source"]]
    g = pd.read_csv(GOISIS).rename(columns={"art_pct_births": "pct"}).replace({"country": {"United Kingdom": "UK"}})
    g = g[g["country"].isin(set(e["country"]))].assign(source="Goisis et al. Fig. 1")
    g = g[~g.set_index(["country", "year"]).index.isin(e.set_index(["country", "year"]).index)]
    return pd.concat([e, g[["country", "year", "pct", "source"]]]).sort_values(["country", "year"])


def main():
    df = load()
    # order panels by latest value, highest first
    latest = df.sort_values("year").groupby("country")["pct"].last().sort_values(ascending=False)
    countries = list(latest.index)
    rows = -(-len(countries) // COLS)
    fig = make_subplots(rows=rows, cols=COLS, shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=0.012, vertical_spacing=0.06)
    for i, country in enumerate(countries):
        r, c = i // COLS + 1, i % COLS + 1
        sub = df[df["country"] == country].set_index("year").reindex(range(2000, 2020)).reset_index()
        for source, color in (("Goisis et al. Fig. 1", GOISIS_COLOR), ("ESHRE", ESHRE_COLOR)):
            s = sub.where(sub["source"] == source)
            fig.add_trace(go.Scatter(
                x=sub["year"], y=s["pct"] / 100, mode="markers", name=source, legendgroup=source,
                showlegend=i == 0, marker=dict(size=7, color=color, line=dict(width=1.5, color="white")),
                hovertemplate=f"{country}<br>%{{x}}<br>%{{y:.1%}}<br>{source}<extra></extra>",
            ), row=r, col=c)
        line = sub.dropna(subset=["pct"])
        fig.add_trace(go.Scatter(x=line["year"], y=line["pct"] / 100, mode="lines", showlegend=False,
                                 hoverinfo="skip", line=dict(width=1.5, color="#9aa4b1")), row=r, col=c)
        fig.add_annotation(text=f"<b>{country}</b>", x=0.04, y=0.97, xref="x domain", yref="y domain",
                           xanchor="left", yanchor="top", showarrow=False, font=LABEL_FONT, row=r, col=c)
    fig.update_yaxes(tickformat=".0%", range=[0, 0.1], dtick=0.02)
    fig.update_xaxes(range=[1999.5, 2019.5], tickvals=[2000, 2010], ticktext=["2000", "2010"], tickfont=dict(size=10))
    fig.update_layout(
        template="plotly_white", height=170 * rows + 80, margin=dict(l=50, r=15, t=50, b=30),
        legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom", xanchor="left"), hovermode="closest",
    )
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, config={"responsive": True})
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT} ({len(countries)} countries, {rows} rows)")
    print(df[df["source"] == "ESHRE"].pivot(index="country", columns="year", values="pct").to_string())


if __name__ == "__main__":
    main()
