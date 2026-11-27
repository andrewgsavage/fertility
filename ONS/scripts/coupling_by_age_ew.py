"""Share of women and men living in a couple, by 5-year age group, England and Wales, 2002-2025.

ONS, Population estimates by marital status and living arrangements, England and Wales
(Labour Force Survey weighted to mid-year population estimates), tables 5 (males) and
6 (females). Living in a couple = married or civil partnered + cohabiting, regardless of
legal marital status. The youngest group is 16-29 up to 2024 and 18-29 in 2025.

Input (download into ONS/data/families/ - not tracked in git):
  maritalstatuslivingarrangements2002to2025englandandwales.xlsx
    https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesbymaritalstatusandlivingarrangements
"""

import pathlib

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.plotting import write_html
from common.paths import data_dir

ROOT = pathlib.Path(__file__).resolve().parent.parent
XLSX = data_dir("ONS") / "families" / "maritalstatuslivingarrangements2002to2025englandandwales.xlsx"
OUTDIR = ROOT / "outputs"

SHEETS = {"6": "Women", "5": "Men"}
AGES = ["16 to 29", "30 to 34", "35 to 39", "40 to 44", "45 to 49"]
COLORS = dict(zip(AGES, ["#440154", "#3b528b", "#21918c", "#5ec962", "#c8a800"]))


def load():
    rows = []
    for sheet, sex in SHEETS.items():
        x = pd.read_excel(XLSX, sheet_name=sheet, header=9)
        x = x.rename(columns={x.columns[0]: "arr", x.columns[1]: "age"})
        x["age"] = x.age.replace({"18 to 29": "16 to 29"})
        est = [c for c in x.columns if str(c).endswith("Estimate")]
        long = x.melt(id_vars=["arr", "age"], value_vars=est, var_name="year", value_name="n")
        long["year"] = long.year.str[:4].astype(int)
        long["n"] = pd.to_numeric(long.n, errors="coerce")
        long = long.dropna(subset=["n"])
        long["status"] = long.arr.map(lambda a: "married" if "Married" in a and a.startswith("Living")
                                      else "cohabiting" if a.startswith("Living") else "not in couple")
        t = long.pivot_table(index=["age", "year"], columns="status", values="n", aggfunc="sum").reset_index()
        t["total"] = t[["married", "cohabiting", "not in couple"]].sum(axis=1)
        t["couple"] = 100 * (t.married + t.cohabiting) / t.total
        t["cohab"] = 100 * t.cohabiting / t.total
        t["sex"] = sex
        rows.append(t)
    d = pd.concat(rows)
    return d[d.age.isin(AGES)][["sex", "age", "year", "couple", "cohab"]]


def plot(d):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=list(SHEETS.values()))
    for j, sex in enumerate(SHEETS.values(), start=1):
        for a in AGES:
            x = d[(d.sex == sex) & (d.age == a)].sort_values("year")
            label = a.replace(" to ", "-")
            fig.add_trace(go.Scatter(
                x=x.year, y=x.couple, mode="lines", name=label, legendgroup=a, showlegend=j == 1,
                line=dict(color=COLORS[a], width=2),
                customdata=x.cohab,
                hovertemplate=f"{sex} {label}, %{{x}}: %{{y:.1f}}% in a couple "
                              "(%{customdata:.1f}% cohabiting)<extra></extra>"), row=1, col=j)
            fig.add_trace(go.Scatter(
                x=x.year, y=x.cohab, mode="lines", name=label + " cohabiting", legendgroup=a,
                showlegend=False, line=dict(color=COLORS[a], width=1.2, dash="dot"),
                hovertemplate=f"{sex} {label}, %{{x}}: %{{y:.1f}}% cohabiting<extra></extra>"), row=1, col=j)
    fig.update_yaxes(ticksuffix="%", range=[0, 90])
    fig.update_yaxes(title_text="% living in a couple (solid) / cohabiting (dotted)", row=1, col=1)
    fig.update_layout(template="plotly_white", title="Living in a couple by age, England and Wales",
                      legend=dict(title="Age", x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=120, t=80), hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    d.round(2).to_csv(OUTDIR / "coupling_by_age_ew.csv", index=False)
    write_html(plot(d), OUTDIR / "coupling_by_age_ew.html")
    print(d[d.year.isin([2002, 2010, 2019, 2025])].pivot_table(
        index=["sex", "age"], columns="year", values="couple").round(1).to_string())
    print(d[d.year.isin([2002, 2010, 2019, 2025])].pivot_table(
        index=["sex", "age"], columns="year", values="cohab").round(1).to_string())
