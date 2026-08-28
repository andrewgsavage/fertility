"""Rate of change of total fertility rate (d(TFR)/d(year)) plotted against
the TFR level itself, by country, from Our World in Data's
"children-born-per-woman" grapher
(https://ourworldindata.org/grapher/children-born-per-woman).

Multi-select checkbox sidebar (search box + scrollable list, like OWID's own
"Add country" picker) rather than Plotly's own dropdown/updatemenu — all
entities are pre-added as traces (initially hidden except DEFAULT_ENTITIES),
and a checkbox toggles a trace's visibility; injected into the written HTML
directly since this needs plain form controls.
"""

import json
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go

INPUT = "data/children-born-per-woman.csv"
OUTPUT = "outputs/tfr_derivative.html"

# Same default selection OWID itself uses for this chart (see the grapher's
# own "selection" list in its metadata).
DEFAULT_ENTITIES = ["World", "United States", "United Kingdom", "Russia", "Germany", "Japan", "India"]

# Plotly's default D3 qualitative colorway — reused here (rather than
# Plotly's own default-assigned trace colors) so JS can hand out/reclaim the
# same fixed palette as checkboxes are toggled (see the color pool in
# post_script below).
PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

# Marker alpha fades by year within each entity's own span (oldest point at
# MIN_ALPHA, most recent at 1.0) — so age reads directly off how faded a
# point is, regardless of how many years of data a given entity has.
MIN_ALPHA = 0.15
DEFAULT_XLIM_MAX = 2.5

# Faded initial view: most defaults sit under DEFAULT_XLIM_MAX, but a couple
# (World, India) range historically much higher — the rangeslider still
# shows their full extent, this just keeps the initial framing on the
# low-TFR range most of the story is in.
DEFAULT_XLIM = (0.5, DEFAULT_XLIM_MAX)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgba(hex_color, alpha):
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha:.3f})"


def alpha_ramp(years):
    y0, y1 = years[0], years[-1]
    span = y1 - y0
    return [MIN_ALPHA + (1 - MIN_ALPHA) * ((y - y0) / span if span else 1.0) for y in years]


df = pd.read_csv(INPUT).sort_values(["entity", "year"])

# entity -> {years, tfr, deriv, alpha}. Every entity in this dataset has a
# consecutive (no-gap) run of years, so a plain central-difference gradient
# (np.gradient, one-sided at the two endpoints) is safe without first
# resampling to a regular grid.
series = {}
for entity, rows in df.groupby("entity"):
    years = rows["year"].to_numpy()
    tfr = rows["fertility_rate_hist"].to_numpy()
    deriv = np.gradient(tfr, years)
    series[entity] = {
        "years": years.tolist(),
        "tfr": tfr.tolist(),
        "deriv": [round(v, 4) for v in deriv],
        "alpha": [round(a, 3) for a in alpha_ramp(years)],
    }

entities = sorted(series)
default_entities = [e for e in DEFAULT_ENTITIES if e in series] or entities[:1]
default_color = {e: PALETTE[i % len(PALETTE)] for i, e in enumerate(default_entities)}

# Y-slider bounds: the full range across every entity (some historical
# famine/war years produce extreme single-year swings) — the default
# *view*, below, is much tighter, sized to what's actually visible with the
# starting country selection.
all_derivs = [v for s in series.values() for v in s["deriv"]]
Y_SLIDER_MIN, Y_SLIDER_MAX = math.floor(min(all_derivs) * 10) / 10, math.ceil(max(all_derivs) * 10) / 10

default_derivs = [v for e in default_entities for v in series[e]["deriv"]]
_y_lo, _y_hi = min(default_derivs), max(default_derivs)
_y_pad = (_y_hi - _y_lo) * 0.08
DEFAULT_YLIM = (_y_lo - _y_pad, _y_hi + _y_pad)

fig = go.Figure(
    data=[
        go.Scatter(
            x=series[entity]["tfr"], y=series[entity]["deriv"],
            customdata=series[entity]["years"],
            mode="lines+markers",
            line=dict(width=1.5, color=rgba(default_color[entity], 0.5) if entity in default_color else "#ccc"),
            marker=dict(size=4, color=[rgba(default_color[entity], a) for a in series[entity]["alpha"]] if entity in default_color else "#ccc"),
            name=entity,
            visible=entity in default_entities,
            hovertemplate=f"<b>{entity}</b><br>Year %{{customdata}}<br>TFR %{{x:.3f}}<br>%{{y:.3f}} / yr<extra></extra>",
        )
        for entity in entities
    ]
)
fig.update_layout(
    template="plotly_white",
    autosize=True,
    margin=dict(t=20, r=20, l=60, b=40),
    xaxis=dict(
        title="TFR (children per woman)",
        range=list(DEFAULT_XLIM), autorange=False,
        rangeslider=dict(visible=True, thickness=0.08),
    ),
    yaxis=dict(title="Change in TFR per year (children per woman / yr)", range=list(DEFAULT_YLIM), autorange=False),
    shapes=[dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=0, y1=0, line=dict(color="#999", width=1, dash="dot"))],
    legend=dict(orientation="h", y=1.08),
)

entity_index = {e: i for i, e in enumerate(entities)}

post_script = f"""
var gd = document.getElementById('{{plot_id}}');
var ENTITY_INDEX = {json.dumps(entity_index)};
var SERIES = {json.dumps({e: {"alpha": series[e]["alpha"]} for e in entities})};
var PALETTE = {json.dumps(PALETTE)};
var DEFAULT_ENTITIES = {json.dumps(default_entities)};

// Fixed-size color pool: checking a box borrows the next free color,
// unchecking returns it — so up to PALETTE.length simultaneously-visible
// countries always get distinct colors, and a re-checked country tends to
// get a fresh one rather than colors drifting as the active set changes.
var colorPool = PALETTE.slice(DEFAULT_ENTITIES.length).concat(PALETTE.slice(0, DEFAULT_ENTITIES.length));
var entityColor = {{}};
DEFAULT_ENTITIES.forEach(function (e, i) {{ entityColor[e] = PALETTE[i % PALETTE.length]; }});

function hexToRgb(hex) {{
    var n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}}

// Same alpha-by-year ramp as the Python-side defaults (see alpha_ramp()) —
// markers fade toward MIN_ALPHA for a country's oldest points, full opacity
// at its most recent; the connecting line stays a fixed, lower opacity so
// the graded markers read clearly against it.
function markerColors(entity, hex) {{
    var rgb = hexToRgb(hex);
    return SERIES[entity].alpha.map(function (a) {{ return 'rgba(' + rgb.join(',') + ',' + a + ')'; }});
}}

function lineColor(hex) {{
    var rgb = hexToRgb(hex);
    return 'rgba(' + rgb.join(',') + ',0.5)';
}}

function setChecked(entity, checked) {{
    var idx = ENTITY_INDEX[entity];
    if (idx === undefined) return;
    if (checked) {{
        var color = entityColor[entity] || colorPool.shift() || PALETTE[idx % PALETTE.length];
        entityColor[entity] = color;
        Plotly.restyle(gd, {{visible: true, 'line.color': lineColor(color), 'marker.color': [markerColors(entity, color)]}}, [idx]);
    }} else {{
        if (entityColor[entity]) {{
            colorPool.push(entityColor[entity]);
            delete entityColor[entity];
        }}
        Plotly.restyle(gd, {{visible: false}}, [idx]);
    }}
}}

document.getElementById('country-list').addEventListener('change', function (ev) {{
    if (ev.target.type !== 'checkbox') return;
    setChecked(ev.target.value, ev.target.checked);
}});

document.getElementById('country-search').addEventListener('input', function (ev) {{
    var q = ev.target.value.trim().toLowerCase();
    document.querySelectorAll('#country-list li').forEach(function (li) {{
        li.style.display = li.dataset.name.indexOf(q) === -1 ? 'none' : '';
    }});
}});

// Y-axis range filter: same idea as the x rangeslider below the chart (a
// single track, dragging either edge narrows the visible range) but built
// from two overlaid vertical <input type=range> thumbs on one rail, since
// Plotly's rangeslider is x-only — no y-axis equivalent exists to reuse
// directly. The shaded #y-slider-fill between the thumbs mirrors the
// shaded window the x rangeslider shows.
//
// #y-slider-panel is written into the HTML just before the closing body
// tag, after this <script> tag (so it lands in grid column 3, after the
// plot div in column 2 — see the grid-template-columns rule) — deferred to
// DOMContentLoaded so its elements exist by the time this runs.
document.addEventListener('DOMContentLoaded', function () {{
    var yMaxSlider = document.getElementById('y-max-slider');
    var yMinSlider = document.getElementById('y-min-slider');
    var yFill = document.getElementById('y-slider-fill');
    var Y_MIN = parseFloat(yMaxSlider.min), Y_MAX = parseFloat(yMaxSlider.max);
    var MIN_GAP = (Y_MAX - Y_MIN) * 0.01;

    function fracFromTop(v) {{ return 1 - (v - Y_MIN) / (Y_MAX - Y_MIN); }}

    function applyYRange() {{
        var lo = parseFloat(yMinSlider.value), hi = parseFloat(yMaxSlider.value);
        if (hi - lo < MIN_GAP) {{
            if (document.activeElement === yMinSlider) lo = hi - MIN_GAP; else hi = lo + MIN_GAP;
            yMinSlider.value = lo; yMaxSlider.value = hi;
        }}
        yFill.style.top = (fracFromTop(hi) * 100) + '%';
        yFill.style.bottom = ((1 - fracFromTop(lo)) * 100) + '%';
        Plotly.relayout(gd, {{'yaxis.range': [lo, hi], 'yaxis.autorange': false}});
    }}

    yMaxSlider.addEventListener('input', applyYRange);
    yMinSlider.addEventListener('input', applyYRange);
    applyYRange();
}});
"""

fig.write_html(
    OUTPUT,
    include_plotlyjs="cdn",
    full_html=True,
    post_script=post_script,
    default_width="100%",
    default_height="100%",
    config={"responsive": True},
)

html = open(OUTPUT, "r", encoding="utf-8").read()
html = html.replace(
    "<head>",
    "<head>\n<style>"
    "html, body { height: 100%; margin: 0; }"
    "body { display: grid; grid-template-columns: 220px 1fr 28px; height: 100%; font-family: sans-serif; }"
    "#sidebar { display: flex; flex-direction: column; border-right: 1px solid #ddd; min-height: 0; }"
    "#country-search { margin: 8px; padding: 4px 6px; font-size: 13px; }"
    "#country-list { list-style: none; margin: 0; padding: 0 8px 8px; overflow-y: auto; flex: 1; min-height: 0; }"
    "#country-list li { font-size: 13px; padding: 2px 0; }"
    "#country-list label { display: flex; gap: 6px; align-items: center; cursor: pointer; }"
    "#y-slider-panel { display: flex; justify-content: center; border-left: 1px solid #ddd; padding: 10px 0; }"
    "#y-slider-track { position: relative; width: 24px; flex: 1; }"
    "#y-slider-rail { position: absolute; left: 10px; top: 0; bottom: 0; width: 4px; background: #eee; border-radius: 2px; }"
    "#y-slider-fill { position: absolute; left: 10px; width: 4px; background: #3366cc; opacity: 0.4; border-radius: 2px; }"
    "#y-slider-track input[type=range] { -webkit-appearance: none; appearance: none;"
    " position: absolute; left: 0; top: 0; width: 24px; height: 100%; margin: 0;"
    " writing-mode: vertical-lr; direction: rtl; background: transparent; pointer-events: none; }"
    "#y-slider-track input[type=range]::-webkit-slider-runnable-track { background: transparent; }"
    "#y-slider-track input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; pointer-events: auto;"
    " width: 24px; height: 10px; background: #3366cc; border-radius: 2px; cursor: ns-resize; }"
    "#y-slider-track input[type=range]::-moz-range-track { background: transparent; }"
    "#y-slider-track input[type=range]::-moz-range-thumb { pointer-events: auto; width: 24px; height: 10px;"
    " background: #3366cc; border-radius: 2px; cursor: ns-resize; border: none; }"
    "</style>",
    1,
)
items = "\n".join(
    f'<li data-name="{e.lower()}"><label><input type="checkbox" value="{e}"'
    f'{" checked" if e in default_entities else ""}> {e}</label></li>'
    for e in entities
)
sidebar_html = (
    '<div id="sidebar">'
    '<input id="country-search" type="text" placeholder="Search countries...">'
    f'<ul id="country-list">{items}</ul>'
    "</div>"
)
y_slider_html = (
    '<div id="y-slider-panel">'
    '<div id="y-slider-track">'
    '<div id="y-slider-rail"></div>'
    '<div id="y-slider-fill"></div>'
    f'<input id="y-max-slider" type="range" min="{Y_SLIDER_MIN}" max="{Y_SLIDER_MAX}" step="0.05" value="{DEFAULT_YLIM[1]:.3f}">'
    f'<input id="y-min-slider" type="range" min="{Y_SLIDER_MIN}" max="{Y_SLIDER_MAX}" step="0.05" value="{DEFAULT_YLIM[0]:.3f}">'
    "</div>"
    "</div>"
)
# Sidebar goes right after <body> (before the plot div, so it lands in grid
# column 1 by source order) and the y-slider panel right before </body> (so
# it lands in column 3, after the plot div's column 2) — see the
# grid-template-columns rule above. Both are referenced by post_script,
# which runs synchronously as part of the plot div's own <script> tag
# in between the two, so its y-slider block is deferred to DOMContentLoaded
# (see post_script) to run after the later one has actually been parsed.
html = html.replace("<body>", f"<body>\n{sidebar_html}", 1)
html = html.replace("</body>", f"{y_slider_html}\n</body>", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(entities)} entities, {len(default_entities)} shown by default)")
