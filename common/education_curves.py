"""Small multiples of birth rate by age and education: one row per country, one column per
education level, a line per year. Shared by the age-curve charts on
docs/factors/education-age-curves.md (ACS fertility_by_education_us.py,
eurostat fertility_by_education_nordic.py and fertility_by_education_europe_curves.py,
NSO latam_fertility_by_education.py) so every section has the same axes, colors and layout.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plot_colors import PERIOD_COLORSCALE, period_axis, sample_color

AGE_RANGE = [18, 44]
RATE_RANGE = [0, 300]
ROW_HEIGHT = 200


def curves_grid(rows, columns, title):
    """rows: [(country, [panel, ...])], one panel per entry of `columns` (education labels).
    A panel is a DataFrame with year, x (age), rate (births per 1,000) and optionally band (an
    age-band label such as "25-29", for rates by 5-year group plotted at the band's middle),
    or None for a level with no data."""
    years = sorted({int(y) for _, panels in rows for p in panels if p is not None for y in p.year})
    axis = period_axis(years[0], years[-1])
    n, k = len(rows), len(columns)
    top = 150 if len(years) <= 12 else 175
    height = ROW_HEIGHT * n + top + 50
    fig = make_subplots(rows=n, cols=k, shared_xaxes=True, shared_yaxes=True,
                        horizontal_spacing=0.03, vertical_spacing=min(0.1, 40 / height),
                        column_titles=columns)
    for y in years:  # legend entries, in year order
        fig.add_trace(go.Scatter(x=[None], y=[None], name=str(y), legendgroup=str(y), mode="lines",
                                 line=dict(color=sample_color(PERIOD_COLORSCALE, y, axis), width=2)),
                      row=1, col=1)
    for i, (country, panels) in enumerate(rows):
        for j, (col, p) in enumerate(zip(columns, panels)):
            if p is None:
                continue
            band = "band" in p
            for y in years:
                r = p[p.year == y].sort_values("x")
                if r.empty:
                    continue
                fig.add_trace(go.Scatter(
                    x=r.x, y=r.rate, name=str(y), legendgroup=str(y), showlegend=False,
                    mode="lines+markers" if band else "lines", marker=dict(size=4),
                    customdata=r.band.str.replace("-", "–") if band else r.x,
                    line=dict(color=sample_color(PERIOD_COLORSCALE, y, axis), width=2),
                    hovertemplate=f"{country}, {col}, {y}, age %{{customdata}}: %{{y:.0f}}<extra></extra>",
                ), row=i + 1, col=j + 1)
        fig.update_yaxes(title_text=f"<b>{country}</b>", row=i + 1, col=1)
    fig.update_layout(template="plotly_white", height=height,
                      title=f"{title}<br><sup>Births per 1,000 women, by age</sup>",
                      title_y=1 - 22 / height, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1 + 45 / (height - top - 50),
                                  xanchor="left", yanchor="bottom"),
                      margin=dict(l=70, r=20, t=top, b=50))
    fig.update_xaxes(range=AGE_RANGE, dtick=10)
    fig.update_xaxes(title_text="Age", row=n)
    fig.update_yaxes(range=RATE_RANGE, dtick=100)
    return fig
