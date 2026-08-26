"""Period TMR, CPM and TFR for England & Wales, reconstructed from ONS
Table 3 (percentage distribution of women by number of live-born children,
by age and year of birth) -- HFD's tfrRRbo.txt (docs/hfd/mdf.md's main data
source) only has UK birth-order data from 2013, so this extends coverage
back using the same cohort-hazard reslicing approach as
ONS/scripts/cond_asfr_uk_ons.py.

At each age, Table 3's cumulative % distribution (0, 1, 2, 3, 4+ children)
differences into discrete parity-progression hazards -- q1: probability of
a first birth, given still childless; q2/q3/q4: probability of a next
birth, given already at parity 1/2/3 -- exactly like cond_asfr_uk_ons.py's
first/second-birth hazards, extended up to the 4th. Reslicing those cohort
hazards onto calendar (period) years (cohort + age = period year) gives,
for each period year, one age profile of hazards -- which a synthetic
cohort is then run through age by age (the same "if current age-specific
rates persisted for a lifetime" assumption behind any period TFR) to get
that year's TMR (share ever reaching parity >=1), CPM (average parity
among those who do) and TFR (= TMR x CPM, matching the paper's own
identity).
"""

import pathlib

import openpyxl

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SOURCE = _SCRIPT_DIR.parent / "data" / "finalisingcohorttables2024finalforupload.xlsx"

# Table 3 caps at "4 or more children"; treated as exactly 4, a small
# underestimate of TFR/CPM in years with many higher-order births.
VALUE_4PLUS = 4.0
# Table 3 tracks ages 20-45, but the youngest age in each cohort has no
# preceding age to difference against, so the first actual hazard is at 21
# (the age20->21 transition) -- 20 is just the simulation's implicit,
# all-childless starting point.
MIN_AGE, MAX_AGE = 21, 45


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
    return max(0.0, min(1.0, numerator / denominator))


def _hazards(shares):
    """{age: (q1, q2, q3, q4)} parity-progression hazards, differenced
    against the previous age (the youngest tracked age has nothing to
    difference against, so it's skipped)."""
    sorted_ages = sorted(a for a in shares if isinstance(a, int))
    hazards = {}
    prev = None
    for age in sorted_ages:
        pct0, pct1, pct2, pct3, pct4plus = shares[age]
        p1, p2, p3, p4 = 100 - pct0, pct2 + pct3 + pct4plus, pct3 + pct4plus, pct4plus
        if prev is not None and age == prev[0] + 1:
            _, p1_prev, p2_prev, p3_prev, p4_prev = prev
            hazards[age] = (
                _safe_ratio(p1 - p1_prev, 100 - p1_prev),
                _safe_ratio(p2 - p2_prev, p1_prev - p2_prev),
                _safe_ratio(p3 - p3_prev, p2_prev - p3_prev),
                _safe_ratio(p4 - p4_prev, p3_prev - p4_prev),
            )
        prev = (age, p1, p2, p3, p4)
    return hazards


def _reslice_to_period(by_cohort_hazards):
    """{period_year: {age: (q1, q2, q3, q4)}} -- period_year = cohort + age."""
    by_period = {}
    for cohort, ages in by_cohort_hazards.items():
        for age, q in ages.items():
            by_period.setdefault(cohort + age, {})[age] = q
    return by_period


def _synthetic_cohort_metrics(age_hazards):
    """Run a synthetic cohort through MIN_AGE..MAX_AGE using one period
    year's age-specific hazards, returning (TMR, CPM, TFR) -- or None if
    any age in that range is missing for this period year (a partial age
    profile would silently understate every metric rather than fail loud).
    """
    if any(age not in age_hazards for age in range(MIN_AGE, MAX_AGE + 1)):
        return None
    s0, s1, s2, s3, s4 = 1.0, 0.0, 0.0, 0.0, 0.0
    for age in range(MIN_AGE, MAX_AGE + 1):
        q1, q2, q3, q4 = age_hazards[age]
        s0, s1, s2, s3, s4 = (
            s0 * (1 - q1),
            s1 * (1 - q2) + s0 * q1,
            s2 * (1 - q3) + s1 * q2,
            s3 * (1 - q4) + s2 * q3,
            s4 + s3 * q4,
        )
    tmr = 1 - s0
    tfr = s1 + 2 * s2 + 3 * s3 + VALUE_4PLUS * s4
    cpm = tfr / tmr if tmr > 0 else None
    return tmr, cpm, tfr


def load_period_metrics():
    """{period_year: (TMR, CPM, TFR)} -- the reusable entry point for other
    scripts, mirroring cond_asfr_uk_ons.py's load_period_rates()."""
    by_cohort = _load_table3_shares()
    by_cohort_hazards = {cohort: _hazards(shares) for cohort, shares in by_cohort.items()}
    by_period_hazards = _reslice_to_period(by_cohort_hazards)

    metrics = {}
    for year, age_hazards in by_period_hazards.items():
        result = _synthetic_cohort_metrics(age_hazards)
        if result is not None:
            metrics[year] = result
    return metrics


if __name__ == "__main__":
    metrics = load_period_metrics()
    for year in sorted(metrics):
        tmr, cpm, tfr = metrics[year]
        print(f"{year}: TMR={tmr:.3f} CPM={cpm:.3f} TFR={tfr:.3f}")
