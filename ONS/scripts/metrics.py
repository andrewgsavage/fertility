"""Shared metric definitions for fertility_by_lad.json, used by both
build_plotly_map.py and build_plotly_scatter.py. Mirrors the metric set and
grouping from the original Leaflet map.html."""

METRIC_LABELS = {
    "tfr": "Total fertility rate (TFR)",
    "crude_birth_rate": "Crude birth rate",
    "gfr": "General fertility rate (GFR)",
    "mean_age_mother": "Mean age of mother",
    "asfr_under18": "ASFR — under 18",
    "asfr_under20": "ASFR — under 20",
    "asfr_20_24": "ASFR — 20–24",
    "asfr_25_29": "ASFR — 25–29",
    "asfr_30_34": "ASFR — 30–34",
    "asfr_35_39": "ASFR — 35–39",
    "asfr_40_44": "ASFR — 40–44",
    "asfr_45plus": "ASFR — 45+",
    "live_births": "Live births",
    "asfr_under18_rel2013": "ASFR under 18 — change vs 2013",
    "asfr_under20_rel2013": "ASFR under 20 — change vs 2013",
    "asfr_20_24_rel2013": "ASFR 20–24 — change vs 2013",
    "asfr_25_29_rel2013": "ASFR 25–29 — change vs 2013",
    "asfr_30_34_rel2013": "ASFR 30–34 — change vs 2013",
    "asfr_35_39_rel2013": "ASFR 35–39 — change vs 2013",
    "asfr_40_44_rel2013": "ASFR 40–44 — change vs 2013",
    "asfr_45plus_rel2013": "ASFR 45+ — change vs 2013",
}
METRIC_ORDER = [
    "tfr", "crude_birth_rate", "gfr", "mean_age_mother",
    "asfr_under18", "asfr_under20", "asfr_20_24", "asfr_25_29",
    "asfr_30_34", "asfr_35_39", "asfr_40_44", "asfr_45plus", "live_births",
]
REL_METRIC_ORDER = [
    "asfr_under18_rel2013", "asfr_under20_rel2013", "asfr_20_24_rel2013", "asfr_25_29_rel2013",
    "asfr_30_34_rel2013", "asfr_35_39_rel2013", "asfr_40_44_rel2013", "asfr_45plus_rel2013",
]
DIVERGING_METRICS = set(REL_METRIC_ORDER)

SEQ_COLORSCALE = [[0, "#cde2fb"], [1, "#0d366b"]]
DIV_COLORSCALE = [[0, "#0d366b"], [0.5, "#f0efec"], [1, "#c1302f"]]
DIV_RANGE = 0.55  # matches the original chroma domain: -55%..+55%


def decimals_for(metric):
    return 2 if metric == "tfr" else 1


def fmt_value(value, metric):
    if value is None:
        return "No data"
    if metric in DIVERGING_METRICS:
        return f"{value * 100:+.0f}%"
    return f"{value:.{decimals_for(metric)}f}"


def dropdown_buttons(default_metric=None):
    """(buttons, active_index) for a Levels/Change-since-2013 grouped
    metric dropdown, in the shared updatemenus button format."""
    buttons = (
        [{"label": "— Levels —", "method": "skip", "args": [None]}]
        + [{"label": METRIC_LABELS[m], "method": "skip", "args": [m]} for m in METRIC_ORDER]
        + [{"label": "— Change since 2013 —", "method": "skip", "args": [None]}]
        + [{"label": METRIC_LABELS[m], "method": "skip", "args": [m]} for m in REL_METRIC_ORDER]
    )
    active = None
    if default_metric is not None:
        active = (
            (2 + len(METRIC_ORDER) + REL_METRIC_ORDER.index(default_metric))
            if default_metric in DIVERGING_METRICS
            else (1 + METRIC_ORDER.index(default_metric))
        )
    return buttons, active
