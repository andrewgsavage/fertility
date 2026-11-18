"""Share of women and men married or in a consensual union, by country and 5-year age group,
from UN World Marriage Data 2019 (censuses, surveys and register estimates, ~1950-2019).

Coupling for one source (country, survey/census, sex, age group):
  - "Married or in consensual union" / "Married or Living together" when reported as one
    category, else
  - Married + "Consensual union" (or "Living together") when the source reports both.
  - Married alone only in countries where cohabitation is rare (LOW_COHAB: East and South
    Asia, Middle East and North Africa).
Sources that report only legal marital status elsewhere are dropped: the UN flag
"Including_consensual_unions" is not used, because register estimates carrying it (Sweden,
Finland) show legal marriage only. Where several sources cover the same year, a census or
survey is preferred over an estimate.

Input (download into UN/data/ - not tracked in git):
  undesa_pd_2019_wmd_marital_status.xlsx
    https://www.un.org/development/desa/pd/data/world-marriage-data
"""

import pathlib

import pandas as pd
import plotly.colors as pc
import plotly.graph_objects as go

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTDIR = ROOT / "outputs"
XLSX = DATA / "undesa_pd_2019_wmd_marital_status.xlsx"

AGES = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
DEFAULT_AGE = "25-29"
FIRST_YEAR = 1970
MIN_OBS = 3
MIN_UNION = 2.0

COMBINED = {"Married or in consensual union", "Married or Living together"}
UNION = {"Consensual union", "Living together"}
LOW_COHAB = {
    "Japan", "Republic of Korea", "China", "China, Hong Kong SAR", "China, Taiwan Province of China",
    "Singapore", "India", "Pakistan", "Bangladesh", "Sri Lanka", "Nepal", "Indonesia", "Malaysia",
    "Viet Nam", "Thailand", "Myanmar", "Iran (Islamic Republic of)", "Turkey", "Egypt", "Tunisia",
    "Morocco", "Algeria", "Jordan", "Iraq", "Saudi Arabia", "Syrian Arab Republic", "Lebanon", "Kuwait",
    "Qatar", "United Arab Emirates", "Oman", "Bahrain", "Yemen", "Libya", "State of Palestine",
    "Afghanistan",
}
SHORT = {"Republic of Korea": "S Korea", "Iran (Islamic Republic of)": "Iran",
         "United States of America": "US", "United Kingdom": "UK", "Bolivia (Plurinational State of)": "Bolivia",
         "Venezuela (Bolivarian Republic of)": "Venezuela", "United Republic of Tanzania": "Tanzania",
         "China, Hong Kong SAR": "Hong Kong", "China, Taiwan Province of China": "Taiwan",
         "Russian Federation": "Russia", "Republic of Moldova": "Moldova", "Côte d'Ivoire": "Côte d'Ivoire"}
SHOWN = ["Canada", "Mexico", "Chile", "Costa Rica", "Peru", "Colombia", "Brazil", "Turkey", "Denmark",
         "Hungary", "S Korea", "Japan"]
PRIORITY = {"Census": 0, "Survey": 1, "GGS": 1, "Multiround surv": 1, "Dual record": 2, "Estimate": 3}


def load():
    cache = DATA / "marital_status_by_age.pkl"
    if cache.exists():
        d = pd.read_pickle(cache)
    else:
        d = pd.read_excel(XLSX, sheet_name="MARITAL_STATUS_BY_AGE", header=2)
        d.to_pickle(cache)
    d = d.rename(columns={"Country or area": "country", "DataCatalog ShortName": "source",
                          "MaritalStatus": "status", "DataValue": "value"})
    d["age"] = d.AgeGroup.str.strip("[]")
    d = d[d.age.isin(AGES) & d.Sex.isin(["Women", "Men"])]
    # Registers report registered partnerships as "Consensual union": not cohabitation.
    reg = d.status.isin(UNION) & d["Note on Marital Status"].str.contains("registered partnership", case=False,
                                                                        na=False)
    d = d[~reg]
    # DHS releases can carry two tables for one survey (Data Source DHS_HH and
    # DHS_STATcompiler), one folding cohabitation into "Married"; keep them apart.
    key = ["country", "YearStart", "YearEnd", "source", "Data Source", "DataProcess", "Sex", "age"]
    w = d.pivot_table(index=key, columns="status", values="value", aggfunc="first").reset_index()

    combined = w[[c for c in COMBINED if c in w]].max(axis=1, skipna=True)
    union = w[[c for c in UNION if c in w]].max(axis=1, skipna=True)
    married = w.get("Married")
    # A "combined" category smaller than Married is mislabelled: it is the union part.
    small = combined.notna() & married.notna() & (combined < married)
    union = union.where(~small, combined)
    combined = combined.where(~small)
    # A near-zero union share outside low-cohabitation countries means the source
    # did not record cohabitation.
    union = union.where((union >= MIN_UNION) | w.country.isin(LOW_COHAB))
    w["share"] = combined
    has_parts = combined.isna() & married.notna() & union.notna()
    w.loc[has_parts, "share"] = married[has_parts] + union[has_parts]
    low = combined.isna() & union.isna() & married.notna() & w.country.isin(LOW_COHAB)
    w.loc[low, "share"] = married[low]
    w = w.dropna(subset=["share"])
    w = w[w.share.between(0, 100)]

    w["year"] = ((w.YearStart + w.YearEnd) / 2).round().astype(int)
    w["priority"] = w.DataProcess.map(PRIORITY).fillna(2)
    w = w.sort_values("priority").drop_duplicates(["country", "year", "Sex", "age"])
    w = w[w.year >= FIRST_YEAR]
    w["country"] = w.country.replace(SHORT)
    n = w[w.age == DEFAULT_AGE].groupby(["country", "Sex"]).year.nunique().groupby("country").min()
    w = w[w.country.isin(n[n >= MIN_OBS].index)]
    return w[["country", "Sex", "age", "year", "share", "source", "DataProcess"]].rename(columns={"Sex": "sex"})


def plot(d, sex):
    d = d[d.sex == sex]
    order = [c for c in SHOWN if c in set(d.country)] + sorted(set(d.country) - set(SHOWN))
    colors = pc.qualitative.Dark24
    fig = go.Figure()
    ys = {a: [] for a in AGES}
    for i, c in enumerate(order):
        x = d[d.country == c]
        years = sorted(x.year.unique())
        for a in AGES:
            v = x[x.age == a].set_index("year")
            ys[a].append([v.share.get(y) for y in years])
        src = x[x.age == DEFAULT_AGE].set_index("year").source.reindex(years).fillna("").tolist()
        fig.add_trace(go.Scatter(
            x=years, y=ys[DEFAULT_AGE][-1], customdata=src, mode="lines+markers", name=c,
            line=dict(color=colors[i % len(colors)], width=1.5), marker=dict(size=6),
            connectgaps=True, visible=True if c in SHOWN else "legendonly",
            hovertemplate=c + " %{x}: %{y:.1f}% (%{customdata})<extra></extra>"))
    buttons = [dict(label=f"Aged {a}", method="update",
                    args=[{"y": ys[a]}, {"yaxis.title.text": f"% of {sex.lower()} {a} married or in a union"}])
               for a in AGES]
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"{sex} married or in a consensual union (click names to add countries)", x=0.01),
        updatemenus=[dict(buttons=buttons, active=AGES.index(DEFAULT_AGE), x=0.0, xanchor="left",
                          y=1.01, yanchor="bottom")],
        legend=dict(x=1.02, y=1.0, xanchor="left", yanchor="top"),
        margin=dict(t=110, r=170), hovermode="closest")
    fig.update_yaxes(title_text=f"% of {sex.lower()} {DEFAULT_AGE} married or in a union", ticksuffix="%",
                     range=[0, 100])
    return fig


def write_html(fig, name):
    out = OUTDIR / name
    fig.write_html(out, include_plotlyjs="cdn", full_html=True, default_width="100%",
                   default_height="100%", config={"responsive": True})
    html = out.read_text(encoding="utf-8")
    out.write_text(html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1),
                   encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    d = load()
    d.round(2).to_csv(OUTDIR / "coupling_un.csv", index=False)
    for sex in ["Women", "Men"]:
        write_html(plot(d, sex), f"coupling_un_{sex.lower()}.html")
    print(d.country.nunique(), "countries")
    s = d[(d.age == "25-29") & (d.sex == "Women")]
    print(s.groupby("country").year.agg(["min", "max", "count"]).sort_values("count").tail(30).to_string())
