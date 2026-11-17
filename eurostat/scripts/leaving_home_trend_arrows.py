"""Women's leaving age vs TFR and vs mean age of mothers at first birth, all
years on one static chart per y metric, by European country (alternatives to
the year-slider scatters in leaving_home_vs_tfr.py).

Every country-year is a faint point. Each country gets one arrow along its
straight-line trend in both variables from START_YEAR to its latest year:
leaving age and the y metric are each regressed on year, and the arrow
joins the fitted values at the first and last year. Hovering an arrow
highlights the country-years it was fitted to.

Inputs: as leaving_home_vs_tfr.py (eurostat/data/).
Outputs: outputs/leaving_home_tfr_fitted.html, outputs/leaving_home_mab1_fitted.html
Run from the eurostat/ directory.
"""

import numpy as np
import plotly.graph_objects as go

from leaving_home_vs_tfr import CODE_REGION, NAMES, REGION_COLOR, load

START_YEAR = 2010
XTITLE = "Women's average age at leaving the parental home"

# y metric -> (axis title, hover label, hover format, axis padding, output file)
METRICS = {
    "tfr": ("Total fertility rate", "TFR", ".2f", 0.05, "outputs/leaving_home_tfr_fitted.html"),
    "mab1": ("Mean age of mothers at first birth", "Age at first birth", ".1f", 0.3,
             "outputs/leaving_home_mab1_fitted.html"),
}


def layout(fig, df, title, **kw):
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, x=0.02, font=dict(size=14)),
        legend=dict(orientation="h", y=-0.15),
        margin=dict(t=50, r=20, l=60, b=40),
        **kw,
    )
    return fig


def ranges(df, ycol, ypad):
    return ([df["age"].min() - 0.5, df["age"].max() + 0.8],
            [df[ycol].min() - ypad, df[ycol].max() + ypad])


def legend_dummies(fig, regions, **kw):
    for region in regions:
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=region,
                                 marker=dict(size=8, color=REGION_COLOR[region])), **kw)


def arrow(fig, x0, y0, x1, y1, color, width=1.5):
    fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=width,
                       arrowcolor=color, text="")


# Hovering an arrow (or one of its points) highlights the country-years the
# arrow was fitted to, joined in year order; moving off resets.
FITTED_HOVER_JS = """
var gd = document.getElementById('{plot_id}');
var idx = {};
gd.data.forEach(function (t, i) { if (t.meta && t.meta.role === 'pts') idx[t.meta.geo] = i; });
var all = Object.values(idx), current = null, busy = false, timer = null;
// The restyle redraws the plot, which can itself fire unhover; ignore events
// while it runs and delay the reset so the highlight doesn't flicker or loop.
function style(geo) {
  if (geo === current) return;
  current = geo;
  busy = true;
  Plotly.restyle(gd, {
    'marker.opacity': all.map(function (i) { return geo === null ? 0.25 : (i === idx[geo] ? 1 : 0.06); }),
    'marker.size': all.map(function (i) { return geo !== null && i === idx[geo] ? 8 : 4; }),
    'mode': all.map(function (i) { return geo !== null && i === idx[geo] ? 'lines+markers' : 'markers'; })
  }, all).then(function () { setTimeout(function () { busy = false; }, 50); });
}
gd.on('plotly_hover', function (e) {
  var m = e.points[0].data.meta;
  if (!m || !(m.geo in idx)) return;
  clearTimeout(timer);
  style(m.geo);
});
gd.on('plotly_unhover', function () {
  if (busy) return;
  clearTimeout(timer);
  timer = setTimeout(function () { style(null); }, 150);
});
"""


def fitted(df, ycol):
    ytitle, ylabel, yfmt, ypad, output = METRICS[ycol]
    df = df.dropna(subset=[ycol])
    hover = (f"<b>%{{customdata[0]}}</b> %{{customdata[1]}}<br>Leaving age %{{x:.1f}}"
             f"<br>{ylabel} %{{y:{yfmt}}}<extra></extra>")
    fig = go.Figure()
    # Years before START_YEAR are not used in any fit: faint, never highlighted.
    early = df[df["year"] < START_YEAR]
    for region, color in REGION_COLOR.items():
        r = early[early["region"] == region]
        fig.add_trace(go.Scatter(
            x=r["age"], y=r[ycol], mode="markers", showlegend=False,
            marker=dict(size=4, color=color, opacity=0.25),
            customdata=np.c_[r["name"], r["year"]], hovertemplate=hover,
        ))
    fits = []
    for geo, g in df[df["year"] >= START_YEAR].sort_values("year").groupby("geo"):
        color = REGION_COLOR[CODE_REGION[geo]]
        # The country-years each arrow is fitted to: one trace per country.
        fig.add_trace(go.Scatter(
            x=g["age"], y=g[ycol], mode="markers", showlegend=False, meta=dict(role="pts", geo=geo),
            marker=dict(size=4, color=color, opacity=0.25), line=dict(color=color, width=1),
            customdata=np.c_[g["name"], g["year"]], hovertemplate=hover,
        ))
        if len(g) >= 3:
            fits.append((geo, g, color))
    ends_x, ends_y = [], []
    for geo, g, color in fits:
        y0, y1 = g["year"].min(), g["year"].max()
        bx, ax_ = np.polyfit(g["year"], g["age"], 1)
        by, ay = np.polyfit(g["year"], g[ycol], 1)
        xs = bx * np.array([y0, y1]) + ax_
        ys = by * np.array([y0, y1]) + ay
        ends_x += list(xs)
        ends_y += list(ys)
        # Invisible points along the arrow so hovering anywhere on it registers.
        t = np.linspace(0, 1, 25)
        fig.add_trace(go.Scatter(
            x=xs[0] + t * (xs[1] - xs[0]), y=ys[0] + t * (ys[1] - ys[0]), mode="markers",
            marker=dict(size=8, color=color, opacity=0), showlegend=False,
            meta=dict(role="arrow", geo=geo),
            hovertemplate=(f"<b>{NAMES[geo]}</b>, trend {int(y0)}-{int(y1)}<br>"
                           f"Leaving age {xs[0]:.1f} → {xs[1]:.1f}<br>"
                           f"{ylabel} {ys[0]:{yfmt}} → {ys[1]:{yfmt}}<extra></extra>"),
        ))
        arrow(fig, xs[0], ys[0], xs[1], ys[1], color, width=2)
        fig.add_annotation(x=xs[1], y=ys[1], text=geo, showarrow=False, yshift=9,
                           font=dict(size=10, color=color))
    legend_dummies(fig, REGION_COLOR)
    x, y = ranges(df, ycol, ypad)
    # Fitted ends can fall outside the observed range; keep every arrow in view.
    x = [min(x[0], min(ends_x) - 0.3), max(x[1], max(ends_x) + 0.3)]
    y = [min(y[0], min(ends_y) - ypad), max(y[1], max(ends_y) + ypad)]
    fig = layout(fig, df, f"Each country's linear trend, {START_YEAR} to latest year (points: every country-year)",
                 xaxis=dict(title=XTITLE, range=x), yaxis=dict(title=ytitle, range=y), hovermode="closest")
    fig.write_html(output, include_plotlyjs="cdn",
                   default_width="100%", default_height="100%", config={"responsive": True},
                   post_script=FITTED_HOVER_JS)


if __name__ == "__main__":
    _, df = load()
    for ycol in METRICS:
        fitted(df, ycol)
