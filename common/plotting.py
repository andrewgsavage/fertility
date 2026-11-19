"""Writing Plotly figures as the standalone HTML pages the docs embed in iframes."""

import json
import pathlib

# write_html's own template doesn't stretch <html>/<body> to fill the iframe, so a
# default_height of 100% would collapse; this style makes it fill the frame.
FULL_PAGE_STYLE = "<style>html, body { height: 100%; margin: 0; }</style>"

# No in-iframe UI: the range control lives in the containing docs page (outside the
# iframe, e.g. docs/uk/cond-asfr.md / later-births.md) so one control can drive several
# charts at once. This exposes the filtering as window.setRange(lo, hi) for that external
# control to call via each iframe's contentWindow.
RANGE_POST_SCRIPT = """
var gd = document.getElementById('{plot_id}');
var traceGroups = __TRACE_GROUPS__;
window.setRange = function (lo, hi) {
    var visible = traceGroups.map(function (g) { return g === null ? true : (g >= lo && g <= hi); });
    Plotly.restyle(gd, {visible: visible});
};
"""


def range_post_script(trace_groups):
    """RANGE_POST_SCRIPT for a figure whose fig.data[i] belongs to group trace_groups[i]
    (None: always visible)."""
    return RANGE_POST_SCRIPT.replace("__TRACE_GROUPS__", json.dumps(trace_groups))


def write_html(fig, path, *, height="100%", post_script=None, full_page=True, log=True):
    """Write fig as a full HTML page loading plotly.js from the CDN, responsive and 100% wide.

    height: default_height (e.g. f"{fig.layout.height}px" for a fixed-height facet grid).
    post_script: JS run after the plot is drawn.
    full_page: inject FULL_PAGE_STYLE so the page fills its iframe.
    log: print "Saved <path>".
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn", full_html=True, post_script=post_script,
                   default_width="100%", default_height=height, config={"responsive": True})
    if full_page:
        html = path.read_text(encoding="utf-8")
        path.write_text(html.replace("<head>", "<head>\n" + FULL_PAGE_STYLE, 1), encoding="utf-8")
    if log:
        print(f"Saved {path}")
    return path
