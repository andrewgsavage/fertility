"""TFR vs year, same threshold-based selection as tfr_threshold_derivative.py
(every major country whose TFR has ever dropped below the chosen threshold,
plotted from the year it first crosses below through to its most recent
year — recoveries back above are not clipped) but the plain, direct chart:
x = year, y = TFR, with a horizontal reference line at the threshold itself
so it's visually obvious every curve dips under it somewhere.

See tfr_threshold_derivative.py for the shared design notes (the JS-side
slicing, the alpha-by-year fade, and the population/ISO3 "major countries"
filter).
"""

import json
import re

import pandas as pd
import plotly.graph_objects as go

INPUT = "data/children-born-per-woman.csv"
POPULATION_INPUT = "data/population.csv"
OUTPUT = "outputs/tfr_threshold_year.html"

DEFAULT_THRESHOLD = 1.4
THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP = 1.0, 6.0, 0.1
DEFAULT_YLIM = [0.5, 2.5]

BASE_COLOR = "#3366cc"
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

all_years = [v for e in entities for v in series[e]["years"]]
X_SLIDER_MIN, X_SLIDER_MAX = min(all_years), max(all_years)
DEFAULT_XLIM = [1980, X_SLIDER_MAX]

fig = go.Figure(
    data=[
        go.Scatter(
            x=[], y=[], customdata=[],
            mode="lines",
            line=dict(width=1, color=LINE_COLOR),
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
    yaxis=dict(title="TFR", range=DEFAULT_YLIM, autorange=False),
    shapes=[dict(
        type="line", xref="paper", x0=0, x1=1, yref="y",
        y0=DEFAULT_THRESHOLD, y1=DEFAULT_THRESHOLD,
        line=dict(color="#999", width=1, dash="dot"),
    )],
    annotations=[dict(
        xref="paper", x=0, xanchor="left",
        yref="y", y=DEFAULT_THRESHOLD, yshift=8, yanchor="bottom",
        text=f"TFR = {DEFAULT_THRESHOLD:.2f}", showarrow=False,
        font=dict(size=11, color="#999"),
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
// would be redundant. Line just uses a fixed, slightly-transparent color
// so overlapping curves stay legible.
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
    // The reference line and its label track the slider itself, not just
    // the initial DEFAULT_THRESHOLD baked into the figure above.
    Plotly.relayout(gd, {{
        'shapes[0].y0': threshold, 'shapes[0].y1': threshold,
        'annotations[0].y': threshold,
        'annotations[0].text': 'TFR = ' + threshold.toFixed(2),
    }});
    var countEl = document.getElementById('match-count');
    if (countEl) countEl.textContent = matched;
    clearSelection();
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

// Click a line to highlight it (dim the rest); click it again, or change
// the threshold, to clear the selection.
var selectedIdx = null;

function clearSelection() {{
    selectedIdx = null;
    Plotly.restyle(gd, {{
        'line.width': ENTITIES.map(function () {{ return 1; }}),
        opacity: ENTITIES.map(function () {{ return 1; }}),
    }}, ENTITIES.map(function (_, i) {{ return i; }}));
}}

gd.on('plotly_click', function (eventData) {{
    if (!eventData.points || !eventData.points.length) return;
    var idx = eventData.points[0].curveNumber;
    selectedIdx = (selectedIdx === idx) ? null : idx;
    Plotly.restyle(gd, {{
        'line.width': ENTITIES.map(function (_, i) {{ return i === selectedIdx ? 2.5 : 1; }}),
        opacity: ENTITIES.map(function (_, i) {{ return selectedIdx === null || i === selectedIdx ? 1 : 0.15; }}),
    }}, ENTITIES.map(function (_, i) {{ return i; }}));
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
    "body { display: flex; flex-direction: column; height: 100%; font-family: sans-serif; }"
    "#threshold-panel { display: flex; align-items: center; gap: 14px; padding: 10px 14px; border-bottom: 1px solid #ddd; font-size: 13px; }"
    "#threshold-panel label { font-weight: 600; white-space: nowrap; }"
    "#threshold-slider { width: 220px; }"
    "#threshold-value { font-size: 18px; font-weight: 600; color: #3366cc; min-width: 3ch; }"
    "#match-count-wrap { color: #666; font-size: 12px; line-height: 1.4; }"
    "#match-count { font-weight: 600; color: #333; }"
    "body > div:not(#threshold-panel) { flex: 1; min-height: 0; }"
    "</style>",
    1,
)

threshold_panel_html = (
    '<div id="threshold-panel">'
    '<label for="threshold-slider">TFR threshold</label>'
    f'<input id="threshold-slider" type="range" min="{THRESHOLD_MIN}" max="{THRESHOLD_MAX}" step="{THRESHOLD_STEP}" value="{DEFAULT_THRESHOLD}">'
    f'<div id="threshold-value">{DEFAULT_THRESHOLD:.2f}</div>'
    '<div id="match-count-wrap"><span id="match-count"></span> countries have dropped below this TFR.</div>'
    "</div>"
)
html = html.replace("<body>", f"<body>\n{threshold_panel_html}", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(entities)} entities)")
