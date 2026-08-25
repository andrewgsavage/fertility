"""d(TFR)/d(year) vs TFR, same idea as tfr_derivative.py, but the curves
shown are chosen by a TFR-threshold filter instead of a manual country
picker: every entity whose TFR has ever dropped below the chosen threshold
is plotted from the year it first crosses below that threshold through to
its most recent year — including any later recovery back above the
threshold, which is not clipped (only the *start* point is threshold-based).

All 261 entities are pre-added as empty, hidden traces; the threshold
slider re-slices SERIES in JS and restyles every trace's x/y/visible in one
batched call (see applyThreshold in post_script) — there's no fixed default
selection to bake into the initial figure the way tfr_derivative.py does,
since which entities qualify depends entirely on the slider's live value.
"""

import json
import math
import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go

INPUT = "data/children-born-per-woman.csv"
POPULATION_INPUT = "data/population.csv"
OUTPUT = "outputs/tfr_threshold_derivative.html"

DEFAULT_THRESHOLD = 2.1  # replacement rate
THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP = 1.0, 6.0, 0.1

MIN_ALPHA = 0.15
BASE_COLOR = "#3366cc"

MIN_POPULATION = 1_000_000
ISO3_RE = re.compile(r"^[A-Z]{3}$")

df = pd.read_csv(INPUT).sort_values(["entity", "year"])

# entity -> {years, tfr, deriv} (full history — the threshold slider slices
# this in JS, so unlike tfr_derivative.py nothing here is pre-filtered).
series = {}
for entity, rows in df.groupby("entity"):
    years = rows["year"].to_numpy()
    tfr = rows["fertility_rate_hist"].to_numpy()
    deriv = np.gradient(tfr, years)
    series[entity] = {"years": years.tolist(), "tfr": tfr.tolist(), "deriv": [round(v, 4) for v in deriv]}

# "Major countries" only: OWID's continent/income-group/former-state
# aggregates (World, Africa, High-income countries, USSR, ...) carry
# non-ISO3 codes (blank, or "OWID_"-prefixed) in both datasets, so a plain
# ISO3-code check filters those out; population > MIN_POPULATION on top of
# that drops small real states (Andorra, Tuvalu, ...) — see the "chrome"
# thread for why this page needs it (261 unfiltered entities was unreadable).
pop_df = pd.read_csv(POPULATION_INPUT).sort_values(["entity", "year"])
latest_pop = pop_df.groupby("entity").last()
major_entities = {
    entity
    for entity, row in latest_pop.iterrows()
    if isinstance(row["code"], str) and ISO3_RE.match(row["code"]) and row["population_historical"] > MIN_POPULATION
}

entities = sorted(e for e in series if e in major_entities)


def slice_from_threshold(s, threshold):
    """None if tfr never drops below threshold; else the (years, tfr, deriv)
    sub-series from the first year it does, through to the last year of
    data — same rule the JS sliceForThreshold() applies on every slider
    move, mirrored here only to size the chart's initial default view."""
    tfr = s["tfr"]
    for i, v in enumerate(tfr):
        if v < threshold:
            return s["years"][i:], s["tfr"][i:], s["deriv"][i:]
    return None


# Default view: percentile-clipped (not min/max) so a handful of extreme
# single-year swings (famine/war-year TFR crashes) don't blow out the
# axes — matched further out is still reachable via the sliders.
matched_tfr, matched_deriv = [], []
for e in entities:
    sliced = slice_from_threshold(series[e], DEFAULT_THRESHOLD)
    if sliced is None:
        continue
    _, tfr_s, deriv_s = sliced
    matched_tfr.extend(tfr_s)
    matched_deriv.extend(deriv_s)


def padded_percentile_range(values, lo_pct=1, hi_pct=99, pad_frac=0.1):
    lo, hi = np.percentile(values, lo_pct), np.percentile(values, hi_pct)
    pad = (hi - lo) * pad_frac
    return [lo - pad, hi + pad]


DEFAULT_XLIM = padded_percentile_range(matched_tfr)
DEFAULT_YLIM = padded_percentile_range(matched_deriv)

# Slider/rangeslider bounds: the full extent across every entity, fixed so
# they don't jitter as the threshold restyles trace data underneath them.
all_tfr = [v for e in entities for v in series[e]["tfr"]]
all_derivs = [v for e in entities for v in series[e]["deriv"]]
X_SLIDER_MIN, X_SLIDER_MAX = math.floor(min(all_tfr) * 10) / 10, math.ceil(max(all_tfr) * 10) / 10
Y_SLIDER_MIN, Y_SLIDER_MAX = math.floor(min(all_derivs) * 10) / 10, math.ceil(max(all_derivs) * 10) / 10

fig = go.Figure(
    data=[
        go.Scatter(
            x=[], y=[], customdata=[],
            mode="lines+markers",
            line=dict(width=1, color=BASE_COLOR),
            marker=dict(size=3, color=BASE_COLOR),
            name=entity,
            visible=False,
            hovertemplate=f"<b>{entity}</b><br>Year %{{customdata}}<br>TFR %{{x:.3f}}<br>%{{y:.3f}} / yr<extra></extra>",
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
        title="TFR (children per woman)",
        range=DEFAULT_XLIM, autorange=False,
        rangeslider=dict(visible=True, thickness=0.08, range=[X_SLIDER_MIN, X_SLIDER_MAX]),
    ),
    yaxis=dict(title="Change in TFR per year (children per woman / yr)", range=DEFAULT_YLIM, autorange=False),
    shapes=[dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=0, y1=0, line=dict(color="#999", width=1, dash="dot"))],
)

post_script = f"""
var gd = document.getElementById('{{plot_id}}');
var ENTITIES = {json.dumps(entities)};
var SERIES = {json.dumps({e: series[e] for e in entities})};
var BASE_COLOR = {json.dumps(BASE_COLOR)};
var MIN_ALPHA = {MIN_ALPHA};

function hexToRgb(hex) {{
    var n = parseInt(hex.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}}
var BASE_RGB = hexToRgb(BASE_COLOR);
function rgba(alpha) {{ return 'rgba(' + BASE_RGB.join(',') + ',' + alpha.toFixed(3) + ')'; }}

// First index where tfr drops below `threshold`; null if it never does.
function sliceForThreshold(entity, threshold) {{
    var s = SERIES[entity];
    var idx = -1;
    for (var i = 0; i < s.tfr.length; i++) {{
        if (s.tfr[i] < threshold) {{ idx = i; break; }}
    }}
    if (idx === -1) return null;
    return {{years: s.years.slice(idx), tfr: s.tfr.slice(idx), deriv: s.deriv.slice(idx)}};
}}

// Same "older = lighter" ramp as the country-picker chart, but keyed to
// each curve's own visible slice (crossing year = MIN_ALPHA, most recent =
// fully opaque) rather than its full history — so the fade is visible
// regardless of how far back the threshold crossing happened.
function alphaRamp(years) {{
    var y0 = years[0], y1 = years[years.length - 1], span = y1 - y0;
    return years.map(function (y) {{ return MIN_ALPHA + (1 - MIN_ALPHA) * (span ? (y - y0) / span : 1); }});
}}

function applyThreshold(threshold) {{
    var xs = [], ys = [], customdatas = [], visibles = [], markerColors = [], lineColors = [];
    var matched = 0;
    ENTITIES.forEach(function (entity) {{
        var sliced = sliceForThreshold(entity, threshold);
        if (sliced) {{
            matched++;
            xs.push(sliced.tfr);
            ys.push(sliced.deriv);
            customdatas.push(sliced.years);
            visibles.push(true);
            markerColors.push(alphaRamp(sliced.years).map(rgba));
            lineColors.push(rgba(0.45));
        }} else {{
            xs.push([]); ys.push([]); customdatas.push([]);
            visibles.push(false);
            markerColors.push(BASE_COLOR);
            lineColors.push(BASE_COLOR);
        }}
    }});
    Plotly.restyle(gd, {{
        x: xs, y: ys, customdata: customdatas, visible: visibles,
        'marker.color': markerColors, 'line.color': lineColors,
    }}, ENTITIES.map(function (_, i) {{ return i; }}));
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

// Y-axis range filter — identical control to the one on the country-picker
// chart (tfr_derivative.py); see that script's post_script for the full
// rationale. #y-slider-panel is written just before the closing body tag,
// after this <script> tag, so it's deferred to DOMContentLoaded.
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
    '<div id="match-count-wrap"><span id="match-count"></span> countries/regions have dropped below this TFR at some point — each plotted from the year it first crosses below, to its most recent year.</div>'
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
# Threshold panel goes right after <body> (before the plot div/script, so
# its elements exist for the synchronous onThresholdInput() call, and it
# lands in grid column 1 by source order); y-slider panel goes right before
# the closing body tag (column 3) — see tfr_derivative.py for why that one
# needs the DOMContentLoaded deferral in post_script.
html = html.replace("<body>", f"<body>\n{threshold_panel_html}", 1)
html = html.replace("</body>", f"{y_slider_html}\n</body>", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(entities)} entities)")
