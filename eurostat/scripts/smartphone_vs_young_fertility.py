"""Mobile internet use among 16-24s against fertility at ages 20-29, one path per country.

Eurostat isoc_ci_im_i (I_IUMP) and demo_frate, each year both exist (2011-2019).
See young_fertility.py for download URLs.
"""

import plotly.colors as pc
import plotly.graph_objects as go

from common.plotting import write_html
from young_fertility import OUTDIR, SHOWN, internet_use, young_fertility

if __name__ == "__main__":
    use, fert = internet_use("imp_slim.csv"), young_fertility()
    countries = [c for c in SHOWN if c in use] + sorted(set(use.columns) & set(fert.columns) - set(SHOWN))
    colors = pc.qualitative.Dark24
    fig = go.Figure()
    for i, c in enumerate(countries):
        d = use[[c]].join(fert[[c]], lsuffix="_u", rsuffix="_f", how="inner").dropna()
        if len(d) < 2:
            continue
        col = colors[i % len(colors)]
        n = len(d)
        fig.add_trace(go.Scatter(
            x=d[f"{c}_u"], y=d[f"{c}_f"], mode="lines+markers+text", name=c,
            visible=True if c in SHOWN else "legendonly",
            text=[str(y) if k in (0, n - 1) else "" for k, y in enumerate(d.index)],
            textposition="top center", textfont=dict(size=9, color=col),
            line=dict(color=col, width=1.8),
            marker=dict(size=[5] * (n - 1) + [10], color=col),
            customdata=d.index, hovertemplate=c + " %{customdata}: %{x:.0f}%, %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="Mobile internet use, ages 16–24", ticksuffix="%", range=[0, 102])
    fig.update_yaxes(title_text="Births per woman across ages 20–29")
    fig.update_layout(template="plotly_white", hovermode="closest",
                      title="Mobile internet use vs young fertility, 2011–2019",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=150, t=60))
    write_html(fig, OUTDIR / "smartphone_vs_young_fertility.html")
