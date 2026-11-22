"""Trend-arrow scatter: every series-year is a faint point, and each series gets one arrow
along its straight-line trend in both variables (x and y are each regressed on year; the
arrow joins the fitted values at the first and last fitted year).

- legend="group": one legend entry per group (a series' "group", else its name); clicking
  it hides the group's points, arrows and labels together.
  legend="series": one entry per series, listed under its group's heading. Clicking a
  series hides that series; clicking a heading hides the whole group; double-clicking a
  series shows only it.
- Hovering an arrow or its points draws that series' fitted years joined in year order,
  on an SVG overlay, so hovering never redraws the plot. Arrowhead labels are on the same
  overlay, each placed at the first spot around its arrowhead clear of other labels.
- With more than one x or y option there are x/y dropdowns, and the arrows are refitted in
  the browser for the chosen pair.

All traces are built in JS from one payload, so the fit lives in one place. Use
write_trend_arrows(path, series, x_opts, y_opts, ...).

series: list of dicts with
  name    hover name
  label   short text at the arrowhead (default: name)
  group   legend group (default: name), e.g. a region
  color   (usually shared within a group)
  years   list of years
  x, y    {option key: values aligned to years}; None marks a missing value
  hidden  optional; start in the legend only
  flags   optional {option key: [bool aligned to years]}: unreliable values (e.g. Eurostat "u"),
          drawn as points but left out of the trend; flag_note names them on hover
"""

import json
import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html

TREND_ARROWS_JS = """
var gd = document.getElementById('{plot_id}');
var P = __PAYLOAD__;
var xk = P.x0, yk = P.y0, fitted = [], labels = [], cur = null, timer = null;
// Panels: one x/y pair per subplot. A single chart is one panel driven by the dropdowns.
var single = !P.panels;
var panels = P.panels || [{x: xk, y: yk, xa: 'xaxis', ya: 'yaxis', xr: 'x', yr: 'y'}];

function line(t, v) {
  var n = t.length, mt = 0, mv = 0, sxx = 0, sxy = 0;
  for (var i = 0; i < n; i++) { mt += t[i] / n; mv += v[i] / n; }
  for (i = 0; i < n; i++) { sxx += (t[i] - mt) * (t[i] - mt); sxy += (t[i] - mt) * (v[i] - mv); }
  var b = sxy / sxx;
  return function (yr) { return mv + b * (yr - mt); };
}

function fmt(v, f) { return v.toFixed(+f.replace(/[^0-9]/g, '') || 0); }

function build(resetAxes) {
  // Keep each series' legend visibility across dropdown changes. A legend click shows up
  // in _fullData, not always in gd.data.
  var vis = {};
  (gd._fullData || []).forEach(function (t) {
    if (!t.meta || t.meta.si === undefined) return;
    if (!(t.meta.si in vis)) vis[t.meta.si] = true;
    if (t.visible === 'legendonly') vis[t.meta.si] = 'legendonly';
  });
  if (single) { panels[0].x = xk; panels[0].y = yk; }
  var traces = [], shown = {};
  fitted = [];
  labels = [];
  panels.forEach(function (p, pi) {
  var xk = p.x, yk = p.y, xl = P.xOpts[xk], yl = P.yOpts[yk], ax = {xaxis: p.xr, yaxis: p.yr};
  fitted.push([]);
  P.series.forEach(function (s, si) {
    var g = s.group || s.name;
    var v = si in vis ? vis[si] : (s.hidden ? 'legendonly' : true);
    var early = {x: [], y: [], c: []}, pts = {x: [], y: [], c: []}, flagged = {x: [], y: [], c: []};
    var fl = s.flags || {}, fx_ = fl[xk] || [], fy_ = fl[yk] || [];
    s.years.forEach(function (yr, i) {
      var x = s.x[xk][i], y = s.y[yk][i];
      if (x === null || y === null) return;
      var d = (P.start !== null && yr < P.start) ? early : (fx_[i] || fy_[i]) ? flagged : pts;
      d.x.push(x); d.y.push(y); d.c.push(yr);
    });
    fitted[pi].push(pts);
    var hov = '<b>' + s.name + '</b> %{customdata}<br>' + xl + ' %{x:' + P.xfmt + '}' + P.xsuf +
              '<br>' + yl + ' %{y:' + P.yfmt + '}' + P.ysuf + '<extra></extra>';
    traces.push(Object.assign({type: 'scatter', mode: 'markers', x: early.x, y: early.y, customdata: early.c,
      legendgroup: g, showlegend: false, visible: v, hovertemplate: hov, meta: {si: si},
      marker: {size: 4, color: s.color, opacity: 0.15}}, ax));
    traces.push(Object.assign({type: 'scatter', mode: 'markers', x: pts.x, y: pts.y, customdata: pts.c,
      legendgroup: g, showlegend: false, visible: v, hovertemplate: hov, meta: {si: si},
      marker: {size: 4, color: s.color, opacity: 0.35}}, ax));
    // Flagged values: drawn like the others, but left out of the trend.
    traces.push(Object.assign({type: 'scatter', mode: 'markers', x: flagged.x, y: flagged.y, customdata: flagged.c,
      legendgroup: g, showlegend: false, visible: v, meta: {si: si},
      hovertemplate: hov.replace('<extra>', '<br><i>' + (s.flagNote || 'flagged') + ', not in trend</i><extra>'),
      marker: {size: 4, color: s.color, opacity: 0.35}}, ax));
    var perSeries = P.legend === 'series';
    var arrow = {type: 'scatter', mode: 'lines+markers', x: [], y: [], legendgroup: g, xaxis: p.xr, yaxis: p.yr,
      name: perSeries ? s.name : g, showlegend: pi === 0 && (perSeries || !(g in shown)), visible: v,
      meta: {si: si}, cliponaxis: false,
      line: {color: s.color, width: 2}};
    var li = labels.length;
    labels.push(null);
    if (perSeries && s.group && pi === 0) arrow.legendgrouptitle = {text: s.group};
    shown[g] = true;
    if (pts.x.length >= P.minPts) {
      var y0 = pts.c[0], y1 = pts.c[pts.c.length - 1];
      var fx = line(pts.c, pts.x), fy = line(pts.c, pts.y);
      var x0 = fx(y0), x1 = fx(y1), ya = fy(y0), yb = fy(y1), n = 25, sizes = [];
      // Points along the arrow so hovering anywhere on it registers; only the last is
      // drawn, as the arrowhead.
      for (var k = 0; k < n; k++) {
        var t = k / (n - 1);
        arrow.x.push(x0 + t * (x1 - x0)); arrow.y.push(ya + t * (yb - ya));
        sizes.push(k === n - 1 ? 11 : 0);
      }
      labels[li] = {x: x1, y: yb, text: s.label || s.name, color: s.color, trace: traces.length, p: p};
      arrow.marker = {size: sizes, symbol: 'arrow', angleref: 'previous', color: s.color, line: {width: 0}};
      arrow.hovertemplate = '<b>' + s.name + '</b>, trend ' + y0 + '-' + y1 + '<br>' +
        xl + ' ' + fmt(x0, P.xfmt) + P.xsuf + ' \\u2192 ' + fmt(x1, P.xfmt) + P.xsuf + '<br>' +
        yl + ' ' + fmt(ya, P.yfmt) + P.ysuf + ' \\u2192 ' + fmt(yb, P.yfmt) + P.ysuf + '<extra></extra>';
    }
    traces.push(arrow);
  });
  });
  // A fresh object, so Plotly.react sees the changes.
  var layout = JSON.parse(JSON.stringify(gd.layout));
  if (single) {
    layout.xaxis.title = {text: P.xOpts[xk]};
    layout.yaxis.title = {text: P.yOpts[yk]};
  }
  if (resetAxes) { layout.xaxis.autorange = true; layout.yaxis.autorange = true; }
  highlight(null);
  return Plotly.react(gd, traces, layout);
}

// Arrowhead labels and the hover highlight are drawn on an SVG overlay, not as Plotly
// traces or annotations: changing those redraws the whole plot, and redraws fire more
// hover/unhover events, which made moving between arrows freeze.
var NS = 'http://www.w3.org/2000/svg', overlay = null, labelLayer = null, hlLayer = null;
function ensureOverlay() {
  if (overlay && overlay.isConnected) return;
  overlay = document.createElementNS(NS, 'svg');
  overlay.setAttribute('style', 'position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;overflow:visible');
  labelLayer = document.createElementNS(NS, 'g');
  hlLayer = document.createElementNS(NS, 'g');
  overlay.appendChild(labelLayer); overlay.appendChild(hlLayer);
  gd.querySelector('.svg-container').appendChild(overlay);
}
function px(x, y, p) {
  var xa = gd._fullLayout[p.xa], ya = gd._fullLayout[p.ya];
  return [xa._offset + xa.l2p(x), ya._offset + ya.l2p(y)];
}
function hits(b, boxes) {
  for (var i = 0; i < boxes.length; i++) {
    var o = boxes[i];
    if (b.x < o.x + o.w && o.x < b.x + b.w && b.y < o.y + o.h && o.y < b.y + b.h) return true;
  }
  return false;
}
// Labels: try spots around each arrowhead (above, below, right, left, diagonals, then
// further out) and take the first that clears the arrowheads and labels already placed.
function drawLabels() {
  labelLayer.innerHTML = '';
  var shown = labels.filter(function (l) { return l && gd._fullData[l.trace] && gd._fullData[l.trace].visible === true; });
  var boxes = shown.map(function (l) { var p = px(l.x, l.y, l.p); return {x: p[0] - 5, y: p[1] - 5, w: 10, h: 10}; });
  shown.forEach(function (l) {
    var p = px(l.x, l.y, l.p), t = document.createElementNS(NS, 'text');
    t.textContent = l.text;
    t.setAttribute('fill', l.color); t.setAttribute('font-size', 10);
    t.setAttribute('font-family', '"Open Sans", verdana, arial, sans-serif');
    t.setAttribute('text-anchor', 'middle'); t.setAttribute('dominant-baseline', 'central');
    labelLayer.appendChild(t);
    var bb = t.getBBox(), w = bb.width + 2, h = bb.height;
    // Offsets clear the label's own arrowhead (half-height + 6 px).
    var v = h / 2 + 6, sx = w / 2 + 7;
    var spots = [[0, -v], [0, v], [sx, 0], [-sx, 0], [sx, -v], [-sx, -v], [sx, v], [-sx, v],
                 [0, -v - h], [0, v + h], [sx + 10, 0], [-sx - 10, 0], [0, -v - 2 * h], [0, v + 2 * h]];
    var pick = spots[0];
    for (var i = 0; i < spots.length; i++) {
      var b = {x: p[0] + spots[i][0] - w / 2, y: p[1] + spots[i][1] - h / 2, w: w, h: h};
      if (!hits(b, boxes)) { pick = spots[i]; break; }
    }
    t.setAttribute('x', p[0] + pick[0]); t.setAttribute('y', p[1] + pick[1]);
    boxes.push({x: p[0] + pick[0] - w / 2, y: p[1] + pick[1] - h / 2, w: w, h: h});
  });
}
function draw() {
  ensureOverlay();
  hlLayer.innerHTML = '';
  if (cur === null) return;
  panels.forEach(function (pan, pi) { drawOne(fitted[pi][cur], pan, P.series[cur].color); });
}
// Each panel highlights the hovered series, so it can be followed across panels.
function drawOne(p, pan, c) {
  var d = '';
  for (var i = 0; i < p.x.length; i++) {
    var q = px(p.x[i], p.y[i], pan);
    d += (i ? 'L' : 'M') + q[0] + ',' + q[1];
    var dot = document.createElementNS(NS, 'circle');
    dot.setAttribute('cx', q[0]); dot.setAttribute('cy', q[1]); dot.setAttribute('r', 3.5);
    dot.setAttribute('fill', c);
    hlLayer.appendChild(dot);
  }
  var path = document.createElementNS(NS, 'path');
  path.setAttribute('d', d); path.setAttribute('fill', 'none');
  path.setAttribute('stroke', c); path.setAttribute('stroke-width', 1.5);
  hlLayer.insertBefore(path, hlLayer.firstChild);
}
// At most one overlay draw per animation frame, however fast hover events arrive.
var frame = null;
function highlight(si) {
  if (si === cur) return;
  cur = si;
  if (frame === null) frame = requestAnimationFrame(function () { frame = null; draw(); });
}
gd.on('plotly_hover', function (e) {
  var m = e.points[0].data.meta;
  if (!m || m.si === undefined) return;
  clearTimeout(timer);
  highlight(m.si);
});
gd.on('plotly_unhover', function () {
  clearTimeout(timer);
  timer = setTimeout(function () { highlight(null); }, 150);
});
// Zoom, pan, resize and legend clicks move or hide arrows: redraw the overlay to match.
gd.on('plotly_afterplot', function () { ensureOverlay(); drawLabels(); draw(); });
// legend="series": several series share a legend group, so Plotly would toggle the whole
// group. Toggle the clicked series' traces instead (group headings keep Plotly's toggle).
// A click waits out the double-click delay so a double-click doesn't toggle first.
function setVisible(map) {
  var idx = [], v = [];
  gd.data.forEach(function (t, i) {
    if (t.meta && t.meta.si in map) { idx.push(i); v.push(map[t.meta.si]); }
  });
  Plotly.restyle(gd, {visible: v}, idx);
}
var clickTimer = null;
gd.on('plotly_legendclick', function (e) {
  var t = e.curveNumber === undefined ? null : gd.data[e.curveNumber];
  if (P.legend !== 'series' || !t || !t.meta) return true;
  var si = t.meta.si, on = gd._fullData[e.curveNumber].visible === true;
  clearTimeout(clickTimer);
  clickTimer = setTimeout(function () { var m = {}; m[si] = on ? 'legendonly' : true; setVisible(m); },
                          gd._context.doubleClickDelay);
  return false;
});
gd.on('plotly_legenddoubleclick', function (e) {
  var t = e.curveNumber === undefined ? null : gd.data[e.curveNumber];
  if (P.legend !== 'series' || !t || !t.meta) return true;
  clearTimeout(clickTimer);
  var si = t.meta.si, alone = true, m = {};
  gd._fullData.forEach(function (f) {
    if (f.meta && f.meta.si !== si && f.showlegend && f.visible === true) alone = false;
  });
  P.series.forEach(function (s, i) { m[i] = alone || i === si ? true : 'legendonly'; });
  setVisible(m);
  return false;
});
gd.on('plotly_buttonclicked', function (e) {
  var key = e.button.args[0];
  if (e.menu.name === 'x') xk = key; else yk = key;
  build(true);
});
build(false);
"""


def _clean(values):
    return [None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v) for v in values]


def trend_arrows_fig(series, x_opts, y_opts, x_default=None, y_default=None, *, title,
                     start_year=None, min_points=3, x_fmt=".1f", y_fmt=".1f", x_suffix="",
                     y_suffix="", legend="group", layout=None, panels=None, cols=2, equal=False):
    """(figure, post_script) for a trend-arrow chart; pass both to write_html, or use
    write_trend_arrows.

    x_opts / y_opts: {option key: axis title}. x_default / y_default: the starting options
    (default: the first). start_year: years before it are drawn fainter and not fitted
    (default: fit every year). min_points: fewest fitted years needed for an arrow.
    legend: "group" or "series" (see the module docstring).
    layout: extra fig.update_layout arguments (e.g. legend placement).
    panels: instead of dropdowns, a grid of subplots, one per {"x": x key, "y": y key,
      "title": subplot title}, `cols` wide, with shared x and y axes (one range for all).
      x_opts / y_opts then give each key's hover label; axis titles come from `layout`.
    equal: one percentage point (or unit) is the same length on x and y. With panels, all
      axes get one shared range instead; the panels are square only as the figure's size allows.
    """
    x_default = x_default or next(iter(x_opts))
    y_default = y_default or next(iter(y_opts))
    payload = {
        "series": [{"name": s["name"], "label": s.get("label", s["name"]), "group": s.get("group"),
                    "color": s["color"], "hidden": bool(s.get("hidden")),
                    "years": [int(y) for y in s["years"]],
                    "x": {k: _clean(s["x"][k]) for k in x_opts},
                    "y": {k: _clean(s["y"][k]) for k in y_opts},
                    **({"flags": {k: [bool(f) for f in v] for k, v in s["flags"].items() if k in x_opts or k in y_opts},
                        "flagNote": s.get("flag_note")} if s.get("flags") else {})} for s in series],
        "xOpts": x_opts, "yOpts": y_opts, "x0": x_default, "y0": y_default,
        "start": start_year, "minPts": min_points,
        "legend": legend, "panels": None, "xfmt": x_fmt, "yfmt": y_fmt, "xsuf": x_suffix, "ysuf": y_suffix,
    }
    if panels:
        return _panels_fig(payload, panels, cols, title, x_suffix, y_suffix, equal, layout)
    menus = []
    for name, opts, default, x in (("x", x_opts, x_default, 0.0), ("y", y_opts, y_default, 0.45)):
        if len(opts) > 1:
            menus.append(dict(
                name=name, active=list(opts).index(default), x=x, xanchor="left", y=1.01, yanchor="bottom",
                buttons=[dict(label=f"{name}: {lab}", method="skip", args=[k]) for k, lab in opts.items()]))
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white", title=dict(text=title, x=0.01, font=dict(size=14)),
        updatemenus=menus, hovermode="closest",
        margin=dict(t=130 if menus else 50, r=20, l=60, b=40),
        # Percentage axes start at 0.
        xaxis=dict(title=dict(text=x_opts[x_default]), ticksuffix=x_suffix,
                   rangemode="tozero" if x_suffix == "%" else "normal"),
        yaxis=dict(title=dict(text=y_opts[y_default]), ticksuffix=y_suffix,
                   rangemode="tozero" if y_suffix == "%" else "normal"),
    )
    if equal:
        # Fixed ranges (from 0 on % axes, to the data's top rounded up to 5), and the plot
        # area shrinks to keep them equal (constrain="domain"), so no axis runs below 0.
        rng = {}
        for ax, key, opts, suf in (("x", "x", x_opts, x_suffix), ("y", "y", y_opts, y_suffix)):
            v = [u for s in payload["series"] for k in opts for u in s[key][k] if u is not None]
            lo = 0 if suf == "%" else 5 * math.floor(min(v) / 5)
            rng[ax] = [lo, 5 * math.ceil(max(v) / 5)]
        fig.update_xaxes(range=rng["x"], constrain="domain")
        fig.update_yaxes(range=rng["y"], scaleanchor="x", scaleratio=1, constrain="domain")
    fig.update_layout(**(layout or {}))
    return fig, TREND_ARROWS_JS.replace("__PAYLOAD__", json.dumps(payload))


def _panels_fig(payload, panels, cols, title, x_suffix, y_suffix, equal, layout):
    rows = -(-len(panels) // cols)
    fig = make_subplots(rows=rows, cols=cols, shared_xaxes="all", shared_yaxes="all",
                        subplot_titles=[p.get("title", "") for p in panels],
                        horizontal_spacing=0.07, vertical_spacing=0.28 / rows)
    payload["panels"] = []
    for i, p in enumerate(panels):
        n = "" if i == 0 else str(i + 1)
        payload["panels"].append({"x": p["x"], "y": p["y"], "xa": f"xaxis{n}", "ya": f"yaxis{n}",
                                  "xr": f"x{n}", "yr": f"y{n}"})
    fig.update_layout(template="plotly_white", title=dict(text=title, x=0.01, font=dict(size=14)),
                      hovermode="closest", margin=dict(t=70, r=20, l=60, b=50))
    fig.update_xaxes(ticksuffix=x_suffix, rangemode="tozero" if x_suffix == "%" else "normal")
    fig.update_yaxes(ticksuffix=y_suffix, rangemode="tozero" if y_suffix == "%" else "normal")
    if equal:
        # scaleanchor conflicts with shared (matched) axes, so instead every axis gets one
        # range, from 0 (or the lowest value) to the highest value in any panel, rounded to 10.
        vals = [v for s in payload["series"] for p in panels for v in s["x"][p["x"]] + s["y"][p["y"]]
                if v is not None]
        lo = 0 if x_suffix == "%" else 10 * math.floor(min(vals) / 10)
        rng = [lo, 10 * math.ceil(max(vals) / 10)]
        fig.update_xaxes(range=rng)
        fig.update_yaxes(range=rng)
    fig.update_layout(**(layout or {}))
    return fig, TREND_ARROWS_JS.replace("__PAYLOAD__", json.dumps(payload))


def write_trend_arrows(path, series, x_opts, y_opts, x_default=None, y_default=None, *,
                       full_page=True, log=True, **kw):
    """Build a trend-arrow chart (see trend_arrows_fig) and write it with write_html."""
    fig, js = trend_arrows_fig(series, x_opts, y_opts, x_default, y_default, **kw)
    return write_html(fig, path, post_script=js, full_page=full_page, log=log)
