"""Two-panel chart: an internet-use series (left) beside young-adult fertility (right)."""

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from young_fertility import SHOWN


def timeline(use, fert, use_title, use_label, fert_min_year=2000):
    countries = [c for c in SHOWN if c in use] + sorted(set(use.columns) & set(fert.columns) - set(SHOWN))
    colors = pc.qualitative.Dark24
    fig = make_subplots(rows=1, cols=2, shared_xaxes=True, horizontal_spacing=0.08,
                        subplot_titles=(use_title, "Births per woman across ages 20–29"))
    for i, c in enumerate(countries):
        vis = True if c in SHOWN else "legendonly"
        col = colors[i % len(colors)]
        u = use[c].dropna()
        f = fert[c].dropna()
        f = f[f.index >= fert_min_year]
        fig.add_trace(go.Scatter(x=u.index, y=u.values, mode="lines+markers", name=c, legendgroup=c,
                                 line=dict(color=col, width=1.8), marker=dict(size=4), visible=vis,
                                 hovertemplate=c + " %{x}: %{y:.0f}%<extra>" + use_label + "</extra>"), row=1, col=1)
        fig.add_trace(go.Scatter(x=f.index, y=f.values, mode="lines", name=c, legendgroup=c,
                                 showlegend=False, line=dict(color=col, width=1.8), visible=vis,
                                 hovertemplate=c + " %{x}: %{y:.2f}<extra>Fertility 20–29</extra>"), row=1, col=2)
    fig.update_yaxes(ticksuffix="%", range=[0, 102], row=1, col=1)
    fig.update_yaxes(rangemode="tozero", row=1, col=2)
    fig.update_layout(template="plotly_white", hovermode="closest",
                      title="Click country names to add or remove",
                      legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=150, t=90))
    return fig
