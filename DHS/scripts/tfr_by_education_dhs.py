"""Total fertility rate by women's education, DHS surveys, and how much of each country's fall
came from falls within education groups versus more women being educated.

Indicators (DHS Program API, standard DHS surveys only):
  FE_FRTR_W_TFR_p{1,2,3}.json  https://api.dhsprogram.com/rest/dhs/data?indicatorIds=FE_FRTR_W_TFR&breakdown=all&f=json&perpage=5000&page={1,2,3}
    TFR for the 3 years before the survey, by "Education" (no education, primary, secondary,
    higher = highest level attended).
  ED_EDUC_W.json  https://api.dhsprogram.com/rest/dhs/data?indicatorIds=ED_EDUC_W_NED,ED_EDUC_W_PRI,ED_EDUC_W_SSC,ED_EDUC_W_CSC,ED_EDUC_W_HGH&breakdown=national&f=json&perpage=5000
    Share of women 15-49 by highest level attended (secondary = some + completed).

Decomposition: first vs last survey with a TFR for every group present in both. With shares
s and group TFRs f, the change in sum(s*f) splits into within = sum(mean s * diff f) and
composition = sum(mean f * diff s). Shares are of all women 15-49, not by age, so this is an
approximation; "residual" is the published TFR change minus the two.

Writes DHS/outputs/tfr_by_education_dhs.{csv,html} (country dropdown) and
tfr_by_education_dhs_change.{csv,html} (first vs last survey, per group, plus decomposition).
"""

import json

import pandas as pd
import plotly.graph_objects as go

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("DHS")
OUT = outputs_dir("DHS")
EDU = [
    ("No education", "#eb6834"),
    ("Primary", "#eda100"),
    ("Secondary", "#1baf7a"),
    ("Higher", "#2a78d6"),
]
GROUPS = [e for e, _ in EDU]
TWO = ["No education or primary", "Secondary or higher"]
MIN_SPAN = 10  # years between first and last survey in the change chart
DEFAULT = "Kenya"


def load_tfr():
    d = pd.concat(pd.DataFrame(json.loads((DATA / f"FE_FRTR_W_TFR_p{p}.json").read_text())["Data"])
                  for p in (1, 2, 3))
    d = d[d.SurveyType == "DHS"]
    e = d[d.CharacteristicCategory == "Education"].pivot_table(
        index=["CountryName", "SurveyYear"], columns="CharacteristicLabel", values="Value")
    e["Total"] = d[d.IsTotal == 1].groupby(["CountryName", "SurveyYear"]).Value.first()
    two = d[d.CharacteristicCategory == "Education (2 groups)"].pivot_table(
        index=["CountryName", "SurveyYear"], columns="CharacteristicLabel", values="Value")
    e[TWO] = two.reindex(e.index)[TWO]
    return e[GROUPS + TWO + ["Total"]].dropna(subset=["Total"])


def load_shares():
    d = pd.DataFrame(json.loads((DATA / "ED_EDUC_W.json").read_text())["Data"])
    d = d[d.SurveyType == "DHS"]
    w = d.pivot_table(index=["CountryName", "SurveyYear"], columns="IndicatorId", values="Value")
    s = pd.DataFrame({
        "No education": w.ED_EDUC_W_NED, "Primary": w.ED_EDUC_W_PRI,
        "Secondary": w.ED_EDUC_W_SSC + w.ED_EDUC_W_CSC, "Higher": w.ED_EDUC_W_HGH,
    })
    return s.div(s.sum(axis=1), axis=0)


def change_table(t, s):
    rows = []
    for c, g in t.groupby(level=0):
        g = g.droplevel(0).dropna(subset=["Secondary"])
        if len(g) < 2:
            continue
        y0, y1 = g.index[0], g.index[-1]
        if y1 - y0 < MIN_SPAN:
            continue
        a, b = g.loc[y0], g.loc[y1]
        r = dict(country=c, first=y0, last=y1, total_first=a.Total, total_last=b.Total)
        for e in GROUPS + TWO:
            r[f"{e}_first"], r[f"{e}_last"] = a[e], b[e]
            r[f"{e}_change"] = (b[e] / a[e] - 1) * 100
        both = [e for e in GROUPS if pd.notna(a[e]) and pd.notna(b[e])]
        if (c, y0) in s.index and (c, y1) in s.index and len(both) >= 3:
            s0, s1 = s.loc[(c, y0), both], s.loc[(c, y1), both]
            s0, s1 = s0 / s0.sum(), s1 / s1.sum()
            r["within"] = (((s0 + s1) / 2) * (b[both] - a[both])).sum()
            r["composition"] = (((a[both] + b[both]) / 2) * (s1 - s0)).sum()
            r["low_share_first"] = s.loc[(c, y0), ["No education", "Primary"]].sum() * 100
            r["low_share_last"] = s.loc[(c, y1), ["No education", "Primary"]].sum() * 100
        rows.append(r)
    c = pd.DataFrame(rows)
    c["total_change"] = c.total_last - c.total_first
    c["residual"] = c.total_change - c.within - c.composition
    return c.sort_values("total_change")


def country_chart(t):
    countries = sorted(t.index.get_level_values(0).unique())
    countries = [c for c in countries if t.loc[c].Secondary.notna().sum() >= 2]
    start = countries.index(DEFAULT)
    series = EDU + [("Total", "#6b6b6b")]
    fig = go.Figure()
    for i, c in enumerate(countries):
        g = t.loc[c]
        for e, color in series:
            fig.add_trace(go.Scatter(
                x=g.index, y=g[e], name=e, visible=i == start, legendgroup=e, connectgaps=True,
                mode="lines+markers", marker=dict(size=8),
                line=dict(color=color, width=2, dash="dash" if e == "Total" else "solid"),
                hovertemplate=f"{e}: %{{y:.1f}}<extra></extra>",
            ))
    k = len(series)
    buttons = [dict(label=c, method="update",
                    args=[{"visible": [j // k == i for j in range(len(countries) * k)]},
                          {"title.text": f"{c}: total fertility rate by women's education"}])
               for i, c in enumerate(countries)]
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        title=dict(text=f"{DEFAULT}: total fertility rate by women's education", y=0.98, yanchor="top"),
        yaxis_title="Total fertility rate", yaxis_rangemode="tozero",
        updatemenus=[dict(buttons=buttons, active=start, x=1, y=1.09, xanchor="right",
                          yanchor="bottom", direction="down", showactive=True)],
        legend=dict(orientation="h", x=0, y=1.0, xanchor="left", yanchor="bottom"),
        margin=dict(l=60, r=20, t=120, b=40),
    )
    return fig


def change_chart(c):
    c = c.dropna(subset=["within"]).sort_values("total_change", ascending=False)
    lab = [f"{r.country} ({r.first}-{r.last})" for r in c.itertuples()]
    fig = go.Figure()
    for name, col, color in [("Falls within education groups", "within", "#2a78d6"),
                             ("More women educated", "composition", "#eb6834")]:
        fig.add_trace(go.Bar(y=lab, x=c[col], name=name, orientation="h", marker_color=color,
                             hovertemplate=f"{name}: %{{x:+.2f}}<extra></extra>"))
    fig.add_trace(go.Scatter(
        y=lab, x=c.total_change, name="Published TFR change", mode="markers",
        marker=dict(symbol="line-ns-open", size=14, color="#1a1a1a", line=dict(width=3)),
        hovertemplate="TFR change: %{x:+.1f}<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#6b6b6b", width=1))
    fig.update_layout(
        template="plotly_white", barmode="relative", bargap=0.3,
        title="Change in total fertility rate, first to last DHS survey, split by source",
        title_y=0.99, title_yanchor="top",
        xaxis_title="Change in TFR (children per woman)", height=max(500, 22 * len(c) + 170),
        legend=dict(orientation="h", x=0, y=1.0, xanchor="left", yanchor="bottom"),
        margin=dict(l=230, r=20, t=110, b=50),
    )
    return fig


def group_change_chart(c):
    lo, hi = TWO
    c = c.dropna(subset=[f"{lo}_change", f"{hi}_change"])
    fig = go.Figure()
    lim = [-60, 60]
    fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", line=dict(color="#6b6b6b", dash="dot", width=1),
                             hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=c[f"{lo}_change"], y=c[f"{hi}_change"], mode="markers", showlegend=False,
        marker=dict(size=10, color="#2a78d6", line=dict(color="white", width=1)),
        text=c.country, customdata=c[["first", "last", f"{lo}_first", f"{lo}_last", f"{hi}_first", f"{hi}_last"]],
        hovertemplate=("%{text} %{customdata[0]}-%{customdata[1]}<br>No education or primary: "
                       "%{customdata[2]:.1f} → %{customdata[3]:.1f} (%{x:+.0f}%)<br>Secondary or higher: "
                       "%{customdata[4]:.1f} → %{customdata[5]:.1f} (%{y:+.0f}%)<extra></extra>"),
    ))
    fig.add_annotation(x=-57, y=50, text="Fell more among the<br>less educated", showarrow=False,
                       xanchor="left", font=dict(color="#6b6b6b"))
    fig.add_annotation(x=57, y=-50, text="Fell more among the<br>more educated", showarrow=False,
                       xanchor="right", font=dict(color="#6b6b6b"))
    fig.update_layout(
        template="plotly_white", height=560,
        title="Change in TFR, first to last DHS survey: less vs more educated women",
        xaxis_title="Change, no education or primary (%)", yaxis_title="Change, secondary or higher (%)",
        margin=dict(l=70, r=20, t=70, b=60),
    )
    fig.update_xaxes(range=lim, ticksuffix="%", zeroline=True)
    fig.update_yaxes(range=lim, ticksuffix="%", zeroline=True)
    return fig


def main():
    t = load_tfr()
    s = load_shares()
    OUT.mkdir(parents=True, exist_ok=True)
    t.round(2).to_csv(OUT / "tfr_by_education_dhs.csv")
    c = change_table(t, s)
    c.round(3).to_csv(OUT / "tfr_by_education_dhs_change.csv", index=False)
    pd.set_option("display.width", 250)
    print(c[["country", "first", "last", "total_change", "within", "composition", "residual"]
            + [f"{e}_change" for e in GROUPS]].round(2).to_string())
    write_html(country_chart(t), OUT / "tfr_by_education_dhs.html")
    write_html(change_chart(c), OUT / "tfr_by_education_dhs_decomposition.html")
    write_html(group_change_chart(c), OUT / "tfr_by_education_dhs_change.html")


if __name__ == "__main__":
    main()
