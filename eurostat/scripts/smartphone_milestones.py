"""Per-country milestone years: mobile internet, young-age fertility peaks and slope breaks,
smartphone take-off and Tinder arrival.

- ASFR at 20-24 and 25-29: Eurostat demo_frate for the countries it covers; otherwise the
  mean of single-year HFD asfrRR.txt rates (UK, whose Eurostat series ends in 2018; US, Canada, Japan, South Korea, Taiwan, Chile,
  Russia, Belarus, Ukraine), Human Fertility Collection vital-registration rates (Australia,
  New Zealand), or MSP births over INE women (Uruguay, HFC/scripts/uruguay_by_order.py).
- Mobile internet: first year Eurostat I_IUMP (isoc_ci_im_i), ages 16-24, exceeds 60%
  (Eurostat countries only).
- ASFR peaks: year of the maximum 3-year centred average from PEAK_FROM on (PEAK_FROM
  itself means already falling then).
- ASFR slope breaks: continuous piecewise-linear fits to log ASFR from PEAK_FROM on, with
  0, 1 or 2 breaks (each segment at least MIN_SEG years), break years found by grid search
  for least squared error. The number of breaks is the one with the lowest BIC, counting
  each break as two parameters (its year and its slope change). Reports the break years and
  each segment's slope (% a year).
- Smartphone take-off: the FT's year (Burn-Murdoch, May 2026) and the Google Trends
  app-store search year, both from FT/outputs/smartphone_takeoff_years.csv
  (FT/scripts/smartphone_takeoff.py).
- Tinder: arrival as dated on docs/factors/dating-apps.md.

Outputs (eurostat/outputs/): smartphone_milestones.csv and
smartphone_milestones.html (segment timeline); prints a Markdown table.
"""

import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.paths import data_dir, outputs_dir
from common.plotting import write_html
from young_fertility import DATA, NAMES, OUTDIR, internet_use

THRESHOLD = 60
PEAK_FROM = 2005
MIN_SEG = 3
LAST_YEAR = 2024
TAKEOFF = outputs_dir("FT") / "smartphone_takeoff_years.csv"
HFD = data_dir("HFD") / "HFD" / "asfrRR.txt"
HFC = DATA / "change_matrix"  # hfc_<ISO>_ASFRstand_TOT.txt, fetched on first use
ROOT = DATA.parents[1]

# ISO3 -> (name, region). Eurostat countries use demo_frate; the rest the source in SOURCE.
COUNTRIES = {
    "DNK": ("Denmark", "Nordic"), "FIN": ("Finland", "Nordic"), "ISL": ("Iceland", "Nordic"),
    "NOR": ("Norway", "Nordic"), "SWE": ("Sweden", "Nordic"),
    "AUT": ("Austria", "Western Europe"), "BEL": ("Belgium", "Western Europe"),
    "CHE": ("Switzerland", "Western Europe"), "DEU": ("Germany", "Western Europe"),
    "FRA": ("France", "Western Europe"), "GBR": ("United Kingdom", "Western Europe"),
    "IRL": ("Ireland", "Western Europe"), "LUX": ("Luxembourg", "Western Europe"),
    "NLD": ("Netherlands", "Western Europe"),
    "CYP": ("Cyprus", "Southern Europe"), "ESP": ("Spain", "Southern Europe"),
    "GRC": ("Greece", "Southern Europe"), "ITA": ("Italy", "Southern Europe"),
    "MLT": ("Malta", "Southern Europe"), "PRT": ("Portugal", "Southern Europe"),
    "BGR": ("Bulgaria", "Central & Eastern Europe"), "CZE": ("Czechia", "Central & Eastern Europe"),
    "EST": ("Estonia", "Central & Eastern Europe"), "HRV": ("Croatia", "Central & Eastern Europe"),
    "HUN": ("Hungary", "Central & Eastern Europe"), "LTU": ("Lithuania", "Central & Eastern Europe"),
    "LVA": ("Latvia", "Central & Eastern Europe"), "POL": ("Poland", "Central & Eastern Europe"),
    "ROU": ("Romania", "Central & Eastern Europe"), "SVK": ("Slovakia", "Central & Eastern Europe"),
    "SVN": ("Slovenia", "Central & Eastern Europe"),
    "ALB": ("Albania", "Balkans, Türkiye, ex-USSR"), "MNE": ("Montenegro", "Balkans, Türkiye, ex-USSR"),
    "MKD": ("North Macedonia", "Balkans, Türkiye, ex-USSR"), "SRB": ("Serbia", "Balkans, Türkiye, ex-USSR"),
    "TUR": ("Turkey", "Balkans, Türkiye, ex-USSR"), "BLR": ("Belarus", "Balkans, Türkiye, ex-USSR"),
    "RUS": ("Russia", "Balkans, Türkiye, ex-USSR"), "UKR": ("Ukraine", "Balkans, Türkiye, ex-USSR"),
    "AUS": ("Australia", "English-speaking"), "CAN": ("Canada", "English-speaking"),
    "NZL": ("New Zealand", "English-speaking"), "USA": ("United States", "English-speaking"),
    "JPN": ("Japan", "East Asia"), "KOR": ("South Korea", "East Asia"), "TWN": ("Taiwan", "East Asia"),
    "CHL": ("Chile", "Latin America"), "URY": ("Uruguay", "Latin America"),
}
REGIONS = list(dict.fromkeys(r for _, r in COUNTRIES.values()))
HFD_CODES = {"GBR": "GBR_NP", "USA": "USA", "CAN": "CAN", "JPN": "JPN", "KOR": "KOR", "TWN": "TWN", "CHL": "CHL",
             "RUS": "RUS", "BLR": "BLR", "UKR": "UKR"}
HFC_CODES = ("AUS", "NZL")
TINDER = {"USA": "2012", "GBR": "2013", "NLD": "2013", "DEU": "2013–14", "FRA": "2013", "ESP": "2013",
          "FIN": "2013–14", "POL": "≥2014"}
# Name in smartphone_takeoff_years.csv, where it differs from COUNTRIES.
TRENDS_NAMES = {"GBR": "UK", "TUR": "Türkiye", "USA": "US", "KOR": "S Korea"}
SHORT = {"United Kingdom": "UK", "United States": "US", "North Macedonia": "N. Macedonia",
         "South Korea": "S. Korea", "New Zealand": "NZ"}
REGION_LABELS = {"Central & Eastern Europe": "Central &<br>Eastern Europe", "Balkans, Türkiye, ex-USSR": "Balkans,<br>Türkiye, ex-USSR",
                 "English-speaking": "English-<br>speaking", "Latin America": "Latin<br>America",
                 "Western Europe": "Western<br>Europe", "Southern Europe": "Southern<br>Europe", "East Asia": "East<br>Asia"}
FALL, MID, RISE = "#e34948", "#f0efec", "#2a78d6"
LIMIT = 10  # % a year at the ends of the colour scale


# ---------- data ----------

YOUNG = ("20-24", "25-29")


def eurostat_asfr(bands=YOUNG):
    """{age: wide table year x ISO3} from demo_frate."""
    d = pd.read_csv(DATA / "demo_frate.csv", usecols=["age", "geo", "TIME_PERIOD", "OBS_VALUE"])
    iso = {v[0]: k for k, v in COUNTRIES.items()}
    d = d[d.geo.isin(NAMES)].assign(iso=lambda x: x.geo.map(NAMES).map(iso)).dropna(subset=["iso"])
    return {a: d[d.age == f"Y{a}"].pivot(index="TIME_PERIOD", columns="iso", values="OBS_VALUE").sort_index()
            for a in bands}


def group_means(d, year, age, rate, bands=YOUNG):
    """Single-year rates -> mean over each 5-year band ("20-24", ...), by year; a band needs all five ages."""
    lo = {b: int(b[:2]) for b in bands}
    d = d[d[age].isin([a for b in bands for a in range(lo[b], lo[b] + 5)])]
    d = d.assign(g=d[age].map({a: b for b in bands for a in range(lo[b], lo[b] + 5)}))
    m = d.groupby([year, "g"])[rate].agg(["mean", "count"])
    m = m[m["count"] == 5]["mean"].unstack()
    return {a: m[a] for a in m}


def hfd_asfr(code, bands=YOUNG):
    d = pd.read_csv(HFD, sep=r"\s+", skiprows=2, dtype={"Age": str})
    d = d[(d.Code == code) & d.Age.str.isdigit()].astype({"Age": int, "ASFR": float})
    return group_means(d, "Year", "Age", "ASFR", bands)


def hfc_asfr(iso, bands=YOUNG):
    path = HFC / f"hfc_{iso}_ASFRstand_TOT.txt"
    if not path.exists():
        import urllib.request
        url = f"https://www.fertilitydata.org/File/GetFile/Country/{iso}%5C{iso}_ASFRstand_TOT.txt"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    d = pd.read_csv(path, skipinitialspace=True, na_values=".")
    d.columns = d.columns.str.strip()
    for k in ("Collection", "AgeDef", "RefCode"):
        d[k] = d[k].str.strip()
    d = d[(d.Year1 == d.Year2) & (d.Collection == "STAT") & (d.AgeDef == "ACY") & (d.AgeInt == 1)]
    d = d.sort_values("RefCode").drop_duplicates(["Year1", "Age"], keep="last")
    return group_means(d, "Year1", "Age", "ASFR", bands)


def uruguay_asfr(bands=YOUNG):
    sys.path.insert(0, str(ROOT / "HFC" / "scripts"))
    import uruguay_by_order as ury
    a = (ury.births() / ury.women()).dropna()
    return {g: a[g] for g in bands if g in a}


def load_asfr(bands=YOUNG):
    """{ISO3: {"20-24": Series, "25-29": Series}}, or the given 5-year bands."""
    eu = eurostat_asfr(bands)
    out = {c: {a: eu[a][c].dropna() for a in eu if c in eu[a]} for c in COUNTRIES if c in eu[bands[0]]}
    for c, code in HFD_CODES.items():
        out[c] = hfd_asfr(code, bands)
    for c in HFC_CODES:
        out[c] = hfc_asfr(c, bands)
    out["URY"] = uruguay_asfr(bands)
    return {c: {a: s[s.index <= LAST_YEAR] for a, s in v.items()} for c, v in out.items()}


# ---------- measures ----------

def peak_year(s):
    s = s.dropna()
    s = s.rolling(3, center=True, min_periods=2).mean()
    s = s[s.index >= PEAK_FROM]
    if not len(s):
        return None
    y = int(s.idxmax())
    return f"≤{y}" if y == s.index[0] else str(y)


def _fit(t, y, breaks):
    x = np.column_stack([np.ones_like(t), t] + [np.maximum(0, t - b) for b in breaks])
    coef = np.linalg.lstsq(x, y, rcond=None)[0]
    return np.sum((y - x @ coef) ** 2), coef


def slope_breaks(s):
    """(break years, segment slopes in % a year, first year, last year) for the BIC-best fit
    with 0-2 breaks."""
    s = s.dropna()
    s = s[s.index >= PEAK_FROM]
    t, y = s.index.to_numpy(float), np.log(s.to_numpy())
    n = len(t)
    if n < 2 * MIN_SEG + 2:
        return None
    cands = list(t[MIN_SEG:-MIN_SEG])
    options = [()] + [(b,) for b in cands] + [(a, b) for a in cands for b in cands if b - a >= MIN_SEG]
    best = {}
    for br in options:
        sse, coef = _fit(t, y, br)
        k = len(br)
        if k not in best or sse < best[k][0]:
            best[k] = (sse, br, coef)
    bic = {k: n * np.log(v[0] / n) + (2 + 2 * k) * np.log(n) for k, v in best.items()}
    _, br, coef = best[min(bic, key=bic.get)]
    slopes = np.cumsum(coef[1:])
    return ([int(b) for b in br], [round(100 * (np.exp(g) - 1), 1) for g in slopes],
            int(t[0]), int(t[-1]))


def first_above(s, t):
    s = s.dropna()
    hit = s[s > t]
    if not len(hit):
        return None
    y = int(hit.index[0])
    return f"≤{y}" if y == s.index[0] else str(y)


def year_of(v):
    return None if v is None else int(str(v).lstrip("≤≥")[:4])


def fmt_breaks(res):
    if res is None:
        return None, None
    br, sl = res[:2]
    return ", ".join(map(str, br)) or "none", " → ".join(f"{v:+.1f}" for v in sl)


def milestones():
    """{ISO3: dict} with every measure, for countries with ASFR data."""
    use = internet_use("imp_slim.csv")
    asfr = load_asfr()
    take = pd.read_csv(TAKEOFF).set_index("country")
    out = {}
    for c, (name, region) in COUNTRIES.items():
        if c not in asfr:
            continue
        t = TRENDS_NAMES.get(c, name)
        t = take.loc[t] if t in take.index else None
        out[c] = dict(
            name=name, region=region,
            mobile=first_above(use[name], THRESHOLD) if name in use else None,
            peak_20_24=peak_year(asfr[c]["20-24"]), peak_25_29=peak_year(asfr[c]["25-29"]),
            fit_20_24=slope_breaks(asfr[c]["20-24"]), fit_25_29=slope_breaks(asfr[c]["25-29"]),
            ft=None if t is None or pd.isna(t.ft_takeoff) else int(t.ft_takeoff),
            search=None if t is None or pd.isna(t.search_takeoff) else int(t.search_takeoff),
            tinder=TINDER.get(c))
    return out


# ---------- outputs ----------

def chart_order(ms):
    """Region blocks in REGIONS order; within a region, by mobile >60% year, search take-off, name."""
    key = lambda c: (REGIONS.index(ms[c]["region"]), year_of(ms[c]["mobile"]) or 9999, ms[c]["search"] or 9999,
                     ms[c]["name"])
    return sorted([c for c in ms if ms[c]["fit_20_24"] or ms[c]["fit_25_29"]], key=key)


def timeline_chart(ms):
    """Countries as rows, fitted ASFR segments coloured by % a year, milestone markers; 20-24 and
    25-29 side by side."""
    order = chart_order(ms)
    label = lambda c: SHORT.get(ms[c]["name"], ms[c]["name"])
    names = [label(c) for c in order]
    n = len(order)
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.03,
                        subplot_titles=("ASFR 20–24, fitted segments", "ASFR 25–29, fitted segments"))
    scale = [[0, FALL], [0.5, MID], [1, RISE]]
    for col, age in enumerate(("20_24", "25_29"), start=1):
        cats, base, length, val, text = [], [], [], [], []
        for c in order:
            res = ms[c][f"fit_{age}"]
            if res is None:
                continue
            br, sl, t0, t1 = res
            edges = [t0, *br, t1]
            for a, b, v in zip(edges[:-1], edges[1:], sl):
                cats.append(label(c)), base.append(a), length.append(b - a), val.append(v)
                text.append(f"{ms[c]['name']}, {a}–{b}: {v:+.1f}% a year")
        fig.add_trace(go.Bar(
            x=length, y=cats, base=base, width=0.75, orientation="h",
            marker=dict(color=val, colorscale=scale, cmin=-LIMIT, cmax=LIMIT,
                        line=dict(color="#fcfcfb", width=2), showscale=col == 1,
                        colorbar=dict(title="% a year", ticksuffix="%", len=0.3, y=1, yanchor="top")),
            hovertext=text, hoverinfo="text", showlegend=False), row=1, col=col)
        for key, name, symbol in (("mobile", "Mobile internet 16–24 >60%", "diamond"),
                                  ("search", "App-store search take-off", "triangle-up"),
                                  ("tinder", "Tinder arrival", "circle-open")):
            pts = [(label(c), year_of(ms[c][key])) for c in order if ms[c][key]]
            fig.add_trace(go.Scatter(
                x=[yr for _, yr in pts], y=[p for p, _ in pts], mode="markers", name=name, legendgroup=key,
                showlegend=col == 1,
                marker=dict(symbol=symbol, size=9, color="#1f1f1e", line=dict(width=1.5, color="#1f1f1e")),
                hovertemplate="%{y}: " + name + " %{x}<extra></extra>"), row=1, col=col)
    # Region labels in the left margin and dividers. Rows run top to bottom, so a country's
    # category position is n - 1 - its index.
    for r in REGIONS:
        idx = [k for k, c in enumerate(order) if ms[c]["region"] == r]
        if not idx:
            continue
        fig.add_annotation(x=0, xref="paper", xanchor="right", xshift=-112, y=n - 1 - (idx[0] + idx[-1]) / 2,
                           yref="y", showarrow=False, align="right", text=REGION_LABELS.get(r, r),
                           font=dict(size=10, color="#6b6b68"))
        if idx[0] > 0:
            for k in ("", "2"):
                fig.add_shape(type="line", y0=n - 0.5 - idx[0], y1=n - 0.5 - idx[0], x0=0, x1=1, yref="y",
                              xref=f"x{k} domain", line=dict(color="#bdbcb8", width=1))
    fig.update_xaxes(range=[PEAK_FROM - 0.5, LAST_YEAR + 0.5], dtick=5, gridcolor="#ecebe8")
    fig.update_yaxes(categoryorder="array", categoryarray=names[::-1], tickfont=dict(size=11))
    fig.update_annotations(selector=dict(text="ASFR 20–24, fitted segments"), font=dict(size=12))
    fig.update_annotations(selector=dict(text="ASFR 25–29, fitted segments"), font=dict(size=12))
    fig.update_layout(template="plotly_white", barmode="overlay", hovermode="closest", height=22 * n + 150,
                      legend=dict(orientation="h", y=1.0, yanchor="top", yref="container", x=0, xanchor="left"),
                      margin=dict(t=90, l=230, r=20, b=40))
    return fig


def main():
    ms = milestones()
    rows = []
    for c in sorted(ms, key=lambda c: ms[c]["name"]):
        m = ms[c]
        b20, s20 = fmt_breaks(m["fit_20_24"])
        b25, s25 = fmt_breaks(m["fit_25_29"])
        rows.append({"iso": c, "country": m["name"], f"mobile_internet_16_24_over_{THRESHOLD}": m["mobile"],
                     "asfr_20_24_peak": m["peak_20_24"], "asfr_25_29_peak": m["peak_25_29"],
                     "asfr_20_24_breaks": b20, "asfr_20_24_pct_a_year": s20,
                     "asfr_25_29_breaks": b25, "asfr_25_29_pct_a_year": s25,
                     "ft_takeoff": m["ft"], "trends_takeoff": m["search"], "tinder": m["tinder"]})
    out = pd.DataFrame(rows)
    for k in ("ft_takeoff", "trends_takeoff"):
        out[k] = out[k].astype("Int64")
    out.to_csv(OUTDIR / "smartphone_milestones.csv", index=False)
    write_html(timeline_chart(ms), OUTDIR / "smartphone_milestones.html")
    cols = ["Country", f"Mobile >{THRESHOLD}%", "20–24 peak", "25–29 peak", "20–24 breaks",
            "20–24 %/yr by segment", "25–29 breaks", "25–29 %/yr by segment", "FT take-off",
            "Search take-off", "Tinder"]
    print("| " + " | ".join(cols) + " |")
    print("|---|" + "--:|" * (len(cols) - 1))
    blank = lambda v: "" if v is None or pd.isna(v) else str(v)
    for r in out.drop(columns="iso").itertuples(index=False):
        print("| " + " | ".join(blank(v) for v in r) + " |")


if __name__ == "__main__":
    main()
