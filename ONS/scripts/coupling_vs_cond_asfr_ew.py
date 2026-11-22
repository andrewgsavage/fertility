"""First-birth conditional ASFR against the share of women living in a couple, England
and Wales, 2002 onward: a connected time series with separate age choices for x and y.

y: first births per childless woman, from the parity-hazard reconstruction in
   cond_asfr_uk_ons.py (ONS cohort table 3), single ages 21-45. A y age range pools its
   single ages, weighted by the share of the cohort still childless at the previous age.
x: % of women in an ONS living-arrangements age group living in a couple (married, civil
   partnered or cohabiting), or cohabiting only, from coupling_by_age_ew.py.

The first-birth rates and dual_dropdown_fig() are in common/coupling_ew.py, shared with
ILO/scripts/coupling_vs_cond_asfr.py and others.

Inputs (ONS/data/, not tracked in git): finalisingcohorttables2024finalforupload.xlsx and
families/maritalstatuslivingarrangements2002to2025englandandwales.xlsx.
"""

import pandas as pd

import coupling_by_age_ew
from common.coupling_ew import (CHILDLESS_AGES, GROUP_OPTS, Y_RANGES, dual_dropdown_fig, first_birth_rates,
                                 mothers_ew, y_options)
from common.paths import outputs_dir
from common.plotting import write_html
from common.ratio_lines import write_ratio_lines
from common.trend_arrows import write_trend_arrows

OUTDIR = outputs_dir("ONS")
FIRST_YEAR = 2002
X_GROUPS = {"16 to 29": "16-29", "30 to 34": "30-34", "35 to 39": "35-39", "40 to 44": "40-44",
            "45 to 49": "45-49"}


def load():
    rates = first_birth_rates().join(mothers_ew(), how="outer")
    c = coupling_by_age_ew.load()
    c = c[c.sex == "Women"]
    years = sorted(set(rates.index) & set(c.year))
    years = [y for y in years if y >= FIRST_YEAR]
    x = {}
    for group, lab in X_GROUPS.items():
        g = c[c.age == group].set_index("year")
        x[f"couple {lab}"] = [g.couple.get(y) for y in years]
        x[f"cohab {lab}"] = [g.cohab.get(y) for y in years]
    y = {k: [None if pd.isna(v) else v for v in rates[k].reindex(years)] for k in y_options(Y_RANGES) | GROUP_OPTS}
    return {"name": "England and Wales", "color": "#444444", "years": years, "x": x, "y": y}


# % with a child only (docs/factors/coupling-vs-mothers.md): by exact age, and among women in
# a 5-year age group.
MOTHER_OPTS = {f"mother {a}": f"% of women with a child by {a}" for a in CHILDLESS_AGES} | GROUP_OPTS


def write_mothers(s):
    """In a couple at 16-29 (married, civil partnered or cohabiting; 18-29 in 2025) against % with
    a child by 30, the end of that age range, as a trend arrow (common/trend_arrows.py), as the
    other charts on docs/factors/coupling-vs-mothers.md."""
    write_trend_arrows(
        OUTDIR / "coupling_vs_mothers_ew.html",
        [{"name": "England and Wales", "label": "E&W", "color": "#444444", "years": s["years"],
          "x": {"couple 16-29": s["x"]["couple 16-29"]}, "y": {"mother 30": s["y"]["mother 30"]}}],
        {"couple 16-29": "% of women in a couple, 16-29"}, {"mother 30": MOTHER_OPTS["mother 30"]},
        title="England and Wales linear trend, 2002 to 2025 (points: every year)",
        x_suffix="%", y_suffix="%", equal=True, layout=dict(showlegend=False))
    write_ratio_lines(
        OUTDIR / "coupling_vs_mothers_ew_ratio.html",
        [{"name": "England and Wales", "label": "E&W", "color": "#444444", "years": s["years"],
          "x": {"couple 16-29": s["x"]["couple 16-29"]}, "y": {"mother 30": s["y"]["mother 30"]}}],
        [{"x": "couple 16-29", "y": "mother 30", "title": "With a child by 30 ÷ in a couple at 16-29"}],
        title="% of women with a child ÷ % in a couple, England and Wales, by year", cols=1)


def plot(s):
    x_opts = {f"couple {lab}": f"in a couple {lab}" for lab in X_GROUPS.values()}
    x_opts |= {f"cohab {lab}": f"cohabiting {lab}" for lab in X_GROUPS.values()}
    return dual_dropdown_fig(
        [s], x_opts, y_options(Y_RANGES), "couple 30-34", "30-34",
        "First-birth rate vs women in a couple, England and Wales",
        "% of women", color_by_year=True)


if __name__ == "__main__":
    s = load()
    pd.DataFrame({"year": s["years"], **s["x"], **{f"y_{k}": v for k, v in s["y"].items()}}).round(3) \
        .to_csv(OUTDIR / "coupling_vs_cond_asfr_ew.csv", index=False)
    write_html(plot(s), OUTDIR / "coupling_vs_cond_asfr_ew.html")
    write_mothers(s)
