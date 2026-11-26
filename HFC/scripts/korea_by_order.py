"""South Korea's period TFR by birth order, 1980-2024, from the Human Fertility Collection.

HFD's Korean series by birth order starts in 2000. HFC also holds research estimates back to
1980: the European Demographic Observatory (ODE, 1980-2007) and Kye (2012, 1981-2015). This
splices ODE for 1980-1999 onto the HFD vital-statistics series for 2000-2024, both with age in
completed years (ACY), and reports the gap between the sources in the years they overlap.

Input: https://www.fertilitydata.org/ KOR_TFRMAB_BO.txt, cached in HFC/data/.
Outputs (HFC/outputs/): kor_tfr_by_order.csv, kor_tfr_by_order_overlap.csv, kor_tfr_by_order.html.
"""

import pandas as pd
import plotly.graph_objects as go
import requests

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

URL = "https://www.fertilitydata.org/File/GetFile/Country/KOR%5CKOR_TFRMAB_BO.txt"
RAW = data_dir("HFC") / "KOR_TFRMAB_BO.txt"
OUT = outputs_dir("HFC")
SPLICE = 2000  # first year taken from HFD
ORDERS = {"TFR1": "First births", "TFR2": "Second births", "TFR3P": "Third and later births"}
SOURCES = {"ODE": "ODE estimate", "RE": "Kye (2012)", "HFD": "HFD vital statistics"}


def load():
    if not RAW.exists():
        RAW.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(URL, timeout=60)
        r.raise_for_status()
        RAW.write_bytes(r.content)
    d = pd.read_csv(RAW, skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    d = d[(d.Year1 == d.Year2) & (d.AgeDef.str.strip() == "ACY")].copy()
    d["Collection"] = d.Collection.str.strip()
    if d.duplicated(["Collection", "Year1"]).any():
        raise ValueError("repeated years within an HFC collection")
    return d.rename(columns={"Year1": "year"})[["Collection", "year", "TFR", *ORDERS]]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load()
    spliced = pd.concat([d[(d.Collection == "ODE") & (d.year < SPLICE)],
                         d[(d.Collection == "HFD") & (d.year >= SPLICE)]])
    spliced = spliced.assign(source=spliced.Collection.map(SOURCES)).drop(columns="Collection")
    spliced.sort_values("year").to_csv(OUT / "kor_tfr_by_order.csv", index=False)

    wide = d.pivot(index="year", columns="Collection", values="TFR")
    overlap = wide.dropna(subset=["HFD"]).dropna(how="all", subset=["ODE", "RE"])
    overlap = overlap[["ODE", "RE", "HFD"]].round(3)
    overlap.to_csv(OUT / "kor_tfr_by_order_overlap.csv")
    print(overlap.assign(ode_gap=overlap.ODE - overlap.HFD, kye_gap=overlap.RE - overlap.HFD))

    s = spliced.sort_values("year")
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig = go.Figure()
    for (col, name), c in zip(ORDERS.items(), colors):
        fig.add_trace(go.Scatter(x=s.year, y=s[col], mode="lines", name=name, line=dict(color=c, width=2),
                                 customdata=s.source,
                                 hovertemplate=f"{name}: %{{y:.2f}} (%{{customdata}})<extra></extra>"))
    fig.add_vline(x=SPLICE - 0.5, line=dict(color="#888", width=1, dash="dot"))
    fig.add_annotation(x=SPLICE - 0.5, y=1.0, yref="paper", text="ODE estimates | HFD", showarrow=False,
                       yanchor="bottom", font=dict(size=11, color="#666"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title="South Korea: period TFR by birth order, 1980–2024",
                      yaxis=dict(title="Births per woman", rangemode="tozero"), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.15))
    write_html(fig, OUT / "kor_tfr_by_order.html")


if __name__ == "__main__":
    main()
