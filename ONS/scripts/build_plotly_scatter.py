import json
import math

import plotly.graph_objects as go

from metrics import (
    ASFR_BASE_KEYS,
    DIV_COLORSCALE,
    DIV_RANGE,
    DIVERGING_METRICS,
    METRIC_LABELS,
    METRIC_ORDER,
    POPULATION_LABELS,
    POPULATION_ORDER,
    REL_METRIC_ORDER,
    SEQ_COLORSCALE,
    decimals_for,
    dropdown_buttons,
)

FERTILITY_IN = "outputs/fertility_by_lad.json"
POPULATION_IN = "outputs/population_by_lad.json"
HOUSING_IN = "outputs/housing_by_lad.json"
OUTPUT = "outputs/scatter_plotly.html"

HOUSING_LABELS = {
    "house_price": "Average house price",
    "affordability_ratio": "Housing affordability ratio",
}
HOUSING_ORDER = list(HOUSING_LABELS)

BASE_YEAR = "2013"
BASE_YEAR_ORDER = [f"{k}_{BASE_YEAR}" for k in ASFR_BASE_KEYS]
BASE_YEAR_LABELS = {f"{k}_{BASE_YEAR}": f"{METRIC_LABELS[k]} ({BASE_YEAR})" for k in ASFR_BASE_KEYS}

# "% change since 2013" and "(2013)" baseline groups for the housing
# metrics — same shape as REL_METRIC_ORDER/BASE_YEAR_ORDER above for ASFR,
# reading the housing_by_lad.json fields parse_housing_csv.py computes the
# same way parse_csv.py computes ASFR's rel2013 fields.
HOUSING_REL_ORDER = [f"{k}_rel2013" for k in HOUSING_ORDER]
HOUSING_REL_LABELS = {f"{k}_rel2013": f"{HOUSING_LABELS[k]} — change vs {BASE_YEAR}" for k in HOUSING_ORDER}
HOUSING_BASE_YEAR_ORDER = [f"{k}_{BASE_YEAR}" for k in HOUSING_ORDER]
HOUSING_BASE_YEAR_LABELS = {f"{k}_{BASE_YEAR}": f"{HOUSING_LABELS[k]} ({BASE_YEAR})" for k in HOUSING_ORDER}
DIVERGING_METRICS = DIVERGING_METRICS | set(HOUSING_REL_ORDER)

# Housing levels are heavily right-skewed (a handful of prime-London LADs
# sit far above the rest), which saturates a linear color scale — shown on
# a log scale instead so mid-range variation stays visible. The 2013
# baseline levels are just as skewed; the % change metrics aren't (they
# use the same fixed diverging range as ASFR's change-vs-2013 group).
LOG_COLOR_METRICS = set(HOUSING_ORDER) | set(HOUSING_BASE_YEAR_ORDER)

ALL_LABELS = {
    **METRIC_LABELS,
    **POPULATION_LABELS,
    **HOUSING_LABELS,
    **BASE_YEAR_LABELS,
    **HOUSING_REL_LABELS,
    **HOUSING_BASE_YEAR_LABELS,
}

DEFAULT_X = "mean_age_mother"
DEFAULT_Y = "tfr"
DEFAULT_COLOR = "crude_birth_rate"
DEFAULT_SIZE = "live_births"
MAX_MARKER_DIAMETER = 34

HOVER_YEARS = ["2013", "2024"]
HOVER_LABELS = {
    "tfr": "TFR",
    "mean_age_mother": "Mean age",
    "asfr_under18": "ASFR <18",
    "asfr_under20": "ASFR <20",
    "asfr_20_24": "ASFR 20-24",
    "asfr_25_29": "ASFR 25-29",
    "asfr_30_34": "ASFR 30-34",
    "asfr_35_39": "ASFR 35-39",
    "asfr_40_44": "ASFR 40-44",
    "asfr_45plus": "ASFR 45+",
    "live_births": "Live births",
    "pop_15_19": "Pop 15-19",
    "pop_20_24": "Pop 20-24",
    "pop_25_29": "Pop 25-29",
    "pop_30_34": "Pop 30-34",
    "pop_35_39": "Pop 35-39",
    "pop_40_44": "Pop 40-44",
    "pop_45_49": "Pop 45-49",
    "house_price": "House price",
    "affordability_ratio": "Afford rat.",
}
LABEL_WIDTH = 11
COL_WIDTH = 8


def pad_left(text, width):
    text = str(text)
    return "&nbsp;" * max(0, width - len(text)) + text


def pad_right(text, width):
    text = str(text)
    return text + "&nbsp;" * max(0, width - len(text))


def nice_log_ticks(lo, hi, count=5):
    """count evenly log-spaced tick values between lo and hi (both > 0),
    each rounded up to a "nice" 1/2/5 x 10^n number for readability."""
    log_lo, log_hi = math.log10(lo), math.log10(hi)
    ticks = []
    for i in range(count):
        raw = 10 ** (log_lo + (log_hi - log_lo) * i / (count - 1))
        exp = math.floor(math.log10(raw))
        nice = next((step * 10**exp for step in (1, 2, 5) if step * 10**exp >= raw), 10 ** (exp + 1))
        if not ticks or nice > ticks[-1]:
            ticks.append(nice)
    return ticks


def format_tick(metric, value):
    if metric == "house_price":
        return f"£{value:,.0f}"
    return f"{value:g}"


def hover_cell(metric, value):
    if value is None:
        return "n/a"
    if metric == "house_price":
        # Abbreviated (not the full comma-grouped number) so it fits the
        # hover table's fixed-width columns without crowding the adjacent
        # year's value.
        return f"£{value / 1e6:.2f}M" if value >= 1_000_000 else f"£{value / 1e3:.0f}k"
    if metric == "live_births" or metric.startswith("pop_"):
        return f"{value:,.0f}"
    return f"{value:.{decimals_for(metric)}f}"


def build_hover_table(name, year_data):
    """A monospace, &nbsp;-padded pseudo-table for the hover tooltip —
    Plotly hover labels render as SVG text, not real HTML, so a <table>
    isn't available; regular spaces also collapse in that rendering, hence
    the non-breaking spaces."""
    lines = [f"<b>{name}</b>", ""]
    lines.append(pad_right("", LABEL_WIDTH) + pad_left(HOVER_YEARS[0], COL_WIDTH) + pad_left(HOVER_YEARS[1], COL_WIDTH))
    for metric, label in HOVER_LABELS.items():
        cells = [hover_cell(metric, year_data[y].get(metric)) for y in HOVER_YEARS]
        lines.append(pad_right(label, LABEL_WIDTH) + "".join(pad_left(c, COL_WIDTH) for c in cells))
    return "<br>".join(lines)


def full_dropdown_buttons(default_metric):
    """Fertility (Levels + Change since 2013) buttons, plus ASFR-in-2013
    (the baseline level itself, not the % change), Female population, and
    Housing groups. Active index is resolved by searching for
    default_metric rather than hand-computed offsets."""
    fert_buttons, _ = dropdown_buttons()
    base_year_buttons = [{"label": f"— ASFR in {BASE_YEAR} —", "method": "skip", "args": [None]}] + [
        {"label": BASE_YEAR_LABELS[m], "method": "skip", "args": [m]} for m in BASE_YEAR_ORDER
    ]
    pop_buttons = [{"label": "— Female population —", "method": "skip", "args": [None]}] + [
        {"label": POPULATION_LABELS[m], "method": "skip", "args": [m]} for m in POPULATION_ORDER
    ]
    housing_buttons = [{"label": "— Housing —", "method": "skip", "args": [None]}] + [
        {"label": HOUSING_LABELS[m], "method": "skip", "args": [m]} for m in HOUSING_ORDER
    ]
    housing_rel_buttons = [{"label": f"— Housing change since {BASE_YEAR} —", "method": "skip", "args": [None]}] + [
        {"label": HOUSING_REL_LABELS[m], "method": "skip", "args": [m]} for m in HOUSING_REL_ORDER
    ]
    housing_base_year_buttons = [{"label": f"— Housing in {BASE_YEAR} —", "method": "skip", "args": [None]}] + [
        {"label": HOUSING_BASE_YEAR_LABELS[m], "method": "skip", "args": [m]} for m in HOUSING_BASE_YEAR_ORDER
    ]
    buttons = (
        fert_buttons
        + base_year_buttons
        + pop_buttons
        + housing_buttons
        + housing_rel_buttons
        + housing_base_year_buttons
    )
    active = next(i for i, b in enumerate(buttons) if b["args"][0] == default_metric)
    return buttons, active


with open(FERTILITY_IN, "r", encoding="utf-8") as f:
    fertility = json.load(f)
with open(POPULATION_IN, "r", encoding="utf-8") as f:
    population = json.load(f)
with open(HOUSING_IN, "r", encoding="utf-8") as f:
    housing = json.load(f)

year = fertility["years"][-1]
lad_names = fertility["lad_names"]
year_rows = fertility["data"][year]
population_year_rows = population["data"].get(year, {})
housing_year_rows = housing["data"].get(year, {})
# City of London has a tiny, atypical resident population (a few thousand
# vs a huge daytime/working population), which makes its rates extreme
# outliers that distort the chart's axis scaling. Isles of Scilly is
# excluded for the same reason (population in the low hundreds).
EXCLUDED_LADS = {"City of London", "Isles of Scilly"}
codes = [code for code in lad_names if code in year_rows and lad_names[code] not in EXCLUDED_LADS]
names = [lad_names[code] for code in codes]

# metric_values[metric] = [value, ...] aligned to `codes`, for swapping into
# x/y via Plotly.restyle. metric_meta[metric] = colorscale/range/title for
# that metric, used for color swaps, axis titles, and (via "title") the
# bubble-size label in the chart title.
metric_values = {}
metric_meta = {}

for metric in METRIC_ORDER + REL_METRIC_ORDER:
    values = [year_rows[code].get(metric) for code in codes]
    metric_values[metric] = values

    pooled = sorted(v for v in values if v is not None)
    if metric in DIVERGING_METRICS:
        metric_meta[metric] = {"colorscale": DIV_COLORSCALE, "cmin": -DIV_RANGE, "cmax": DIV_RANGE, "title": METRIC_LABELS[metric], "pct": True}
    else:
        metric_meta[metric] = {"colorscale": SEQ_COLORSCALE, "cmin": pooled[0], "cmax": pooled[-1], "title": METRIC_LABELS[metric], "pct": False}

for metric in POPULATION_ORDER:
    values = [population_year_rows.get(code, {}).get(metric) for code in codes]
    metric_values[metric] = values
    pooled = sorted(v for v in values if v is not None)
    metric_meta[metric] = {"colorscale": SEQ_COLORSCALE, "cmin": pooled[0], "cmax": pooled[-1], "title": POPULATION_LABELS[metric], "pct": False}

for metric in HOUSING_ORDER + HOUSING_REL_ORDER:
    values = [housing_year_rows.get(code, {}).get(metric) for code in codes]
    metric_values[metric] = values
    pooled = sorted(v for v in values if v is not None)
    if metric in DIVERGING_METRICS:
        metric_meta[metric] = {"colorscale": DIV_COLORSCALE, "cmin": -DIV_RANGE, "cmax": DIV_RANGE, "title": HOUSING_REL_LABELS[metric], "pct": True}
    else:
        metric_meta[metric] = {
            "colorscale": SEQ_COLORSCALE,
            "cmin": pooled[0],
            "cmax": pooled[-1],
            "title": HOUSING_LABELS[metric],
            "pct": False,
            "log_color": True,
        }

base_year_rows = fertility["data"].get(BASE_YEAR, {})
for base_key, metric in zip(ASFR_BASE_KEYS, BASE_YEAR_ORDER):
    values = [base_year_rows.get(code, {}).get(base_key) for code in codes]
    metric_values[metric] = values
    pooled = sorted(v for v in values if v is not None)
    metric_meta[metric] = {"colorscale": SEQ_COLORSCALE, "cmin": pooled[0], "cmax": pooled[-1], "title": BASE_YEAR_LABELS[metric], "pct": False}

housing_2013_rows = housing["data"].get(BASE_YEAR, {})
for housing_key, metric in zip(HOUSING_ORDER, HOUSING_BASE_YEAR_ORDER):
    values = [housing_2013_rows.get(code, {}).get(housing_key) for code in codes]
    metric_values[metric] = values
    pooled = sorted(v for v in values if v is not None)
    metric_meta[metric] = {
        "colorscale": SEQ_COLORSCALE,
        "cmin": pooled[0],
        "cmax": pooled[-1],
        "title": HOUSING_BASE_YEAR_LABELS[metric],
        "pct": False,
        "log_color": True,
    }

# size_data[metric] = {sizes, sizeref} for every selectable metric — marker
# size can't be negative or null, so this clamps/substitutes those to 0
# (relevant for "change vs 2013" metrics, which can be negative).
size_data = {}
for metric, values in metric_values.items():
    sizes_m = [max(v, 0) if v is not None else 0 for v in values]
    max_v = max(sizes_m, default=0)
    size_data[metric] = {"sizes": sizes_m, "sizeref": (2 * max_v / (MAX_MARKER_DIAMETER**2)) if max_v > 0 else 1}

# time_values[metric][year] = [value, ...] aligned to `codes`, covering
# every year — used so the Levels metrics (TFR, ASFR, live births, etc),
# Female population, and Housing metrics can animate with a year control,
# unlike the fixed 2013-baseline group and "change vs 2013" which stay
# pinned to the latest year regardless of it.
TIME_YEARS = fertility["years"]
time_values = {}
time_size = {}
for metric in METRIC_ORDER:
    time_values[metric] = {}
    for y in TIME_YEARS:
        rows = fertility["data"].get(y, {})
        time_values[metric][y] = [rows.get(code, {}).get(metric) for code in codes]
for metric in POPULATION_ORDER:
    time_values[metric] = {}
    for y in TIME_YEARS:
        rows = population["data"].get(y, {})
        time_values[metric][y] = [rows.get(code, {}).get(metric) for code in codes]
for metric in HOUSING_ORDER:
    time_values[metric] = {}
    for y in TIME_YEARS:
        rows = housing["data"].get(y, {})
        time_values[metric][y] = [rows.get(code, {}).get(metric) for code in codes]

# cmin/cmax (color scale) and the marker sizeref are computed from the
# pooled values across ALL years, not just the latest — so a time-varying
# metric's color/size scale stays fixed as the year control animates.
# Per-year min/max would make the same absolute value look different
# (or saturate the color scale) depending on which year happened to set
# that year's own range.
for metric, by_year in time_values.items():
    pooled = sorted(v for values in by_year.values() for v in values if v is not None)
    if metric in metric_meta:
        if metric in LOG_COLOR_METRICS:
            lo, hi = pooled[0], pooled[-1]
            metric_meta[metric]["cmin"] = math.log10(lo)
            metric_meta[metric]["cmax"] = math.log10(hi)
            tick_values = nice_log_ticks(lo, hi)
            metric_meta[metric]["tickvals"] = [math.log10(v) for v in tick_values]
            metric_meta[metric]["ticktext"] = [format_tick(metric, v) for v in tick_values]
        else:
            metric_meta[metric]["cmin"] = pooled[0]
            metric_meta[metric]["cmax"] = pooled[-1]
    sizes_by_year = {y: [max(v, 0) if v is not None else 0 for v in values] for y, values in by_year.items()}
    max_v = max((v for sizes in sizes_by_year.values() for v in sizes), default=0)
    sizeref = (2 * max_v / (MAX_MARKER_DIAMETER**2)) if max_v > 0 else 1
    time_size[metric] = {y: {"sizes": sizes, "sizeref": sizeref} for y, sizes in sizes_by_year.items()}

# metric_meta[metric]["range"] = a fixed, padded [min, max] for use as an
# x/y axis range — pooled across all years for time-varying metrics (so the
# axis doesn't rescale/jump as the year control animates), or across the
# single available snapshot otherwise. Used instead of Plotly's default
# autorange, which would recompute from whichever year's data is currently
# plotted.
for metric, meta in metric_meta.items():
    if metric in time_values:
        pooled = sorted(v for values in time_values[metric].values() for v in values if v is not None)
    else:
        pooled = sorted(v for v in metric_values.get(metric, []) if v is not None)
    if not pooled:
        continue
    lo, hi = pooled[0], pooled[-1]
    pad = (hi - lo) * 0.05 or (abs(hi) * 0.05 if hi else 1)
    meta["range"] = [lo - pad, hi + pad]
    if metric in LOG_COLOR_METRICS:
        # Plotly log axes take their "range" in log10 space (range: [a, b]
        # actually spans 10**a..10**b) — a separate field so the linear
        # "range" above still works unchanged for metrics that aren't
        # shown on a log axis.
        log_lo, log_hi = math.log10(lo), math.log10(hi)
        log_pad = (log_hi - log_lo) * 0.05 or 0.05
        meta["log_range"] = [log_lo - log_pad, log_hi + log_pad]


def wrap_title(text, width=18):
    """Word-wrap `text` to `width` characters per line via <br> — the
    colorbar sits in a narrow strip and Plotly doesn't wrap its title on
    its own, so long metric names (e.g. "Housing affordability ratio")
    would otherwise overflow past the plot edge."""
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "<br>".join(lines)


for metric, meta in metric_meta.items():
    meta["colorbar_title"] = wrap_title(meta["title"])


def hover_record(code, hover_year):
    record = dict(fertility["data"].get(hover_year, {}).get(code, {}))
    record.update(population["data"].get(hover_year, {}).get(code, {}))
    record.update(housing["data"].get(hover_year, {}).get(code, {}))
    return record


hover_text = [
    build_hover_table(name, {y: hover_record(code, y) for y in HOVER_YEARS})
    for code, name in zip(codes, names)
]

x_buttons, x_active = full_dropdown_buttons(DEFAULT_X)
y_buttons, y_active = full_dropdown_buttons(DEFAULT_Y)
color_buttons, color_active = full_dropdown_buttons(DEFAULT_COLOR)
size_buttons, size_active = full_dropdown_buttons(DEFAULT_SIZE)
color_meta = metric_meta[DEFAULT_COLOR]


def color_values_for(metric):
    """marker.color values for `metric` — log10-transformed when its
    metric_meta marks it log_color (see LOG_COLOR_METRICS), matching
    coloraxis.cmin/cmax which are in the same log space."""
    values = metric_values[metric]
    if not metric_meta[metric].get("log_color"):
        return values
    return [math.log10(v) if v is not None and v > 0 else None for v in values]

# All four dropdowns share an identical button list (full_dropdown_buttons()
# always returns the same buttons, just a different active index) — so one
# metric->button-index lookup covers all of them. Needed so external preset
# buttons (outside the iframe, driving the chart via window.setPreset) can
# keep each dropdown's own displayed label in sync, since only clicking the
# widget itself updates that natively.
metric_to_index = {b["args"][0]: i for i, b in enumerate(x_buttons) if b["args"][0] is not None}

# Captured separately (not just inlined into fig.update_layout) so the same
# list can be embedded into post_script as BASE_ANNOTATIONS — the sync-axes
# toggle below adds its own reference-line annotations via a full
# Plotly.relayout({annotations: [...]}) replace, which would otherwise wipe
# these out.
label_annotations = [
    {"text": "X axis", "x": 0.0, "xanchor": "left", "y": 1.36, "yanchor": "bottom", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 11}},
    {"text": "Y axis", "x": 0.52, "xanchor": "left", "y": 1.36, "yanchor": "bottom", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 11}},
    {"text": "Color", "x": 0.0, "xanchor": "left", "y": 1.19, "yanchor": "bottom", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 11}},
    {"text": "Size", "x": 0.52, "xanchor": "left", "y": 1.19, "yanchor": "bottom", "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 11}},
]

fig = go.Figure(
    data=[
        go.Scatter(
            x=metric_values[DEFAULT_X],
            y=metric_values[DEFAULT_Y],
            mode="markers",
            text=hover_text,
            hoverinfo="text",
            hoverlabel={"font": {"family": "Menlo, Consolas, 'Courier New', monospace", "size": 11}, "align": "left"},
            marker={
                "size": size_data[DEFAULT_SIZE]["sizes"],
                "sizemode": "area",
                "sizeref": size_data[DEFAULT_SIZE]["sizeref"],
                "sizemin": 3,
                "color": color_values_for(DEFAULT_COLOR),
                "coloraxis": "coloraxis",
                "line": {"width": 0.5, "color": "#666"},
                "opacity": 0.8,
            },
        )
    ]
)

def axis_layout(metric):
    """xaxis/yaxis layout dict for `metric` — log-scale metrics (see
    LOG_COLOR_METRICS) get axis type "log" with their range in log10
    space (Plotly's requirement for log axes), everything else linear."""
    meta = metric_meta[metric]
    layout = {"title": {"text": meta["title"]}, "tickformat": ".0%" if meta["pct"] else "", "autorange": False}
    if meta.get("log_color"):
        layout["type"] = "log"
        layout["range"] = meta["log_range"]
    else:
        layout["type"] = "linear"
        layout["range"] = meta["range"]
    return layout


fig.update_layout(
    margin={"r": 10, "t": 160, "l": 60, "b": 60},
    autosize=True,
    xaxis=axis_layout(DEFAULT_X),
    yaxis=axis_layout(DEFAULT_Y),
    coloraxis={
        "colorscale": color_meta["colorscale"],
        "cmin": color_meta["cmin"],
        "cmax": color_meta["cmax"],
        "colorbar": {
            "title": {"text": color_meta["colorbar_title"]},
            "xpad": 30,
            "tickmode": "array" if color_meta.get("tickvals") else "auto",
            "tickvals": color_meta.get("tickvals", []),
            "ticktext": color_meta.get("ticktext", []),
        },
    },
    # Two dropdowns per row (X/Y, then Color/Size) — each box auto-sizes to
    # ~250px (driven by the longest metric label), which doesn't reliably
    # fit three or more side by side without overlapping, but two per row
    # comfortably fits typical container widths.
    # Despite declaring yref="paper", both updatemenus and annotations here
    # render on a scale relative to the plot area's own height, not the
    # full figure (confirmed by measuring rendered pixel positions
    # directly: pixel ~= plotBottom - y*plotHeight). Tightened to the
    # minimum spacing that doesn't visually collide, now that margin.t is
    # much smaller (160, vs 360 previously) to give the chart more height.
    updatemenus=[
        {"buttons": x_buttons, "direction": "down", "x": 0.0, "xanchor": "left", "y": 1.35, "yanchor": "top", "showactive": True, "active": x_active, "name": "xmenu"},
        {"buttons": y_buttons, "direction": "down", "x": 0.52, "xanchor": "left", "y": 1.35, "yanchor": "top", "showactive": True, "active": y_active, "name": "ymenu"},
        {"buttons": color_buttons, "direction": "down", "x": 0.0, "xanchor": "left", "y": 1.18, "yanchor": "top", "showactive": True, "active": color_active, "name": "colormenu"},
        {"buttons": size_buttons, "direction": "down", "x": 0.52, "xanchor": "left", "y": 1.18, "yanchor": "top", "showactive": True, "active": size_active, "name": "sizemenu"},
    ],
    annotations=[
        *label_annotations,
    ],
)

post_script = f"""
var gd = document.getElementById('{{plot_id}}');
var METRIC_VALUES = {json.dumps(metric_values)};
var METRIC_META = {json.dumps(metric_meta)};
var SIZE_DATA = {json.dumps(size_data)};
var METRIC_TO_INDEX = {json.dumps(metric_to_index)};
var MENU_INDEX = {{x: 0, y: 1, color: 2, size: 3}};
var BASE_ANNOTATIONS = {json.dumps(label_annotations)};
var REF_LINE_PCTS = [0, -0.2, -0.4, -0.6];
var TIME_VALUES = {json.dumps(time_values)};
var TIME_SIZE = {json.dumps(time_size)};
var TIME_YEARS = {json.dumps(TIME_YEARS)};

// Which metric is currently on each of x/y/color/size — kept in sync by
// applyAxis/setPreset so the year control (below) knows what to re-fetch.
var currentMetric = {{x: {json.dumps(DEFAULT_X)}, y: {json.dumps(DEFAULT_Y)}, color: {json.dumps(DEFAULT_COLOR)}, size: {json.dumps(DEFAULT_SIZE)}}};
var currentYear = TIME_YEARS[TIME_YEARS.length - 1];

// Levels metrics (TFR, ASFR, live births, etc) and Female population
// metrics are time-varying (animate with the year control below); the
// fixed 2013-baseline group and "change vs 2013" stay pinned to the latest
// year regardless of currentYear — these helpers pick whichever applies.
function valuesFor(metric) {{
    return (TIME_VALUES[metric] && TIME_VALUES[metric][currentYear]) || METRIC_VALUES[metric];
}}

function sizeFor(metric) {{
    return (TIME_SIZE[metric] && TIME_SIZE[metric][currentYear]) || SIZE_DATA[metric];
}}

// Housing metrics are heavily right-skewed, so their coloraxis is shown on
// a log scale (cmin/cmax and colorbar.tickvals in METRIC_META are already
// in log space for these) — the marker.color values fed in need the same
// log10 transform applied.
function toColorValues(metric, values) {{
    if (!METRIC_META[metric].log_color) return values;
    return values.map(function (v) {{ return (v === null || v === undefined || v <= 0) ? null : Math.log10(v); }});
}}

function colorValuesFor(metric) {{
    return toColorValues(metric, valuesFor(metric));
}}

// Sync X/Y axis limits + y=x*(1+pct) reference lines — toggled from outside
// the iframe (see docs/uk/scatter.md). Off by default; when on, re-applied
// after every change that could touch the x or y data.
var syncEnabled = false;

function applySync() {{
    if (!syncEnabled) return;
    // Use the metrics' fixed, all-years-pooled ranges (METRIC_META[...].range)
    // rather than whichever year's data is currently plotted — otherwise the
    // sync range (and its reference lines) would rescale with the year
    // control just like the un-synced axes used to before that was fixed.
    var xMeta = METRIC_META[currentMetric.x], yMeta = METRIC_META[currentMetric.y];
    if (!xMeta.range || !yMeta.range) return;
    // The y=x*(1+pct) reference lines and combined-range math below only
    // make sense on linear axes — skip syncing (leave each axis on its
    // own fixed range) if either side is log-scale.
    if (xMeta.log_color || yMeta.log_color) return;
    var rangeLo = Math.min(xMeta.range[0], yMeta.range[0]);
    var rangeHi = Math.max(xMeta.range[1], yMeta.range[1]);
    var shapes = REF_LINE_PCTS.map(function (pct) {{
        return {{
            type: 'line', xref: 'x', yref: 'y',
            x0: rangeLo, y0: rangeLo * (1 + pct), x1: rangeHi, y1: rangeHi * (1 + pct),
            line: {{color: '#999', width: 1, dash: pct === 0 ? 'dot' : 'dash'}},
        }};
    }});
    var refAnnotations = REF_LINE_PCTS.map(function (pct) {{
        return {{
            x: rangeHi, y: rangeHi * (1 + pct), xref: 'x', yref: 'y',
            xanchor: 'left', yanchor: 'middle', showarrow: false,
            text: (pct * 100).toFixed(0) + '%',
            font: {{size: 10, color: '#888'}},
        }};
    }});
    Plotly.relayout(gd, {{
        'xaxis.range': [rangeLo, rangeHi],
        'xaxis.autorange': false,
        'yaxis.range': [rangeLo, rangeHi],
        'yaxis.autorange': false,
        shapes: shapes,
        annotations: BASE_ANNOTATIONS.concat(refAnnotations),
    }});
}}

function clearSync() {{
    var xMeta = METRIC_META[currentMetric.x], yMeta = METRIC_META[currentMetric.y];
    Plotly.relayout(gd, {{
        'xaxis.type': xMeta.log_color ? 'log' : 'linear',
        'xaxis.range': xMeta.log_color ? xMeta.log_range : xMeta.range,
        'xaxis.autorange': false,
        'yaxis.type': yMeta.log_color ? 'log' : 'linear',
        'yaxis.range': yMeta.log_color ? yMeta.log_range : yMeta.range,
        'yaxis.autorange': false,
        shapes: [], annotations: BASE_ANNOTATIONS,
    }});
}}

window.setSyncAxes = function (enabled) {{
    syncEnabled = enabled;
    if (enabled) applySync(); else clearSync();
}};

function applyAxis(which, metric, fromWidgetClick) {{
    if (!metric || !METRIC_VALUES[metric]) return;
    var meta = METRIC_META[metric];
    currentMetric[which] = metric;
    var p;
    if (which === 'x') {{
        p = Plotly.restyle(gd, {{x: [valuesFor(metric)]}}, [0]).then(function () {{
            return Plotly.relayout(gd, {{
                'xaxis.title.text': meta.title, 'xaxis.tickformat': meta.pct ? '.0%' : '',
                'xaxis.type': meta.log_color ? 'log' : 'linear',
                'xaxis.range': meta.log_color ? meta.log_range : meta.range,
                'xaxis.autorange': false,
            }});
        }});
    }} else if (which === 'y') {{
        p = Plotly.restyle(gd, {{y: [valuesFor(metric)]}}, [0]).then(function () {{
            return Plotly.relayout(gd, {{
                'yaxis.title.text': meta.title, 'yaxis.tickformat': meta.pct ? '.0%' : '',
                'yaxis.type': meta.log_color ? 'log' : 'linear',
                'yaxis.range': meta.log_color ? meta.log_range : meta.range,
                'yaxis.autorange': false,
            }});
        }});
    }} else if (which === 'color') {{
        p = Plotly.restyle(gd, {{'marker.color': [colorValuesFor(metric)]}}, [0]).then(function () {{
            return Plotly.relayout(gd, {{
                'coloraxis.colorscale': meta.colorscale,
                'coloraxis.cmin': meta.cmin,
                'coloraxis.cmax': meta.cmax,
                'coloraxis.colorbar.title.text': meta.colorbar_title,
                'coloraxis.colorbar.tickmode': meta.tickvals ? 'array' : 'auto',
                'coloraxis.colorbar.tickvals': meta.tickvals || [],
                'coloraxis.colorbar.ticktext': meta.ticktext || [],
            }});
        }});
    }} else if (which === 'size') {{
        var sd = sizeFor(metric);
        p = Plotly.restyle(gd, {{'marker.size': [sd.sizes], 'marker.sizeref': sd.sizeref}}, [0]);
    }} else {{
        return;
    }}
    p.then(function () {{
        // Clicking the widget itself already updates its own displayed
        // label natively; calls that come from outside (e.g. a preset
        // button) bypass that, so sync it explicitly via the updatemenu's
        // "active" index.
        if (fromWidgetClick) return;
        var patch = {{}};
        patch['updatemenus[' + MENU_INDEX[which] + '].active'] = METRIC_TO_INDEX[metric];
        return Plotly.relayout(gd, patch);
    }}).then(function () {{
        if (which === 'x' || which === 'y') applySync();
    }});
}}

gd.on('plotly_buttonclicked', function (ev) {{
    if (!ev.menu || !ev.button || !ev.button.args || ev.button.args[0] === null) return;
    var metric = ev.button.args[0];
    if (ev.menu.name === 'xmenu') applyAxis('x', metric, true);
    else if (ev.menu.name === 'ymenu') applyAxis('y', metric, true);
    else if (ev.menu.name === 'colormenu') applyAxis('color', metric, true);
    else if (ev.menu.name === 'sizemenu') applyAxis('size', metric, true);
}});

// Entry point for controls outside the iframe (see docs/uk/scatter.md) —
// call as document.getElementById('scatter-frame').contentWindow.setPreset
// (x, y, color, size) with metric keys from METRIC_VALUES. Batched into a
// single restyle + single relayout (rather than 4 applyAxis calls) so rapid
// clicks between presets can't race: each is async and unsequenced calls
// could otherwise resolve out of order and leave a mixed, stale state.
window.setPreset = function (x, y, color, size) {{
    if (!METRIC_VALUES[x] || !METRIC_VALUES[y] || !METRIC_VALUES[color] || !SIZE_DATA[size]) return;
    var xMeta = METRIC_META[x], yMeta = METRIC_META[y], colorMeta = METRIC_META[color];
    currentMetric.x = x; currentMetric.y = y; currentMetric.color = color; currentMetric.size = size;
    var sd = sizeFor(size);
    Plotly.restyle(gd, {{
        x: [valuesFor(x)],
        y: [valuesFor(y)],
        'marker.color': [colorValuesFor(color)],
        'marker.size': [sd.sizes],
        'marker.sizeref': sd.sizeref,
    }}, [0]).then(function () {{
        var patch = {{
            'xaxis.title.text': xMeta.title,
            'xaxis.tickformat': xMeta.pct ? '.0%' : '',
            'xaxis.type': xMeta.log_color ? 'log' : 'linear',
            'xaxis.range': xMeta.log_color ? xMeta.log_range : xMeta.range,
            'xaxis.autorange': false,
            'yaxis.title.text': yMeta.title,
            'yaxis.tickformat': yMeta.pct ? '.0%' : '',
            'yaxis.type': yMeta.log_color ? 'log' : 'linear',
            'yaxis.range': yMeta.log_color ? yMeta.log_range : yMeta.range,
            'yaxis.autorange': false,
            'coloraxis.colorscale': colorMeta.colorscale,
            'coloraxis.cmin': colorMeta.cmin,
            'coloraxis.cmax': colorMeta.cmax,
            'coloraxis.colorbar.title.text': colorMeta.colorbar_title,
            'coloraxis.colorbar.tickmode': colorMeta.tickvals ? 'array' : 'auto',
            'coloraxis.colorbar.tickvals': colorMeta.tickvals || [],
            'coloraxis.colorbar.ticktext': colorMeta.ticktext || [],
        }};
        patch['updatemenus[' + MENU_INDEX.x + '].active'] = METRIC_TO_INDEX[x];
        patch['updatemenus[' + MENU_INDEX.y + '].active'] = METRIC_TO_INDEX[y];
        patch['updatemenus[' + MENU_INDEX.color + '].active'] = METRIC_TO_INDEX[color];
        patch['updatemenus[' + MENU_INDEX.size + '].active'] = METRIC_TO_INDEX[size];
        return Plotly.relayout(gd, patch);
    }}).then(function () {{
        applySync();
    }});
}};

// Year control for the time-varying metrics (Levels + Female population)
// — entry point for controls outside the iframe, called as
// document.getElementById('scatter-frame').contentWindow.setYear(year).
// Whichever of x/y/color/size currently holds a time-varying metric is
// re-fetched for the new year; fixed metrics (TFR, 2013-baseline ASFR,
// "change vs 2013", ...) are left untouched.
window.setYear = function (yr) {{
    yr = String(yr);
    if (TIME_YEARS.indexOf(yr) === -1) return;
    currentYear = yr;
    var restyle = {{}};
    if (TIME_VALUES[currentMetric.x] && TIME_VALUES[currentMetric.x][yr]) restyle.x = [TIME_VALUES[currentMetric.x][yr]];
    if (TIME_VALUES[currentMetric.y] && TIME_VALUES[currentMetric.y][yr]) restyle.y = [TIME_VALUES[currentMetric.y][yr]];
    if (TIME_VALUES[currentMetric.color] && TIME_VALUES[currentMetric.color][yr]) restyle['marker.color'] = [toColorValues(currentMetric.color, TIME_VALUES[currentMetric.color][yr])];
    if (TIME_SIZE[currentMetric.size] && TIME_SIZE[currentMetric.size][yr]) {{
        var sd = TIME_SIZE[currentMetric.size][yr];
        restyle['marker.size'] = [sd.sizes];
        restyle['marker.sizeref'] = sd.sizeref;
    }}
    if (Object.keys(restyle).length === 0) return;
    Plotly.restyle(gd, restyle, [0]).then(function () {{
        applySync();
    }});
}};
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
html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
open(OUTPUT, "w", encoding="utf-8").write(html)

print(f"Wrote {OUTPUT} ({len(codes)} LADs, {year}, {len(metric_values)} metrics)")

# --- Static PNG snapshots for the cohorts discussed in the docs page's
# narrative — unlike the interactive chart these can't be driven by the
# year slider, so each is a fixed 2013-baseline-vs-{year} snapshot (the Y
# axis title spells out the year explicitly for that reason, unlike the
# interactive chart's dropdown label which stays year-agnostic since it
# tracks whichever year the slider is on).
STATIC_COHORTS = ["asfr_20_24", "asfr_25_29", "asfr_30_34", "asfr_35_39"]
color_meta_static = metric_meta["mean_age_mother"]
REF_LINE_PCTS = [0, -0.2, -0.4, -0.6]
for asfr_key in STATIC_COHORTS:
    x_key = f"{asfr_key}_2013"
    pop_key = asfr_key.replace("asfr_", "pop_")
    x_meta, y_meta = metric_meta[x_key], metric_meta[asfr_key]

    # Same "sync axes" treatment as the interactive chart's checkbox
    # (matching combined x/y range plus y=x*(1+pct) reference lines) —
    # applied here directly rather than needing a screenshot of it toggled
    # on in the live page.
    range_lo = min(x_meta["range"][0], y_meta["range"][0])
    range_hi = max(x_meta["range"][1], y_meta["range"][1])
    shapes = [
        {
            "type": "line",
            "x0": range_lo,
            "y0": range_lo * (1 + pct),
            "x1": range_hi,
            "y1": range_hi * (1 + pct),
            "line": {"color": "#999", "width": 1, "dash": "dot" if pct == 0 else "dash"},
        }
        for pct in REF_LINE_PCTS
    ]
    annotations = [
        {
            "x": range_hi,
            "y": range_hi * (1 + pct),
            "xanchor": "left",
            "yanchor": "middle",
            "showarrow": False,
            "text": f"{pct * 100:.0f}%",
            "font": {"size": 10, "color": "#888"},
        }
        for pct in REF_LINE_PCTS
    ]

    fig_static = go.Figure(
        data=[
            go.Scatter(
                x=metric_values[x_key],
                y=metric_values[asfr_key],
                mode="markers",
                marker={
                    "size": size_data[pop_key]["sizes"],
                    "sizemode": "area",
                    "sizeref": size_data[pop_key]["sizeref"],
                    "sizemin": 3,
                    "color": metric_values["mean_age_mother"],
                    "colorscale": color_meta_static["colorscale"],
                    "cmin": color_meta_static["cmin"],
                    "cmax": color_meta_static["cmax"],
                    "colorbar": {"title": {"text": color_meta_static["colorbar_title"]}, "xpad": 30},
                    "showscale": True,
                    "line": {"width": 0.5, "color": "#666"},
                    "opacity": 0.8,
                },
            )
        ]
    )
    fig_static.update_layout(
        template="plotly_white",
        width=700,
        height=500,
        margin={"r": 10, "t": 20, "l": 60, "b": 60},
        xaxis={"title": {"text": x_meta["title"]}, "range": [range_lo, range_hi]},
        yaxis={"title": {"text": f"{METRIC_LABELS[asfr_key]} ({year})"}, "range": [range_lo, range_hi]},
        shapes=shapes,
        annotations=annotations,
    )
    static_out = f"outputs/scatter_{asfr_key}.png"
    fig_static.write_image(static_out, scale=2)
    print(f"Wrote {static_out}")

# --- Static PNG snapshots for the same cohorts against average house
# price instead of the 2013 baseline — mirrors the Housing preset row's
# X = house_price, Y = ASFR, Color = mean age, Size = population. No sync-
# axes reference lines here (house price and ASFR are different units, so
# a y=x*(1+pct) line wouldn't mean anything), and the x axis is log-scale
# like the interactive chart's Housing presets.
house_price_meta = metric_meta["house_price"]
for asfr_key in STATIC_COHORTS:
    pop_key = asfr_key.replace("asfr_", "pop_")
    y_meta = metric_meta[asfr_key]
    fig_housing = go.Figure(
        data=[
            go.Scatter(
                x=metric_values["house_price"],
                y=metric_values[asfr_key],
                mode="markers",
                marker={
                    "size": size_data[pop_key]["sizes"],
                    "sizemode": "area",
                    "sizeref": size_data[pop_key]["sizeref"],
                    "sizemin": 3,
                    "color": metric_values["mean_age_mother"],
                    "colorscale": color_meta_static["colorscale"],
                    "cmin": color_meta_static["cmin"],
                    "cmax": color_meta_static["cmax"],
                    "colorbar": {"title": {"text": color_meta_static["colorbar_title"]}, "xpad": 30},
                    "showscale": True,
                    "line": {"width": 0.5, "color": "#666"},
                    "opacity": 0.8,
                },
            )
        ]
    )
    fig_housing.update_layout(
        template="plotly_white",
        width=700,
        height=500,
        margin={"r": 10, "t": 20, "l": 60, "b": 60},
        xaxis={"title": {"text": f"{house_price_meta['title']} ({year})"}, "type": "log", "range": house_price_meta["log_range"]},
        yaxis={"title": {"text": f"{METRIC_LABELS[asfr_key]} ({year})"}, "range": y_meta["range"]},
    )
    housing_out = f"outputs/scatter_housing_{asfr_key}.png"
    fig_housing.write_image(housing_out, scale=2)
    print(f"Wrote {housing_out}")
