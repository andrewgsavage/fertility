"""Where young adults (18-24) in Europe live: with a partner, with their parents, alone, or other.

No single Eurostat table splits young adults this way, so two surveys are combined:

  lfst_hhindws_living.csv  EU-LFS, persons by household composition, 2006-2025, thousands
      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfst_hhindws/A.M+F+T.Y18-24+Y25-49.A1+A1_NCH+A_CPL+A_OTH+TOTAL.THS_PER.POP.?format=SDMX-CSV
      partner = A_CPL (adult in a couple household, with or without children)
      alone   = A1_NCH (one adult, no resident children)
  ilc_lvps08.csv           EU-SILC, share of young adults living with their parents, 2003-2025, %
      https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_lvps08?format=SDMX-CSV

Ages 18-24 only: the LFS's next band is 25-49 and SILC does not publish the with-parents share
for it. Other = 100 minus partner, alone and with parents (lone parents, flatshares, other
relatives). Other also absorbs the gap between the two surveys, so it goes negative where they
disagree; countries where it is below -5 points at either end are left out of the chart and
region means (keep = False in the CSV).

The change runs 2010 to 2019 (or the latest year from 2017 on), before the SILC break in
Germany (2020) and the EU-LFS household methodology break (2021), which shift some series by
10-30 points (Sweden, the Netherlands, Germany).

Outputs (eurostat/outputs/):
  living_arrangements_europe.csv          shares by country, sex and year
  living_arrangements_europe_change.csv   change 2010 -> 2019 per country, then region means
  living_arrangements_europe_change.html  change by country, sex dropdown
"""

import pandas as pd
import plotly.graph_objects as go

from common.plotting import write_html
from eurostat.scripts._common import DATA, NAMES, OUTDIR

BASE_YEAR, END_YEAR, MIN_END = 2010, 2019, 2017
MIN_OTHER = -5
CATS = ["partner", "parents", "alone", "other"]
LABELS = {"partner": "With a partner", "parents": "With parents", "alone": "Alone",
          "other": "Other (lone parent, shared, relatives)"}
COLORS = {"partner": "#4c78a8", "parents": "#f58518", "alone": "#54a24b", "other": "#bab0ac"}
REGION = {
    "Nordic": ["DK", "FI", "NO", "SE", "IS"],
    "Western": ["AT", "BE", "CH", "DE", "FR", "IE", "LU", "NL", "UK"],
    "Southern": ["CY", "EL", "ES", "IT", "MT", "PT"],
    "Central & Eastern": ["BG", "CZ", "EE", "HR", "HU", "LT", "LV", "PL", "RO", "SI", "SK"],
    "Balkans & Türkiye": ["AL", "BA", "ME", "MK", "RS", "TR"],
}
CODE_REGION = {c: r for r, codes in REGION.items() for c in codes}
SEXES = {"T": "Both sexes", "F": "Women", "M": "Men"}


def load():
    h = pd.read_csv(DATA / "lfst_hhindws_living.csv")
    h = h[h.age == "Y18-24"]
    h = h.pivot_table(index=["geo", "sex", "TIME_PERIOD"], columns="phhcomp", values="OBS_VALUE").reset_index()
    h = h.dropna(subset=["TOTAL", "A_CPL", "A1_NCH"])
    h["partner"] = 100 * h.A_CPL / h.TOTAL
    h["alone"] = 100 * h.A1_NCH / h.TOTAL
    h = h.rename(columns={"TIME_PERIOD": "year"})[["geo", "sex", "year", "partner", "alone"]]

    s = pd.read_csv(DATA / "ilc_lvps08.csv")
    s = s[s.age == "Y18-24"].rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "parents"})
    d = h.merge(s[["geo", "sex", "year", "parents"]], on=["geo", "sex", "year"], how="inner")
    d["other"] = 100 - d.partner - d.alone - d.parents
    d = d[d.geo.isin(NAMES)]
    return d[["geo", "sex", "year"] + CATS].sort_values(["geo", "sex", "year"])


def change(d):
    rows = []
    for (g, sx), x in d.groupby(["geo", "sex"]):
        x = x.set_index("year")
        ends = [y for y in x.index if MIN_END <= y <= END_YEAR]
        if BASE_YEAR not in x.index or not ends:
            continue
        last = max(ends)
        r = {"geo": g, "country": NAMES[g], "region": CODE_REGION.get(g, "EU27"), "sex": sx, "latest": last}
        for k in CATS:
            r[f"{k}_{BASE_YEAR}"] = x.at[BASE_YEAR, k]
            r[f"{k}_latest"] = x.at[last, k]
            r[f"d_{k}"] = x.at[last, k] - x.at[BASE_YEAR, k]
        r["keep"] = min(r[f"other_{BASE_YEAR}"], r["other_latest"]) >= MIN_OTHER
        rows.append(r)
    c = pd.DataFrame(rows)
    k = c[c.keep & (c.geo != "EU27_2020")]
    g = k.groupby(["region", "sex"])
    reg = g[[f"d_{k}" for k in CATS]].mean()
    reg["n"] = g.size()
    reg["countries"] = g.geo.agg(" ".join)
    return c, reg.reset_index().assign(country="Region mean (unweighted)")


def plot_change(c):
    fig = go.Figure()
    views = []
    for sx in SEXES:
        x = c[(c.sex == sx) & c.keep].sort_values("d_partner", ascending=False)
        ylab = [f"{r.country} ({BASE_YEAR}-{r.latest})" for r in x.itertuples()]
        start = len(fig.data)
        for k in CATS:
            fig.add_trace(go.Bar(y=ylab, x=x[f"d_{k}"].round(2), orientation="h", name=LABELS[k],
                                 marker_color=COLORS[k], visible=(sx == "T"),
                                 hovertemplate="%{y}: %{x:+.1f} points<extra>" + LABELS[k] + "</extra>"))
        views.append((sx, start, len(fig.data)))
    n = len(fig.data)
    title = lambda sx: f"{SEXES[sx]} aged 18-24: change in where they live, {BASE_YEAR} to {END_YEAR}"
    buttons = [dict(label=SEXES[sx], method="update",
                    args=[{"visible": [a <= i < b for i in range(n)]}, {"title.text": title(sx)}])
               for sx, a, b in views]
    fig.update_layout(template="plotly_white", barmode="relative", title=dict(text=title("T"), x=0.01),
                      updatemenus=[dict(buttons=buttons, active=0, x=0.0, xanchor="left", y=1.0, yanchor="bottom")],
                      legend=dict(orientation="h", x=0, y=-0.08), margin=dict(t=110, l=190))
    fig.update_xaxes(title_text="Change in percentage points", zeroline=True)
    fig.update_yaxes(autorange="reversed")
    return fig


if __name__ == "__main__":
    d = load()
    d.round(3).to_csv(OUTDIR / "living_arrangements_europe.csv", index=False)
    c, reg = change(d)
    pd.concat([c, reg], ignore_index=True).round(2).to_csv(OUTDIR / "living_arrangements_europe_change.csv",
                                                           index=False)
    write_html(plot_change(c), OUTDIR / "living_arrangements_europe_change.html")
    pd.set_option("display.width", 200)
    print(reg.round(1).to_string(index=False))
    print(c[c.sex == "T"][["geo", "keep", "latest"] + [f"d_{k}" for k in CATS]].round(1).to_string(index=False))
