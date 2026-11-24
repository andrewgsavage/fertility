"""Share of women living in a couple by local authority (Census 2011 and 2021) vs local ASFR,
England and Wales.

Living in a couple = married or civil partnered, cohabiting, or separated but living with a new
partner (every "Living in a couple" category). Denominator = usual residents in households of that
sex and age: the 2011 table covers household residents only, so the 2021 "Does not apply"
category (communal establishments) is left out to match.

Inputs (download into ONS/data/census/ - not tracked in git):
  ons2021_living_age_sex_ltla.json
    Census 2021 custom dataset, ONS "create your own dataset" API, usual residents,
    lower-tier local authorities x living_arrangements_11a x resident_age_12a x sex:
    https://api.beta.ons.gov.uk/v1/population-types/UR/census-observations?area-type=ltla&dimensions=living_arrangements_11a,resident_age_12a,sex
    (Isles of Scilly is blocked by disclosure control; 330 of 331 LADs are returned.)
  nomis2011_dc1108ew_lad.csv
    Census 2011 DC1108EW "Living arrangements by sex by age" (Nomis NM_747_1), females,
    20-24/25-29/30-34, local authorities (district/unitary, prior to April 2015):
    https://www.nomisweb.co.uk/api/v01/dataset/NM_747_1.data.csv?geography=2092957703TYPE464&c_age=3,4,5&c_sex=2&c_larpuk11=0,1,2,3&measures=20100&select=geography_code,geography_name,c_age_name,c_larpuk11,obs_value

ASFRs come from ONS/intermediate/fertility_by_lad.json (Nomis lebirthrates, see parse_csv.py),
which uses April 2023 LAD codes; both censuses are summed up to those codes (2019-2023 mergers).

Outputs (ONS/outputs/):
  coupling_by_lad_ew.csv              one row per LAD x age band
  coupling_by_lad_ew_stats.csv        r, R^2, n, spreads, per age band
  coupling_vs_asfr_lad_ew.html        coupling share vs ASFR, 2021, by LAD
  births_per_coupled_lad_ew.html      spread of ASFR vs births per coupled woman
  coupling_change_lad_ew.html         coupling share 2011 vs 2021, by LAD
"""

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, intermediate_dir, outputs_dir
from common.plotting import write_html

CENSUS_DIR = data_dir("ONS") / "census"
IN_2021 = CENSUS_DIR / "ons2021_living_age_sex_ltla.json"
IN_2011 = CENSUS_DIR / "nomis2011_dc1108ew_lad.csv"
FERT = intermediate_dir("ONS") / "fertility_by_lad.json"
OUT = outputs_dir("ONS")

BANDS = {"25-29": "asfr_25_29", "30-34": "asfr_30_34"}
AGE_2021 = {"Aged 25 to 29 years": "25-29", "Aged 30 to 34 years": "30-34"}
AGE_2011 = {"Age 25 to 29": "25-29", "Age 30 to 34": "30-34"}

# Census LAD code -> April 2023 LAD code (fertility file). Mergers 2019-2023, plus the
# Barnsley/Sheffield code reissue.
MERGE = {
    "E08000016": "E08000038", "E08000019": "E08000039",
    "E06000028": "E06000058", "E06000029": "E06000058", "E07000048": "E06000058",
    **{c: "E06000059" for c in ["E07000049", "E07000050", "E07000051", "E07000052", "E07000053"]},
    **{c: "E06000060" for c in ["E07000004", "E07000005", "E07000006", "E07000007"]},
    **{c: "E06000061" for c in ["E07000150", "E07000152", "E07000153", "E07000156"]},
    **{c: "E06000062" for c in ["E07000151", "E07000154", "E07000155"]},
    **{c: "E06000063" for c in ["E07000026", "E07000028", "E07000029"]},
    **{c: "E06000064" for c in ["E07000027", "E07000030", "E07000031"]},
    **{c: "E06000065" for c in ["E07000163", "E07000164", "E07000165", "E07000166",
                                "E07000167", "E07000168", "E07000169"]},
    **{c: "E06000066" for c in ["E07000187", "E07000188", "E07000189", "E07000190",
                                "E07000191", "E07000246"]},
    "E07000201": "E07000245", "E07000204": "E07000245",
    "E07000205": "E07000244", "E07000206": "E07000244",
}

GROUP_COLORS = {"London": "#c0392b", "Rest of England": "#2c7fb8", "Wales": "#2ca25f"}
OUTLIER_Z = 2.5  # |standardised residual| above which a LAD is labelled


def load_2021():
    obs = json.loads(IN_2021.read_text(encoding="utf-8"))["observations"]
    rows = []
    for o in obs:
        d = {x["dimension_id"]: x for x in o["dimensions"]}
        if d["sex"]["option"] != "Female" or d["resident_age_12a"]["option"] not in AGE_2021:
            continue
        if d["living_arrangements_11a"]["option"] == "Does not apply":  # communal establishments
            continue
        rows.append({"code": d["ltla"]["option_id"], "band": AGE_2021[d["resident_age_12a"]["option"]],
                     "couple": d["living_arrangements_11a"]["option"].startswith("Living in"),
                     "n": o["observation"]})
    x = pd.DataFrame(rows)
    x["code"] = x.code.replace(MERGE)
    t = x.groupby(["code", "band", "couple"]).n.sum().unstack("couple")
    return pd.DataFrame({"women_2021": t.sum(axis=1), "coupled_2021": t[True]})


def load_2011():
    x = pd.read_csv(IN_2011)
    x = x[x.C_AGE_NAME.isin(AGE_2011) & x.C_LARPUK11.isin([0, 1])].copy()
    x["band"] = x.C_AGE_NAME.map(AGE_2011)
    x["code"] = x.GEOGRAPHY_CODE.replace(MERGE)
    t = x.groupby(["code", "band", "C_LARPUK11"]).OBS_VALUE.sum().unstack("C_LARPUK11")
    return pd.DataFrame({"women_2011": t[0], "coupled_2011": t[1]})


def load_asfr():
    f = json.loads(FERT.read_text(encoding="utf-8"))
    rows = []
    for code, name in f["lad_names"].items():
        for band, key in BANDS.items():
            r = {"code": code, "name": name, "band": band}
            for y in ("2013", "2021"):
                rec = f["data"].get(y, {}).get(code)
                r[f"asfr_{y}"] = rec.get(key) if rec else None
            rows.append(r)
    return pd.DataFrame(rows).set_index(["code", "band"])


def group(code):
    if code.startswith("W"):
        return "Wales"
    return "London" if code.startswith("E09") else "Rest of England"


def fit(x, y):
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    return a, b, resid / resid.std(ddof=2)


def build():
    d = load_asfr().join(load_2021(), how="inner").join(load_2011(), how="left").reset_index()
    d["share_2021"] = 100 * d.coupled_2021 / d.women_2021
    d["share_2011"] = 100 * d.coupled_2011 / d.women_2011
    d["share_change"] = d.share_2021 - d.share_2011
    # Births per 1,000 coupled women: ASFR (births per 1,000 women, mid-2021 population)
    # divided by the census share of those women living in a couple.
    d["births_per_1000_coupled_2021"] = d.asfr_2021 / (d.share_2021 / 100)
    d["asfr_change_pct_2013_2021"] = 100 * (d.asfr_2021 / d.asfr_2013 - 1)
    d["group"] = d.code.map(group)
    d = d.dropna(subset=["asfr_2021", "share_2021"])
    d["resid_z"] = np.nan
    stats = []
    for band, g in d.groupby("band"):
        a, b, z = fit(g.share_2021.values, g.asfr_2021.values)
        d.loc[g.index, "resid_z"] = z
        keep = np.abs(z) <= OUTLIER_Z
        r = np.corrcoef(g.share_2021, g.asfr_2021)[0, 1]
        r_trim = np.corrcoef(g.share_2021[keep], g.asfr_2021[keep])[0, 1]
        rho = g[["share_2021", "asfr_2021"]].rank().corr().iloc[0, 1]
        bpc = g.births_per_1000_coupled_2021
        la, ls, lb = np.log(g.asfr_2021), np.log(g.share_2021), np.log(bpc)
        ch = g.dropna(subset=["share_change", "asfr_change_pct_2013_2021"])
        stats.append({
            "band": band, "n": len(g), "r": r, "r2": r ** 2, "spearman": rho,
            "slope_asfr_per_pt": b, "n_outliers": int((~keep).sum()), "r_without_outliers": r_trim,
            "cv_asfr": g.asfr_2021.std() / g.asfr_2021.mean(),
            "cv_births_per_coupled": bpc.std() / bpc.mean(),
            "cv_share": g.share_2021.std() / g.share_2021.mean(),
            "sd_log_asfr": la.std(), "sd_log_births_per_coupled": lb.std(), "sd_log_share": ls.std(),
            "corr_log_share_log_bpc": np.corrcoef(ls, lb)[0, 1],
            "asfr_2021_ew": None,
            "share_2021_mean": g.share_2021.mean(), "share_2011_mean": g.share_2011.mean(),
            "share_2021_pooled": 100 * g.coupled_2021.sum() / g.women_2021.sum(),
            "share_2011_pooled": 100 * g.coupled_2011.sum() / g.women_2011.sum(),
            "n_share_fell": int((g.share_change < 0).sum()), "n_change": int(g.share_change.notna().sum()),
            "share_change_min": g.share_change.min(), "share_change_max": g.share_change.max(),
            "r_change_vs_asfr_change": np.corrcoef(ch.share_change, ch.asfr_change_pct_2013_2021)[0, 1],
            "n_change_pairs": len(ch),
            "r_share2011_vs_share2021": np.corrcoef(ch.share_2011, ch.share_2021)[0, 1],
        })
    stats = pd.DataFrame(stats).drop(columns="asfr_2021_ew")
    return d, stats


def label_mask(g):
    lo = g.nsmallest(5, "share_2021").index
    return g.index.isin(lo) | (g.resid_z.abs() > OUTLIER_Z)


def plot_scatter(d, stats):
    bands = list(BANDS)
    fig = make_subplots(rows=1, cols=2, subplot_titles=[
        f"Women {b}: r = {stats.set_index('band').r[b]:.2f}, n = {stats.set_index('band').n[b]}"
        for b in bands])
    for j, band in enumerate(bands, start=1):
        g = d[d.band == band]
        for grp, color in GROUP_COLORS.items():
            h = g[g.group == grp]
            fig.add_trace(go.Scatter(
                x=h.share_2021, y=h.asfr_2021, mode="markers", name=grp, legendgroup=grp,
                showlegend=j == 1, marker=dict(color=color, size=6, opacity=0.75),
                customdata=np.c_[h.name, h.births_per_1000_coupled_2021, h.resid_z],
                hovertemplate="%{customdata[0]}<br>In a couple: %{x:.1f}%<br>ASFR: %{y:.1f}"
                              "<br>Births per 1,000 coupled women: %{customdata[1]:.0f}"
                              "<br>Residual z: %{customdata[2]:.1f}<extra></extra>"), row=1, col=j)
        a, b, _ = fit(g.share_2021.values, g.asfr_2021.values)
        xs = np.array([g.share_2021.min(), g.share_2021.max()])
        fig.add_trace(go.Scatter(x=xs, y=a + b * xs, mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#555", width=1, dash="dash")), row=1, col=j)
        lab = g[label_mask(g)]
        fig.add_trace(go.Scatter(x=lab.share_2021, y=lab.asfr_2021, mode="text", text=lab.name,
                                 textposition="top center", textfont=dict(size=9, color="#333"),
                                 showlegend=False, hoverinfo="skip"), row=1, col=j)
        fig.update_xaxes(title_text="% of women living in a couple (Census 2021)", ticksuffix="%",
                         row=1, col=j)
    fig.update_yaxes(title_text="ASFR 2021 (births per 1,000 women)", row=1, col=1)
    fig.update_layout(template="plotly_white", hovermode="closest",
                      title="Coupling vs fertility by local authority, England and Wales, 2021",
                      legend=dict(orientation="h", y=-0.18, x=0), margin=dict(t=90, b=90))
    return fig


def plot_spread(d):
    """Each LAD's ASFR and births per coupled woman, as % of the median LAD."""
    fig = go.Figure()
    for i, band in enumerate(BANDS):
        g = d[d.band == band]
        for k, (col, lab, color) in enumerate([
                ("asfr_2021", "ASFR (per woman)", "#2c7fb8"),
                ("births_per_1000_coupled_2021", "Births per coupled woman", "#d95f02")]):
            rel = 100 * g[col] / g[col].median()
            fig.add_trace(go.Box(
                x=[f"Women {band}"] * len(g), y=rel, name=lab, legendgroup=lab, showlegend=i == 0,
                marker_color=color, boxpoints="all", jitter=0.4, pointpos=0, marker=dict(size=3),
                offsetgroup=str(k), customdata=np.c_[g.name, g[col]],
                hovertemplate="%{customdata[0]}: %{y:.0f}% of median (%{customdata[1]:.0f} per 1,000)"
                              "<extra></extra>"))
    fig.update_layout(template="plotly_white", boxmode="group",
                      title="Spread across local authorities, 2021 (median LAD = 100)",
                      yaxis=dict(title="% of median local authority", ticksuffix="%"),
                      legend=dict(orientation="h", y=-0.12, x=0), margin=dict(t=70, b=80))
    return fig


def plot_change(d):
    bands = list(BANDS)
    fig = make_subplots(rows=1, cols=2, subplot_titles=[f"Women {b}" for b in bands])
    for j, band in enumerate(bands, start=1):
        g = d[(d.band == band)].dropna(subset=["share_2011"])
        for grp, color in GROUP_COLORS.items():
            h = g[g.group == grp]
            fig.add_trace(go.Scatter(
                x=h.share_2011, y=h.share_2021, mode="markers", name=grp, legendgroup=grp,
                showlegend=j == 1, marker=dict(color=color, size=6, opacity=0.75),
                customdata=np.c_[h.name, h.share_change],
                hovertemplate="%{customdata[0]}<br>2011: %{x:.1f}%<br>2021: %{y:.1f}%"
                              "<br>Change: %{customdata[1]:+.1f} pts<extra></extra>"), row=1, col=j)
        lo, hi = 0, 85
        fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", showlegend=False, hoverinfo="skip",
                                 line=dict(color="#555", width=1, dash="dot")), row=1, col=j)
        fig.update_xaxes(title_text="% in a couple, 2011", ticksuffix="%", range=[lo, hi], row=1, col=j)
        fig.update_yaxes(ticksuffix="%", range=[lo, hi], row=1, col=j)
    fig.update_yaxes(title_text="% in a couple, 2021", row=1, col=1)
    fig.update_layout(template="plotly_white", hovermode="closest",
                      title="Women living in a couple by local authority, Census 2011 vs 2021",
                      legend=dict(orientation="h", y=-0.18, x=0), margin=dict(t=80, b=90))
    return fig


if __name__ == "__main__":
    d, stats = build()
    cols = ["code", "name", "group", "band", "women_2011", "coupled_2011", "share_2011",
            "women_2021", "coupled_2021", "share_2021", "share_change", "asfr_2013", "asfr_2021",
            "asfr_change_pct_2013_2021", "births_per_1000_coupled_2021", "resid_z"]
    d[cols].sort_values(["band", "code"]).round(3).to_csv(OUT / "coupling_by_lad_ew.csv", index=False)
    stats.round(4).to_csv(OUT / "coupling_by_lad_ew_stats.csv", index=False)
    print(stats.T.to_string())
    for band in BANDS:
        g = d[d.band == band]
        print(f"\n{band} labelled:")
        print(g[label_mask(g)][["name", "share_2021", "asfr_2021", "births_per_1000_coupled_2021",
                                "resid_z"]].round(2).to_string(index=False))
    write_html(plot_scatter(d, stats), OUT / "coupling_vs_asfr_lad_ew.html")
    write_html(plot_spread(d), OUT / "births_per_coupled_lad_ew.html")
    write_html(plot_change(d), OUT / "coupling_change_lad_ew.html")
