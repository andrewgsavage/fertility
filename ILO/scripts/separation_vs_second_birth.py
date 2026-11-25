"""Change in second-birth rates at 30-44 against change in separation and lone motherhood,
by country, 2010 to 2019 (or the last year before 2019 that both series have).

y: second births per woman with one child, ages 30-44 (HFD mi.txt, m2x), pooled over single
   ages with the HFD parity-1 exposures (exposRRpa.txt, E1x) as weights; % change.
x, left: women 35-44 divorced or separated, % of ever married (ILO, separated_ilo.py),
   change in points. Legal marital status in most of the countries shown.
x, right: lone mothers, % of women 25-49 living with children (Eurostat lfst_hhindws,
   lone_parents_divorce_europe.py), change in points. Stops at 2019, before the 2021 EU-LFS break.

Inputs (not tracked in git): HFD/data/HFD/mi.txt and exposRRpa.txt (humanfertility.org),
plus ILO/outputs/separated_ilo.csv and eurostat/outputs/lone_parents_europe.csv.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.country_names import COUNTRY_NAMES
from common.hfd import age_to_int, read_hfd
from common.paths import outputs_dir
from common.plotting import write_html

OUTDIR = outputs_dir("ILO")
START, END, MIN_END = 2010, 2019, 2016
AGES = range(30, 45)
ISO3_TO_HFD = {"DEU": "DEUTNP", "FRA": "FRATNP", "GBR": "GBR_NP"}
EU_TO_HFD = {"AT": "AUT", "BE": "BEL", "BG": "BGR", "CH": "CHE", "CZ": "CZE", "DE": "DEUTNP", "DK": "DNK",
             "EE": "EST", "ES": "ESP", "FI": "FIN", "FR": "FRATNP", "HR": "HRV", "HU": "HUN", "IE": "IRL",
             "LT": "LTU", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT", "SE": "SWE", "SI": "SVN",
             "SK": "SVK", "UK": "GBR_NP"}


def second_birth_rate():
    m = read_hfd("mi.txt", ["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"])
    e = read_hfd("exposRRpa.txt", ["code", "year", "age", "E0x", "E1x", "E2x", "E3x", "E4px"])
    for x in (m, e):
        x["age"] = age_to_int(x["age"])
    d = m.merge(e, on=["code", "year", "age"])
    d = d[d.age.isin(AGES)].dropna(subset=["m2x", "E1x"])
    d["b2"] = d.m2x * d.E1x
    g = d.groupby(["code", "year"])[["b2", "E1x"]].sum()
    return (1000 * g.b2 / g.E1x).rename("rate").reset_index()


def changes(x, rates, col):
    """Per country: x and rate at START and at the last year <= END both have."""
    out = []
    for code, xs in x.groupby("code"):
        r = rates[rates.code == code].set_index("year").rate
        both = sorted(set(xs.year) & set(r.index))
        if START not in both:
            continue
        end = max(y for y in both if y <= END)
        if end < MIN_END:
            continue
        xv = xs.set_index("year")[col]
        out.append({"code": code, "country": COUNTRY_NAMES.get(code, code), "end": end,
                    "x0": xv[START], "x1": xv[end], "r0": r[START], "r1": r[end]})
    c = pd.DataFrame(out)
    c["dx"] = c.x1 - c.x0
    c["dr"] = 100 * (c.r1 / c.r0 - 1)
    return c


def plot(panels):
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.06,
                        subplot_titles=[p[0] for p in panels])
    for j, (_, c, xl) in enumerate(panels, start=1):
        fig.add_trace(go.Scatter(
            x=c.dx, y=c.dr, mode="markers+text", text=c.country, textposition="top center",
            marker=dict(size=9, color="#3b528b"), showlegend=False,
            customdata=c[["end", "x0", "x1", "r0", "r1"]],
            hovertemplate="%{text}, " + str(START) + "-%{customdata[0]}<br>" + xl +
                          ": %{customdata[1]:.1f}% -> %{customdata[2]:.1f}%<br>second-birth rate: "
                          "%{customdata[3]:.0f} -> %{customdata[4]:.0f} per 1,000<extra></extra>"), row=1, col=j)
        fig.update_xaxes(title_text=f"Change in {xl}, points", zeroline=True, row=1, col=j)
    fig.update_yaxes(title_text="% change in second-birth rate, 30-44", zeroline=True, ticksuffix="%", row=1, col=1)
    fig.update_layout(template="plotly_white", height=520, margin=dict(t=80),
                      title=f"Second births at 30-44 vs separation and lone motherhood, {START} to {END} or latest")
    return fig


if __name__ == "__main__":
    rates = second_birth_rate()
    ilo = pd.read_csv(outputs_dir("ILO") / "separated_ilo.csv")
    ilo = ilo[(ilo.sex == "women") & (ilo.age == "35-44")]
    ilo = ilo.assign(code=ilo.ref_area.replace(ISO3_TO_HFD))
    lone = pd.read_csv(outputs_dir("eurostat") / "lone_parents_europe.csv")
    lone = lone[(lone.sex == "Women") & lone.geo.isin(EU_TO_HFD)]
    lone = lone.assign(code=lone.geo.map(EU_TO_HFD))
    a = changes(ilo, rates, "sep_ever")
    b = changes(lone, rates, "lone")
    pd.concat([a.assign(measure="separated_35_44_pct_ever_married"),
               b.assign(measure="lone_mothers_25_49_pct")]).round(2).to_csv(
        OUTDIR / "separation_vs_second_birth.csv", index=False)
    write_html(plot([("Women 35-44 divorced/separated (ILO)", a, "% divorced or separated of ever married"),
                     ("Lone mothers 25-49 (Eurostat)", b, "% lone mothers")]),
               OUTDIR / "separation_vs_second_birth.html", height="520px")
    for c in (a, b):
        print(c.round(1).to_string(index=False))
        print("corr", round(c.dx.corr(c.dr), 2), "n", len(c))
