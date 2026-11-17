"""Abortions as a share of births + abortions, England & Wales residents.

Top panel: all ages, 1968-2023 (DHSC Table 1 abortions; HFD GBRTENW births,
plus the ONS 2023 count). Bottom panel: by age group, 2013-2022 (DHSC
Table 3b abortions; HFD births by mother's age).

Inputs (not in git):
  ONS/data/abortion-statistics-2023-england-and-wales-residents.ods
      https://www.gov.uk/government/statistics/abortion-statistics-for-england-and-wales-2023
  HFD/data/HFD/birthsRR.txt  (Human Fertility Database, all-countries zip)
"""

import pathlib
import re
import zipfile
import xml.etree.ElementTree as ET

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
ODS = _SCRIPT_DIR.parent / "data" / "abortion-statistics-2023-england-and-wales-residents.ods"
HFD_BIRTHS = _SCRIPT_DIR.parent.parent / "HFD" / "data" / "HFD" / "birthsRR.txt"
OUTPUT = _SCRIPT_DIR.parent / "outputs" / "abortion_share_uk.html"

# ONS Births in England and Wales: 2023 (HFD ends at 2022).
ONS_BIRTHS = {2023: 591_072}

AGE_GROUPS = {  # label: (DHSC Table 3b rows, HFD age range inclusive)
    "Under 20": (["Under 18", "18 to 19"], (0, 19)),
    "20–24": (["20 to 24"], (20, 24)),
    "25–29": (["25 to 29"], (25, 29)),
    "30–34": (["30 to 34"], (30, 34)),
    "35+": (["35 or over"], (35, 99)),
}

_T = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
_O = "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}"
_P = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p"


def read_ods_sheet(path, sheet):
    """Rows of a sheet in an .ods file as lists of strings (stdlib only)."""
    root = ET.fromstring(zipfile.ZipFile(path).read("content.xml"))
    for table in root.iter(_T + "table"):
        if table.get(_T + "name") != sheet:
            continue
        rows = []
        for r in table.iter(_T + "table-row"):
            row = []
            for c in r.iter(_T + "table-cell"):
                n = min(int(c.get(_T + "number-columns-repeated", "1")), 50)
                v = c.get(_O + "value") or "".join(p.text or "" for p in c.iter(_P))
                row += [v] * n
            rows.append(row)
        return rows
    raise KeyError(sheet)


def year_of(s):
    m = re.match(r"(\d{4})", s)
    return int(m.group(1)) if m else None


def abortions_total():
    """{year: abortions to E&W residents}, Table 1."""
    out = {}
    for row in read_ods_sheet(ODS, "Table_1"):
        if len(row) > 2 and year_of(row[0]) and row[2].isdigit():
            out[year_of(row[0])] = int(row[2])
    return out


def abortions_by_age():
    """{group: {year: abortions}}, Table 3b numbers."""
    rows = read_ods_sheet(ODS, "Table_3b")
    header = next(r for r in rows if len(r) > 2 and r[1] == "Age group")
    years = {i: int(h) for i, h in enumerate(header) if h.isdigit()}
    numbers = {r[1]: r for r in rows if r and r[0] == "Numbers"}
    out = {}
    for group, (labels, _) in AGE_GROUPS.items():
        out[group] = {y: sum(float(numbers[l][i]) for l in labels) for i, y in years.items()}
    return out


def births():
    """{year: {age: births}} for England & Wales from HFD."""
    out = {}
    with open(HFD_BIRTHS, encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4 and parts[0] == "GBRTENW":
                age = int(re.sub(r"\D", "", parts[2]))
                out.setdefault(int(parts[1]), {})[age] = float(parts[3])
    return out


def plot():
    ab = abortions_total()
    bi = births()
    total_births = {y: sum(a.values()) for y, a in bi.items()}
    total_births.update(ONS_BIRTHS)
    years = sorted(y for y in ab if y in total_births)
    share = [100 * ab[y] / (ab[y] + total_births[y]) for y in years]

    fig = make_subplots(
        rows=2, cols=1, vertical_spacing=0.14,
        subplot_titles=(
            "All ages, 1968–2023",
            "By age of woman, 2013–2022",
        ),
    )
    fig.add_trace(go.Scatter(
        x=years, y=share, mode="lines+markers", marker=dict(size=4),
        name="All ages", line=dict(color="#333"), legend="legend",
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ), row=1, col=1)

    by_age = abortions_by_age()
    colors = pc.qualitative.Safe
    for i, (group, (_, (lo, hi))) in enumerate(AGE_GROUPS.items()):
        ys = sorted(y for y in by_age[group] if y in bi)
        b = [sum(v for a, v in bi[y].items() if lo <= a <= hi) for y in ys]
        s = [100 * by_age[group][y] / (by_age[group][y] + bb) for y, bb in zip(ys, b)]
        fig.add_trace(go.Scatter(
            x=ys, y=s, mode="lines+markers", marker=dict(size=4), name=group,
            line=dict(color=colors[i]), legend="legend2",
            hovertemplate=group + " %{x}: %{y:.1f}%<extra></extra>",
        ), row=2, col=1)

    fig.update_yaxes(title_text="% of births + abortions", ticksuffix="%", rangemode="tozero")
    fig.update_layout(
        template="plotly_white",
        title="Abortions as a share of births + abortions, England & Wales residents",
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        legend2=dict(title="Age", x=1.02, y=0.43, xanchor="left", yanchor="top"),
        margin=dict(r=120, t=80),
    )
    return fig


if __name__ == "__main__":
    fig = plot()
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = OUTPUT.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Saved {OUTPUT}")
