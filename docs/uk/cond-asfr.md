# Conditional ASFR

The [First vs Second Birth](../hfd/first-vs-second-birth) page compares the conditional age specific fertility rate (ASFR) — the probability a woman has her next child in a given year — for first and second births across countries, including a UK column reconstructed from ONS cohort data (HFD itself has no conditional-ASFR tables for the UK).

This page shows that same UK reconstruction on its own, with every available year plotted and a slider to narrow the range shown.

```{raw} html
<iframe src="../_static/ons/cond_asfr_uk_ons.html" style="width: 100%; height: 620px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

HFD has no conditional-ASFR tables for the UK, so this is reconstructed from that data:
at each age, the conditional (parity-progression) rate is estimated as a discrete
hazard on the cumulative % of the cohort with at least 1 / at least 2 children, then
re-sliced from cohort into period (calendar) year to match HFD's chart convention. See
`ONS/scripts/cond_asfr_uk_ons.py`.
```
