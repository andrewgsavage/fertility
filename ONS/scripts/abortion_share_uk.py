"""Abortions as a share of births + abortions, England & Wales residents.

Top panel: all ages, 1968-2023 (DHSC Table 1 abortions; HFD GBRTENW births,
plus the ONS 2023 count). Bottom panel: by age group, 2013-2022 (DHSC
Table 3b abortions; HFD births by mother's age).

Inputs (not in git):
  ONS/data/abortion-statistics-2023-england-and-wales-residents.ods
      https://www.gov.uk/government/statistics/abortion-statistics-for-england-and-wales-2023
  HFD/data/HFD/birthsRR.txt  (Human Fertility Database, all-countries zip)
"""

import plotly.colors as pc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.ons_abortion import ONS_BIRTHS, ODS, abortions_total, births, read_ods_sheet
from common.paths import outputs_dir
from common.plotting import write_html

OUTPUT = outputs_dir("ONS") / "abortion_share_uk.html"

AGE_GROUPS = {  # label: (DHSC Table 3b rows, HFD age range inclusive)
    "Under 20": (["Under 18", "18 to 19"], (0, 19)),
    "20–24": (["20 to 24"], (20, 24)),
    "25–29": (["25 to 29"], (25, 29)),
    "30–34": (["30 to 34"], (30, 34)),
    "35+": (["35 or over"], (35, 99)),
}


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
    write_html(fig, OUTPUT)
