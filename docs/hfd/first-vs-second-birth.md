# First vs Second Birth

The global drop in fertility is almost entirely down to the drop in fertility of first time mothers. The drop is strongest in younger women and reduces with age. By age 30-32 fertility rates return to their historic values. This can be seen by comparing the [conditional age specific fertility rates (ASFR)](https://www.humanfertility.org/Data/ExplanatoryNotes) for first and second births.

The conditional ASFR gives the probability that a woman will give birth to their next child in a given year. The charts below show that a 30 year old woman in South Korea in 2005 had approximately a 15% chance of having a child, and in 2024 that dropped to 4%.

This reduction in first birth fertility rates can be seen in almost all countries the [Human Fertility Database](https://www.humanfertility.org/) has data on. In contrast, the second birth fertility rates do not show the same trend; in most countries the second birth rates are fairly static.

```{region-tabs}
```

From this it is clear the factors causing the global fertility decline must affect first birth rates, but NOT second birth rates.

Factors that make it less likely for people to form couples, or factors that make it less likely for a couple to have their first child would explain these trends.

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.
```

````{note}
The UK column in the Western Europe tab is not from HFD, which has no
conditional-ASFR tables for the UK. It is reconstructed from the Office for
National Statistics' cohort fertility tables ("Childbearing for women born in
different years, England and Wales"), Table 3 (percentage of women by number
of live-born children, by age and year of birth).
Available at [ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

At each exact age, the conditional (parity-progression) rate is estimated as a discrete
hazard from the cumulative % of the cohort with at least 1 / at least 2 children (P1, P2):

```
cond1(age) = (P1(age) - P1(age-1)) / (100 - P1(age-1))
cond2(age) = (P2(age) - P2(age-1)) / (P1(age-1) - P2(age-1))
```

Each line is plotted by period (calendar) year — the year the age/cohort transition
occurred — to match HFD's chart convention, even though the hazard itself is computed
along each birth cohort. See `ONS/scripts/cond_asfr_uk_ons.py`.
````