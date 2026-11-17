"""Women's average age at leaving the parental home vs the same birth
cohort's fertility, by European country.

TFR and mean age at first birth are period measures: they mix births from
many cohorts, and mean age at first birth only covers women who became
mothers. Here each cohort's leaving age is taken as Eurostat's value for
the year the cohort turned LEAVE_AGE, and compared with that cohort's own
cumulative fertility from the Human Fertility Database:

  ccf35   children per woman by exact age 35 (ccfrVH, CCFR at age 34)
  ccf1_30 first births per woman by exact age 30 (ccfrVHbo, CCFR1 at age 29),
          i.e. the share of the cohort who are mothers by 30; childless
          women count as zero

Inputs:
  eurostat/data/yth_demo_030.csv   (see leaving_home_vs_tfr.py)
  HFD/data/HFD/ccfrVH.txt, ccfrVHbo.txt  (Human Fertility Database bulk
      download; not tracked in git; path set by HFD_DIR)

Outputs:
  outputs/leaving_home_cohort_ccf35.html
  outputs/leaving_home_cohort_ccf1_30.html
  outputs/leaving_home_cohort_corr.csv

Run from the eurostat/ directory.
"""

import os
import pathlib

import pandas as pd
import plotly.graph_objects as go

from leaving_home_vs_tfr import CODE_REGION, NAMES, REGION_COLOR, SEX, fit_line

LEAVE_AGE = 25
MIN_COUNTRIES = 10

HFD_DIR = pathlib.Path(os.environ.get("HFD_DIR", "../HFD/data/HFD"))

# HFD population code -> Eurostat geo code
HFD_TO_GEO = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "CZE": "CZ", "DEUTNP": "DE", "DNK": "DK",
    "EST": "EE", "ESP": "ES", "FIN": "FI", "FRATNP": "FR", "HRV": "HR", "HUN": "HU",
    "IRL": "IE", "ITA": "IT", "LTU": "LT", "NLD": "NL", "NOR": "NO", "POL": "PL",
    "PRT": "PT", "SWE": "SE", "SVN": "SI", "SVK": "SK", "GBR_NP": "UK",
}

# y metric -> (file, column, HFD age, axis title, hover label, hover format, padding, output)
METRICS = {
    "ccf35": ("ccfrVH.txt", "CCFR", 34, "Children per woman by age 35", "By 35", ".2f", 0.1,
              "outputs/leaving_home_cohort_ccf35.html"),
    "ccf1_30": ("ccfrVHbo.txt", "CCFR1", 29, "Share of women who are mothers by age 30", "Mothers by 30",
                ".0%", 0.05, "outputs/leaving_home_cohort_ccf1_30.html"),
}


def read_hfd(fname, column, age):
    df = pd.read_csv(HFD_DIR / fname, sep=r"\s+", skiprows=2, na_values=".", dtype={"Age": str})
    df = df[(df["Age"] == str(age)) & df["Code"].isin(HFD_TO_GEO)]
    return pd.DataFrame({
        "geo": df["Code"].map(HFD_TO_GEO),
        "cohort": df["Cohort"].astype(int),
        "value": df[column].astype(float),
    }).dropna()


def load_leaving():
    age = pd.read_csv("data/yth_demo_030.csv")
    age = age[(age["sex"] == SEX) & age["geo"].isin(NAMES)]
    return pd.DataFrame({
        "geo": age["geo"],
        "cohort": age["TIME_PERIOD"] - LEAVE_AGE,
        "age": age["OBS_VALUE"],
    })


def build(metric):
    fname, column, hfd_age = METRICS[metric][:3]
    df = load_leaving().merge(read_hfd(fname, column, hfd_age), on=["geo", "cohort"]).rename(columns={"value": metric})
    df["name"] = df["geo"].map(NAMES)
    df["region"] = df["geo"].map(CODE_REGION)
    counts = df.groupby("cohort")["geo"].transform("size")
    return df[counts >= MIN_COUNTRIES].sort_values(["cohort", "geo"])


def correlations(df, metric):
    return pd.DataFrame([
        {"cohort": c, "n": len(g), "r": round(g["age"].corr(g[metric]), 2)}
        for c, g in df.groupby("cohort")
    ])


def scatter(df, corr, metric):
    _, _, _, ytitle, ylabel, yfmt, ypad, output = METRICS[metric]
    cohorts = corr["cohort"].tolist()
    x_range = [df["age"].min() - 0.5, df["age"].max() + 0.5]
    y_range = [df[metric].min() - ypad, df[metric].max() + ypad]

    def traces(cohort):
        g = df[df["cohort"] == cohort]
        out = []
        for region, color in REGION_COLOR.items():
            r = g[g["region"] == region]
            out.append(go.Scatter(
                x=r["age"], y=r[metric], text=r["geo"], customdata=r["name"],
                mode="markers+text", textposition="top center",
                textfont=dict(size=10, color=color), marker=dict(size=10, color=color),
                name=region, legendgroup=region,
                hovertemplate=f"<b>%{{customdata}}</b><br>Leaving age %{{x:.1f}}<br>{ylabel} %{{y:{yfmt}}}<extra></extra>",
            ))
        xs, ys, _ = fit_line(g, metric)
        out.append(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#999", dash="dot", width=1.5),
                              name="Linear fit", hoverinfo="skip"))
        return out

    def title(cohort):
        row = corr[corr["cohort"] == cohort].iloc[0]
        return (f"Women born {cohort} (leaving age in {cohort + LEAVE_AGE}): "
                f"r = {row['r']:+.2f} across {int(row['n'])} countries")

    # Restyle arrays wholesale per step (see leaving_home_vs_tfr.scatter).
    def step(cohort):
        ts = traces(cohort)
        data = {k: [list(getattr(t, k)) if getattr(t, k) is not None else None for t in ts]
                for k in ("x", "y", "text", "customdata")}
        return dict(label=str(cohort), method="update", args=[data, {"title.text": title(cohort)}])

    last = cohorts[-1]
    fig = go.Figure(data=traces(last))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title(last), x=0.02, font=dict(size=14)),
        xaxis=dict(title=f"Women's average age at leaving the parental home (year cohort turned {LEAVE_AGE})",
                   range=x_range),
        yaxis=dict(title=ytitle, range=y_range, tickformat=yfmt.replace("f", "f") if "%" not in yfmt else ".0%"),
        legend=dict(orientation="h", y=-0.28),
        margin=dict(t=50, r=20, l=60, b=40),
        sliders=[dict(active=len(cohorts) - 1, currentvalue=dict(prefix="Cohort: "), pad=dict(t=40),
                      steps=[step(c) for c in cohorts])],
    )
    fig.write_html(output, include_plotlyjs="cdn", default_width="100%", default_height="100%",
                   config={"responsive": True})


if __name__ == "__main__":
    corrs = []
    for metric in METRICS:
        df = build(metric)
        corr = correlations(df, metric)
        scatter(df, corr, metric)
        corrs.append(corr.rename(columns={"n": f"n_{metric}", "r": f"r_{metric}"}))
        print(f"\n{metric}")
        print(corr.to_string(index=False))
        last = df[df["cohort"] == corr["cohort"].max()]
        print(last.sort_values("age")[["name", "region", "age", metric]].round(3).to_string(index=False))
    combined = corrs[0].merge(corrs[1], on="cohort", how="outer").sort_values("cohort")
    combined.to_csv("outputs/leaving_home_cohort_corr.csv", index=False)
