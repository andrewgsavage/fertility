"""Expected number of children a woman will have, given her first birth was at exact
age X, England & Wales, by birth cohort, from ONS cohort Table 3. Prints a sample;
the calculation lives in common/ons_births_per_mother.py (shared with
HFD/scripts/births_per_mother_region_grid.py).
"""

from common.ons_births_per_mother import load_expected_children_curves

if __name__ == "__main__":
    curves = load_expected_children_curves()
    for cohort in [1930, 1950, 1969, 1979]:
        curve = curves[cohort]
        sample = {age: round(curve[age], 2) for age in sorted(curve) if age % 5 == 0}
        print(f"{cohort}: {sample}")
