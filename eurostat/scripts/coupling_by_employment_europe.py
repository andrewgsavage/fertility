"""Share of adults living in a couple, by employment status, and a shift-share of its change.

Persons aged 25-49 (and 18-24) in couple households as a share of all persons in private
households, split by working status: employed full-time, employed part-time, not employed
(unemployed plus inactive; Eurostat does not split these in this table). EU Labour Force
Survey, lfst_hhindws, 2006-2025, by sex.

"In a couple" is Eurostat's household type A_CPL: married or cohabiting couples living on
their own or with their children. Couples living with other adults (e.g. with parents) are
classed as "other type of household", so the share is lower than married-or-cohabiting
shares from other sources, most of all where young couples often live with parents.

Shift-share (symmetric, exact): with s_g the share of the age group in status g and r_g the
couple share in g, the change in the overall couple share between two years is
    dC = sum_g ds_g * mean(r_g)   (composition: change in the employment mix)
       + sum_g mean(s_g) * dr_g   (within: change in coupling inside each status)
using groups full-time / part-time / not employed. Employed persons with no full/part-time
answer are folded in proportionally (shares use FT + PT + not employed as the total).

Input (download into eurostat/data/ - not tracked in git):
  lfst_hhindws_wstatus.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/A.M+F.Y25-49+Y18-24.A_CPL+TOTAL.THS_PER.POP+EMP+EMP_FT+EMP_PT+NEMP.?format=SDMX-CSV

Outputs (eurostat/outputs/):
  coupling_by_employment_europe.html        couple share by status over time, men and women
  coupling_by_employment_shift_share.html   2010 -> latest change split into mix vs within
  coupling_by_employment_shift_share.csv    the numbers behind the bar chart
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("eurostat")
OUT = outputs_dir("eurostat")

NAMES = {
    "AT": "Austria", "BE": "Belgium", "BG": "Bulgaria", "CY": "Cyprus", "CZ": "Czechia",
    "DE": "Germany", "DK": "Denmark", "EE": "Estonia", "EL": "Greece", "ES": "Spain",
    "EU27_2020": "EU27", "FI": "Finland", "FR": "France", "HR": "Croatia", "HU": "Hungary",
    "IE": "Ireland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg", "LV": "Latvia",
    "MT": "Malta", "NL": "Netherlands", "NO": "Norway", "PL": "Poland", "PT": "Portugal",
    "RO": "Romania", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "CH": "Switzerland",
    "RS": "Serbia", "MK": "North Macedonia", "ME": "Montenegro", "TR": "Türkiye", "UK": "United Kingdom",
    "BA": "Bosnia & Herzegovina",
}
GROUPS = {"EMP_FT": "Employed full-time", "EMP_PT": "Employed part-time", "NEMP": "Not employed"}
COLORS = {"EMP_FT": "#1f77b4", "EMP_PT": "#2ca02c", "NEMP": "#d62728", "POP": "#444444"}
SEXES = {"M": "Men", "F": "Women"}
BASE_YEAR = 2010
DEFAULT = "EU27"


def load():
    d = pd.read_csv(DATA / "lfst_hhindws_wstatus.csv")
    d = d[d.geo.isin(NAMES)].assign(country=lambda x: x.geo.map(NAMES))
    p = d.pivot_table(index=["country", "sex", "age", "TIME_PERIOD"], columns=["phhcomp", "wstatus"],
                      values="OBS_VALUE")
    rows = []
    for key, r in p.iterrows():
        rec = dict(zip(["country", "sex", "age", "year"], key))
        for w in ["POP", *GROUPS]:
            rec[f"pop_{w}"] = r.get(("TOTAL", w))
            rec[f"cpl_{w}"] = r.get(("A_CPL", w))
        rows.append(rec)
    return pd.DataFrame(rows)


def shift_share(df, age="Y25-49"):
    """Change in couple share from BASE_YEAR to each country's latest year, by sex."""
    out = []
    d = df[df.age == age].dropna(subset=[f"{k}_{g}" for k in ("pop", "cpl") for g in GROUPS])
    for (country, sex), x in d.groupby(["country", "sex"]):
        x = x.set_index("year")
        if BASE_YEAR not in x.index:
            continue
        y1 = x.index.max()
        if y1 - BASE_YEAR < 10:
            continue
        res = {"country": country, "sex": sex, "age": age, "year0": BASE_YEAR, "year1": y1}
        comp = within = 0.0
        tot = {}
        for t, yr in (("0", BASE_YEAR), ("1", y1)):
            r = x.loc[yr]
            n = sum(r[f"pop_{g}"] for g in GROUPS)
            tot[t] = sum(r[f"cpl_{g}"] for g in GROUPS) / n * 100
            for g in GROUPS:
                res[f"share_{g}_{t}"] = r[f"pop_{g}"] / n * 100
                res[f"rate_{g}_{t}"] = r[f"cpl_{g}"] / r[f"pop_{g}"] * 100
        for g in GROUPS:
            ds = res[f"share_{g}_1"] - res[f"share_{g}_0"]
            dr = res[f"rate_{g}_1"] - res[f"rate_{g}_0"]
            comp += ds / 100 * (res[f"rate_{g}_0"] + res[f"rate_{g}_1"]) / 2
            within += (res[f"share_{g}_0"] + res[f"share_{g}_1"]) / 200 * dr
            res[f"within_{g}"] = (res[f"share_{g}_0"] + res[f"share_{g}_1"]) / 200 * dr
        res.update(couple_0=tot["0"], couple_1=tot["1"], change=tot["1"] - tot["0"],
                   composition=comp, within=within)
        out.append(res)
    return pd.DataFrame(out).round(2)


def plot_lines(df, age="Y25-49"):
    d = df[df.age == age]
    countries = [DEFAULT] + sorted(set(d.country) - {DEFAULT})
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.05,
                        subplot_titles=[f"{s}, aged 25-49" for s in SEXES.values()])
    traces = []
    for c in countries:
        for j, sex in enumerate(SEXES):
            x = d[(d.country == c) & (d.sex == sex)].sort_values("year")
            for g in ["POP", *GROUPS]:
                y = 100 * x[f"cpl_{g}"] / x[f"pop_{g}"]
                name = "All" if g == "POP" else GROUPS[g]
                fig.add_trace(go.Scatter(
                    x=x.year, y=y, mode="lines+markers", name=name, legendgroup=g,
                    showlegend=(j == 0), visible=(c == DEFAULT), marker=dict(size=4),
                    line=dict(color=COLORS[g], width=3 if g == "POP" else 1.8,
                              dash="dot" if g == "POP" else "solid"),
                    hovertemplate=f"{c}, {SEXES[sex].lower()}, {name.lower()} %{{x}}: %{{y:.1f}}%<extra></extra>",
                ), row=1, col=j + 1)
                traces.append(c)
    buttons = [dict(label=c, method="update", args=[{"visible": [t == c for t in traces]},
                                                     {"title.text": f"Living in a couple by employment status: {c}"}])
               for c in countries]
    fig.update_yaxes(ticksuffix="%", title_text="% in a couple household", row=1, col=1)
    fig.update_layout(
        template="plotly_white", title=f"Living in a couple by employment status: {DEFAULT}",
        updatemenus=[dict(buttons=buttons, direction="down", x=0, xanchor="left", y=1.18, yanchor="top")],
        legend=dict(orientation="h", y=-0.12), margin=dict(t=110), hovermode="closest",
    )
    return fig


def plot_shift(ss):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=[f"{s}, aged 25-49" for s in SEXES.values()])
    men = ss[ss.sex == "M"].sort_values("change", ascending=False)
    order = list(men.country)
    for j, sex in enumerate(SEXES):
        x = ss[ss.sex == sex].set_index("country").reindex(order).reset_index()
        for col, name, color in [("composition", "Change in employment mix", "#ff7f0e"),
                                 ("within", "Change within status groups", "#1f77b4")]:
            fig.add_trace(go.Bar(
                y=x.country, x=x[col], orientation="h", name=name, legendgroup=col, showlegend=(j == 0),
                marker_color=color, customdata=x[["change", "year1"]],
                hovertemplate="%{y} " + str(BASE_YEAR) + "-%{customdata[1]}: " + name.lower()
                              + " %{x:+.1f} pts (total %{customdata[0]:+.1f})<extra></extra>",
            ), row=1, col=j + 1)
        fig.add_trace(go.Scatter(
            y=x.country, x=x.change, mode="markers", name="Total change", legendgroup="total",
            showlegend=(j == 0), marker=dict(color="black", symbol="diamond", size=7),
            hovertemplate="%{y}: total %{x:+.1f} pts<extra></extra>",
        ), row=1, col=j + 1)
    fig.update_xaxes(title_text="Percentage points", zeroline=True, zerolinecolor="#888")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        template="plotly_white", barmode="relative", height=760,
        title=f"Change in share living in a couple, {BASE_YEAR} to latest year: employment mix vs within groups",
        legend=dict(orientation="h", y=-0.08), margin=dict(t=90, l=130),
    )
    return fig


if __name__ == "__main__":
    df = load()
    ss = shift_share(df)
    ss.to_csv(OUT / "coupling_by_employment_shift_share.csv", index=False)
    write_html(plot_lines(df), OUT / "coupling_by_employment_europe.html")
    write_html(plot_shift(ss), OUT / "coupling_by_employment_shift_share.html")
    pd.set_option("display.width", 200)
    print(ss[["country", "sex", "year1", "couple_0", "couple_1", "change", "composition", "within",
              "within_EMP_FT", "within_EMP_PT", "within_NEMP", "share_NEMP_0", "share_NEMP_1"]].to_string())
