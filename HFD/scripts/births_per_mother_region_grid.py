import pathlib
import sys

import pandas as pd

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from births_per_mother_uk_ons import load_expected_children_curves as load_uk_curves  # noqa: E402

# HFD's cft.txt caps its birth-order breakdown at "5th or higher order" (a
# woman who reaches it is folded into a single q5px hazard with no further
# split). This approximates that terminal state as exactly 5 children — a
# small undercount for the shrinking few who go on to a 6th+, negligible in
# these mostly-modern, mostly-low-fertility cohorts.
VALUE_5PLUS = 5.0

# The backward recursion treats "no data past this age" as "assume she has
# no more children past this age" — a safe assumption near the end of the
# fertile window, but a severe *under*-estimate for a cohort that's simply
# too young for the data to have caught up with yet (e.g. a cohort tracked
# only to age 25 would have every one of its curves collapse to ~1 by 25,
# as if every woman stopped at her first child). So only cohorts whose
# tracked data reaches this age are used at all — this is why some
# countries with only recently-started HFD coverage (Belgium, Croatia,
# South Korea) show no lines: none of their tracked cohorts are old enough
# yet for this page's terminal-age assumption to be safe.
MIN_COMPLETE_AGE = 40
X_LIM = (18, 45)
Y_LIM = (1.0, 4.0)


def load_data():
    cft = pd.read_csv(
        "data/HFD/cft.txt",
        sep=r"\s+",
        skiprows=3,
        names=["code", "cohort", "x", "b1x", "l0x", "m1x", "q1x", "Sb1x",
               "b2x", "l1x", "m2x", "q2x", "Sb2x",
               "b3x", "l2x", "m3x", "q3x", "Sb3x",
               "b4x", "l3x", "m4x", "q4x", "Sb4x",
               "b5px", "l4x", "m5px", "q5px", "Sb5px", "chix"],
        na_values=".",
    )
    cft = cft[pd.to_numeric(cft["x"], errors="coerce").notna()].copy()
    cft["x"] = cft["x"].astype(int)

    max_tracked_age = cft.dropna(subset=["q2x"]).groupby(["code", "cohort"])["x"].max()
    complete_cohorts = max_tracked_age[max_tracked_age >= MIN_COMPLETE_AGE].index

    rows = []
    for (code, cohort), sub in cft.groupby(["code", "cohort"]):
        if (code, cohort) not in complete_cohorts:
            continue
        for age, value in _expected_children_curve(sub).items():
            rows.append({"code": code, "cohort": cohort, "age": age, "expected_children": value})

    uk_rows = [
        {"code": "UK_ONS", "cohort": cohort, "age": age, "expected_children": value}
        for cohort, curve in load_uk_curves().items()
        for age, value in curve.items()
    ]
    return pd.DataFrame(rows + uk_rows)


def _expected_children_curve(sub):
    """{age: E[total children | first birth at exactly this age]} for one
    (code, cohort) group of cft.txt — a backward recursion over age using
    that cohort's own parity-progression hazards (q2x..q5px): starting from
    the oldest tracked age and working down, at each step folding in that
    age's chance of moving up one more parity. A woman still short of the
    next parity past the oldest tracked age is assumed done having
    children (terminal value = her current parity)."""
    sub = sub.sort_values("x")
    ages = sub["x"].to_numpy()
    q2 = sub["q2x"].fillna(0).to_numpy()
    q3 = sub["q3x"].fillna(0).to_numpy()
    q4 = sub["q4x"].fillna(0).to_numpy()
    q5p = sub["q5px"].fillna(0).to_numpy()

    e1_next, e2_next, e3_next, e4_next = 1.0, 2.0, 3.0, 4.0
    curve = {}
    for i in range(len(ages) - 1, -1, -1):
        e4 = q5p[i] * VALUE_5PLUS + (1 - q5p[i]) * e4_next
        e3 = q4[i] * e4_next + (1 - q4[i]) * e3_next
        e2 = q3[i] * e3_next + (1 - q3[i]) * e2_next
        e1 = q2[i] * e2_next + (1 - q2[i]) * e1_next
        curve[ages[i]] = e1
        e1_next, e2_next, e3_next, e4_next = e1, e2, e3, e4
    return curve
