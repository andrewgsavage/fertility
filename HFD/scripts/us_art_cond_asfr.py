"""US conditional ASFR (HFD mi.txt) split into ART and non-ART parts, 2016-2024.

The ART part of each rate is the rate times the share of births in that age
band and birth order whose birth certificate records ART (CDC WONDER Natality
2016-2024 expanded). Second+ ART shares are applied to the second-birth rate.
Run from the HFD directory.
"""

import pathlib

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
WONDER_CSV = _REPO_ROOT / "research" / "data" / "us_natality_2016_2024_age_order_art.csv"
OUTPUT = "outputs/us_art_cond_asfr.html"

YEARS = list(range(2016, 2025))
BANDS = [(20, 24), (25, 29), (30, 34), (35, 39), (40, 44)]
ORDERS = [("m1x", "first", "First birth"), ("m2x", "second", "Second birth")]
NON_ART_COLOR = "#2a78d6"
ART_COLOR = "#eb6834"
LABEL_FONT = dict(size=14, family='"Open Sans", verdana, arial, sans-serif', color="#2a3f5f")


def band_label(lo, hi):
    return f"{lo}-{hi}"


def load_rates():
    df = pd.read_csv(
        "data/HFD/mi.txt", sep=r"\s+", skiprows=3,
        names=["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"], na_values=".",
    )
    df["age"] = df["age"].astype(str).str.strip("-+").astype(int)
    df = df[(df["code"] == "USA") & df["year"].isin(YEARS)]
    rows = []
    for lo, hi in BANDS:
        sub = df[df["age"].between(lo, hi)].groupby("year")[["m1x", "m2x"]].mean()
        for year, r in sub.iterrows():
            rows.append({"year": year, "band": band_label(lo, hi), "first": r["m1x"], "second": r["m2x"]})
    return pd.DataFrame(rows).melt(id_vars=["year", "band"], var_name="order", value_name="rate")


def load_art_shares():
    w = pd.read_csv(WONDER_CSV, thousands=",")
    w = w[w["live_birth_order"] != "Unknown or Not Stated"]
    w = w[w["art"].isin(["Yes", "No", "Not Applicable"])]
    w["order"] = w["live_birth_order"].map(lambda o: "first" if o == "1" else "second")
    w["age_lo"] = w["age_of_mother"].str.extract(r"^(\d+)-")[0].astype(float)
    w = w.dropna(subset=["age_lo"])
    w["band"] = w["age_lo"].astype(int).map(lambda a: band_label(a, a + 4))
    w["is_art"] = w["art"] == "Yes"
    g = w.groupby(["year", "band", "order"])
    return (g.apply(lambda x: x.loc[x["is_art"], "births"].sum() / x["births"].sum(), include_groups=False)
            .rename("art_share").reset_index())


def build(df):
    fig = make_subplots(
        rows=2, cols=len(BANDS), subplot_titles=[f"Age {band_label(*b)}" for b in BANDS] + [""] * len(BANDS),
        horizontal_spacing=0.05, vertical_spacing=0.09,
    )
    for annotation in fig.layout.annotations:
        annotation.font = LABEL_FONT
    for row, (_, order, order_label) in enumerate(ORDERS, start=1):
        for col, (lo, hi) in enumerate(BANDS, start=1):
            band = band_label(lo, hi)
            sub = df[(df["order"] == order) & (df["band"] == band)].sort_values("year")
            first_panel = row == 1 and col == 1
            for part, name, color in (("non_art", "Non-ART", NON_ART_COLOR), ("art", "ART", ART_COLOR)):
                fig.add_trace(
                    go.Scatter(
                        x=sub["year"], y=sub[part], name=name, legendgroup=name, showlegend=first_panel,
                        mode="lines", line=dict(width=2, color=color), fillcolor=color,
                        stackgroup=f"{order}-{band}",
                        customdata=sub[["rate", "art_share"]],
                        hovertemplate=(
                            f"{order_label}, age {band}<br>%{{x}}<br>{name}: %{{y:.2%}}"
                            "<br>Total: %{customdata[0]:.2%}<br>ART share: %{customdata[1]:.1%}<extra></extra>"
                        ),
                    ),
                    row=row, col=col,
                )
            fig.update_yaxes(rangemode="tozero", tickformat=".1~%", row=row, col=col)
            fig.update_xaxes(tickvals=[2016, 2020, 2024], ticktext=["2016", "2020", "2024"], tickfont=dict(size=10), row=row, col=col)
        fig.update_yaxes(title_text=order_label, title_font=LABEL_FONT, row=row, col=1)
    fig.update_layout(
        template="plotly_white", height=560, margin=dict(l=70, r=20, t=70, b=40),
        legend=dict(orientation="h", x=0, y=1.12, xanchor="left"), hovermode="closest",
    )
    return fig


def main():
    df = load_rates().merge(load_art_shares(), on=["year", "band", "order"])
    df["art"] = df["rate"] * df["art_share"]
    df["non_art"] = df["rate"] - df["art"]
    fig = build(df)
    fig.write_html(OUTPUT, include_plotlyjs="cdn", full_html=True, config={"responsive": True})
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")

    table = df[df["year"].isin([2016, 2024])].pivot_table(index=["order", "band"], columns="year",
                                                           values=["rate", "art", "non_art"])
    for (order, band), r in table.iterrows():
        print(f"| {order} | {band} | {r[('rate', 2016)]:.2%} | {r[('rate', 2024)]:.2%} | "
              f"{r[('rate', 2024)] / r[('rate', 2016)] - 1:+.0%} | "
              f"{r[('art', 2016)]:.2%} -> {r[('art', 2024)]:.2%} | "
              f"{r[('non_art', 2024)] / r[('non_art', 2016)] - 1:+.0%} |")


if __name__ == "__main__":
    main()
