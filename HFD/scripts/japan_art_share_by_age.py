"""Japan: ART live births as a share of all live births, by mother's age, 2015-2023.

Numerator: JSOG registry cycles resulting in a live birth, by woman's age at treatment
(summary reports, Table 4). Denominator: HFD live births by mother's age (birthsRR.txt),
same calendar year.
"""

import pandas as pd
import plotly.graph_objects as go

from common.hfd import read_hfd
from common.paths import REPO, outputs_dir
from common.plotting import write_html

JSOG = REPO / "research" / "data" / "jsog_japan_art_livebirth_cycles_by_age_2015_2023.csv"
OUTPUT = outputs_dir("HFD") / "japan_art_share_by_age.html"

BANDS = [("25-29", 25, 29), ("30-34", 30, 34), ("35-39", 35, 39), ("40-44", 40, 44), ("All ages", 0, 99)]
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]


def load():
    art = pd.read_csv(JSOG)
    births = read_hfd("birthsRR.txt", na_values=None)
    births = births[births["Code"] == "JPN"].copy()
    births["age"] = births["Age"].astype(str).str.strip("-+").astype(int)
    rows = []
    for year in sorted(art["year"].unique()):
        a = art[art["year"] == year]
        b = births[births["Year"] == year]
        for label, lo, hi in BANDS:
            n_art = a[a["age"].between(lo, hi)]["live_birth_cycles"].sum()
            n_all = b[b["age"].between(lo, hi)]["Total"].sum()
            rows.append({"year": year, "band": label, "art": n_art, "births": n_all, "share": n_art / n_all})
    return pd.DataFrame(rows)


def main():
    df = load()
    fig = go.Figure()
    for (label, _, _), color in zip(BANDS, COLORS):
        sub = df[df["band"] == label]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["share"], name=label, mode="lines+markers",
            line=dict(width=2, color=color, dash="dot" if label == "All ages" else "solid"),
            marker=dict(size=8, color=color, line=dict(width=2, color="white")),
            customdata=sub[["art", "births"]],
            hovertemplate=f"Mother {label}<br>%{{x}}<br>%{{y:.1%}}<br>ART %{{customdata[0]:,}} of %{{customdata[1]:,.0f}} births<extra></extra>",
        ))
    fig.update_layout(
        template="plotly_white", height=420, margin=dict(l=60, r=20, t=40, b=40),
        yaxis=dict(title="ART share of births", tickformat=".0%", rangemode="tozero"),
        xaxis=dict(dtick=1), legend=dict(orientation="h", x=0, y=1.1, xanchor="left"), hovermode="closest",
    )
    write_html(fig, OUTPUT)
    print(df.pivot(index="band", columns="year", values="share").map(lambda v: f"{v:.1%}").to_string())


if __name__ == "__main__":
    main()
