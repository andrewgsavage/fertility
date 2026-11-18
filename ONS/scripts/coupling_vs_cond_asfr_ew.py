"""Conditional ASFR against the share of women living in a couple, England and Wales,
2002 onward, one connected time series per age band.

y: first-birth rate of childless women and second-birth rate of one-child women, from
   the parity-hazard reconstruction in cond_asfr_uk_ons.py (ONS cohort table 3). Single
   ages are pooled into the living-arrangements age bands, weighted by the share of the
   cohort at risk (childless, or with one child) at the previous age. Rates exist for
   ages 21-45, so the "16-29" band covers 21-29.
x: % of women in the band living in a couple (married, civil partnered or cohabiting),
   or cohabiting only (dropdown), from coupling_by_age_ew.py (ONS living arrangements).

Inputs (ONS/data/, not tracked in git): finalisingcohorttables2024finalforupload.xlsx and
families/maritalstatuslivingarrangements2002to2025englandandwales.xlsx.
"""

import pathlib
import sys

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / "HFD" / "scripts"))

import coupling_by_age_ew  # noqa: E402
from cond_asfr_uk_ons import load_table3  # noqa: E402
from plot_colors import PERIOD_COLORSCALE, period_axis  # noqa: E402

OUTDIR = _SCRIPT_DIR.parent / "outputs"
BANDS = {"16 to 29": (21, 29), "30 to 34": (30, 34), "35 to 39": (35, 39), "40 to 44": (40, 44)}
FIRST_YEAR = 2002


def band_rates():
    """year, band -> pooled first- and second-birth conditional rates (%)."""
    rows = []
    for cohort, ages in load_table3().items():
        for age, (p1, p2) in ages.items():
            if age - 1 not in ages:
                continue
            p1_prev, p2_prev = ages[age - 1]
            rows.append({"year": cohort + age, "age": age,
                         "b1": max(0.0, p1 - p1_prev), "r1": 100 - p1_prev,
                         "b2": max(0.0, p2 - p2_prev), "r2": p1_prev - p2_prev})
    d = pd.DataFrame(rows)
    d = d[d.year >= FIRST_YEAR]
    out = []
    for band, (lo, hi) in BANDS.items():
        g = d[d.age.between(lo, hi)].groupby("year")[["b1", "r1", "b2", "r2"]].sum()
        # Only years with every single age in the band present.
        n = d[d.age.between(lo, hi)].groupby("year").size()
        g = g[n == hi - lo + 1]
        out.append(pd.DataFrame({"band": band, "year": g.index,
                                 "first": 100 * g.b1 / g.r1, "second": 100 * g.b2 / g.r2}))
    return pd.concat(out, ignore_index=True)


def load():
    c = coupling_by_age_ew.load()
    c = c[c.sex == "Women"].rename(columns={"age": "band"})[["band", "year", "couple", "cohab"]]
    return band_rates().merge(c, on=["band", "year"])


def label(band):
    lo, hi = BANDS[band]
    return f"{lo}-{hi}"


def plot(d):
    years = sorted(d.year.unique())
    caxis = period_axis(years[0], years[-1])
    panels = {"first": "First birth (childless women)", "second": "Second birth (one-child women)"}
    fig = make_subplots(rows=1, cols=2, subplot_titles=list(panels.values()), horizontal_spacing=0.1)
    bands = list(BANDS)
    xs = {"couple": [], "cohab": []}
    for b in bands:
        x = d[d.band == b].sort_values("year")
        for j, (col, title) in enumerate(panels.items(), start=1):
            text = [str(y) if y in (x.year.min(), x.year.max()) or y % 5 == 0 else "" for y in x.year]
            fig.add_trace(go.Scatter(
                x=x.couple, y=x[col], mode="lines+markers+text", text=text, textposition="top center",
                textfont=dict(size=10), name=label(b), visible=b == "30 to 34", showlegend=False,
                line=dict(color="#bbbbbb", width=1),
                marker=dict(size=9, color=x.year, colorscale=PERIOD_COLORSCALE, cmin=caxis[0], cmax=caxis[1],
                            showscale=j == 2, colorbar=dict(title="Year", x=1.02)),
                customdata=x[["year", "couple", "cohab"]].values,
                hovertemplate=(f"Women {label(b)}, %{{customdata[0]}}<br>"
                               "In a couple %{customdata[1]:.1f}%, cohabiting %{customdata[2]:.1f}%<br>"
                               f"{title.split(' (')[0]} rate %{{y:.2f}}%<extra></extra>")), row=1, col=j)
            xs["couple"].append(x.couple.tolist())
            xs["cohab"].append(x.cohab.tolist())

    n = len(fig.data)
    age_buttons = [dict(label=f"Age {label(b)}", method="restyle",
                        args=[{"visible": [bands[i // 2] == b for i in range(n)]}]) for b in bands]
    x_titles = {"couple": "% of women living in a couple", "cohab": "% of women cohabiting (not married)"}
    x_buttons = [dict(label=t, method="update",
                      args=[{"x": xs[k]}, {"xaxis.title.text": t, "xaxis2.title.text": t}])
                 for k, t in x_titles.items()]
    fig.update_layout(
        template="plotly_white",
        title=dict(text="Conditional birth rate vs women in a couple, England and Wales", x=0.01),
        updatemenus=[
            dict(buttons=age_buttons, active=1, x=0.62, xanchor="right", y=1.2, yanchor="bottom"),
            dict(buttons=x_buttons, active=0, x=1.0, xanchor="right", y=1.2, yanchor="bottom"),
        ],
        margin=dict(t=130, r=80), hovermode="closest",
    )
    for j in (1, 2):
        fig.update_xaxes(title_text=x_titles["couple"], ticksuffix="%", row=1, col=j)
        fig.update_yaxes(title_text="Conditional ASFR (% per year)", ticksuffix="%", rangemode="tozero",
                         row=1, col=j)
    return fig


if __name__ == "__main__":
    d = load()
    d.round(3).to_csv(OUTDIR / "coupling_vs_cond_asfr_ew.csv", index=False)
    coupling_by_age_ew.OUTDIR = OUTDIR
    coupling_by_age_ew.write_html(plot(d), "coupling_vs_cond_asfr_ew.html")
    print(d[d.year.isin([2002, 2010, 2019, 2024, 2025])].round(2).to_string())
