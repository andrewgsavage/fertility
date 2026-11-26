"""Uruguay's conditional first-birth rates by age, 2016-2021, digitised from Cabella et al. (2024)
"The big decline: Lowest-low fertility in Uruguay (2016-2021)", Demographic Research 50(16), Figure 5.

The figure is a raster image (994 x 596 px) with one line per year; no data file is published.
Each line is traced pixel by pixel from seed points where the lines are apart, keeping pixels
whose nearest reference colour is that year's. Where a line is hidden under one drawn later
(2016 is drawn first, 2021 last), it takes the covering line's position. A few points where
2017's grey-teal line runs into 2018's and 2019's could not be traced and were read by eye from
5x zooms with gridlines drawn in (BY_EYE; flagged "by eye" in the CSV). Axis calibration is from
the figure's gridlines: age 20 at x=292.5 and 50 at x=935; 0.00 at y=380.5, 0.03 per 91 px.

From the rates it also builds a period first-birth table per year (childless women decremented
by exp(-rate) each year of age): the share having a first birth by 25, 30 and 50, and the
table's mean age at first birth.

Input: the paper's PDF, cached in HFC/data/. Outputs: research/data/cabella2024_fig5_ury_casfr1.csv,
HFC/outputs/ury_first_births_fig5.csv (table measures) and HFC/outputs/ury_first_births_fig5.html.
"""

import io

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pypdf
import requests
from PIL import Image

from common.paths import REPO, data_dir, outputs_dir
from common.plotting import write_html

PDF_URL = "https://www.demographic-research.org/volumes/vol50/16/50-16.pdf"
PDF = data_dir("HFC") / "cabella2024_dr50-16.pdf"
CSV = REPO / "research" / "data" / "cabella2024_fig5_ury_casfr1.csv"
OUT = outputs_dir("HFC")

# Line colours in the figure, in drawing order (later years on top).
REF = {2016: (98, 194, 176), 2017: (102, 134, 132), 2018: (80, 128, 151), 2019: (88, 124, 106),
       2020: (190, 190, 190), 2021: (8, 8, 8)}
SEEDS = {2016: [(335, 195), (550, 57.5)], 2017: [(335, 204), (550, 91)], 2018: [(335, 209.5), (550, 105.5)],
         2019: [(335, 225), (550, 120.5)], 2020: [(335, 233)], 2021: [(335, 248.5), (550, 140.5)]}
BY_EYE = {2017: {15: 0.017, 16: 0.028, 21: 0.064, 23: 0.056, 25: 0.057, 26: 0.060, 33: 0.093, 34: 0.089, 35: 0.082},
          2018: {30: 0.081}, 2020: {35: 0.074}}
X0, PXY = 292.5, (935 - 292.5) / 30
Y0, PXU = 380.5, 91 / 0.03
XS = range(140, 941)
AGES = range(13, 50)


def figure5():
    if not PDF.exists():
        PDF.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(PDF_URL, timeout=120)
        r.raise_for_status()
        PDF.write_bytes(r.content)
    page = next(p for p in pypdf.PdfReader(PDF).pages if "Figure 5:" in (p.extract_text() or ""))
    (img,) = page.images
    a = np.asarray(Image.open(io.BytesIO(img.data)).convert("RGB")).astype(float)
    if a.shape[:2] != (596, 994):
        raise ValueError(f"unexpected Figure 5 size {a.shape}; calibration would be wrong")
    return a


def masks(a):
    dist = np.stack([np.linalg.norm(a - np.array(v), axis=2) for v in REF.values()])
    out = {}
    for i, k in enumerate(REF):
        m = (dist.argmin(0) == i) & (dist[i] < (14 if k == 2020 else 25))
        if k == 2020:  # light grey: drop the black line's anti-aliased edges
            dark = a.sum(2) < 450
            near = np.zeros_like(dark)
            for s in range(-3, 4):
                near |= np.roll(dark, s, axis=0)
            m &= (np.ptp(a, axis=2) < 6) & ~near
        out[k] = m
    return out


def trace_from(m, x0, y0):
    ys = {}
    for step in (1, -1):
        y, miss, x = y0, 0, x0
        while XS.start <= x < XS.stop:
            cand = np.where(m[45:386, x])[0] + 45
            cand = cand[abs(cand - y) <= 3 + 1.5 * miss]
            if len(cand):
                nearest = cand[np.argmin(abs(cand - y))]
                y = cand[abs(cand - nearest) <= 2].mean()
                ys[x], miss = y, 0
            else:
                miss += 1
            x += step
    return ys


def trace(m, seeds):
    runs = [trace_from(m, x0, y0) for x0, y0 in seeds]
    out = {}
    for x in sorted(set().union(*runs)):  # each column from the nearest seed's run that reached it
        for i in sorted(range(len(runs)), key=lambda i: abs(seeds[i][0] - x)):
            if x in runs[i]:
                out[x] = runs[i][x]
                break
    return pd.Series(out).sort_index()


def digitise(a):
    ms = masks(a)
    lines = {}
    for k in reversed(list(REF)):  # top-most first, so covering lines are already resolved
        seen = trace(ms[k], SEEDS[k])
        est = seen.reindex(XS).interpolate(limit_area="inside")
        for x in XS:
            if x in seen.index or np.isnan(est[x]):
                continue
            cover = [lines[j][x] for j in lines if not np.isnan(lines[j][x]) and abs(lines[j][x] - est[x]) <= 15]
            if cover:
                est[x] = min(cover, key=lambda c: abs(c - est[x]))
        lines[k] = est
    rows = []
    for k in REF:
        for age in AGES:
            y = lines[k][int(round(X0 + (age - 20) * PXY))]
            if age in BY_EYE.get(k, {}):
                rows.append((k, age, BY_EYE[k][age], "by eye"))
            elif not np.isnan(y):
                rows.append((k, age, max((Y0 - y) / PXU, 0), "traced"))
    return pd.DataFrame(rows, columns=["year", "age", "casfr1", "method"]).sort_values(["year", "age"])


def first_birth_table(d):
    rows = []
    for year, g in d.groupby("year"):
        m = g.set_index("age").casfr1.reindex(AGES).interpolate(limit_direction="both").to_numpy()
        childless = np.exp(-np.concatenate([[0], np.cumsum(m)]))  # at exact ages 13..50
        births = childless[:-1] - childless[1:]
        rows.append({"year": year, "first_birth_by_25": 1 - childless[25 - 13], "first_birth_by_30": 1 - childless[30 - 13],
                     "first_birth_by_50": 1 - childless[-1],
                     "mean_age_first_birth": (births * (np.array(AGES) + 0.5)).sum() / births.sum()})
    return pd.DataFrame(rows).round(3)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = digitise(figure5())
    d.round(4).to_csv(CSV, index=False)
    table = first_birth_table(d)
    table.to_csv(OUT / "ury_first_births_fig5.csv", index=False)
    print(table.to_string(index=False))

    colors = {2016: "#9ecae1", 2017: "#6baed6", 2018: "#4292c6", 2019: "#2171b5", 2020: "#08519c", 2021: "#08306b"}
    fig = go.Figure()
    for year, g in d.groupby("year"):
        fig.add_trace(go.Scatter(x=g.age, y=g.casfr1, mode="lines", name=str(year),
                                 line=dict(color=colors[year], width=3 if year in (2016, 2021) else 1.5),
                                 hovertemplate=f"{year}, age %{{x}}: %{{y:.3f}}<extra></extra>"))
    fig.update_layout(template="plotly_white", margin=dict(l=60, r=20, t=70, b=60),
                      title="Uruguay: first births per childless woman, by age, 2016–2021",
                      xaxis_title="Age", yaxis=dict(title="First births per childless woman", rangemode="tozero"),
                      hovermode="x unified", legend=dict(orientation="h", y=-0.18))
    write_html(fig, OUT / "ury_first_births_fig5.html")


if __name__ == "__main__":
    main()
