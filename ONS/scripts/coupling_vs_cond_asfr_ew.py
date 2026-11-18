"""First-birth conditional ASFR against the share of women living in a couple, England
and Wales, 2002 onward: a connected time series with separate age choices for x and y.

y: first births per childless woman, from the parity-hazard reconstruction in
   cond_asfr_uk_ons.py (ONS cohort table 3), single ages 21-45. A y age range pools its
   single ages, weighted by the share of the cohort still childless at the previous age.
x: % of women in an ONS living-arrangements age group living in a couple (married, civil
   partnered or cohabiting), or cohabiting only, from coupling_by_age_ew.py.

dual_dropdown_fig() is shared with ILO/scripts/coupling_vs_cond_asfr.py.

Inputs (ONS/data/, not tracked in git): finalisingcohorttables2024finalforupload.xlsx and
families/maritalstatuslivingarrangements2002to2025englandandwales.xlsx.
"""

import pathlib
import sys

import pandas as pd
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
sys.path.insert(0, str(_SCRIPT_DIR.parent.parent / "HFD" / "scripts"))

import coupling_by_age_ew  # noqa: E402
from cond_asfr_uk_ons import load_table3  # noqa: E402
from plot_colors import PERIOD_COLORSCALE, period_axis  # noqa: E402

OUTDIR = _SCRIPT_DIR.parent / "outputs"
FIRST_YEAR = 2002
# First-birth rate age ranges (single ages pooled). ONS rates start at 21.
Y_RANGES = {"21-24": (21, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39),
            "40-44": (40, 44), "21-29": (21, 29), "30-39": (30, 39)}
X_GROUPS = {"16 to 29": "16-29", "30 to 34": "30-34", "35 to 39": "35-39", "40 to 44": "40-44",
            "45 to 49": "45-49"}


def first_birth_rates(ranges=Y_RANGES):
    """year, age_range -> pooled first-birth conditional rate (%); a range needs all its ages."""
    rows = []
    for cohort, ages in load_table3().items():
        for age, (p1, _) in ages.items():
            if age - 1 in ages:
                p1_prev = ages[age - 1][0]
                rows.append({"year": cohort + age, "age": age,
                             "births": max(0.0, p1 - p1_prev), "at_risk": 100 - p1_prev})
    d = pd.DataFrame(rows)
    out = {}
    for name, (lo, hi) in ranges.items():
        g = d[d.age.between(lo, hi)].groupby("year").agg(births=("births", "sum"), at_risk=("at_risk", "sum"),
                                                         n=("age", "size"))
        g = g[g.n == hi - lo + 1]
        out[name] = 100 * g.births / g.at_risk
    return pd.DataFrame(out)


def dual_dropdown_fig(series, x_opts, y_opts, x_default, y_default, title, x_label, y_label,
                      color_by_year=False):
    """Connected scatter, one trace per series, with independent x and y dropdowns.

    series: list of dicts with name, color, years (list), x {option: values aligned to years},
    y {option: values}. Points where x or y is missing are left out (gaps), so switching one
    axis never misaligns years.
    """
    fig = go.Figure()
    all_years = sorted({y for s in series for y in s["years"]})
    caxis = period_axis(all_years[0], all_years[-1])
    for s in series:
        yrs = s["years"]
        lo, hi = min(yrs), max(yrs)
        size = [5 + 6 * (y - lo) / max(1, hi - lo) for y in yrs]
        marker = dict(size=size, color=s["color"])
        text = None
        if color_by_year:
            marker = dict(size=9, color=yrs, colorscale=PERIOD_COLORSCALE, cmin=caxis[0], cmax=caxis[1],
                          showscale=True, colorbar=dict(title="Year"))
            text = [str(y) if y % 5 == 0 or y in (lo, hi) else "" for y in yrs]
        fig.add_trace(go.Scatter(
            x=s["x"][x_default], y=s["y"][y_default], customdata=yrs, name=s["name"],
            mode="lines+markers+text" if text else "lines+markers", text=text,
            textposition="top center", textfont=dict(size=10),
            line=dict(color="#bbbbbb" if color_by_year else s["color"], width=1.2),
            marker=marker, connectgaps=False,
            hovertemplate=f"{s['name']} %{{customdata}}<br>x %{{x:.1f}}%<br>y %{{y:.2f}}%<extra></extra>"))

    x_buttons = [dict(label=f"{x_label}: {lab}", method="update",
                      args=[{"x": [s["x"][k] for s in series]}, {"xaxis.title.text": f"{x_label}, {lab}"}])
                 for k, lab in x_opts.items()]
    y_buttons = [dict(label=f"{y_label}: {lab}", method="update",
                      args=[{"y": [s["y"][k] for s in series]}, {"yaxis.title.text": f"{y_label}, {lab}"}])
                 for k, lab in y_opts.items()]
    fig.update_layout(
        template="plotly_white", title=dict(text=title, x=0.01),
        updatemenus=[
            dict(buttons=x_buttons, active=list(x_opts).index(x_default), x=0.0, xanchor="left",
                 y=1.01, yanchor="bottom"),
            dict(buttons=y_buttons, active=list(y_opts).index(y_default), x=0.45, xanchor="left",
                 y=1.01, yanchor="bottom"),
        ],
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(t=130, r=150), hovermode="closest",
    )
    fig.update_xaxes(title_text=f"{x_label}, {x_opts[x_default]}", ticksuffix="%")
    fig.update_yaxes(title_text=f"{y_label}, {y_opts[y_default]}", ticksuffix="%", rangemode="tozero")
    return fig


def load():
    rates = first_birth_rates()
    c = coupling_by_age_ew.load()
    c = c[c.sex == "Women"]
    years = sorted(set(rates.index) & set(c.year))
    years = [y for y in years if y >= FIRST_YEAR]
    x = {}
    for group, lab in X_GROUPS.items():
        g = c[c.age == group].set_index("year")
        x[f"couple {lab}"] = [g.couple.get(y) for y in years]
        x[f"cohab {lab}"] = [g.cohab.get(y) for y in years]
    y = {k: [None if pd.isna(v) else v for v in rates[k].reindex(years)] for k in Y_RANGES}
    return {"name": "England and Wales", "color": "#444444", "years": years, "x": x, "y": y}


def plot(s):
    x_opts = {f"couple {lab}": f"in a couple {lab}" for lab in X_GROUPS.values()}
    x_opts |= {f"cohab {lab}": f"cohabiting {lab}" for lab in X_GROUPS.values()}
    return dual_dropdown_fig(
        [s], x_opts, {k: k for k in Y_RANGES}, "couple 30-34", "30-34",
        "First-birth rate vs women in a couple, England and Wales",
        "% of women", "First births per childless woman", color_by_year=True)


if __name__ == "__main__":
    s = load()
    pd.DataFrame({"year": s["years"], **s["x"], **{f"first_birth_{k}": v for k, v in s["y"].items()}}).round(3) \
        .to_csv(OUTDIR / "coupling_vs_cond_asfr_ew.csv", index=False)
    coupling_by_age_ew.OUTDIR = OUTDIR
    coupling_by_age_ew.write_html(plot(s), "coupling_vs_cond_asfr_ew.html")
