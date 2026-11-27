"""Previously married people at 30-44: living without a partner vs with a new partner,
England and Wales, 2002-2025.

ONS, Population estimates by marital status and living arrangements, England and Wales
(Labour Force Survey weighted to mid-year population estimates), tables 5 (males) and
6 (females). "Previously married" = legally separated (still married or civil partnered but
not living with the spouse), divorced or widowed. Per age group and sex:

- prev_single: % of all people who are previously married and not living in a couple.
- prev_cohab: % of all people who are previously married and cohabiting with a new partner.
- repartnered: prev_cohab / (prev_cohab + prev_single), % of previously married people who
  have not remarried who live with a new partner. People who remarried are counted as married
  and cannot be told apart from people in a first marriage, so this understates re-partnering.
- not_in_couple: % of all people not living in a couple, for scale.
- married_pct, never_cohab, never_single: % of all people who are married and living with
  the spouse (first marriage or remarried), never married and cohabiting, and never married
  and not in a couple. With prev_single and prev_cohab these five sum to 100.

Marital status is legal status: a cohabiting couple who were never married and split up
shows up only as "never married, not living in a couple". Partners living apart for work,
prison or a care home are also counted as previously married not in a couple (ONS note 10).

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
AGES = ["30 to 34", "35 to 39", "40 to 44"]
COLORS = dict(zip(AGES, ["#3b528b", "#21918c", "#5ec962"]))
PANELS = {"prev_single": "Previously married, not in a couple (% of all)",
          "prev_cohab": "Previously married, cohabiting (% of all)",
          "repartnered": "Cohabiting with a new partner (% of previously married, not remarried)"}


def status(a):
    if a.startswith("Living in a couple: Married"):
        return "married"
    if a.startswith("Living in a couple: Cohabiting - never"):
        return "cohab_never"
    if a.startswith("Living in a couple: Cohabiting - previously"):
        return "cohab_prev"
    if a.startswith("Not living in a couple: Never"):
        return "single_never"
    return "single_prev"


def load():
    rows = []
    for sheet, sex in SHEETS.items():
        x = pd.read_excel(XLSX, sheet_name=sheet, header=9)
        x = x.rename(columns={x.columns[0]: "arr", x.columns[1]: "age"})
        x = x[x.age.isin(AGES)]
        est = [c for c in x.columns if str(c).endswith("Estimate")]
        long = x.melt(id_vars=["arr", "age"], value_vars=est, var_name="year", value_name="n")
        long["year"] = long.year.str[:4].astype(int)
        long["n"] = pd.to_numeric(long.n, errors="coerce")
        long = long.dropna(subset=["n"])
        long["status"] = long.arr.map(status)
        t = long.pivot_table(index=["age", "year"], columns="status", values="n", aggfunc="sum").reset_index()
        total = t[["married", "cohab_never", "cohab_prev", "single_never", "single_prev"]].sum(axis=1)
        t["prev_single"] = 100 * t.single_prev / total
        t["prev_cohab"] = 100 * t.cohab_prev / total
        t["repartnered"] = 100 * t.cohab_prev / (t.cohab_prev + t.single_prev)
        t["not_in_couple"] = 100 * (t.single_never + t.single_prev) / total
        # Remaining shares of all people, so that with prev_single and prev_cohab they sum to 100.
        t["married_pct"] = 100 * t.married / total
        t["never_cohab"] = 100 * t.cohab_never / total
        t["never_single"] = 100 * t.single_never / total
        t["sex"] = sex
        rows.append(t)
    d = pd.concat(rows)
    return d[["sex", "age", "year", "married_pct", "never_cohab", "never_single",
              "prev_cohab", "prev_single", "repartnered", "not_in_couple"]]


def plot(d):
    fig = make_subplots(rows=3, cols=2, shared_xaxes=True, vertical_spacing=0.08,
                        subplot_titles=[f"{s}: {p}" for p in ["previously married, not in a couple",
                                                               "previously married, cohabiting",
                                                               "re-partnered share"] for s in SHEETS.values()])
    for r, col in enumerate(PANELS, start=1):
        for j, sex in enumerate(SHEETS.values(), start=1):
            for a in AGES:
                x = d[(d.sex == sex) & (d.age == a)].sort_values("year")
                label = a.replace(" to ", "-")
                fig.add_trace(go.Scatter(
                    x=x.year, y=x[col], mode="lines", name=label, legendgroup=a,
                    showlegend=(r == 1 and j == 1), line=dict(color=COLORS[a], width=2),
                    hovertemplate=f"{sex} {label}, %{{x}}: %{{y:.1f}}%<extra></extra>"), row=r, col=j)
        fig.update_yaxes(title_text="% of all" if r < 3 else "% of prev. married", row=r, col=1)
    fig.update_yaxes(ticksuffix="%", rangemode="tozero")
    fig.update_layout(template="plotly_white", height=820,
                      title="Previously married at 30-44, England and Wales (legal marital status)",
                      legend=dict(title="Age", x=1.02, y=1.0, xanchor="left", yanchor="top"),
                      margin=dict(r=110, t=90), hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    d.round(2).to_csv(OUTDIR / "union_stability_ew.csv", index=False)
    write_html(plot(d), OUTDIR / "union_stability_ew.html", height="820px")
    print(d[d.year.isin([2002, 2010, 2019, 2025])].round(1).to_string(index=False))
