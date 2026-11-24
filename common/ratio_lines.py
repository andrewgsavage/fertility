"""Ratio over time: % of women with a child divided by % of women in a couple, by year, one
line per series, in a grid of panels. The companion of the trend-arrow charts on
docs/factors/coupling-vs-mothers.md: a constant ratio is an arrow pointing at the origin
(fewer couples, the same number of mothers per coupled woman); a falling ratio is an arrow
steeper than that.

Both shares are of all women, so the ratio is mothers per coupled woman, not the share of
couples with a child: mothers outside couples push it up, and it can exceed 1.

diff=True plots y minus x instead (e.g. years between two mean ages), on a linear axis with a
dotted line at 0.

series: as common/trend_arrows.py (name, label, color, group, years, x {key: values},
  y {key: values}, hidden, flags, flag_note). Line segments touching a flagged value are dashed.
panels: [{"x": x key, "y": y key, "title": subplot title, optional "series": the panel's own
  series list}], `cols` wide, shared x (year) axes; each panel has its own y range.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html


# Explicit ticks on every panel: Plotly's own log ticks label the in-between digits as bare
# "2 … 9", so 0.9 reads as 9. Dense set for panels spanning under a factor of 10, sparse otherwise.
TICKS = [0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8,
         10, 15, 20, 30, 40, 50]
TICKS_WIDE = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]


def _ratio(xs, ys):
    return [None if x is None or y is None or x != x or y != y or x == 0 else y / x for x, y in zip(xs, ys)]


def _diff(xs, ys):
    return [None if x is None or y is None or x != x or y != y else y - x for x, y in zip(xs, ys)]


def ratio_fig(series, panels, *, title, cols=2, legend=False, height=None, min_points=2, diff=False,
              y_title="% with a child ÷ % in a couple", hover_label="with a child ÷ in a couple",
              y_suffix=""):
    rows = -(-len(panels) // cols)
    # Each panel gets its own y range: the ratio differs by an order of magnitude between ages.
    fig = make_subplots(rows=rows, cols=cols, shared_xaxes="all", shared_yaxes=False,
                        subplot_titles=[p.get("title", "") for p in panels],
                        horizontal_spacing=0.07, vertical_spacing=0.28 / rows)
    shown = set()
    spans = []
    for i, p in enumerate(panels):
        r, c = divmod(i, cols)
        span = []
        for s in p.get("series", series):
            fl = s.get("flags") or {}
            fxy = [a or b for a, b in zip(fl.get(p["x"], [False] * len(s["years"])),
                                          fl.get(p["y"], [False] * len(s["years"])))]
            op = _diff if diff else _ratio
            pts = [(yr, v, f) for yr, v, f in zip(s["years"], op(s["x"][p["x"]], s["y"][p["y"]]), fxy)
                   if v is not None]
            if len(pts) < min_points:
                continue
            yrs, vals, flags = zip(*pts)
            span += [v for v in vals if diff or v > 0]
            group = s.get("group") or s["name"]
            first = group not in shown
            shown.add(group)
            label = s.get("label", s["name"])
            common = dict(legendgroup=group, visible="legendonly" if s.get("hidden") else True, cliponaxis=False)
            note = s.get("flag_note") or "flagged"
            fig.add_trace(go.Scatter(
                x=yrs, y=vals, mode="markers+text", name=group if legend else s["name"],
                showlegend=legend and first, marker=dict(size=4, color=s["color"]),
                text=[""] * (len(yrs) - 1) + [label], textposition="middle right",
                textfont=dict(size=10, color=s["color"]),
                customdata=[f"<br><i>{note}</i>" if f else "" for f in flags],
                hovertemplate=f"<b>{s['name']}</b> %{{x}}<br>{hover_label}: %{{y:.2f}}{y_suffix}%{{customdata}}<extra></extra>",
                **common), row=r + 1, col=c + 1)
            # Solid line between reliable points; dashed for any segment touching a flagged one.
            for dash, keep in ((None, False), ("dash", True)):
                lx, ly = [], []
                for k in range(len(yrs) - 1):
                    if (flags[k] or flags[k + 1]) == keep:
                        if lx and lx[-1] != yrs[k]:
                            lx.append(None); ly.append(None)
                        if not lx or lx[-1] != yrs[k]:
                            lx.append(yrs[k]); ly.append(vals[k])
                        lx.append(yrs[k + 1]); ly.append(vals[k + 1])
                if lx:
                    fig.add_trace(go.Scatter(x=lx, y=ly, mode="lines", showlegend=False, hoverinfo="skip",
                                             line=dict(color=s["color"], width=1.6, dash=dash), **common),
                                  row=r + 1, col=c + 1)
        spans.append(span)
    fig.update_layout(template="plotly_white", title=dict(text=title, x=0.01, font=dict(size=14)),
                      hovermode="closest", showlegend=legend, margin=dict(t=70, r=40, l=60, b=50))
    if height:
        fig.update_layout(height=height)
    # Log scale: the ratio is multiplicative (0.5 and 2 are equally far from 1), and where few
    # young women live in a couple it runs into double figures. A dotted line marks 1.
    # A difference is additive: linear axis, dotted line at 0.
    if not diff:
        fig.update_yaxes(type="log")
    fig.add_hline(y=0 if diff else 1, line=dict(color="#999999", width=1, dash="dot"), row="all", col="all")
    for i in range(len(panels)):
        n = "" if i == 0 else str(i + 1)
        fig.layout[f"xaxis{n}"].update(showticklabels=True)
        fig.layout[f"yaxis{n}"].update(showticklabels=True)
        if not diff:
            ticks = TICKS if spans[i] and max(spans[i]) / min(spans[i]) < 10 else TICKS_WIDE
            fig.layout[f"yaxis{n}"].update(tickvals=ticks, ticktext=[f"{t:g}" for t in ticks])
        else:
            fig.layout[f"yaxis{n}"].update(ticksuffix=y_suffix)
        if i % cols == 0:
            fig.layout[f"yaxis{n}"].update(title_text=y_title)
    return fig


def write_ratio_lines(path, series, panels, **kw):
    return write_html(ratio_fig(series, panels, **kw), path)
