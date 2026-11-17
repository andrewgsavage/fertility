"""ART share of births, 2000-2019, for Denmark, France, Spain, the UK and the US,
digitised from Goisis et al. (2024) Figure 1. Run from the HFD directory.
"""

import pathlib

import pandas as pd
import plotly.graph_objects as go

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
DATA = _REPO_ROOT / "research" / "data" / "goisis2024_fig1_art_share_births.csv"
OUTPUT = "outputs/goisis_fig1_art_share.html"

COUNTRY_COLORS = {
    "Denmark": "#2a78d6",
    "France": "#eb6834",
    "Spain": "#1baf7a",
    "United Kingdom": "#eda100",
    "United States": "#e87ba4",
}


def main():
    df = pd.read_csv(DATA)
    fig = go.Figure()
    for country, color in COUNTRY_COLORS.items():
        sub = df[df["country"] == country].set_index("year").reindex(range(2000, 2020)).reset_index()
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["art_pct_births"] / 100, name=country, mode="lines+markers",
            line=dict(width=2, color=color), marker=dict(size=8, color=color, line=dict(width=2, color="white")),
            hovertemplate=f"{country}<br>%{{x}}<br>%{{y:.2%}}<extra></extra>",
        ))
    fig.update_layout(
        template="plotly_white", height=420, margin=dict(l=60, r=20, t=40, b=40),
        yaxis=dict(title="ART share of births", tickformat=".0%", rangemode="tozero"),
        legend=dict(orientation="h", x=0, y=1.1, xanchor="left"), hovermode="closest",
    )
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, config={"responsive": True})
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
