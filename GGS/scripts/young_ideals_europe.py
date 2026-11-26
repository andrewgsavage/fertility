"""Personal ideal number of children of young European women: Eurobarometer 2011 vs
Generations and Gender Survey round 2 (2020-2023).

Values are transcribed from two published tables (no microdata):
  Eurobarometer 2011: M R Testa, "Family sizes in Europe: evidence from the 2011 Eurobarometer
    survey", European Demographic Research Papers 2012/2, VID, Table A.2.2 (mean personal ideal
    number of children by gender, age and country) -
    https://www.oeaw.ac.at/fileadmin/subsites/Institute/VID/PDF/Publications/EDRP/edrp_2012_02.pdf
  GGS-II: C Friedrich & M Bujard, "Intended, ideal, and actual fertility in 11 European countries",
    BiB Working Paper 2/2025, Table 1 (women, weighted) -
    https://www.bib.bund.de/Publikation/2025/pdf/Intended-ideal-and-actual-fertility-in-11-European-countries-Evidence-on-fertility-gaps-in-different-age-groups-from-the-Generations-and-Gender-Survey.pdf

Outputs: GGS/outputs/young_ideals_europe.html, young_ideals_europe.csv, and ideal_matrix_europe.csv
(rows for eurostat/scripts/change_matrix.py)
"""

import pandas as pd
import plotly.graph_objects as go

from common.paths import outputs_dir
from common.plotting import write_html

OUT = outputs_dir("GGS")

# Eurobarometer 2011, women: personal ideal at 15-24 and 25-39
EB2011 = {
    "Austria": (1.96, 1.79), "Czech Republic": (2.04, 1.93), "Denmark": (2.47, 2.62),
    "Estonia": (2.28, 2.50), "Finland": (2.45, 2.47), "Germany": (2.08, 2.04),
    "Netherlands": (2.49, 2.17), "United Kingdom": (2.37, 2.27),
}
# GGS-II, women: personal ideal at 18-29 and 30-39, intended at 18-29
GGS2 = {
    "Germany": (2.38, 2.32, 1.98), "Austria": (2.16, 2.21, 1.97), "Netherlands": (2.21, 2.13, 2.07),
    "Czech Republic": (2.07, 2.12, 1.94), "Croatia": (2.34, 2.39, 2.18), "Estonia": (2.24, 2.37, 2.11),
    "Norway": (2.39, 2.36, 2.17), "Denmark": (2.28, 2.36, 2.10), "Finland": (2.08, 2.10, 1.82),
    "Moldova": (2.64, 2.79, 2.47), "United Kingdom": (2.40, 2.20, 2.11),
}
GGS_YEARS = {
    "Germany": "2021-22", "Austria": "2022-23", "Netherlands": "2022-23", "Czech Republic": "2020-22",
    "Croatia": "2023", "Estonia": "2021-22", "Norway": "2020", "Denmark": "2021", "Finland": "2021-22",
    "Moldova": "2020", "United Kingdom": "2022-23",
}


# Eurobarometer 2011, women, Testa Tables A.2.3-A.2.4: ultimately intended (actual + additionally intended) at 15-24 and 25-39.
EB2011_INTENDED = {  # (15-24, 25-39)
    "Austria": (0.14 + 1.73, 1.07 + 0.67), "Czech Republic": (0.18 + 1.76, 1.30 + 0.65),
    "Denmark": (0.23 + 2.20, 1.44 + 0.92), "Estonia": (0.34 + 1.83, 1.50 + 0.94), "Finland": (0.21 + 2.38, 1.53 + 0.84),
    "Germany": (0.13 + 1.83, 1.19 + 0.72), "Netherlands": (0.04 + 2.39, 1.02 + 0.96), "United Kingdom": (0.53 + 1.75, 1.38 + 0.90),
}
# GGS-II intended at 30-39 (Friedrich & Bujard Table 1)
GGS2_INTENDED_30_39 = {"Germany": 1.85, "Austria": 1.92, "Netherlands": 1.88, "Czech Republic": 1.90, "Croatia": 2.18,
                       "Estonia": 2.21, "Norway": 2.09, "Denmark": 1.97, "Finland": 1.78, "Moldova": 2.51,
                       "United Kingdom": 2.03}
ISO = {"Austria": "AUT", "Czech Republic": "CZE", "Denmark": "DNK", "Estonia": "EST", "Finland": "FIN",
       "Germany": "DEU", "Netherlands": "NLD", "United Kingdom": "GBR", "Croatia": "HRV", "Norway": "NOR"}
GGS_FIRST_YEAR = {c: int(y[:4]) for c, y in GGS_YEARS.items()}


def matrix_series():
    """Rows for the country comparison matrix (eurostat/scripts/change_matrix.py): key, iso, year, value, source.
    Each country's Eurobarometer 2011 value and its GGS-II value; countries with only one end are left out."""
    pairs = {
        "ideal_young": ({c: v[0] for c, v in EB2011.items()}, {c: v[0] for c, v in GGS2.items()}, "15–24", "18–29"),
        "ideal_30s": ({c: v[1] for c, v in EB2011.items()}, {c: v[1] for c, v in GGS2.items()}, "25–39", "30–39"),
        "intended_young": ({c: v[0] for c, v in EB2011_INTENDED.items()}, {c: v[2] for c, v in GGS2.items()}, "15–24", "18–29"),
        "intended_30s": ({c: v[1] for c, v in EB2011_INTENDED.items()}, GGS2_INTENDED_30_39, "25–39", "30–39"),
    }
    rows = []
    for key, (start, end, a0, a1) in pairs.items():
        for c in sorted(set(start) & set(end)):
            src = f"Eurobarometer 2011 ({a0}) to GGS-II {GGS_YEARS.get(c, '2020–23')} ({a1})"
            rows.append(dict(key=key, iso=ISO[c], year=2011, value=round(start[c], 2), source=src))
            rows.append(dict(key=key, iso=ISO[c], year=GGS_FIRST_YEAR[c], value=end[c], source=src))
    return pd.DataFrame(rows)


def load():
    rows = []
    for c, (i1829, i3039, int1829) in GGS2.items():
        eb = EB2011.get(c, (None, None))
        rows.append(dict(country=c, eb2011_15_24=eb[0], eb2011_25_39=eb[1], ggs_years=GGS_YEARS[c],
                         ggs_ideal_18_29=i1829, ggs_ideal_30_39=i3039, ggs_intended_18_29=int1829))
    d = pd.DataFrame(rows)
    d["change_young"] = (d.ggs_ideal_18_29 - d.eb2011_15_24).round(2)
    return d.sort_values("ggs_ideal_18_29")


def plot(d):
    fig = go.Figure()
    for _, r in d.dropna(subset=["eb2011_15_24"]).iterrows():
        fig.add_trace(go.Scatter(x=[r.eb2011_15_24, r.ggs_ideal_18_29], y=[r.country] * 2, mode="lines",
                                 line=dict(color="#9e9e9e", width=2), showlegend=False, hoverinfo="skip"))
    for col, name, color, symbol in [
        ("eb2011_15_24", "Ideal, aged 15-24 in 2011 (Eurobarometer)", "#93c5fd", "circle"),
        ("ggs_ideal_18_29", "Ideal, aged 18-29 in 2020-23 (GGS-II)", "#1d4ed8", "circle"),
        ("ggs_intended_18_29", "Intended, aged 18-29 in 2020-23 (GGS-II)", "#c00000", "diamond-open"),
    ]:
        fig.add_trace(go.Scatter(x=d[col], y=d.country, mode="markers", name=name,
                                 marker=dict(color=color, size=11, symbol=symbol, line=dict(width=2, color=color)),
                                 hovertemplate="%{y}: %{x:.2f}<extra>" + name + "</extra>"))
    fig.update_xaxes(range=[1.7, 2.9], title_text="Mean number of children")
    fig.update_layout(template="plotly_white", title="Young women's ideal and intended number of children, Europe",
                      legend=dict(orientation="h", x=0, y=-0.15), margin=dict(t=70, b=130),
                      hovermode="closest")
    return fig


if __name__ == "__main__":
    d = load()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "young_ideals_europe.csv", index=False)
    matrix_series().to_csv(OUT / "ideal_matrix_europe.csv", index=False)
    print(d.to_string(index=False))
    write_html(plot(d), OUT / "young_ideals_europe.html")
