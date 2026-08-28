"""Same expected-children-given-first-birth-age recursion as
births_per_mother_region_grid.py, run on HFD's period fertility tables
(pft.txt) instead of cohort tables (cft.txt) -- one line per calendar year
instead of one line per birth cohort -- for every country in
COUNTRY_REGIONS. A period-basis cross-check of the same estimation method
against the main (cohort-based) chart, covering every country rather than
just the handful with register-measured parity data.

UK_ONS is skipped: it has no HFD period table to run this on (the main
chart's UK column comes from ONS Table 3 instead, which is inherently
cohort-based).
"""

import pandas as pd

from births_per_mother_region_grid import _expected_children_curve as expected_children_curve

COLS = ["code", "year", "x", "w0x", "m1x", "q1x", "l0x", "b1x", "L0x", "Sb1x",
        "w1x", "m2x", "q2x", "l1x", "b2x", "L1x", "Sb2x",
        "w2x", "m3x", "q3x", "l2x", "b3x", "L2x", "Sb3x",
        "w3x", "m4x", "q4x", "l3x", "b4x", "L3x", "Sb4x",
        "w4x", "m5px", "q5px", "l4x", "b5px", "L4x", "Sb5px"]


def load_data():
    df = pd.read_csv("data/HFD/pft.txt", sep=r"\s+", skiprows=3, names=COLS, na_values=".")
    df = df[pd.to_numeric(df["x"], errors="coerce").notna()].copy()
    df["x"] = df["x"].astype(int)

    rows = []
    for (code, year), sub in df.groupby(["code", "year"]):
        for age, value in expected_children_curve(sub).items():
            rows.append({"code": code, "year": year, "age": age, "expected_children": value})
    return pd.DataFrame(rows)
