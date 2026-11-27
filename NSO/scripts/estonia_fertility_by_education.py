"""Estonia: birth rates and children ever born by women's education, all from Statistics Estonia's
register-based tables (births and population use the same education records).

Tables (PxWeb API, downloaded into NSO/data/ee_*.json if missing):
  RV142U   live births by mother's age group and education, 2017-2025
           https://andmed.stat.ee/api/v1/en/stat/RV142U
  RV0231U  persons by education, sex and age group, 1 January 2018-2026
           https://andmed.stat.ee/api/v1/en/stat/RV0231U
  RV096    women by number of live-born children, education and age group, 1 January 2012-2026
           https://andmed.stat.ee/api/v1/en/stat/RV096
Education: below upper secondary (ISCED 0-2), upper secondary and post-secondary non-tertiary
(3-4), tertiary (5-8); unknown is spread in proportion (births) or dropped (women).
Women in year y = mean of 1 January y and y+1 (2025: 1 January 2025 and 2026). Births at
"40 and over" are divided by women 40-44. Births per woman at 25-44 = 5 x the sum of the
25-29 ... 40+ rates.

Writes NSO/outputs/estonia_fertility_by_education.{csv,html} and
estonia_children_ever_born_by_education.{csv,html}.
"""

import itertools
import json
import urllib.request

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

API = "https://andmed.stat.ee/api/v1/en/stat/"
EDU = {"2": "low", "3": "medium", "4": "tertiary"}
SERIES = [("low", "Below upper secondary", "#eb6834"), ("medium", "Upper secondary", "#eda100"),
          ("tertiary", "Tertiary", "#2a78d6")]
BIRTH_AGES = {"3": "20-24", "4": "25-29", "5": "30-34", "6": "35-39", "7": "40-44"}
POP_AGES = {"3": "20-24", "4": "25-29", "5": "30-34", "6": "35-39", "7": "40-44"}


def fetch(table, query):
    path = data_dir("NSO") / f"ee_{table.lower()}.json"
    if not path.exists():
        body = json.dumps({"query": query, "response": {"format": "json-stat2"}}).encode()
        req = urllib.request.Request(API + table, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    j = json.loads(path.read_text(encoding="utf-8"))
    ids = j["id"]
    cats = []
    for d in ids:
        idx = j["dimension"][d]["category"]["index"]
        cats.append(sorted(idx, key=idx.get))
    df = pd.DataFrame(list(itertools.product(*cats)), columns=ids)
    df["value"] = j["value"]
    return df


def item(code, values):
    return {"code": code, "selection": {"filter": "item", "values": values}}


def births():
    d = fetch("RV142U", [item("Asustuspiirkonna liik", ["1"]), item("Ema vanus", list(BIRTH_AGES)),
                         item("Ema haridustase", ["1", "2", "3", "4"])])
    d["age"] = d["Ema vanus"].map(BIRTH_AGES)
    w = d.pivot_table(index=["Aasta", "age"], columns="Ema haridustase", values="value")
    known = w[["2", "3", "4"]].sum(axis=1)
    for e in ["2", "3", "4"]:
        w[e] = w[e] / known * w["1"]
    b = w[["2", "3", "4"]].rename(columns=EDU).stack().rename("births").reset_index()
    b = b.rename(columns={"Aasta": "year", "Ema haridustase": "ed"})
    b["year"] = b.year.astype(int)
    return b


def women():
    d = fetch("RV0231U", [item("Maakond", ["1"]), item("Haridustase", ["2", "7", "11"]),
                          item("Sugu", ["3"]), item("Vanuserühm", list(POP_AGES))])
    d["ed"] = d.Haridustase.map({"2": "low", "7": "medium", "11": "tertiary"})
    d["age"] = d["Vanuserühm"].map(POP_AGES)
    d["jan1"] = d.Aasta.astype(int)
    p = d.pivot_table(index=["age", "ed"], columns="jan1", values="value")
    mid = {y: (p[y] + p[y + 1]) / 2 for y in range(2018, 2026)}
    mid[2017] = p[2018]
    out = pd.DataFrame(mid).stack().rename("women").reset_index().rename(columns={"level_2": "year"})
    return out


def rates():
    d = births().merge(women(), on=["year", "age", "ed"])
    d["rate"] = d.births / d.women
    old = d[d.age != "20-24"]
    t = (old.groupby(["year", "ed"]).rate.sum() * 5).unstack()
    g = old.groupby(["year", "age"])[["births", "women"]].sum()
    t["all"] = (g.births / g.women).groupby("year").sum() * 5
    y = d[d.age == "20-24"].pivot_table(index="year", columns="ed", values="rate") * 1000
    g = d[d.age == "20-24"].groupby("year")[["births", "women"]].sum()
    y["all"] = g.births / g.women * 1000
    return t, y


def ceb():
    d = fetch("RV096", [item("Naise vanuserühm", ["2", "3", "4"]), item("Naise haridustase", ["2", "3", "4"]),
                        item("Naise elukoht", ["1"]), item("Sünnitatud laste arv", ["1", "2", "3", "4", "5", "6", "7", "8", "9"])])
    w = d.pivot_table(index=["Aasta", "Naise vanuserühm", "Naise haridustase"],
                      columns="Sünnitatud laste arv", values="value").reset_index()
    w["year"] = w.Aasta.astype(int)
    w["age"] = w["Naise vanuserühm"].map({"2": "15-24", "3": "25-34", "4": "35-44"})
    w["ed"] = w["Naise haridustase"].map(EDU)
    w["children_per_woman"] = w["2"]
    known = w[["3", "4", "5", "6", "7", "8"]].sum(axis=1)  # women with a known number of children
    w["childless_pct"] = w["3"] / known * 100
    return w[["year", "age", "ed", "children_per_woman", "childless_pct"]]


def rate_chart(t, y):
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.09,
                        subplot_titles=["Births per woman, ages 25-44", "Births per 1,000 women, ages 20-24"])
    for k, (tab, fmt) in enumerate([(t, ".2f"), (y, ".0f")]):
        for e, lab, color in SERIES + [("all", "All women", "#6b6b6b")]:
            fig.add_trace(go.Scatter(
                x=tab.index, y=tab[e], name=lab, legendgroup=lab, showlegend=k == 0, mode="lines+markers",
                marker=dict(size=7), line=dict(color=color, width=2, dash="dash" if e == "all" else "solid"),
                hovertemplate=f"{lab}, %{{x}}: %{{y:{fmt}}}<extra></extra>",
            ), row=1, col=k + 1)
    fig.update_layout(template="plotly_white", height=460, title="Estonia: birth rates by women's education",
                      title_y=0.98, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1.08, xanchor="left", yanchor="bottom"),
                      margin=dict(l=50, r=20, t=110, b=40))
    return fig


def ceb_chart(c):
    ages = ["25-34", "35-44"]
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.12, horizontal_spacing=0.08,
                        subplot_titles=[f"Children per woman, {a}" for a in ages] + [f"% childless, {a}" for a in ages])
    for r, (col, fmt) in enumerate([("children_per_woman", ".2f"), ("childless_pct", ".0f")]):
        for k, a in enumerate(ages):
            for e, lab, color in SERIES:
                s = c[(c.age == a) & (c.ed == e)].sort_values("year")
                fig.add_trace(go.Scatter(
                    x=s.year, y=s[col], name=lab, legendgroup=lab, showlegend=r == 0 and k == 0,
                    mode="lines+markers", marker=dict(size=6), line=dict(color=color, width=2),
                    hovertemplate=f"{lab}, 1 Jan %{{x}}: %{{y:{fmt}}}<extra></extra>",
                ), row=r + 1, col=k + 1)
    fig.update_layout(template="plotly_white", height=600,
                      title="Estonia: children ever born and childlessness by women's education",
                      title_y=0.98, title_yanchor="top",
                      legend=dict(orientation="h", x=0, y=1.07, xanchor="left", yanchor="bottom"),
                      margin=dict(l=50, r=20, t=120, b=40))
    return fig


def main():
    t, y = rates()
    c = ceb()
    out = outputs_dir("NSO")
    out.mkdir(parents=True, exist_ok=True)
    t.round(3).join(y.round(1).add_suffix("_20_24")).to_csv(out / "estonia_fertility_by_education.csv")
    c.round(3).to_csv(out / "estonia_children_ever_born_by_education.csv", index=False)
    print(t.round(2).to_string())
    print(y.round(0).to_string())
    print(c.pivot_table(index=["age", "ed"], columns="year", values=["children_per_woman", "childless_pct"])
          .round(2).loc[:, (slice(None), [2012, 2017, 2022, 2026])].to_string())
    write_html(rate_chart(t, y), out / "estonia_fertility_by_education.html")
    write_html(ceb_chart(c), out / "estonia_children_ever_born_by_education.html")


if __name__ == "__main__":
    main()
