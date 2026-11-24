"""Where young adults live: with a partner, with their parents, alone, or other, by sex,
single-year age and year, from national registers (Netherlands, Finland) and the US CPS.

  Netherlands  CBS StatLine 37620, persons in households by position, 1 January 1995-2025
               https://opendata.cbs.nl/ODataApi/odata/37620/TypedDataSet (nl_37620_pos_*.json)
               partner = married + unmarried partners (with or without children)
               parents = thuiswonend kind (child living at home)
               alone   = alleenstaand (one-person household)
               other   = lone parent, other household member, institutional household
  Finland      Statistics Finland 12c6, population by family status, 31 December 1992-2025
               https://pxdata.stat.fi/PxWeb/api/v1/en/StatFin/perh/12c6.px (fi_12c6_status.json)
               partner = spouses + cohabiting partners; parents = child in a family;
               alone = not in a family, lives alone;
               other = lone parent, not in a family and not alone, institutional/unclassified
  US           Census Bureau CPS ASEC Table AD-3, 18-24 and 25-34 only, 1967-2023
               https://www2.census.gov/programs-surveys/demo/tables/families/time-series/adults/ad3-{18-24,25-34}.xls
               partner = living with spouse + with partner; parents = child of householder;
               alone = living alone; other = with other relatives + with nonrelatives

Run NSO/scripts/download.py first. Outputs (NSO/outputs/):
  living_arrangements_nso.csv               shares (%) by country, sex, age, year
  living_arrangements_nso_change.csv        change in points, 2010 -> latest, bands
  living_arrangements_nso_{women,men}.html  stacked shares over time, country/age dropdown
  living_arrangements_nso_change_by_age.html change 2010 -> latest by single age
"""

import json

import pandas as pd
import plotly.graph_objects as go

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("NSO")
OUTDIR = outputs_dir("NSO")

CATS = ["partner", "parents", "alone", "other"]
LABELS = {"partner": "With a partner", "parents": "With parents", "alone": "Alone",
          "other": "Other (lone parent, relatives, shared, institution)"}
COLORS = {"partner": "#4c78a8", "parents": "#f58518", "alone": "#54a24b", "other": "#bab0ac"}
BANDS = {"18-24": (18, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39), "25-34": (25, 34)}
SINGLE = range(18, 40)
BASE_YEAR = 2010


def netherlands():
    ages = {r["Key"]: r["Title"] for r in json.loads((DATA / "nl_37620_leeftijd.json").read_text("utf-8"))["value"]}
    rows = []
    for code, sex in [("3000", "Men"), ("4000", "Women")]:
        for r in json.loads((DATA / f"nl_37620_pos_{code}.json").read_text("utf-8"))["value"]:
            lab = ages[r["Leeftijd"]]
            keys = ("TotaalPersonenInHuishoudens_1", "ThuiswonendKind_3", "Alleenstaand_4",
                    "PartnerInNietGehuwdPaarZonderKi_6", "PartnerInGehuwdPaarZonderKinderen_7",
                    "PartnerInNietGehuwdPaarMetKinderen_8", "PartnerInGehuwdPaarMetKinderen_9")
            if not lab.split()[0].isdigit() or "of ouder" in lab or any(r[k] is None for k in keys):
                continue
            partner = sum(r[k] for k in ("PartnerInNietGehuwdPaarZonderKi_6", "PartnerInGehuwdPaarZonderKinderen_7",
                                         "PartnerInNietGehuwdPaarMetKinderen_8", "PartnerInGehuwdPaarMetKinderen_9"))
            total = r["TotaalPersonenInHuishoudens_1"]
            rows.append({"sex": sex, "age": int(lab.split()[0]), "year": int(r["Perioden"][:4]),
                         "partner": partner, "parents": r["ThuiswonendKind_3"], "alone": r["Alleenstaand_4"],
                         "other": total - partner - r["ThuiswonendKind_3"] - r["Alleenstaand_4"], "total": total})
    return pd.DataFrame(rows).assign(country="Netherlands")


def finland():
    j = json.loads((DATA / "fi_12c6_status.json").read_text("utf-8"))
    dims = j["id"]
    idx = pd.MultiIndex.from_product([list(j["dimension"][k]["category"]["index"]) for k in dims], names=dims)
    s = pd.Series(j["value"], index=idx).reset_index(name="n")
    s.columns = ["year", "area", "status", "sex", "age", "content", "n"]
    s = s[s.age != "SSS"]
    w = s.pivot_table(index=["sex", "age", "year"], columns="status", values="n").reset_index()
    out = pd.DataFrame({"sex": w.sex.map({"1": "Men", "2": "Women"}), "age": w.age.astype(int),
                        "year": w.year.astype(int), "partner": w[["1", "2", "3", "4"]].sum(axis=1),
                        "parents": w["6"], "alone": w["7"], "other": w[["5", "8", "9"]].sum(axis=1),
                        "total": w["SSS"]})
    return out.assign(country="Finland")


def us():
    rows = []
    # columns: 5/6 alone, 7/8 spouse, 9/10 child of householder, 11/12 partner, 13/14 other relatives,
    # 15/16 nonrelatives (men/women)
    for t, band in [("ad3-18-24", "18-24"), ("ad3-25-34", "25-34")]:
        x = pd.read_excel(DATA / f"us_{t}.xls", header=None)
        x = x[x[0].astype(str).str.match(r"^\d{4}")]
        x["year"] = x[0].astype(str).str[:4].astype(int)
        x = x.drop_duplicates("year")  # revised ("2021r") rows come first; keep them
        v = x.iloc[:, 5:17].apply(pd.to_numeric, errors="coerce")
        for k, sex in [(0, "Men"), (1, "Women")]:
            c = lambda i: v.iloc[:, i + k].to_numpy()
            part = pd.DataFrame({"year": x.year.to_numpy(), "alone": c(0), "partner": c(2) + c(6), "parents": c(4),
                                 "other": c(8) + c(10)})
            rows.append(part.assign(sex=sex, age=band))
    d = pd.concat(rows, ignore_index=True)
    tot = d[CATS].sum(axis=1)
    for k in CATS:  # rescale so the four add to 100 (published shares are rounded)
        d[k] = 100 * d[k] / tot
    return d.assign(country="US")


def to_shares(d):
    out = [d[d.age.isin(SINGLE)].assign(age=lambda x: x.age.astype(str))]
    for name, (lo, hi) in BANDS.items():
        g = d[d.age.between(lo, hi)].groupby(["country", "sex", "year"])[CATS + ["total"]].sum().reset_index()
        out.append(g.assign(age=name))
    s = pd.concat(out, ignore_index=True)
    for k in CATS:
        s[k] = 100 * s[k] / s.total
    return s.drop(columns="total")


def load():
    d = pd.concat([netherlands(), finland()], ignore_index=True)
    return pd.concat([to_shares(d), us()], ignore_index=True)[["country", "sex", "age", "year"] + CATS]


def change(d):
    rows = []
    for (c, s, a), g in d.groupby(["country", "sex", "age"]):
        g = g.set_index("year")
        if BASE_YEAR not in g.index:
            continue
        last = g.index.max()
        r = {"country": c, "sex": s, "age": a, "base": BASE_YEAR, "latest": last}
        for k in CATS:
            r[f"{k}_{BASE_YEAR}"] = g.at[BASE_YEAR, k]
            r[f"{k}_latest"] = g.at[last, k]
            r[f"d_{k}"] = g.at[last, k] - g.at[BASE_YEAR, k]
        rows.append(r)
    return pd.DataFrame(rows)


OPTIONS = [("Netherlands", a) for a in BANDS] + [("Finland", a) for a in BANDS] + [("US", "18-24"), ("US", "25-34")]
DEFAULT = ("Netherlands", "25-29")


def plot_stack(d, sex):
    d = d[d.sex == sex]
    fig = go.Figure()
    data = {}
    for c, a in OPTIONS:
        x = d[(d.country == c) & (d.age == a)].sort_values("year")
        data[(c, a)] = (x.year.tolist(), [x[k].round(2).tolist() for k in CATS])
    xs, ys = data[DEFAULT]
    for i, k in enumerate(CATS):
        fig.add_trace(go.Scatter(x=xs, y=ys[i], name=LABELS[k], mode="lines", stackgroup="one",
                                 line=dict(width=0.5, color=COLORS[k]), fillcolor=COLORS[k],
                                 hovertemplate=LABELS[k] + " %{x}: %{y:.1f}%<extra></extra>"))
    buttons = []
    for c, a in OPTIONS:
        xs, ys = data[(c, a)]
        buttons.append(dict(label=f"{c}, {a}", method="update",
                            args=[{"x": [xs] * len(CATS), "y": ys},
                                  {"title.text": f"{sex} aged {a}, {c}: where they live"}]))
    fig.update_layout(template="plotly_white", title=dict(text=f"{sex} aged {DEFAULT[1]}, {DEFAULT[0]}: where they live",
                                                          x=0.01),
                      updatemenus=[dict(buttons=buttons, active=OPTIONS.index(DEFAULT), x=0.0, xanchor="left",
                                        y=1.01, yanchor="bottom")],
                      legend=dict(orientation="h", x=0, y=-0.12), margin=dict(t=110, b=90), hovermode="x unified")
    fig.update_yaxes(title_text=f"% of {sex.lower()} in the age group", ticksuffix="%", range=[0, 100])
    return fig


def plot_change_by_age(d):
    opts = [(c, s) for c in ["Netherlands", "Finland"] for s in ["Women", "Men"]]
    fig = go.Figure()
    data = {}
    for c, s in opts:
        x = d[(d.country == c) & (d.sex == s) & d.age.str.isdigit()].copy()
        x["age"] = x.age.astype(int)
        last = x.year.max()
        a = x[x.year == BASE_YEAR].set_index("age").sort_index()
        b = x[x.year == last].set_index("age").sort_index()
        data[(c, s)] = (a.index.tolist(), [(b[k] - a[k]).round(2).tolist() for k in CATS], last)
    ages, ys, last = data[opts[0]]
    for i, k in enumerate(CATS):
        fig.add_trace(go.Bar(x=ages, y=ys[i], name=LABELS[k], marker_color=COLORS[k],
                             hovertemplate=LABELS[k] + ", age %{x}: %{y:+.1f} points<extra></extra>"))
    title = lambda c, s, last: f"{s}, {c}: change in share by living arrangement, {BASE_YEAR} to {last}"
    buttons = [dict(label=f"{c}, {s}", method="update",
                    args=[{"y": data[(c, s)][1]}, {"title.text": title(c, s, data[(c, s)][2])}]) for c, s in opts]
    fig.update_layout(template="plotly_white", barmode="relative", title=dict(text=title(*opts[0], last), x=0.01),
                      updatemenus=[dict(buttons=buttons, active=0, x=0.0, xanchor="left", y=1.01, yanchor="bottom")],
                      legend=dict(orientation="h", x=0, y=-0.15), margin=dict(t=110, b=100), hovermode="x unified")
    fig.update_xaxes(title_text="Age", dtick=1)
    fig.update_yaxes(title_text="Change in percentage points", ticksuffix="")
    return fig


if __name__ == "__main__":
    d = load()
    d.round(3).to_csv(OUTDIR / "living_arrangements_nso.csv", index=False)
    ch = change(d)
    ch.round(2).to_csv(OUTDIR / "living_arrangements_nso_change.csv", index=False)
    for sex in ["Women", "Men"]:
        write_html(plot_stack(d, sex), OUTDIR / f"living_arrangements_nso_{sex.lower()}.html")
    write_html(plot_change_by_age(d), OUTDIR / "living_arrangements_nso_change_by_age.html")
    pd.set_option("display.width", 200)
    print(ch[~ch.age.str.isdigit()][["country", "sex", "age", "latest"] + [f"d_{k}" for k in CATS]]
          .round(1).to_string(index=False))
