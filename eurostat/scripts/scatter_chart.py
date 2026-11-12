"""Scatter of change in internet use against change in young-adult fertility, by country."""

import numpy as np
import plotly.graph_objects as go

from young_fertility import young_fertility


def changes(use, y0, y1, fert=None):
    fert = young_fertility() if fert is None else fert
    rows = []
    for c in use.columns:
        if c not in fert:
            continue
        u0, u1 = use[c].get(y0), use[c].get(y1)
        f0, f1 = fert[c].get(y0), fert[c].get(y1)
        if any(v is None or np.isnan(v) for v in (u0, u1, f0, f1)):
            continue
        rows.append(dict(country=c, u0=u0, u1=u1, du=u1 - u0, f0=f0, f1=f1, df=100 * (f1 / f0 - 1)))
    return rows


def scatter(rows, xtitle, label, y0, y1):
    x = np.array([r["du"] for r in rows])
    y = np.array([r["df"] for r in rows])
    m, b = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers+text", text=[r_["country"] for r_ in rows], textposition="top center",
        marker=dict(size=9), name="Countries",
        customdata=[[r_["u0"], r_["u1"], r_["f0"], r_["f1"]] for r_ in rows],
        hovertemplate=("%{text}<br>" + label + " %{customdata[0]:.0f}% → %{customdata[1]:.0f}%"
                       "<br>Fertility 20–29 %{customdata[2]:.2f} → %{customdata[3]:.2f}<extra></extra>")))
    xs = np.array([x.min(), x.max()])
    fig.add_trace(go.Scatter(x=xs, y=m * xs + b, mode="lines", name=f"Fit (r = {r:.2f}, n = {len(x)})",
                             line=dict(dash="dash", color="grey")))
    fig.update_xaxes(title_text=xtitle, ticksuffix=" pp")
    fig.update_yaxes(title_text=f"Change in births per woman across ages 20–29, {y0}–{y1}", ticksuffix="%",
                     zeroline=True)
    fig.update_layout(template="plotly_white", hovermode="closest",
                      title=f"Rise in {label.lower()} vs change in young fertility, {y0}–{y1}",
                      legend=dict(orientation="h", y=-0.2), margin=dict(t=60))
    return fig, r
