# Births per Mother vs Age of First Birth

Expected total children for a woman whose first birth happens at exactly age X, one line per birth cohort.

```{region-tabs} births_per_mother_region Expected total children given first birth at that age, {region}
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Backward recursion over each cohort's own parity-progression hazards (cft.txt: q2x-q5px),
giving expected total children for a woman at parity 1 at each age. 5th-or-higher order
approximated as exactly 5. Only cohorts whose tracked data reaches age 40 are shown.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

UK column reconstructed from Table 3 (HFD has no UK parity-progression tables): cumulative
% of the cohort with >=1/2/3/4 children, differenced by age into the same kind of discrete
hazard, capped at 4+ (coarser than HFD's 5+).
```

## How accurate is this estimate?

Same recursion run per calendar year on HFD's period fertility tables: an estimated version (pft.txt) and, for the five countries with continuous population-register coverage, a version measured directly from register data (pftc.txt).

```{image} /_static/hfd/births_per_mother_accuracy.png
:alt: Estimated (pft.txt, dashed) vs register-measured (pftc.txt, solid) expected children by age of first birth, for Denmark, Finland, Hungary, Norway, and Sweden
:width: 100%
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Mean absolute error across every (year, age 18-39) cell: 0.006-0.010 children, against a range of roughly 1.0-3.0.
```

## Estimated across all countries, period basis

Same recursion applied to HFD's period fertility tables (pft.txt: q2x-q5px) per calendar year instead of per birth cohort, for every HFD country.

```{region-tabs} births_per_mother_estimated_region Estimated expected total children given first birth at that age (period basis), {region}
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

UK excluded: no HFD period fertility table exists for it.
```
