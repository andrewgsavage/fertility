"""Youth temporary-contract share against mean age at first birth, by country and year.

Eurostat lfsa_etpgan (temporary employees, % of employees aged 15-29) and
demo_find (indic_de=AGEMOTH1, mean age of mother at first birth). Download
into eurostat/data/ (not tracked in git):
  lfsa_etpgan.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/lfsa_etpgan/A.PC.T..TOTAL.?format=SDMX-CSV
  demo_find_agemoth1.csv  https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_find/A.AGEMOTH1.?format=SDMX-CSV
"""

import pandas as pd
import plotly.express as px

from _common import DATA, NAMES, write_html


def load():
    t = pd.read_csv(DATA / "lfsa_etpgan.csv")
    t = t[t.age == "Y15-29"][["geo", "TIME_PERIOD", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "temp"})
    f = pd.read_csv(DATA / "demo_find_agemoth1.csv")
    f = f[f.indic_de == "AGEMOTH1"][["geo", "TIME_PERIOD", "OBS_VALUE"]].rename(columns={"OBS_VALUE": "age"})
    d = t.merge(f, on=["geo", "TIME_PERIOD"]).dropna()
    d = d[d.geo.isin(NAMES) & (d.geo != "EU27_2020")]
    d["country"] = d.geo.map(NAMES)
    return d.rename(columns={"TIME_PERIOD": "year"}).sort_values("year")


def plot(d):
    fig = px.scatter(
        d, x="temp", y="age", animation_frame="year", text="geo", hover_name="country",
        range_x=[0, 70], range_y=[24, 33],
        labels={"temp": "Temporary employees, % of employees aged 15-29",
                "age": "Mean age at first birth"},
    )
    fig.update_traces(textposition="top center", marker=dict(size=9),
                      hovertemplate="%{hovertext}<br>temp %{x:.1f}%<br>age %{y:.1f}<extra></extra>")
    fig.update_layout(template="plotly_white",
                      title="Youth temporary contracts vs mean age at first birth",
                      margin=dict(t=60))
    return fig


if __name__ == "__main__":
    write_html(plot(load()), "temp_contracts_vs_first_birth_age.html")
