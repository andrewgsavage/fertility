"""TFR vs year, same threshold-based selection as tfr_threshold_derivative.py
(every major country whose TFR has ever dropped below the chosen threshold,
plotted from the year it first crosses below through to its most recent
year — recoveries back above are not clipped) but the plain, direct chart:
x = year, y = TFR, with a horizontal reference line at the threshold itself
so it's visually obvious every curve dips under it somewhere.

See tfr_threshold_derivative.py for the shared design notes (the JS-side
slicing, the alpha-by-year fade, the population/ISO3 "major countries"
filter, and why the y-range control is a custom dual-thumb slider rather
than a second native Plotly rangeslider).
"""

import json
import math
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go

INPUT = "data/children-born-per-woman.csv"
POPULATION_INPUT = "data/population.csv"
OUTPUT = "outputs/tfr_threshold_year.html"

DEFAULT_THRESHOLD = 2.1  # replacement rate
THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP = 1.0, 6.0, 0.1

BASE_COLOR = "#3366cc"
MARKER_COLOR = "rgba(51,102,204,0.6)"
LINE_COLOR = "rgba(51,102,204,0.4)"

MIN_POPULATION = 1_000_000
ISO3_RE = re.compile(r"^[A-Z]{3}$")

df = pd.read_csv(INPUT).sort_values(["entity", "year"])

series = {}
for entity, rows in df.groupby("entity"):
    years = rows["year"].to_numpy()
    tfr = rows["fertility_rate_hist"].to_numpy()
    series[entity] = {"years": years.tolist(), "tfr": tfr.tolist()}

pop_df = pd.read_csv(POPULATION_INPUT).sort_values(["entity", "year"])
latest_pop = pop_df.groupby("entity").last()
major_entities = {
    entity
    for entity, row in latest_pop.iterrows()
    if isinstance(row["code"], str) and ISO3_RE.match(row["code"]) and row["population_historical"] > MIN_POPULATION
}

entities = sorted(e for e in series if e in major_entities)


def slice_from_threshold(s, threshold):
    tfr = s["tfr"]
    for i, v in enumerate(tfr):
        if v < threshold:
            return s["years"][i:], s["tfr"][i:]
    return None


matched_years, matched_tfr = [], []
for e in entities:
    sliced = slice_from_threshold(series[e], DEFAULT_THRESHOLD)
    if sliced is None:
        continue
    years_s, tfr_s = sliced
    matched_years.extend(years_s)
    matched_tfr.extend(tfr_s)


def padded_percentile_range(values, lo_pct=1, hi_pct=99, pad_frac=0.1):
    lo, hi = np.percentile(values, lo_pct), np.percentile(values, hi_pct)
    pad = (hi - lo) * pad_frac
    return [lo - pad, hi + pad]


DEFAULT_XLIM = padded_percentile_range(matched_years)
DEFAULT_YLIM = [0, padded_percentile_range(matched_tfr)[1]]  # TFR floor at 0 reads more naturally than a padded negative

all_years = [v for e in entities for v in series[e]["years"]]
all_tfr = [v for e in entities for v in series[e]["tfr"]]
X_SLIDER_MIN, X_SLIDER_MAX = min(all_years), max(all_years)
Y_SLIDER_MIN, Y_SLIDER_MAX = 0, math.ceil(max(all_tfr) * 10) / 10

fig = go.Figure(
    data=[
        go.Scatter(
            x=[], y=[], customdata=[],
            mode="lines+markers",
            line=dict(width=1, color=LINE_COLOR),
            marker=dict(size=3, color=MARKER_COLOR),
            name=entity,
            visible=False,
            hovertemplate=f"<b>{entity}</b><br>Year %{{x}}<br>TFR %{{y:.3f}}<extra></extra>",
        )
        for entity in entities
    ]
)
fig.update_layout(
    template="plotly_white",
    autosize=True,
    showlegend=False,
    margin=dict(t=20, r=20, l=60, b=40),
    xaxis=dict(
        title="Year",
        range=DEFAULT_XLIM, autorange=False,
        rangeslider=dict(visible=True, thickness=0.08, range=[X_SLIDER_MIN, X_SLIDER_MAX]),
    ),
    yaxis=dict(title="TFR (children per woman)", range=DEFAULT_YLIM, autorange=False),
    shapes=[dict(
        type="line", xref="paper", x0=0, x1=1, yref="y",
        y0=DEFAULT_THRESHOLD, y1=DEFAULT_THRESHOLD,
        line=dict(color="#999", width=1, dash="dot"),
    )],
)

post_script = f"""
var gd = document.getElementById('{{plot_id}}');
var ENTITIES = {json.dumps(entities)};
var SERIES = {json.dumps({e: series[e] for e in entities})};

function sliceForThreshold(entity, threshold) {{
    var s = SERIES[entity];
    var idx = -1;
    for (var i = 0; i < s.tfr.length; i++) {{
        if (s.tfr[i] < threshold) {{ idx = i; break; }}
    }}
    if (idx === -1) return null;
    return {{years: s.years.slice(idx), tfr: s.tfr.slice(idx)}};
}}

// No alpha-by-year fade here (unlike the derivative chart) — year is
// already the x-axis, so recency reads directly off position and a fade
// would be redundant. Marker/line just use a fixed, slightly-transparent
// color so overlapping curves stay legible.
function applyThreshold(threshold) {{
    var xs = [], ys = [], customdatas = [], visibles = [];
    var matched = 0;
    ENTITIES.forEach(function (entity) {{
        var sliced = sliceForThreshold(entity, threshold);
        if (sliced) {{
            matched++;
            xs.push(sliced.years);
            ys.push(sliced.tfr);
            customdatas.push(sliced.years);
            visibles.push(true);
        }} else {{
            xs.push([]); ys.push([]); customdatas.push([]);
            visibles.push(false);
        }}
    }});
    Plotly.restyle(gd, {{
        x: xs, y: ys, customdata: customdatas, visible: visibles,
    }}, ENTITIES.map(function (_, i) {{ return i; }}));
    // The reference line tracks the slider itself, not just the initial
    // DEFAULT_THRESHOLD baked into the figure above.
    Plotly.relayout(gd, {{'shapes[0].y0': threshold, 'shapes[0].y1': threshold}});
    var countEl = document.getElementById('match-count');
    if (countEl) countEl.textContent = matched;
}}

var thresholdSlider = document.getElementById('threshold-slider');
var thresholdValue = document.getElementById('threshold-value');

function onThresholdInput() {{
    var t = parseFloat(thresholdSlider.value);
    thresholdValue.textContent = t.toFixed(2);
    applyThreshold(t);
}}

thresholdSlider.addEventListener('input', onThresholdInput);
onThresholdInput();

// Y-axis (TFR) range filter — same custom dual-thumb control as the other
// OWID pages; see tfr_derivative.py's post_script for the full rationale.
// #y-slider-panel is written just before the closing body tag, after this
// <script> tag, so it's deferred to DOMContentLoaded.
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
    "#threshold-panel { display: flex; flex-direction: column; gap: 8px; padding: 14px; border-right: 1px solid #ddd; font-size: 13px; }"
    "#threshold-panel label { font-weight: 600; }"
    "#threshold-value { font-size: 24px; font-weight: 600; text-align: center; color: #3366cc; }"
    "#threshold-slider { width: 100%; }"
    "#match-count-wrap { color: #666; font-size: 12px; line-height: 1.4; }"
    "#match-count { font-weight: 600; color: #333; }"
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

threshold_panel_html = (
    '<div id="threshold-panel">'
    '<label for="threshold-slider">TFR threshold</label>'
    f'<input id="threshold-slider" type="range" min="{THRESHOLD_MIN}" max="{THRESHOLD_MAX}" step="{THRESHOLD_STEP}" value="{DEFAULT_THRESHOLD}">'
    f'<div id="threshold-value">{DEFAULT_THRESHOLD:.2f}</div>'
    '<div id="match-count-wrap"><span id="match-count"></span> countries have dropped below this TFR at some point — each plotted from the year it first crosses below, to its most recent year. The dotted line marks the threshold itself.</div>'
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
html = html.replace("<body>", f"<body>\n{threshold_panel_html}", 1)
html = html.replace("</body>", f"{y_slider_html}\n</body>", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(entities)} entities)")
