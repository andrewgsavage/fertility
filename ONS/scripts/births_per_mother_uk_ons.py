"""Expected number of children a woman will have, given her first birth was
at exact age X, England & Wales, by birth cohort. HFD has no cohort parity-
progression life tables for the UK, so this reconstructs the equivalent
from ONS Table 3 (percentage distribution of women by number of live-born
children, by age and year of birth).

At each age, Table 3's percentage distribution gives the cumulative share
of the cohort with >=1 / >=2 / >=3 / >=4 children. Differencing consecutive
ages turns each of those into a discrete conditional hazard — e.g. the
probability of having a second child during that age, given she had her
first but not yet her second as of the previous age (the same discrete-
hazard idea cond_asfr_uk_ons.py uses for its first/second-birth curves,
extended here up to fourth birth). Table 3 caps at "4 or more", so a woman
who ever reaches a fourth (or higher-order) birth is treated as ending on
exactly 4 — a small approximation, since only a shrinking minority of
modern cohorts go on to a 5th child.

Given those age-specific hazards, load_expected_children_curves() computes,
for every age X, the expected total number of children for a woman whose
*first* birth happened at exactly that age — not a cohort-wide average. It
does this with a backward recursion over age: starting from the oldest
tracked age and working down to X, at each step folding in that age's
chance of the woman moving up one more parity. A woman who has her first
child young has many more years left in which she might have a second,
third, etc., so this curve is decreasing in X by construction.
"""

import pathlib

import openpyxl

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SOURCE = _SCRIPT_DIR.parent / "data" / "finalisingcohorttables2024finalforupload.xlsx"

VALUE_4PLUS = 4.0

# The backward recursion treats "no data past this age" as "assume she has
# no more children past this age" — safe near the end of the fertile
# window, but a severe *under*-estimate for a cohort simply too young for
# the data to have caught up with yet. Only cohorts whose tracked hazards
# reach this age are used at all (mirrors HFD/scripts/births_per_mother_region_grid.py's
# MIN_COMPLETE_AGE for the same reason).
MIN_COMPLETE_AGE = 45


def _load_table3_shares():
    """cohort -> {age: (pct0, pct1, pct2, pct3, pct4plus)}"""
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    ws = wb["Table 3"]
    rows = list(ws.iter_rows(values_only=True))[9:]

    by_cohort = {}
    for year, age, pct0, pct1, pct2, pct3, pct4plus, *_ in rows:
        if year is None or age == "Final":
            continue
        by_cohort.setdefault(year, {})[age] = (pct0, pct1, pct2, pct3, pct4plus)
    return by_cohort


def _safe_ratio(numerator, denominator):
    if denominator is None or denominator <= 0:
        return 0.0
    return max(0.0, numerator / denominator)


def _hazards(shares):
    """{age: (q2, q3, q4)} — discrete parity-progression hazards at each
    age, differenced against the previous age (so the youngest age in a
    cohort's data has none, with nothing to difference against)."""
    sorted_ages = sorted(shares)
    hazards = {}
    prev = None
    for age in sorted_ages:
        pct0, pct1, pct2, pct3, pct4plus = shares[age]
        p1, p2, p3, p4 = 100 - pct0, pct2 + pct3 + pct4plus, pct3 + pct4plus, pct4plus
        if prev is not None and age == prev[0] + 1:
            _, p1_prev, p2_prev, p3_prev, p4_prev = prev
            hazards[age] = (
                _safe_ratio(p2 - p2_prev, p1_prev - p2_prev),
                _safe_ratio(p3 - p3_prev, p2_prev - p3_prev),
                _safe_ratio(p4 - p4_prev, p3_prev - p4_prev),
            )
        prev = (age, p1, p2, p3, p4)
    return hazards


def _expected_children_curve(hazards):
    """{age: E[total children | first birth at exactly this age]}, via
    backward recursion: a woman still at parity k past the oldest tracked
    age is assumed done having children (terminal value k)."""
    ages = sorted(hazards)
    if not ages:
        return {}

    e1_next, e2_next, e3_next = 1.0, 2.0, 3.0
    curve = {}
    for age in reversed(ages):
        q2, q3, q4 = hazards[age]
        e3 = q4 * VALUE_4PLUS + (1 - q4) * e3_next
        e2 = q3 * e3_next + (1 - q3) * e2_next
        e1 = q2 * e2_next + (1 - q2) * e1_next
        curve[age] = e1
        e1_next, e2_next, e3_next = e1, e2, e3
    return curve


def load_expected_children_curves():
    """{cohort: {age: expected total children given first birth at that
    age}} — the reusable entry point for other scripts (see
    HFD/scripts/births_per_mother_region_grid.py, which folds this into
    the Western Europe region grid as a "UK_ONS" column)."""
    by_cohort = _load_table3_shares()
    curves = {}
    for cohort, shares in by_cohort.items():
        curve = _expected_children_curve(_hazards(shares))
        if curve and max(curve) >= MIN_COMPLETE_AGE:
            curves[cohort] = curve
    return curves


if __name__ == "__main__":
    curves = load_expected_children_curves()
    for cohort in [1930, 1950, 1969, 1979]:
        curve = curves[cohort]
        sample = {age: round(curve[age], 2) for age in sorted(curve) if age % 5 == 0}
        print(f"{cohort}: {sample}")
