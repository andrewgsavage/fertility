"""Mean age at first marriage against mean age at first birth, by country and year, for
docs/factors/union-to-first-birth.md: trend arrows (x = age at first marriage, y = age at
first birth, with the line where the two are equal) and the gap over time (first birth
minus first marriage, years).

y: period mean age at first birth, HFD mabRRbo.txt (MAB1).
x: women's mean age at first marriage:
   - Eurostat demo_nind FAGEMAR1 (registered first marriages), European HFD countries.
   - Japan: MHLW, mean age of wives at first marriage (research/data/jpn_kor_union_to_first_birth.csv).
   - US, Canada, S Korea, Taiwan, Chile: UN World Marriage Data 2019 SMAM (singulate mean age
     at marriage, from census proportions never married), census years only.

Inputs (not tracked in git): HFD/data/HFD/mabRRbo.txt, eurostat/data/demo_nind.csv
(https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_nind/?format=SDMX-CSV),
UN/data/undesa_pd_2019_wmd_marital_status.xlsx (sheet SMAM).
"""

import pandas as pd
import plotly.colors as pc

from common.hfd import read_hfd
from common.paths import REPO, data_dir, outputs_dir
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows

OUTDIR = outputs_dir("HFD")
FIRST_YEAR = 1970
FIT_FROM = 1990

EUROSTAT = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "CH": "CHE", "CZ": "CZE", "DE": "DEUTNP", "DK": "DNK",
    "EE": "EST", "ES": "ESP", "FI": "FIN", "FR": "FRATNP", "HR": "HRV", "HU": "HUN", "IE": "IRL",
    "IS": "ISL", "IT": "ITA", "LT": "LTU", "NL": "NLD", "NO": "NOR", "PL": "POL", "PT": "PRT",
    "SE": "SWE", "SI": "SVN", "SK": "SVK", "UK": "GBR_NP", "BY": "BLR", "UA": "UKR", "RU": "RUS",
}
UN = {"United States of America": "USA", "Canada": "CAN", "Republic of Korea": "KOR",
      "China, Taiwan Province of China": "TWN", "Chile": "CHL"}
NAMES = {
    "AUT": "Austria", "BEL": "Belgium", "BGR": "Bulgaria", "CHE": "Switzerland", "CZE": "Czechia",
    "DEUTNP": "Germany", "DNK": "Denmark", "EST": "Estonia", "ESP": "Spain", "FIN": "Finland",
    "FRATNP": "France", "HRV": "Croatia", "HUN": "Hungary", "IRL": "Ireland", "ISL": "Iceland",
    "ITA": "Italy", "LTU": "Lithuania", "NLD": "Netherlands", "NOR": "Norway", "POL": "Poland",
    "PRT": "Portugal", "SWE": "Sweden", "SVN": "Slovenia", "SVK": "Slovakia", "GBR_NP": "UK",
    "BLR": "Belarus", "UKR": "Ukraine", "RUS": "Russia", "USA": "US", "CAN": "Canada",
    "KOR": "S Korea", "TWN": "Taiwan", "CHL": "Chile", "JPN": "Japan",
}
LABELS = {"DEUTNP": "DEU", "FRATNP": "FRA", "GBR_NP": "GBR"}
REGIONS = {
    "Americas & East Asia": ["USA", "CAN", "CHL", "JPN", "KOR", "TWN"],
    "Nordic": ["DNK", "FIN", "ISL", "NOR", "SWE"],
    "Western Europe": ["AUT", "BEL", "CHE", "DEUTNP", "FRATNP", "GBR_NP", "IRL", "NLD"],
    "Southern Europe": ["ESP", "ITA", "PRT"],
    "Central & Eastern Europe": ["BGR", "BLR", "CZE", "EST", "HRV", "HUN", "LTU", "POL", "RUS", "SVK",
                                 "SVN", "UKR"],
}
REGION_COLORS = dict(zip(REGIONS, pc.qualitative.D3))


def mab1():
    d = read_hfd("mabRRbo.txt")
    return d.rename(columns={"Code": "code", "Year": "year"})[["code", "year", "MAB1"]].dropna()


def marriage_age():
    n = pd.read_csv(data_dir("eurostat") / "demo_nind.csv")
    n = n[(n.indic_de == "FAGEMAR1") & n.geo.isin(EUROSTAT)]
    eu = pd.DataFrame({"code": n.geo.map(EUROSTAT), "year": n.TIME_PERIOD, "marriage": n.OBS_VALUE,
                       "source": "Eurostat"})
    j = pd.read_csv(REPO / "research" / "data" / "jpn_kor_union_to_first_birth.csv", comment="#")
    j = j[j.country == "Japan"].dropna(subset=["wife_first_marriage_age"])
    jp = pd.DataFrame({"code": "JPN", "year": j.year, "marriage": j.wife_first_marriage_age, "source": "MHLW"})
    s = pd.read_excel(data_dir("UN") / "undesa_pd_2019_wmd_marital_status.xlsx", "SMAM", header=2)
    # Censuses only: survey and estimate rows come from other definitions (the US NSFG rows
    # run 4 years below the 2010 census) and would show as jumps.
    s = s[s["Country or area"].isin(UN) & (s.Sex == "Women") & (s.DataProcess == "Census")].copy()
    s["year"] = s.YearStart
    s = s.drop_duplicates(["Country or area", "year"])
    un = pd.DataFrame({"code": s["Country or area"].map(UN), "year": s.year, "marriage": s.DataValue,
                       "source": "UN SMAM"})
    return pd.concat([eu, jp, un])


def build():
    d = marriage_age().merge(mab1(), on=["code", "year"])
    d = d[d.year >= FIRST_YEAR].sort_values(["code", "year"])
    d["gap"] = d.MAB1 - d.marriage
    series = []
    for region, codes in REGIONS.items():
        for code in codes:
            g = d[d.code == code]
            if len(g) < 2:
                continue
            series.append({"name": f"{NAMES[code]} ({g.source.iloc[0]})", "label": LABELS.get(code, code),
                           "code": code, "group": region, "color": REGION_COLORS[region],
                           "years": g.year.tolist(), "x": {"m": g.marriage.tolist()}, "y": {"b": g.MAB1.tolist()}})
    return d, series


if __name__ == "__main__":
    d, series = build()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    d.round(2).to_csv(OUTDIR / "marriage_age_vs_first_birth_age.csv", index=False)
    lo = 5 * (min(d.marriage.min(), d.MAB1.min()) // 5)
    hi = 5 * -(-max(d.marriage.max(), d.MAB1.max()) // 5)
    write_trend_arrows(
        OUTDIR / "marriage_age_vs_first_birth_age.html", series,
        {"m": "Mean age at first marriage, women"}, {"b": "Mean age at first birth"},
        title=f"Mean age at first birth against mean age at first marriage, {FIRST_YEAR}–latest "
              f"(arrows: trend from {FIT_FROM})",
        start_year=FIT_FROM, x_fmt=".1f", y_fmt=".1f", legend="series",
        layout=dict(xaxis=dict(range=[lo, hi], constrain="domain", title=dict(text="Mean age at first marriage, women")),
                    yaxis=dict(range=[lo, hi], scaleanchor="x", scaleratio=1, constrain="domain",
                               title=dict(text="Mean age at first birth")),
                    shapes=[dict(type="line", x0=lo, y0=lo, x1=hi, y1=hi, layer="below",
                                 line=dict(color="#999999", width=1, dash="dot"))],
                    annotations=[dict(x=hi - 1, y=hi - 1, text="same age", showarrow=False, textangle=-45,
                                      yshift=10, font=dict(size=10, color="#999999"))],
                    legend=dict(x=1.02, y=1, xanchor="left", groupclick="toggleitem"),
                    margin=dict(r=210)))
    panels = []
    for region in REGIONS:
        members = [s for s in series if s["group"] == region]
        if members:
            panels.append({"x": "m", "y": "b", "title": region, "series": members})
    write_ratio_lines(
        OUTDIR / "marriage_age_vs_first_birth_age_gap.html", series, panels, diff=True, cols=2,
        title="Mean age at first birth minus mean age at first marriage (years)", height=1000,
        y_title="First birth − first marriage", hover_label="first birth − first marriage", y_suffix=" yrs")
    last = d.sort_values("year").groupby("code").tail(1).set_index("code")
    first = d[d.year >= FIT_FROM].sort_values("year").groupby("code").head(1).set_index("code")
    print(pd.concat({"from": first[["year", "gap"]], "to": last[["year", "gap", "source"]]}, axis=1).round(1)
          .to_string())
