"""Read the data behind a Flourish chart from its embed page (flo.uri.sh/visualisation/<id>/embed).

Flourish inlines each chart's data in the embed HTML as `_Flourish_data_column_names` and
`_Flourish_data` JS literals, and its settings (title, subtitle, footer) as
`_Flourish_settings`. Dates appear as `new Date(<ms>)`, which are replaced by the year.
"""

import json
import re

import pandas as pd


def _html(path):
    h = path.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"new Date\((-?\d+)\)", lambda m: str(pd.Timestamp(int(m.group(1)), unit="ms").year), h)


def _grab(h, name):
    m = re.search(r"\b" + name + r"\s*=\s*(?=[\[{])", h)
    return json.JSONDecoder().raw_decode(h, m.end())[0]


def flourish(path):
    """Long DataFrame (facet, year, series, value) from a Flourish line/area chart embed.

    `facet` is None for charts with no small multiples.
    """
    h = _html(path)
    cols = _grab(h, "_Flourish_data_column_names")["data"]
    rows = []
    for r in _grab(h, "_Flourish_data")["data"]:
        for s, v in zip(cols["value"], r["value"]):
            if v not in (None, ""):
                rows.append({"facet": r.get("facet"), "year": int(r["label"]), "series": s, "value": float(v)})
    return pd.DataFrame(rows)


def flourish_settings(path):
    """The chart's settings dict (layout.title, layout.subtitle, layout.footer_note, ...)."""
    return _grab(_html(path), "_Flourish_settings")
