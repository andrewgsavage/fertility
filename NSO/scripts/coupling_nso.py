"""Share of women and men living with a spouse or partner (married or cohabiting), by
single-year age, from national statistics offices: the original sources behind the FT's
Western coupling series where they are open (see download.py).

  Netherlands  (married + unmarried partners) / persons in households      CBS 37620
  Denmark      persons in married, registered, consensual-union or cohabiting couples
               (FAM100N) / population (BEFOLK1)
  Finland      (spouses + cohabiting partners) / population                Statistics Finland 12c6
  US           living with spouse + living with partner, % of age group    Census AD-3 (CPS ASEC)
               - only 18-24 and 25-34. Partner measure changes in 1996 and 2007.

Outputs: NSO/outputs/coupling_nso.csv (single ages and bands) and a chart per sex with an
age dropdown.
"""

import json
import pathlib

import pandas as pd
import plotly.graph_objects as go

from common.plotting import write_html

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"

BANDS = {"18-24": (18, 24), "20-24": (20, 24), "25-29": (25, 29), "30-34": (30, 34), "35-39": (35, 39),
         "40-44": (40, 44), "25-34": (25, 34), "15-24": (15, 24), "35-44": (35, 44)}
SINGLE = list(range(18, 46))
COLORS = {"Netherlands": "#ff7f0e", "Denmark": "#d62728", "Finland": "#1f77b4", "US": "#2ca02c"}
DEFAULT = "25-29"


def netherlands():
    ages = {r["Key"]: r["Title"] for r in json.loads((DATA / "nl_37620_leeftijd.json").read_text("utf-8"))["value"]}
    rows = []
    for sex, name in [("3000", "Men"), ("4000", "Women")]:
        for r in json.loads((DATA / f"nl_37620_{sex}.json").read_text("utf-8"))["value"]:
            lab = ages[r["Leeftijd"]]
            parts = [r[k] for k in ("PartnerInGehuwdPaarZonderKinderen_7", "PartnerInGehuwdPaarMetKinderen_9",
                                    "PartnerInNietGehuwdPaarZonderKi_6", "PartnerInNietGehuwdPaarMetKinderen_8",
                                    "TotaalPersonenInHuishoudens_1")]
            if not lab.split()[0].isdigit() or "of ouder" in lab or None in parts:
                continue
            married = r["PartnerInGehuwdPaarZonderKinderen_7"] + r["PartnerInGehuwdPaarMetKinderen_9"]
            cohab = r["PartnerInNietGehuwdPaarZonderKi_6"] + r["PartnerInNietGehuwdPaarMetKinderen_8"]
            rows.append({"sex": name, "age": int(lab.split()[0]), "year": int(r["Perioden"][:4]),
                         "couple": married + cohab, "cohab": cohab, "pop": r["TotaalPersonenInHuishoudens_1"]})
    return pd.DataFrame(rows).assign(country="Netherlands")


def denmark():
    f = pd.read_csv(DATA / "dk_fam100n.csv", sep=";", encoding="utf-8-sig")
    f = f[~f.FAMTYP.str.startswith("Single")]
    f["age"] = pd.to_numeric(f.ALDER.str.split().str[0], errors="coerce")
    f["cohab"] = f.FAMTYP.isin(["Couple living in consensual union", "Cohabiting couples"]) * f.INDHOLD
    c = f.dropna(subset=["age"]).groupby(["KØN", "age", "TID"]).agg(couple=("INDHOLD", "sum"),
                                                                     cohab=("cohab", "sum")).reset_index()
    p = pd.read_csv(DATA / "dk_befolk1.csv", sep=";", encoding="utf-8-sig")
    p["age"] = pd.to_numeric(p.ALDER.str.split().str[0], errors="coerce")
    p = p.dropna(subset=["age"]).rename(columns={"INDHOLD": "pop"})[["KØN", "age", "TID", "pop"]]
    d = c.merge(p, on=["KØN", "age", "TID"])
    return d.rename(columns={"KØN": "sex", "TID": "year"}).assign(country="Denmark")


def finland():
    j = json.loads((DATA / "fi_12c6.json").read_text("utf-8"))
    dims = j["id"]
    idx = pd.MultiIndex.from_product([list(j["dimension"][k]["category"]["index"]) for k in dims], names=dims)
    s = pd.Series(j["value"], index=idx).reset_index(name="n")
    s.columns = ["year", "area", "status", "sex", "age", "content", "n"]
    s = s[s.age != "SSS"]
    w = s.pivot_table(index=["sex", "age", "year"], columns="status", values="n").reset_index()
    out = pd.DataFrame({"sex": w.sex.map({"1": "Men", "2": "Women"}), "age": w.age.astype(int),
                        "year": w.year.astype(int), "couple": w[["1", "2", "3", "4"]].sum(axis=1),
                        "cohab": w[["3", "4"]].sum(axis=1), "pop": w["SSS"]})
    return out.assign(country="Finland")


def us():
    rows = []
    for t, band in [("ad3-18-24", "18-24"), ("ad3-25-34", "25-34")]:
        x = pd.read_excel(DATA / f"us_{t}.xls", header=None)
        x = x[x[0].astype(str).str.match(r"^\d{4}")]
        x["year"] = x[0].astype(str).str[:4].astype(int)
        x = x.drop_duplicates("year")  # revised ("2021r") rows come first; keep them
        for sex, sp, pa in [("Men", 7, 11), ("Women", 8, 12)]:
            v = x[[sp, pa]].apply(pd.to_numeric, errors="coerce")
            rows += [{"country": "US", "sex": sex, "age": band, "year": y, "share": s + c, "cohab_share": c}
                     for y, s, c in zip(x.year, v[sp], v[pa])]
    return pd.DataFrame(rows)


def to_shares(d):
    """Single ages -> shares, plus pooled bands."""
    singles = d.assign(share=100 * d.couple / d["pop"], cohab_share=100 * d.cohab / d["pop"])
    out = [singles.assign(age=singles.age.astype(int).astype(str))]
    for name, (lo, hi) in BANDS.items():
        g = d[d.age.between(lo, hi)].groupby(["country", "sex", "year"])[["couple", "cohab", "pop"]].sum()
        g = g.assign(share=100 * g.couple / g["pop"], cohab_share=100 * g.cohab / g["pop"], age=name)
        out.append(g.reset_index())
    return pd.concat(out)[["country", "sex", "age", "year", "share", "cohab_share"]]


def load():
    d = pd.concat([netherlands(), denmark(), finland()], ignore_index=True)
    return pd.concat([to_shares(d), us()], ignore_index=True)


def plot(d, sex):
    d = d[d.sex == sex]
    ages = list(BANDS) + [str(a) for a in SINGLE]
    fig = go.Figure()
    ys = {a: [] for a in ages}
    for c, col in COLORS.items():
        x = d[d.country == c]
        years = sorted(x.year.unique())
        for a in ages:
            v = x[x.age == a].set_index("year").share
            ys[a].append([None if pd.isna(v.get(y)) else float(v.get(y)) for y in years])
        fig.add_trace(go.Scatter(x=years, y=ys[DEFAULT][-1], mode="lines", name=c, line=dict(color=col, width=2),
                                 hovertemplate=c + " %{x}: %{y:.1f}%<extra></extra>"))
    labels = {a: (f"Aged {a}" if "-" in a else f"Age {a}") for a in ages}
    buttons = [dict(label=labels[a], method="update",
                    args=[{"y": ys[a]}, {"yaxis.title.text": f"% of {sex.lower()} aged {a} living with a spouse or partner"}])
               for a in ages]
    fig.update_layout(
        template="plotly_white", title=dict(text=f"{sex} living with a spouse or partner, national registers and CPS", x=0.01),
        updatemenus=[dict(buttons=buttons, active=ages.index(DEFAULT), x=0.0, xanchor="left", y=1.01,
                          yanchor="bottom")],
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"), margin=dict(t=110, r=130), hovermode="closest")
    fig.update_yaxes(title_text=f"% of {sex.lower()} aged {DEFAULT} living with a spouse or partner", ticksuffix="%",
                     range=[0, 100])
    return fig


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    d = load()
    d.round(3).to_csv(OUTDIR / "coupling_nso.csv", index=False)
    for sex in ["Women", "Men"]:
        write_html(plot(d, sex), OUTDIR / f"coupling_nso_{sex.lower()}.html")
    print(d[(d.age == "25-29") & d.year.isin([1995, 2010, 2023])].pivot_table(
        index="country", columns=["sex", "year"], values="share").round(1).to_string())
