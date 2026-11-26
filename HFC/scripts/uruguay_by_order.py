"""Uruguay's period TFR by birth order: HFC 1978-2011, plus estimates for 2013 and 2021.

HFC holds Uruguayan rates by birth order from the Latin American Fertility Database (LAFD):
Nathan's estimates for 1978-1988 and 1993, and Cabella, Nathan and Pardo's for 1996-2011
(Live-Birth Certificate plus Perinatal Information System). Nothing later is published by order.

Estimates for later years:
- Age-specific fertility rates by 5-year age group: Ministry of Public Health (MSP) live births
  by single year of mother's age, 1996-2021 (unknown ages spread pro rata, under-15s counted
  at 15-19, 50+ at 45-49), over INE's female population at 30 June (Revision 2025, based on
  the 2023 census). The 1996-2011 totals are checked against HFC's.
- Order shares: MSP's public Perinatal Information System (SIP) microdata for 2013 and 2021,
  order = previous deliveries ("partos previos") + 1, as a share of births in each age group.
  TFR_i = sum over age groups of 5 x ASFR x share of order i.
The MSP files are no longer reachable on the ministry's site from outside Uruguay; they are
fetched from the Internet Archive's copies. They are RAR archives, extracted with bsdtar
(Windows' tar.exe).

Inputs (cached in HFC/data/): URY_TFRMAB_BO.txt (fertilitydata.org), MSP natality table 3,
SIP 2013 and 2021 public microdata, INE A.1.1 Uruguay.xlsx.
Outputs (HFC/outputs/): ury_tfr_by_order.csv, ury_tfr_check.csv, ury_tfr_by_order.html.
"""

import subprocess

import pandas as pd
import plotly.graph_objects as go
import requests
import truststore

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

truststore.inject_into_ssl()  # www5.ine.gub.uy omits its intermediate certificate; the OS store fetches it

WAYBACK = "https://web.archive.org/web/20230215183142id_/https://uins.msp.gub.uy/materiales/"
HFC_URL = "https://www.fertilitydata.org/File/GetFile/Country/URY%5CURY_TFRMAB_BO.txt"
BIRTHS_URL = WAYBACK + "2021/cuadro3natalidad.rar"
SIP_URLS = {year: WAYBACK + f"perinatal/Base_de_datos_SIP_{year}.rar" for year in (2013, 2021)}
INE_URL = ("https://www5.ine.gub.uy/documents/Demograf%C3%ADayEESS/SERIES%20Y%20OTROS/"
           "Estimaciones%20y%20proyecciones/Revisi%C3%B3n%202025/A.1.1%20Uruguay.xlsx")
DATA = data_dir("HFC")
OUT = outputs_dir("HFC")
ORDERS = {"TFR1": "First births", "TFR2": "Second births", "TFR3P": "Third and later births"}
GROUPS = ["15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"]
# SIP maternal age groups (codes in 2013, labels in 2021); under-15s and 45+ fold into the
# nearest group, unknown ages are dropped.
SIP_AGE = {1: "15-19", 2: "15-19", 3: "20-24", 4: "25-29", 5: "30-34", 6: "35-39", 7: "40-44", 8: "45-49",
           "14 o menos": "15-19", "15-19": "15-19", "20-24": "20-24", "25-29": "25-29", "30-34": "30-34",
           "35-39": "35-39", "40-44": "40-44", "45 o más": "45-49"}


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def unrar(url, name, pattern):
    """Download an MSP RAR archive and return the extracted file matching pattern."""
    raw = fetch(url, DATA / f"{name}.rar")
    dest = DATA / name
    if not any(dest.glob(pattern)):
        dest.mkdir(exist_ok=True)
        subprocess.run(["tar", "-xf", str(raw), "-C", str(dest)], check=True)
    return next(dest.glob(pattern))


def group(age):
    return GROUPS[min(max(age, 15), 49) // 5 - 3]


def hfc():
    d = pd.read_csv(fetch(HFC_URL, DATA / "URY_TFRMAB_BO.txt"), skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    d = d[(d.Year1 == d.Year2) & (d.AgeDef.str.strip() == "ACY")].drop_duplicates()
    if d.Year1.duplicated().any():
        raise ValueError("conflicting HFC rows for the same year")
    return d.rename(columns={"Year1": "year"})[["year", "TFR", *ORDERS]].assign(source="HFC (LAFD)")


def births():
    """MSP live births by 5-year group of mother's age, 1996-2021, unknown ages spread pro rata."""
    t = pd.read_excel(unrar(BIRTHS_URL, "msp_births_age", "*.ods"), header=None, engine="odf")
    years = t.iloc[8].infer_objects().ffill()
    rows = []
    for col in t.columns[t.iloc[10] == "Total"]:
        for label, n in zip(t.iloc[11:50, 0], t.iloc[11:50, col]):
            age = {"12 o menos": 12, "50 o más": 50}.get(label, label)
            rows.append({"year": int(years[col]), "age": group(int(age)), "births": n})
    b = pd.DataFrame(rows).groupby(["year", "age"]).births.sum().unstack()
    known = b.sum(axis=1)
    total = t.loc[t.iloc[:, 0] == "Total", t.iloc[10] == "Total"].iloc[0].to_numpy(dtype=float)
    return b.mul(total / known.to_numpy(), axis=0)


def women():
    """INE female population at 30 June by 5-year group, Revision 2025."""
    t = pd.read_excel(fetch(INE_URL, DATA / "INE_A.1.1_Uruguay.xlsx"), header=None)
    start = t.index[t.iloc[:, 0] == "Mujeres"][0]
    f = t.iloc[start + 1:].set_index(0)
    f.columns = t.iloc[4, 1:].astype(int)
    f.index = pd.to_numeric(f.index, errors="coerce")
    f = f[f.index.to_series().between(15, 49).to_numpy()].iloc[:35]
    f.index = f.index.astype(int)
    return f.groupby(f.index.map(group)).sum().T


def sip_shares(year):
    """Share of births of each order within each maternal age group, SIP public microdata."""
    csv = unrar(SIP_URLS[year], f"sip_{year}", "*.csv")
    d = pd.read_csv(csv, sep=";", encoding="latin-1", low_memory=False, usecols=["rec_0009", "VAR_0046"])
    prev = pd.to_numeric(d.VAR_0046, errors="coerce")
    d = d.assign(age=d.rec_0009.map(SIP_AGE), order=(prev + 1).clip(upper=3))[prev.lt(99)].dropna(subset=["age"])
    share = d.groupby("age").order.value_counts(normalize=True).unstack(fill_value=0)
    return share.rename(columns={1: "TFR1", 2: "TFR2", 3: "TFR3P"}), len(d)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    h = hfc()
    asfr = (births() / women()).dropna()
    tfr = (5 * asfr.sum(axis=1)).rename("TFR")

    check = pd.concat([tfr.rename("msp_ine"), h.set_index("year").TFR.rename("hfc")], axis=1).dropna()
    check = check.assign(gap=check.msp_ine - check.hfc).round(3)
    check.index.name = "year"
    check.to_csv(OUT / "ury_tfr_check.csv")
    print(check.to_string())

    rows = []
    for year in SIP_URLS:
        share, n = sip_shares(year)
        by_order = share.mul(5 * asfr.loc[year], axis=0).sum()
        rows.append({"year": year, "TFR": round(tfr[year], 3), **by_order.round(3).to_dict(),
                     "source": "MSP/INE ASFR x SIP order shares"})
        print(year, "SIP births with age and parity:", n)
    est = pd.DataFrame(rows)
    out = pd.concat([h, est]).sort_values("year")
    out.to_csv(OUT / "ury_tfr_by_order.csv", index=False)
    print(out.tail(6).to_string(index=False))

    # Reindex to every year so the HFC gaps (1989-92, 1994-95) show as breaks.
    hh = h.set_index("year").reindex(range(h.year.min(), h.year.max() + 1)).reset_index()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    fig = go.Figure()
    for (col, name), c in zip(ORDERS.items(), colors):
        fig.add_trace(go.Scatter(x=hh.year, y=hh[col], mode="lines+markers", name=name, legendgroup=name,
                                 line=dict(color=c, width=2), marker=dict(size=4),
                                 hovertemplate=f"{name}: %{{y:.2f}} (HFC)<extra></extra>"))
        fig.add_trace(go.Scatter(x=est.year, y=est[col], mode="markers", name=name, legendgroup=name,
                                 showlegend=False, marker=dict(color=c, size=9, symbol="diamond"),
                                 hovertemplate=f"{name}: %{{y:.2f}} (estimate)<extra></extra>"))
    fig.add_annotation(x=2017, y=1.0, yref="paper", text="◆ estimates from SIP order shares", showarrow=False,
                       yanchor="bottom", font=dict(size=11, color="#666"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title="Uruguay: period TFR by birth order, 1978–2021",
                      yaxis=dict(title="Births per woman", rangemode="tozero"), hovermode="x unified",
                      legend=dict(orientation="h", y=-0.15))
    write_html(fig, OUT / "ury_tfr_by_order.html")


if __name__ == "__main__":
    main()
