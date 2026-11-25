"""Split the change in fertility between two years into "fewer couples" and "fewer births per
couple", by country (shift-share decomposition of age-specific fertility, summed to a TFR).

At each age group a (n_a single years wide), fertility f = c*g + (1-c)*h, where c is the share
of women living in a couple (married or cohabiting), g births per coupled woman and h births
per woman not in a couple. Between a base and an end year, with bars for the two-year means,

    n*df = n*dc*(g_bar - h_bar)   fewer couples
         + n*c_bar*dg             births per coupled woman
         + n*(1 - c_bar)*dh       births per woman not in a couple

which adds up exactly. Summed over ages it splits the change in TFR; each part is shown as a
% of the base-year TFR (the FT/Lyman Stone convention: US 2000-2022, -14.5% from fewer couples
and -2.5% from fewer births among couples).

Two kinds of input:
  * Births split by the mother's union status (full split):
      US: ACS/outputs/acs_births_by_union.csv (ACS PUMS, births in the past 12 months by
          single year of age 15-50 and whether the woman lives with a spouse or partner).
      England and Wales: ONS/outputs/births_by_union_ew.csv (birth registrations, married or
          joint-same-address = couple; LFS couple shares; ages 15-29 pooled, 30-34, 35-39,
          40+ over women 40-44).
  * Births not split (all births attributed to couples, h = 0, g = f/c): HFD period ASFR
    (asfrRR.txt) with women's coupling shares from NSO/outputs/coupling_nso.csv (Denmark,
    Finland, Netherlands; single years 15-49), ILO/outputs/coupling_ilo.csv (15-24, 25-34,
    35-44) and UN/outputs/coupling_un.csv (5-year groups 15-49, census and survey years).
    One source per country, in that order. Because births outside couples are counted as
    couples' births, the "fewer couples" part here is an upper bound: each lost couple is
    charged the full births per coupled woman instead of the gap g - h. Ages outside the
    coupling groups go to "other ages". The US and England and Wales are also run this way
    to show the size of that bias.

Years: end = latest year with both fertility and coupling; base = the year closest to 2010 at
least 5 years before it (US: 2008, the nearest ACS year downloaded with comparable coding).

Outputs: HFD/outputs/couples_vs_births_per_couple.csv (one row per country x method) and
couples_vs_births_per_couple_by_age.csv; couples_vs_births_per_couple.html (bar chart).
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from common.country_names import COUNTRY_NAMES
from common.coupling_hfd import ILO_CODES, UN_HFD_CODES
from common.hfd import age_to_int, read_hfd
from common.paths import outputs_dir
from common.plotting import write_html

OUT = outputs_dir("HFD")
TARGET_BASE = 2010
MIN_GAP = 5
MIN_END = 2010  # drop countries whose latest year with both series is earlier
NSO = {"DNK": "Denmark", "FIN": "Finland", "NLD": "Netherlands"}
NSO_AGES = range(15, 50)
ILO_GROUPS = {"15-24": (15, 24), "25-34": (25, 34), "35-44": (35, 44)}
UN_GROUPS = {f"{lo}-{lo + 4}": (lo, lo + 4) for lo in range(15, 50, 5)}
PARTS = [("couples", "Fewer couples", "#d95f02"), ("within", "Births per coupled woman", "#1b9e77"),
         ("outside", "Births per woman not in a couple", "#7570b3"), ("other", "Other ages", "#999999")]


def name(code):
    return {"KOR": "S Korea", "GBRTENW": "England and Wales", "USA": "US"}.get(code, COUNTRY_NAMES.get(code, code))


def split(t, base, end):
    """t: rows for base and end, columns year, age, n (width), c, g, h. Returns per-age parts."""
    b = t[t.year == base].set_index("age")
    e = t[t.year == end].set_index("age")
    cb, gb, hb = ((b[k] + e[k]) / 2 for k in ("c", "g", "h"))
    out = pd.DataFrame({
        "couples": b.n * (e.c - b.c) * (gb - hb),
        "within": b.n * cb * (e.g - b.g),
        "outside": b.n * (1 - cb) * (e.h - b.h),
        "c_base": b.c, "c_end": e.c, "g_base": b.g, "g_end": e.g, "h_base": b.h, "h_end": e.h,
        "f_base": b.n * b.f, "f_end": e.n * e.f,
    })
    return out


def pick_years(years):
    years = sorted(years)
    if not years:
        return None
    end = years[-1]
    cand = [y for y in years if y <= end - MIN_GAP]
    if not cand:
        return None
    return min(cand, key=lambda y: (abs(y - TARGET_BASE), y)), end


def summarise(country, method, source, base, end, by_age, tfr_base, tfr_end):
    s = by_age[["couples", "within", "outside"]].sum()
    covered = by_age.f_end.sum() - by_age.f_base.sum()
    row = {"country": country, "method": method, "coupling_source": source, "base": base, "end": end,
           "tfr_base": tfr_base, "tfr_end": tfr_end, **s.to_dict(), "other": (tfr_end - tfr_base) - covered}
    for k in ["couples", "within", "outside", "other"]:
        row[f"{k}_pct"] = 100 * row[k] / tfr_base
    row["total_pct"] = 100 * (tfr_end - tfr_base) / tfr_base
    return row


# --- full split ---------------------------------------------------------------------------

def full_rows(d, widths):
    d = d.copy()
    d["n"] = d.age.map(widths).fillna(1)
    d["c"] = d.coupled / d.women
    d["g"] = d.births_coupled / d.coupled
    d["h"] = d.births_uncoupled / (d.women - d.coupled)
    d["f"] = (d.births_coupled + d.births_uncoupled) / d.women
    return d


def bound_from_full(d):
    d = d.copy()
    d["g"] = d.f / d.c
    d["h"] = 0.0
    return d


def full_split():
    rows, ages = [], []
    acs = full_rows(pd.read_csv(outputs_dir("ACS") / "acs_births_by_union.csv"), {})
    ew = full_rows(pd.read_csv(outputs_dir("ONS") / "births_by_union_ew.csv"),
                   {"15-29": 15, "30-34": 5, "35-39": 5, "40-44": 5})
    for country, d, base, end, src in [("US", acs, 2008, acs.year.max(), "ACS"),
                                       ("England and Wales", ew, TARGET_BASE, 2024, "ONS LFS")]:
        tb = (d[d.year == base].n * d[d.year == base].f).sum()
        te = (d[d.year == end].n * d[d.year == end].f).sum()
        for method, dd in [("births split by union status", d), ("all births to couples", bound_from_full(d))]:
            a = split(dd, base, end)
            rows.append(summarise(country, method, src, base, end, a, tb, te))
            ages.append(a.reset_index().assign(country=country, method=method, base=base, end=end))
    return rows, ages


# --- HFD + coupling, all births attributed to couples ---------------------------------------

def hfd_asfr():
    a = read_hfd("asfrRR.txt", ["code", "year", "age", "asfr"])
    a["age"] = age_to_int(a.age)
    return a


def bound_rows(asfr, coup, groups, code, country, source):
    """coup: year x group coupling share (0-1); groups: {label: (lo, hi)}."""
    a = asfr[asfr.code == code]
    tfr = a.groupby("year").asfr.sum()
    recs = []
    for g, (lo, hi) in groups.items():
        x = a[a.age.between(lo, hi)].groupby("year").agg(s=("asfr", "sum"), k=("age", "size"))
        x = x[x.k == hi - lo + 1]
        recs.append(pd.DataFrame({"year": x.index, "age": g, "n": hi - lo + 1, "f": x.s.values / (hi - lo + 1)}))
    f = pd.concat(recs)
    d = f.merge(coup, on=["year", "age"])
    full = d.groupby("year").age.nunique()
    years = [y for y in full[full == len(groups)].index if y in tfr.index]
    yrs = pick_years(years)
    if yrs is None:
        return None, None
    base, end = yrs
    if end < MIN_END:
        return None, None
    d["g"] = d.f / d.c
    d["h"] = 0.0
    by_age = split(d[d.year.isin([base, end])], base, end)
    return (summarise(country, "all births to couples", source, base, end, by_age, tfr[base], tfr[end]),
            by_age.reset_index().assign(country=country, method="all births to couples", base=base, end=end))


def hfd_bound():
    asfr = hfd_asfr()
    rows, ages, done = [], [], set()
    nso = pd.read_csv(outputs_dir("NSO") / "coupling_nso.csv")
    nso = nso[(nso.sex == "Women") & nso.age.astype(str).str.isdigit()]
    nso["age"] = nso.age.astype(int)
    for code, country in NSO.items():
        c = nso[(nso.country == country) & nso.age.isin(NSO_AGES)].copy()
        # 5-year groups (mean of single-year shares): at single ages under 18 almost no one is
        # in a couple, so f/c is unstable.
        c["grp"] = c.age.map(lambda a: f"{a - (a - 15) % 5}-{a - (a - 15) % 5 + 4}")
        c = c.groupby(["year", "grp"]).share.agg(["mean", "size"]).reset_index()
        c = c[c["size"] == 5]
        c = pd.DataFrame({"year": c.year, "age": c.grp, "c": c["mean"] / 100})
        r, a = bound_rows(asfr, c, UN_GROUPS, code, country, "national register")
        if r:
            rows.append(r), ages.append(a), done.add(country)
    ilo = pd.read_csv(outputs_dir("ILO") / "coupling_ilo.csv")
    ilo = ilo[(ilo.sex == "women") & ilo.age.isin(ILO_GROUPS)]
    for code, country in ILO_CODES.items():
        if country in done:
            continue
        c = ilo[ilo.ref_area == code]
        c = pd.DataFrame({"year": c.year, "age": c.age, "c": c.share / 100})
        r, a = bound_rows(asfr, c, ILO_GROUPS, code, country, "ILO")
        if r:
            rows.append(r), ages.append(a), done.add(country)
    un = pd.read_csv(outputs_dir("UN") / "coupling_un.csv")
    un = un[(un.sex == "Women") & un.age.isin(UN_GROUPS)]
    for country, code in UN_HFD_CODES.items():
        if country in done:
            continue
        c = un[un.country == country].groupby(["year", "age"]).share.mean().reset_index()
        c = pd.DataFrame({"year": c.year, "age": c.age, "c": c.share / 100})
        r, a = bound_rows(asfr, c, UN_GROUPS, code, country, "UN")
        if r:
            rows.append(r), ages.append(a), done.add(country)
    return rows, ages


def chart(s):
    full = s[s.method == "births split by union status"].sort_values("total_pct")
    bound = s[s.method == "all births to couples"].sort_values("total_pct")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                        row_heights=[len(full) + 1, len(bound) + 1],
                        subplot_titles=["Births split by the mother's union status",
                                        "All births attributed to couples (fewer couples = upper bound)"])
    shown = set()
    for r, d in [(1, full), (2, bound)]:
        labels = [f"{c} {b}–{e}" for c, b, e in zip(d.country, d.base, d.end)]
        for key, label, color in PARTS:
            # no births outside couples in the bound panel; no uncovered ages in the full split
            if (key == "outside" and r == 2) or (key == "other" and r == 1):
                continue
            fig.add_trace(go.Bar(
                y=labels, x=d[f"{key}_pct"], orientation="h", name=label, legendgroup=key,
                marker_color=color, showlegend=key not in shown,
                customdata=d[["tfr_base", "tfr_end", "coupling_source"]],
                hovertemplate=(f"%{{y}}<br>{label}: %{{x:.1f}}% of base TFR<br>TFR %{{customdata[0]:.2f}} → "
                               "%{customdata[1]:.2f}<br>Coupling: %{customdata[2]}<extra></extra>")), row=r, col=1)
            shown.add(key)
        fig.add_trace(go.Scatter(
            y=labels, x=d.total_pct, mode="markers", name="Total change in TFR", legendgroup="total",
            marker=dict(symbol="line-ns-open", size=14, color="black", line=dict(width=2)), showlegend=r == 1,
            hovertemplate="%{y}<br>Total: %{x:.1f}%<extra></extra>"), row=r, col=1)
    fig.update_layout(barmode="relative", template="plotly_white", height=260 + 26 * len(s),
                      legend=dict(orientation="h", y=-0.06), margin=dict(l=10, r=20, t=40, b=40))
    fig.update_xaxes(zeroline=True, zerolinecolor="#444")
    fig.update_xaxes(title_text="% of base-year TFR", row=2, col=1)
    fig.update_yaxes(autorange="reversed")  # largest fall at the top
    return fig


def main():
    r1, a1 = full_split()
    r2, a2 = hfd_bound()
    s = pd.DataFrame(r1 + r2)
    s.round(4).to_csv(OUT / "couples_vs_births_per_couple.csv", index=False)
    pd.concat(a1 + a2).round(5).to_csv(OUT / "couples_vs_births_per_couple_by_age.csv", index=False)
    fig = chart(s)
    write_html(fig, OUT / "couples_vs_births_per_couple.html")
    cols = ["country", "method", "coupling_source", "base", "end", "tfr_base", "tfr_end",
            "couples_pct", "within_pct", "outside_pct", "other_pct", "total_pct"]
    print(s[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
