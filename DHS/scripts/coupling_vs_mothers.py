"""% of women in a 5-year age group with a child against the coupling rate: Demographic and
Health Survey (DHS) countries alongside the HFD countries. Connected time series, with separate
dropdowns for the coupling age group (x) and the motherhood age group (y).

y: % of women aged 20-24 / 25-29 / 30-34 / 35-39 with at least one child.
   - DHS: 100 - women with no children ever born (dhs_mothers.py), surveys of all women.
   - HFD: 100 - childless women's share of all female exposure in the age group (exposRRpa.txt).
   - UK: England and Wales, ONS cohort table 3 (ONS/scripts/coupling_vs_cond_asfr_ew.py).
x, two charts:
   - coupling_vs_mothers.html: ILO (women, 10-year bands), national registers/CPS or FT (both
     sexes, 25-34), as in ILO/scripts/coupling_vs_cond_asfr.py.
   - coupling_vs_mothers_un.html: UN World Marriage Data, women, 5-year groups (coupling_un.py).

Inputs: DHS/outputs/dhs_mothers.csv, the coupling CSV outputs of the ILO, FT, NSO and UN
scripts, HFD/data/HFD/mi.txt and exposRRpa.txt.
"""

import pandas as pd
import plotly.colors as pc

from common import coupling_ew as ew
from common import coupling_hfd as ilo
from common.paths import outputs_dir
from common.plotting import write_html

OUTDIR = outputs_dir("DHS")

Y_OPTS = ew.GROUP_OPTS
Y_DEFAULT = "mothers 25-29"
# DHS countries with ILO coupling (women) or FT coupling (both sexes, 25-34; used where FT
# matches more survey years than ILO).
DHS_ILO = {"ARM": "Armenia", "BOL": "Bolivia", "COL": "Colombia", "DOM": "Dominican Rep",
           "GTM": "Guatemala", "HND": "Honduras", "IDN": "Indonesia", "PER": "Peru",
           "PHL": "Philippines", "RWA": "Rwanda", "SEN": "Senegal", "ZAF": "South Africa", "TUR": "Turkey",
           "ZMB": "Zambia"}
DHS_FT = {"AGO": "Angola", "KHM": "Cambodia", "IND": "India", "GHA": "Ghana", "KEN": "Kenya", "NGA": "Nigeria"}
# UN country name -> DHS country name, where they differ.
DHS_NAMES = {"Democratic Republic of the Congo": "Congo Democratic Republic", "Côte d'Ivoire": "Cote d'Ivoire",
             "Viet Nam": "Vietnam"}
HFD_COLOR = "#999999"


def dhs_wide(key):
    """DHS % with a child, one row per (key, year), columns 'mothers 20-24' ..."""
    m = pd.read_csv(OUTDIR / "dhs_mothers.csv")
    m = m[m.age.isin(ew.MOTHER_GROUPS)]
    w = m.pivot_table(index=[key, "year"], columns="age", values="mother")
    w.columns = [f"mothers {a}" for a in w.columns]
    return w.reset_index().rename(columns={key: "code"})


def make_series(name, color, years, x, y_rows):
    y = {k: [None if k not in y_rows or pd.isna(y_rows.at[yr, k]) else float(y_rows.at[yr, k]) for yr in years]
         for k in Y_OPTS}
    return {"name": name, "color": color, "years": years, "x": x, "y": y}


def series_ilo_ft():
    rates = pd.concat([ilo.hfd_first_birth_rates(), ilo.uk_first_birth_rates(), dhs_wide("iso3")], ignore_index=True)
    cp = ilo.coupling(ilo.ILO_CODES | DHS_ILO, ilo.FT_CODES | DHS_FT)
    hfd_names = {**{k: f"{v} (ILO, women)" for k, v in ilo.ILO_CODES.items()},
                 **{k: f"{v} (register, women)" for k, v in ilo.NSO_CODES.items()},
                 **{k: f"{v} (FT, both sexes)" for k, v in ilo.FT_CODES.items()},
                 "USA": "US (CPS, women)", "UK": "UK (FT, both sexes; births E&W)"}
    dhs_names = {**{k: f"{v} (ILO, women)" for k, v in DHS_ILO.items()},
                 **{k: f"{v} (FT, both sexes)" for k, v in DHS_FT.items()}}
    colors = pc.qualitative.Dark24
    series = []
    for code, name in (hfd_names | dhs_names).items():
        r = rates[rates.code == code].set_index("year")
        c = cp[cp.code == code]
        is_dhs = code in dhs_names
        years = sorted(y for y in set(r.index) & set(c.year) if is_dhs or y >= ilo.FIRST_YEAR)
        if not years:
            print("no overlap:", code)
            continue
        x = {a: [c[(c.age == a) & (c.year == y)].share.squeeze() if ((c.age == a) & (c.year == y)).any()
                 else None for y in years] for a in ilo.X_AGES}
        color = colors[len([s for s in series if s["dhs"]]) % len(colors)] if is_dhs else HFD_COLOR
        s = make_series(name + (" DHS" if is_dhs else ""), color, years, x, r)
        s["dhs"] = is_dhs
        series.append(s)
    return series


def series_un():
    un = pd.read_csv(outputs_dir("UN") / "coupling_un.csv")
    un = un[un.sex == "Women"]
    dhs = dhs_wide("country")
    dhs_codes = {c: DHS_NAMES.get(c, c) for c in sorted(set(un.country))
                 if c not in ilo.UN_HFD_CODES and DHS_NAMES.get(c, c) in set(dhs.code)}
    rates = pd.concat([ilo.hfd_first_birth_rates(), dhs], ignore_index=True)
    colors = pc.qualitative.Dark24 + pc.qualitative.Alphabet
    series = []
    for country, code in (ilo.UN_HFD_CODES | dhs_codes).items():
        is_dhs = country in dhs_codes
        r = rates[rates.code == code].set_index("year")
        c = un[un.country == country].pivot_table(index="year", columns="age", values="share")
        years = sorted(set(r.index) & set(c.index))
        if len(years) < ilo.UN_MIN_POINTS:
            print("too few overlapping years:", country, years)
            continue
        x = {a: [None if a not in c or pd.isna(c.at[y, a]) else float(c.at[y, a]) for y in years]
             for a in ilo.UN_X_AGES}
        n_dhs = len([s for s in series if s["dhs"]])
        s = make_series(country + (" DHS" if is_dhs else ""), colors[n_dhs % len(colors)] if is_dhs else HFD_COLOR,
                        years, x, r)
        s["dhs"] = is_dhs
        series.append(s)
    return series


def write(series, x_ages, x_default, title, x_label, fname):
    rows = [{"country": s["name"], "year": yr, **{f"coupling_{a}": s["x"][a][i] for a in x_ages},
             **{f"y_{k}": s["y"][k][i] for k in Y_OPTS}} for s in series for i, yr in enumerate(s["years"])]
    pd.DataFrame(rows).round(3).to_csv(OUTDIR / fname.replace(".html", ".csv"), index=False)
    fig = ew.dual_dropdown_fig(series, {a: a for a in x_ages}, Y_OPTS, x_default, Y_DEFAULT, title, x_label,
                               auto_hide=True)
    write_html(fig, OUTDIR / fname)
    print(fname, len(series), "series,", sum(s["dhs"] for s in series), "DHS")


if __name__ == "__main__":
    OUTDIR.mkdir(exist_ok=True)
    write(series_ilo_ft(), ilo.X_AGES, "25-34",
          "% of women with a child vs coupling rate, DHS and HFD countries (grey: HFD; marker grows with year)",
          "% married or cohabiting", "coupling_vs_mothers.html")
    write(series_un(), ilo.UN_X_AGES, "25-29",
          "% of women with a child vs women married or in a union, UN data (grey: HFD; marker grows with year)",
          "% of women married or in a union", "coupling_vs_mothers_un.html")
