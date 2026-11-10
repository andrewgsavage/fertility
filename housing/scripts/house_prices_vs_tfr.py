"""Real house prices, rents and price-to-income vs total fertility rate, by
country, from the OECD analytical house price indicators.

Inputs (download into housing/data/ — not tracked in git):
  oecd_hpi.csv      OECD analytical house price indicators, annual, all measures
                    https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/.A..?format=csvfilewithlabels
  oecd_hpi_all.csv  same, all frequencies, selected countries (quarterly for the
                    country chart)
                    https://sdmx.oecd.org/public/rest/data/OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0/GBR+NLD+FIN+ITA+KOR+USA+DEU+FRA+ESP+SWE...?format=csvfilewithlabels
  demo_find.csv     Eurostat fertility indicators, TOTFERRT
                    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_find/A.TOTFERRT.?format=SDMX-CSV
  wb_tfr.csv        World Bank SP.DYN.TFRT.IN (JSON), for non-European countries
                    https://api.worldbank.org/v2/country/all/indicator/SP.DYN.TFRT.IN?format=json&per_page=20000&date=1990:2025
  birthssummary2022.xlsx, {2023,2024,2025}birthregistrations.xlsx
                    ONS births in England and Wales (TFR 1938-2022 from the
                    summary tables, 2023-2025 from each year's Table 1)
                    https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/birthsummarytables
                    https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/birthsinenglandandwalesbirthregistrations

Outputs:
  outputs/price_change_vs_tfr_change.html  scatter, % change in real house
      prices / real rents / price-to-income vs change in TFR, START->END
  outputs/price_change_vs_tfr_change.csv   the data behind it
  outputs/country_prices_tfr.html          real house prices and TFR over time,
      country dropdown (UK default)

Run from the housing/ directory.
"""

import json

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

START, END = 2013, 2024

# Non-OECD economies in the OECD file, and aggregates.
EXCLUDE = {"EA", "EA17", "OECD", "BRA", "CHN", "IND", "IDN", "RUS", "SAU", "ZAF"}

ISO2 = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "CHE": "CH", "CZE": "CZ", "DEU": "DE",
    "DNK": "DK", "ESP": "ES", "EST": "EE", "FIN": "FI", "FRA": "FR", "GRC": "EL",
    "HRV": "HR", "HUN": "HU", "IRL": "IE", "ISL": "IS", "ITA": "IT", "LTU": "LT",
    "LUX": "LU", "LVA": "LV", "NLD": "NL", "NOR": "NO", "POL": "PL", "PRT": "PT",
    "ROU": "RO", "SVK": "SK", "SVN": "SI", "SWE": "SE", "TUR": "TR",
}

HIGHLIGHT = {"NLD": "#d62728", "GBR": "#1f77b4", "FIN": "#2ca02c", "KOR": "#9467bd", "ITA": "#ff7f0e"}

MEASURES = {
    "price": "Real house prices",
    "rent": "Real rents",
    "pti": "House price to income ratio",
}


def load_oecd(path, freq="A"):
    h = pd.read_csv(path)
    h = h[h["FREQ"] == freq]
    names = h.drop_duplicates("REF_AREA").set_index("REF_AREA")["Reference area"]

    def pv(m):
        return h[h["MEASURE"] == m].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="OBS_VALUE")

    rhp, hpi, rpi, pti = pv("RHP"), pv("HPI"), pv("RPI"), pv("HPI_YDH")
    # OECD publishes nominal rents only; deflate with the same deflator the
    # real house price index uses (HPI / RHP).
    rent = rpi * rhp / hpi
    return {"price": rhp, "rent": rent, "pti": pti}, names


def load_ons_tfr():
    s = pd.read_excel("data/birthssummary2022.xlsx", "Table_1", header=8)
    s = s.rename(columns={s.columns[0]: "year", s.columns[6]: "tfr"})[["year", "tfr"]]
    s = s[pd.to_numeric(s["year"], errors="coerce").notna()]
    s["year"] = s["year"].astype(int)
    rows = []
    for y in (2023, 2024, 2025):
        t = pd.read_excel(f"data/{y}birthregistrations.xlsx", "Table_1", header=5)
        col = [c for c in t.columns if str(c).startswith("Total Fertility Rate")][0]
        rows.append({"year": y, "tfr": float(t.loc[t.iloc[:, 1] == "ENGLAND AND WALES", col].iloc[0])})
    s = pd.concat([s, pd.DataFrame(rows)])
    return pd.to_numeric(s.set_index("year")["tfr"], errors="coerce").dropna().sort_index()


def load_tfr():
    """TFR by ISO3 x year: Eurostat for Europe, ONS (England & Wales) for the
    UK, World Bank otherwise. World Bank figures are UN estimates and run
    ~0.1 above ONS for the UK, so they are only the fallback."""
    w = json.load(open("data/wb_tfr.csv"))[1]
    wb = pd.DataFrame([{"iso": d["countryiso3code"], "year": int(d["date"]), "tfr": d["value"]} for d in w])
    wb = wb[wb["iso"] != ""].dropna().pivot_table(index="iso", columns="year", values="tfr")
    wb["source"] = "World Bank"

    es = pd.read_csv("data/demo_find.csv").pivot_table(index="geo", columns="TIME_PERIOD", values="OBS_VALUE")
    es = es.reindex([ISO2.get(i) for i in wb.index])
    es.index = wb.index
    es["source"] = "Eurostat"

    tfr = wb.copy()
    has_es = es[[START, END]].notna().all(axis=1)
    tfr.loc[has_es] = es.loc[has_es, tfr.columns]

    ons = load_ons_tfr()
    tfr.loc["GBR", [c for c in tfr.columns if c != "source"]] = ons.reindex(
        [c for c in tfr.columns if c != "source"]).values
    tfr.loc["GBR", "source"] = "ONS (England & Wales)"
    return tfr, ons


def change_table(measures, names, tfr):
    d = pd.DataFrame({
        k: (m[END] / m[START] - 1) * 100 for k, m in measures.items()
    })
    d["tfr0"] = tfr[START]
    d["tfr1"] = tfr[END]
    d["dtfr"] = tfr[END] - tfr[START]
    d["tfr_source"] = tfr["source"]
    d = d.drop(EXCLUDE, errors="ignore").dropna(subset=["price", "dtfr"])
    d["name"] = names.reindex(d.index)
    return d


def scatter(d):
    fig = go.Figure()
    buttons = []
    keys = list(MEASURES)
    for i, (key, label) in enumerate(MEASURES.items()):
        g = d.dropna(subset=[key])
        colors = [HIGHLIGHT.get(c, "#8c8c8c") for c in g.index]
        sizes = [13 if c in HIGHLIGHT else 9 for c in g.index]
        fig.add_trace(go.Scatter(
            x=g[key], y=g["dtfr"], text=g.index, customdata=g[["name", "tfr0", "tfr1", "tfr_source"]],
            mode="markers+text", textposition="top center", textfont=dict(size=10, color=colors),
            marker=dict(size=sizes, color=colors), visible=(i == 0), showlegend=False,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" + label + f" {START}-{END}: " + "%{x:+.0f}%<br>"
                + f"TFR {START} " + "%{customdata[1]:.2f} → " + f"{END} " + "%{customdata[2]:.2f} (%{y:+.2f})"
                + "<br>TFR source: %{customdata[3]}<extra></extra>"
            ),
        ))
        r = g[key].corr(g["dtfr"])
        title = f"{label} vs fertility, {START}-{END}: r = {r:+.2f} across {len(g)} countries"
        buttons.append(dict(
            label=label, method="update",
            args=[{"visible": [j == i for j in range(len(keys))]},
                  {"title.text": title, "xaxis.title.text": f"Change in {label.lower()}, {START}-{END} (%)"}],
        ))
    r0 = d["price"].corr(d["dtfr"])
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"{MEASURES['price']} vs fertility, {START}-{END}: r = {r0:+.2f} across {len(d)} countries",
                   x=0.02, y=0.98, yref="container", yanchor="top", font=dict(size=14)),
        xaxis=dict(title=f"Change in real house prices, {START}-{END} (%)", zeroline=True),
        yaxis=dict(title=f"Change in TFR, {START}-{END}", zeroline=True),
        margin=dict(t=100, r=20, l=60, b=50),
        updatemenus=[dict(buttons=buttons, direction="down", x=0, xanchor="left", y=1.02, yanchor="bottom")],
    )
    fig.write_html("outputs/price_change_vs_tfr_change.html", include_plotlyjs="cdn",
                   default_width="100%", default_height="100%", config={"responsive": True})


COUNTRIES = ["GBR", "NLD", "FIN", "ITA", "KOR", "USA", "DEU", "FRA", "ESP", "SWE"]


def country_chart(tfr):
    qm, names = load_oecd("data/oecd_hpi_all.csv", freq="Q")

    def qdate(cols):
        return pd.PeriodIndex([c.replace("-", "") for c in cols], freq="Q").to_timestamp(how="end")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[0.55, 0.45],
                        subplot_titles=("Real house prices and rents (index, 2015 = 100)", "Total fertility rate"))
    per_country = 4
    buttons = []
    for i, iso in enumerate(COUNTRIES):
        vis = i == 0
        for key, color, dash in (("price", "#1f77b4", "solid"), ("rent", "#ff7f0e", "dot")):
            s = qm[key].loc[iso].dropna()
            s = s[s.index >= "1990"]
            fig.add_trace(go.Scatter(
                x=qdate(s.index), y=s.values, name=MEASURES[key], line=dict(color=color, dash=dash),
                visible=vis, legendgroup=key, showlegend=True,
                hovertemplate=MEASURES[key] + " %{y:.0f}<extra></extra>",
            ), row=1, col=1)
        s = qm["price"].loc[iso].dropna()
        s = s[s.index >= "1990"]
        peak = s.idxmax()
        fig.add_trace(go.Scatter(
            x=[qdate([peak])[0]], y=[s.max()], mode="markers+text", text=[f"peak {peak}"],
            textposition="top center", marker=dict(color="#1f77b4", size=8), visible=vis,
            showlegend=False, hoverinfo="skip",
        ), row=1, col=1)
        t = tfr.loc[iso].drop("source").dropna().astype(float)
        t = t[t.index >= 1990]
        fig.add_trace(go.Scatter(
            x=pd.to_datetime([f"{y}-07-01" for y in t.index]), y=t.values, name="TFR",
            line=dict(color="#2ca02c"), visible=vis, showlegend=False,
            hovertemplate="TFR %{y:.2f}<extra></extra>",
        ), row=2, col=1)
        label = names.get(iso, iso)
        src = tfr.loc[iso, "source"]
        buttons.append(dict(
            label=label, method="update",
            args=[{"visible": [j // per_country == i for j in range(per_country * len(COUNTRIES))]},
                  {"title.text": f"{label}: real house prices peaked {peak}; TFR source: {src}"}],
        ))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=buttons[0]["args"][1]["title.text"], x=0.02, y=0.98, yref="container",
                   yanchor="top", font=dict(size=14)),
        legend=dict(orientation="h", y=-0.08),
        margin=dict(t=120, r=20, l=60, b=40),
        hovermode="x unified",
        updatemenus=[dict(buttons=buttons, direction="down", x=0, xanchor="left", y=1.07, yanchor="bottom")],
    )
    fig.write_html("outputs/country_prices_tfr.html", include_plotlyjs="cdn",
                   default_width="100%", default_height="100%", config={"responsive": True})


def main():
    measures, names = load_oecd("data/oecd_hpi.csv")
    tfr, ons = load_tfr()
    d = change_table(measures, names, tfr)
    d.round(3).sort_values("price").to_csv("outputs/price_change_vs_tfr_change.csv")
    print(d.round(2).sort_values("price").to_string())
    for k in MEASURES:
        g = d.dropna(subset=[k])
        print(k, len(g), round(g[k].corr(g["dtfr"]), 2))
    print("NL price rank", d["price"].rank(ascending=False)["NLD"], "of", len(d),
          "| NL TFR-fall rank", d["dtfr"].rank()["NLD"])
    print(ons.loc[2005:])
    scatter(d)
    country_chart(tfr)


if __name__ == "__main__":
    main()
