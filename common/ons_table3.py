"""ONS cohort fertility tables, Table 3: percentage distribution of women by number of
live-born children, by age and year of birth, England & Wales.

Input (ONS/data/, not tracked in git): finalisingcohorttables2024finalforupload.xlsx.

Conditional (parity-progression) rates for first and second births, used by
ONS/scripts/cond_asfr_uk_ons.py and folded into HFD and cross-country charts as the UK.
At each exact age, the conditional rate is estimated as a discrete hazard:
  cond1(age) = (P1(age) - P1(age-1)) / (100 - P1(age-1))
  cond2(age) = (P2(age) - P2(age-1)) / (P1(age-1) - P2(age-1))
where P1/P2 are cumulative % of the cohort with >=1 / >=2 children.
"""

import openpyxl

from common.paths import REPO

SOURCE = REPO / "ONS" / "data" / "finalisingcohorttables2024finalforupload.xlsx"
MIN_PERIOD_YEAR = 2005


def _table3_rows():
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    ws = wb["Table 3"]
    return list(ws.iter_rows(values_only=True))[9:]


def load_table3():
    """cohort -> {age: (P1, P2)}, cumulative % with >=1 / >=2 children."""
    by_cohort = {}
    for year, age, pct0, pct1, pct2, pct3, pct4plus, *_ in _table3_rows():
        if year is None or age == "Final":
            continue
        p1 = 100 - pct0
        p2 = pct2 + pct3 + pct4plus
        by_cohort.setdefault(year, {})[age] = (p1, p2)
    return by_cohort


def load_table3_shares():
    """cohort -> {age: (pct0, pct1, pct2, pct3, pct4plus)}"""
    by_cohort = {}
    for year, age, pct0, pct1, pct2, pct3, pct4plus, *_ in _table3_rows():
        if year is None or age == "Final":
            continue
        by_cohort.setdefault(year, {})[age] = (pct0, pct1, pct2, pct3, pct4plus)
    return by_cohort


def conditional_rates(by_cohort):
    """cohort -> {age: (cond1, cond2)}, skipping the first age each cohort has."""
    result = {}
    for cohort, ages in by_cohort.items():
        sorted_ages = sorted(ages)
        cohort_rates = {}
        for prev_age, age in zip(sorted_ages, sorted_ages[1:]):
            if age != prev_age + 1:
                continue
            p1_prev, p2_prev = ages[prev_age]
            p1, p2 = ages[age]
            childless_prev = 100 - p1_prev
            one_child_prev = p1_prev - p2_prev
            c1 = max(0.0, (p1 - p1_prev) / childless_prev) if childless_prev > 0 else None
            c2 = max(0.0, (p2 - p2_prev) / one_child_prev) if one_child_prev > 0 else None
            cohort_rates[age] = (c1, c2)
        result[cohort] = cohort_rates
    return result


def to_period(rates, min_period_year):
    """Reslice the cohort-hazard Lexis diagram into period-year lines: for
    period year Y and age A, the transition happened to cohort (Y - A).
    Gives one age-profile line per calendar year, like HFD's period charts,
    even though the underlying hazard is still computed along each cohort.
    """
    by_period = {}
    for cohort, ages in rates.items():
        for age, (c1, c2) in ages.items():
            period_year = cohort + age
            if period_year < min_period_year:
                continue
            by_period.setdefault(period_year, {})[age] = (c1, c2)
    return by_period


def load_period_rates(min_period_year=MIN_PERIOD_YEAR):
    """{period_year: {age: (cond1, cond2)}} — the reusable entry point for
    other scripts (see HFD/scripts/cond_asfr_facet.py, which folds this
    in as a "UK_ONS" column)."""
    by_cohort = load_table3()
    rates = conditional_rates(by_cohort)
    return to_period(rates, min_period_year)


def load_cohort_cumulative():
    """{cohort: {age: (P1, P2)}} — the cumulative % of the cohort with
    >=1 / >=2 children, i.e. load_table3()'s raw values directly (already
    cohort-indexed, like load_cohort_rates()).
    """
    return load_table3()


def load_cohort_rates():
    """{cohort: {age: (cond1, cond2)}} — the cohort-indexed counterpart to
    load_period_rates()."""
    by_cohort = load_table3()
    return conditional_rates(by_cohort)
