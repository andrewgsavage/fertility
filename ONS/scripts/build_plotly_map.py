import json

import plotly.graph_objects as go

from metrics import (
    DIV_COLORSCALE,
    DIV_RANGE,
    DIVERGING_METRICS,
    METRIC_LABELS,
    METRIC_ORDER,
    REL_METRIC_ORDER,
    SEQ_COLORSCALE,
    dropdown_buttons,
    fmt_value,
)

GEOJSON_IN = "outputs/lad_boundaries_simplified.geojson"
FERTILITY_IN = "outputs/fertility_by_lad.json"
OUTPUT = "outputs/map_plotly.html"

DEFAULT_METRIC = "asfr_25_29_rel2013"


def geometry_bounds(geometries):
    """[west, south, east, north] lon/lat bounding box across geometries."""
    lons, lats = [], []

    def walk(coords, depth):
        if depth == 1:
            lons.append(coords[0])
            lats.append(coords[1])
        else:
            for c in coords:
                walk(c, depth - 1)

    for geom in geometries:
        depth = 3 if geom["type"] == "Polygon" else 4
        walk(geom["coordinates"], depth)
    return min(lons), min(lats), max(lons), max(lats)


with open(GEOJSON_IN, "r", encoding="utf-8") as f:
    geojson = json.load(f)

with open(FERTILITY_IN, "r", encoding="utf-8") as f:
    fertility = json.load(f)

years = fertility["years"]
lad_names = fertility["lad_names"]
data = fertility["data"]
codes = [feat["properties"]["code"] for feat in geojson["features"]]

# metric_frames[metric] = list of {name, data:[{z, text}]} per year, in the
# shape Plotly.addFrames() expects. metric_meta[metric] = colorscale/range/
# title for that metric's shared coloraxis, applied via Plotly.relayout().
metric_frames = {}
metric_meta = {}

for metric in METRIC_ORDER + REL_METRIC_ORDER:
    frames = []
    pooled = []
    for year in years:
        year_rows = data[year]
        z, text = [], []
        for code in codes:
            record = year_rows.get(code)
            value = record.get(metric) if record else None
            z.append(value)
            text.append(f"<b>{fmt_value(value, metric)}</b><br>{lad_names.get(code, code)}")
            if value is not None:
                pooled.append(value)
        frames.append({"name": year, "data": [{"z": z, "text": text}]})
    metric_frames[metric] = frames

    if metric in DIVERGING_METRICS:
        metric_meta[metric] = {
            "colorscale": DIV_COLORSCALE,
            "cmin": -DIV_RANGE,
            "cmax": DIV_RANGE,
            "title": METRIC_LABELS[metric],
        }
    else:
        pooled.sort()
        metric_meta[metric] = {
            "colorscale": SEQ_COLORSCALE,
            "cmin": pooled[0],
            "cmax": pooled[-1],
            "title": METRIC_LABELS[metric],
        }

initial_frame = metric_frames[DEFAULT_METRIC][-1]  # most recent year
initial_meta = metric_meta[DEFAULT_METRIC]
metric_buttons, metric_active = dropdown_buttons(DEFAULT_METRIC)

# go.Choropleth's "geo" subplot always reserves a fixed ~2:1 aspect-ratio
# box for itself (a leftover of its world-map defaults: 360deg lon / 180deg
# lat), regardless of the figure's actual shape or fitbounds — confirmed by
# measuring the rendered geolayer at several container sizes and finding it
# locked at exactly 2.0 every time. go.Choroplethmap (MapLibre-based) has no
# such constraint and genuinely fills whatever box it's given.
data_geoms = [feat["geometry"] for feat in geojson["features"] if feat["properties"]["code"] in lad_names]
west, south, east, north = geometry_bounds(data_geoms)
pad_lon = (east - west) * 0.03
pad_lat = (north - south) * 0.03

fig = go.Figure(
    data=[
        go.Choroplethmap(
            locations=codes,
            z=initial_frame["data"][0]["z"],
            text=initial_frame["data"][0]["text"],
            hoverinfo="text",
            geojson=geojson,
            featureidkey="properties.code",
            coloraxis="coloraxis",
            marker={"opacity": 0.85, "line": {"width": 0.5, "color": "#666"}},
        )
    ]
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    map={
        "style": "white-bg",
        "bounds": {"west": west - pad_lon, "east": east + pad_lon, "south": south - pad_lat, "north": north + pad_lat},
    },
)
fig.update_layout(
    title={
        "text": "England & Wales fertility rates by local authority",
        "x": 0.5,
        "xanchor": "center",
        "y": 0.99,
        "yanchor": "top",
    },
    margin={"r": 10, "t": 130, "l": 10, "b": 10},
    autosize=True,
    coloraxis={
        "colorscale": initial_meta["colorscale"],
        "cmin": initial_meta["cmin"],
        "cmax": initial_meta["cmax"],
        "colorbar": {"title": {"text": initial_meta["title"]}},
    },
    sliders=[
        {
            "active": len(years) - 1,
            "currentvalue": {"prefix": "Year: "},
            "steps": [
                {"label": year, "method": "animate", "args": [[year], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}}]}
                for year in years
            ],
        }
    ],
    updatemenus=[
        {
            "buttons": metric_buttons,
            "direction": "down",
            "x": 0,
            "xanchor": "left",
            "y": 0.90,
            "yanchor": "top",
            "showactive": True,
            "active": metric_active,
        }
    ],
)

# Only the default metric's frames are wired into the figure at save time;
# the rest travel as embedded JS data and get swapped in on demand (see
# post_script) — this keeps Plotly's own frame/slider machinery in charge
# of year animation while a small custom handler keeps the metric dropdown
# in sync with it, since Plotly's declarative controls can't reference each
# other's live state. Plain dicts don't carry trace-type context for
# validation, so wrap these (Python-side only — the JSON embedded for JS
# stays as plain dicts) in go.Frame/go.Choroplethmap explicitly.
fig.frames = [
    go.Frame(name=frame["name"], data=[go.Choroplethmap(z=frame["data"][0]["z"], text=frame["data"][0]["text"])])
    for frame in metric_frames[DEFAULT_METRIC]
]

post_script = f"""
var gd = document.getElementById('{{plot_id}}');
var METRIC_FRAMES = {json.dumps(metric_frames)};
var METRIC_META = {json.dumps(metric_meta)};

function applyMetric(metric) {{
    if (!metric || !METRIC_FRAMES[metric]) return;
    var meta = METRIC_META[metric];
    var slider = gd.layout.sliders[0];
    var year = slider.steps[slider.active].label;
    Plotly.addFrames(gd, METRIC_FRAMES[metric]);
    Plotly.relayout(gd, {{
        'coloraxis.colorscale': meta.colorscale,
        'coloraxis.cmin': meta.cmin,
        'coloraxis.cmax': meta.cmax,
        'coloraxis.colorbar.title.text': meta.title,
    }}).then(function () {{
        Plotly.animate(gd, [year], {{frame: {{duration: 0, redraw: true}}, mode: 'immediate', transition: {{duration: 0}}}});
    }});
}}

gd.on('plotly_buttonclicked', function (ev) {{
    if (!ev.button || !ev.button.args || ev.button.args[0] === null) return;
    applyMetric(ev.button.args[0]);
}});

// The slider's declared "active" index alone doesn't reliably sync the
// actually-displayed frame on first paint — force it explicitly so the
// map opens on the latest year with no visible transition.
Plotly.animate(gd, ['{years[-1]}'], {{frame: {{duration: 0, redraw: true}}, mode: 'immediate', transition: {{duration: 0}}}});
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

# write_html's own template doesn't stretch <html>/<body> to fill the
# iframe — without that, the plot div's height:100% resolves against an
# auto-height body (i.e. 0) instead of the actual iframe viewport. The
# containing page locks the iframe's box to a fixed aspect ratio (see
# docs/uk/fertility-map.md); this makes the plot itself fill that box
# and redraw responsively as it's resized.
html = open(OUTPUT, "r", encoding="utf-8").read()
html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(codes)} LADs, {len(years)} years, {len(metric_frames)} metrics)")
