"""First-birth rates and % of women with a child for England and Wales (ONS cohort Table 3,
via common.ons_table3), and the connected-scatter figure with independent x and y
dropdowns, shared by the coupling-vs-first-birth-rate charts (ONS/scripts/
coupling_vs_cond_asfr_ew.py, ILO/, UN/, eurostat/ and DHS/ equivalents).
"""

import pandas as pd
import plotly.graph_objects as go

from common.ons_table3 import load_table3
from common.plot_colors import PERIOD_COLORSCALE, period_axis

# First-birth rate age ranges (single ages pooled). ONS rates start at 21.
Y_RANGES = {"21-24": (21, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39),
            "40-44": (40, 44), "21-29": (21, 29), "30-39": (30, 39)}
CHILDLESS_AGES = [25, 30, 35, 40]
# 5-year age groups for "% of women aged X with a child" (the measure surveys such as DHS report).
MOTHER_GROUPS = {"20-24": (20, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39)}
RATE_LABEL = "First births per childless woman"


def y_options(ranges):
    """y dropdown: key -> axis label. First-birth rates by age range, then % with a child."""
    opts = {k: f"{RATE_LABEL}, {k}" for k in ranges}
    opts |= {f"mother {a}": f"% of women with a child by {a}" for a in CHILDLESS_AGES}
    return opts


GROUP_OPTS = {f"mothers {g}": f"% of women aged {g} with a child" for g in MOTHER_GROUPS}


def mothers_ew():
    """year -> % of women with at least one child by exact ages 25/30/35/40 (100 - childless;
    ONS table 3, year = cohort + age), and among women in 5-year age groups (unweighted mean
    over single ages; a group needs all its ages)."""
    rows = [{"year": cohort + age, "age": age, "p1": p1}
            for cohort, ages in load_table3().items() for age, (p1, _) in ages.items()]
    d = pd.DataFrame(rows).drop_duplicates(["year", "age"])
    out = d[d.age.isin(CHILDLESS_AGES)].pivot(index="year", columns="age", values="p1")
    out.columns = [f"mother {a}" for a in out.columns]
    # Women aged a (last birthday) are on average a + 0.5: use the mean of p1 at exact a and a + 1.
    nxt = d.assign(age=d.age - 1).set_index(["year", "age"]).p1
    d["mid"] = (d.set_index(["year", "age"]).p1 + nxt).reindex(d.set_index(["year", "age"]).index).values / 2
    for g, (lo, hi) in MOTHER_GROUPS.items():
        s = d[d.age.between(lo, hi)].dropna(subset=["mid"]).groupby("year").mid.agg(["mean", "size"])
        out[f"mothers {g}"] = s["mean"].where(s["size"] == hi - lo + 1)
    return out


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


def dual_dropdown_fig(series, x_opts, y_opts, x_default, y_default, title, x_label,
                      color_by_year=False, auto_hide=False):
    """Connected scatter, one trace per series, with independent x and y dropdowns.

    series: list of dicts with name, color, years (list), x {option: values aligned to years},
    y {option: values}, optional hidden (start in the legend only). With auto_hide, a series
    with no data for the selected y option is moved to the legend. Points where x or y is missing are left out (gaps), so switching one
    axis never misaligns years. x_opts values are suffixed to x_label; y_opts values are the
    full y-axis labels.
    """
    def visible(s, k):
        has = not auto_hide or any(v is not None for v in s["y"][k])
        return "legendonly" if s.get("hidden") or not has else True

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
            marker=marker, connectgaps=False, visible=visible(s, y_default),
            hovertemplate=f"{s['name']} %{{customdata}}<br>x %{{x:.1f}}%<br>y %{{y:.2f}}%<extra></extra>"))

    x_buttons = [dict(label=f"{x_label}: {lab}", method="update",
                      args=[{"x": [s["x"][k] for s in series]}, {"xaxis.title.text": f"{x_label}, {lab}"}])
                 for k, lab in x_opts.items()]
    y_buttons = [dict(label=lab, method="update",
                      args=[{"y": [s["y"][k] for s in series]}
                            | ({"visible": [visible(s, k) for s in series]} if auto_hide else {}),
                            {"yaxis.title.text": lab}])
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
    fig.update_xaxes(title_text=f"{x_label}, {x_opts[x_default]}", ticksuffix="%", rangemode="tozero")
    fig.update_yaxes(title_text=y_opts[y_default], ticksuffix="%", rangemode="tozero")
    return fig
