"""Mean ideal number of children vs children ever born to women aged 45-49, latest DHS survey
per country.

Indicators (DHS Program API, breakdown=all):
  PR_IDLC_W_MNA  mean ideal number of children, all women 15-49 (numeric responses only)
  FE_CEBA_W_MNC  mean number of children ever born, by 5-year age group (45-49 used)

Inputs (download into DHS/data/ - not tracked in git):
  PR_IDLC_W_MNA.json  https://api.dhsprogram.com/rest/dhs/data?indicatorIds=PR_IDLC_W_MNA&breakdown=all&f=json&perpage=50000
  FE_CEBA_W_MNC.json  https://api.dhsprogram.com/rest/dhs/data?indicatorIds=FE_CEBA_W_MNC&breakdown=all&f=json&perpage=50000
Outputs: DHS/outputs/ideal_vs_actual_dhs.html, ideal_vs_actual_dhs.csv
"""

import json

import pandas as pd
import plotly.graph_objects as go

from common.paths import data_dir, outputs_dir
from common.plotting import write_html

DATA = data_dir("DHS")
OUT = outputs_dir("DHS")


def read(indicator):
    d = pd.DataFrame(json.loads((DATA / f"{indicator}.json").read_text(encoding="utf-8"))["Data"])
    return d[d.SurveyType == "DHS"]


def load():
    ideal = read("PR_IDLC_W_MNA")
    ideal = ideal[ideal.IsTotal == 1][["SurveyId", "CountryName", "SurveyYear", "Value"]]
    ceb = read("FE_CEBA_W_MNC")
    ceb = ceb[(ceb.CharacteristicCategory == "Age (5-year groups)") & (ceb.CharacteristicLabel == "45-49")]
    d = ideal.rename(columns={"Value": "ideal"}).merge(
        ceb[["SurveyId", "Value"]].rename(columns={"Value": "ceb_45_49"}), on="SurveyId")
    d = d.sort_values("SurveyYear").groupby("CountryName").tail(1)
    d["ceb_45_49"] = d.ceb_45_49.round(2)
    d["gap"] = (d.ideal - d.ceb_45_49).round(2)
    return d.rename(columns={"CountryName": "country", "SurveyYear": "year"}).sort_values("gap")[
        ["country", "year", "ideal", "ceb_45_49", "gap"]]


def plot(d):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 9], y=[1, 9], mode="lines", line=dict(color="#9e9e9e", dash="dash"),
                             name="Ideal = actual", hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=d.ceb_45_49, y=d.ideal, mode="markers", name="Latest DHS survey",
        marker=dict(color="#1d4ed8", size=9, opacity=0.75), customdata=d[["country", "year"]],
        hovertemplate="%{customdata[0]} %{customdata[1]}<br>Children ever born, 45-49: %{x:.1f}"
                      "<br>Ideal, all women: %{y:.1f}<extra></extra>"))
    fig.update_xaxes(range=[1, 9], constrain="domain", title_text="Children ever born, women aged 45-49")
    fig.update_yaxes(range=[1, 9], title_text="Mean ideal number of children, women 15-49",
                     scaleanchor="x", scaleratio=1, constrain="domain")
    fig.update_layout(template="plotly_white", title="Ideal vs actual number of children, DHS countries",
                      legend=dict(orientation="h", x=0, y=-0.15), margin=dict(t=70, b=100))
    return fig


if __name__ == "__main__":
    d = load()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "ideal_vs_actual_dhs.csv", index=False)
    print(d.to_string(index=False))
    write_html(plot(d), OUT / "ideal_vs_actual_dhs.html")
