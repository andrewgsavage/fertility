"""Average age at leaving the parental home vs total fertility rate, by
European country, from Eurostat.

Inputs (download into eurostat/data/ — not tracked in git):
  yth_demo_030.csv  Estimated average age of young people leaving the
                    parental household, by sex
                    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/yth_demo_030?format=SDMX-CSV
  demo_find.csv     Fertility indicators, TOTFERRT (total fertility rate)
                    https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_find/A.TOTFERRT.?format=SDMX-CSV

Outputs:
  outputs/leaving_home_vs_tfr.html    scatter, women's leaving age vs TFR, year slider
  outputs/leaving_home_trend.html     women's leaving age over time, by country
  outputs/leaving_home_corr.csv       per-year Pearson r and country count

Run from the eurostat/ directory.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

AGE_INPUT = "data/yth_demo_030.csv"
TFR_INPUT = "data/demo_find.csv"

SEX = "F"  # women, matching Billari & Kohler (2002) Figure 6
AGGREGATES = {"EU27_2020", "EA21", "EA20", "EA19", "EU28"}

NAMES = {
    "AT": "Austria", "BA": "Bosnia and Herzegovina", "BE": "Belgium", "BG": "Bulgaria",
    "CY": "Cyprus", "CZ": "Czechia", "DE": "Germany", "DK": "Denmark", "EE": "Estonia",
    "EL": "Greece", "ES": "Spain", "FI": "Finland", "FR": "France", "HR": "Croatia",
    "HU": "Hungary", "IE": "Ireland", "IT": "Italy", "LT": "Lithuania", "LU": "Luxembourg",
    "LV": "Latvia", "ME": "Montenegro", "MK": "North Macedonia", "MT": "Malta",
    "NL": "Netherlands", "NO": "Norway", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "RS": "Serbia", "SE": "Sweden", "SI": "Slovenia", "SK": "Slovakia", "TR": "Türkiye",
    "UK": "United Kingdom",
}

# Broad regional grouping used for marker colour.
REGION = {
    "Nordic": ["DK", "FI", "NO", "SE"],
    "Western": ["AT", "BE", "DE", "FR", "IE", "LU", "NL", "UK"],
    "Southern": ["CY", "EL", "ES", "IT", "MT", "PT"],
    "Central & Eastern": ["BG", "CZ", "EE", "HR", "HU", "LT", "LV", "PL", "RO", "SI", "SK"],
    "Balkans & Türkiye": ["BA", "ME", "MK", "RS", "TR"],
}
REGION_COLOR = {
    "Nordic": "#1f77b4",
    "Western": "#2ca02c",
    "Southern": "#d62728",
    "Central & Eastern": "#9467bd",
    "Balkans & Türkiye": "#8c564b",
}
CODE_REGION = {c: r for r, codes in REGION.items() for c in codes}

HIGHLIGHT = ["IT", "ES", "HR", "FR", "UK", "SE", "FI"]


def load():
    age = pd.read_csv(AGE_INPUT)
    age = age[(age["sex"] == SEX) & ~age["geo"].isin(AGGREGATES)]
    age = age.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "age"})[["geo", "year", "age"]]

    tfr = pd.read_csv(TFR_INPUT)
    tfr = tfr.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "tfr"})[["geo", "year", "tfr"]]

    df = age.merge(tfr, on=["geo", "year"], how="inner").dropna()
    df = df[df["geo"].isin(NAMES)]
    df["name"] = df["geo"].map(NAMES)
    df["region"] = df["geo"].map(CODE_REGION)
    return age[age["geo"].isin(NAMES)], df.sort_values(["year", "geo"])


def correlations(df):
    rows = []
    for year, g in df.groupby("year"):
        if len(g) < 10:
            continue
        rows.append({"year": year, "n": len(g), "r": round(g["age"].corr(g["tfr"]), 2)})
    return pd.DataFrame(rows)


def fit_line(g):
    slope, intercept = np.polyfit(g["age"], g["tfr"], 1)
    xs = np.array([g["age"].min(), g["age"].max()])
    return xs, slope * xs + intercept, slope


def scatter(df, corr):
    years = corr["year"].tolist()
    x_range = [df["age"].min() - 0.5, df["age"].max() + 0.5]
    y_range = [df["tfr"].min() - 0.1, df["tfr"].max() + 0.1]

    def traces(year):
        g = df[df["year"] == year]
        out = []
        for region, color in REGION_COLOR.items():
            r = g[g["region"] == region]
            out.append(go.Scatter(
                x=r["age"], y=r["tfr"], text=r["geo"], customdata=r["name"],
                mode="markers+text", textposition="top center",
                textfont=dict(size=10, color=color),
                marker=dict(size=10, color=color),
                name=region, legendgroup=region,
                hovertemplate="<b>%{customdata}</b><br>Leaving age %{x:.1f}<br>TFR %{y:.2f}<extra></extra>",
            ))
        xs, ys, slope = fit_line(g)
        out.append(go.Scatter(
            x=xs, y=ys, mode="lines", line=dict(color="#999", dash="dot", width=1.5),
            name="Linear fit", hoverinfo="skip",
        ))
        return out

    def title(year):
        row = corr[corr["year"] == year].iloc[0]
        return f"{year}: r = {row['r']:+.2f} across {int(row['n'])} countries"

    # The slider restyles every trace's arrays wholesale ("update") rather
    # than animating frames: the number of countries per region changes
    # between years, and frame animation then mismatches markers and labels.
    def step(year):
        ts = traces(year)
        data = {
            "x": [list(t.x) for t in ts],
            "y": [list(t.y) for t in ts],
            "text": [list(t.text) if t.text is not None else None for t in ts],
            "customdata": [list(t.customdata) if t.customdata is not None else None for t in ts],
        }
        return dict(label=str(year), method="update", args=[data, {"title.text": title(year)}])

    last = years[-1]
    fig = go.Figure(data=traces(last))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title(last), x=0.02, font=dict(size=14)),
        xaxis=dict(title="Women's average age at leaving the parental home", range=x_range),
        yaxis=dict(title="Total fertility rate", range=y_range),
        legend=dict(orientation="h", y=-0.28),
        margin=dict(t=50, r=20, l=60, b=40),
        sliders=[dict(
            active=len(years) - 1,
            currentvalue=dict(prefix="Year: "),
            pad=dict(t=40),
            steps=[step(y) for y in years],
        )],
    )
    fig.write_html("outputs/leaving_home_vs_tfr.html", include_plotlyjs="cdn",
                   default_width="100%", default_height="100%", config={"responsive": True})


def trend(age):
    fig = go.Figure()
    for geo, g in age.sort_values("year").groupby("geo"):
        if geo in HIGHLIGHT:
            continue
        fig.add_trace(go.Scatter(
            x=g["year"], y=g["age"], mode="lines", line=dict(color="#d0d0d0", width=1),
            name=NAMES[geo], showlegend=False,
            hovertemplate=f"<b>{NAMES[geo]}</b><br>%{{x}}: %{{y:.1f}}<extra></extra>",
        ))
    for geo in HIGHLIGHT:
        g = age[age["geo"] == geo].sort_values("year")
        color = REGION_COLOR[CODE_REGION[geo]]
        fig.add_trace(go.Scatter(
            x=g["year"], y=g["age"], mode="lines", line=dict(color=color, width=2),
            name=NAMES[geo],
            hovertemplate=f"<b>{NAMES[geo]}</b><br>%{{x}}: %{{y:.1f}}<extra></extra>",
        ))
        end = g.iloc[-1]
        fig.add_annotation(x=end["year"], y=end["age"], text=NAMES[geo], showarrow=False,
                           xanchor="left", xshift=4, font=dict(size=11, color=color))
    fig.update_layout(
        template="plotly_white",
        xaxis=dict(title=None, range=[age["year"].min() - 0.5, age["year"].max() + 3.5]),
        yaxis=dict(title="Women's average age at leaving the parental home"),
        showlegend=False,
        margin=dict(t=20, r=20, l=60, b=40),
    )
    fig.write_html("outputs/leaving_home_trend.html", include_plotlyjs="cdn",
                   default_width="100%", default_height="100%", config={"responsive": True})


if __name__ == "__main__":
    age, df = load()
    corr = correlations(df)
    corr.to_csv("outputs/leaving_home_corr.csv", index=False)
    scatter(df, corr)
    trend(age)
    print(corr.to_string(index=False))
    latest = df[df["year"] == corr["year"].max()]
    _, _, slope = fit_line(latest)
    print(f"{corr['year'].max()} slope: {slope:+.3f} TFR per year of leaving age")
    print(latest.sort_values("age")[["name", "age", "tfr"]].to_string(index=False))
