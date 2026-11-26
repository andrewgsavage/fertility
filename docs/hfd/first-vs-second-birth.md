# First vs Second Birth

The global drop in fertility since the 2000s is almost entirely down to the drop in fertility of first time mothers. The drop is strongest in younger women and reduces with age. By age 30-32 fertility rates return to their historic values. This can be seen by comparing the [conditional age specific fertility rates (ASFR)](https://www.humanfertility.org/Data/ExplanatoryNotes) for first and second births.

The conditional ASFR gives the probability that a woman will give birth to their next child in a given year. The charts below show that a 30 year old woman in South Korea in 2005 had approximately a 15% chance of having a child, and in 2024 that dropped to 4%.

This reduction in first birth fertility rates can be seen in almost all countries the [Human Fertility Database](https://www.humanfertility.org/) has data on. In contrast, the second birth fertility rates do not show the same trend; in most countries the second birth rates are fairly static.

Uruguay, which is not in the Human Fertility Database, shows the same first-birth pattern in [Cabella et al. (2024)](https://www.demographic-research.org/articles/volume/50/16): between 2016 and 2021 the first-birth rate of childless women fell 36% at age 20, 29% at 30 and 12% at 35.

::::{tab-set}

:::{tab-item} Linear

```{raw} html
<iframe src="../_static/hfd/cond_asfr_facet.html" style="width: 100%; height: 1490px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Change since 2009-11

Each rate is shown as the change from the same country's average at that age over 2009-2011, on a log axis. Ages where that baseline rate is under 0.5% are omitted.

```{raw} html
<iframe src="../_static/hfd/cond_asfr_facet_change.html" style="width: 100%; height: 1490px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Notes
```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

HFD has limited data for the UK, so the UK data is reconstructed from this data: at each age, the conditional (parity-progression)
rate is estimated as a discrete hazard on the cumulative % of the cohort with at least
1 / at least 2 children, then re-sliced from cohort into period (calendar) year to
match HFD's chart convention.
```

```{note}
Uruguay is not in HFD. Its first-birth panel is Figure 5 of Cabella W, Fernández Soto M, Pardo I, Pedetti G.
["The big decline: Lowest-low fertility in Uruguay (2016-2021)"](https://www.demographic-research.org/articles/volume/50/16),
*Demographic Research* 2024;50(16), digitised from the published image (no data file is published; a few points read by eye).
Its rates are first births per childless woman by single age, the same measure as HFD's first-birth conditional rate, with
births from the Live Birth Certificate and Perinatal Information System and childless women from INE projections split by
parity in the 2011 census. Uruguay has no published second-birth conditional rates and none before 2016, so its
second-birth panel is empty and it is not in the change since 2009-11 chart. The
[Human Fertility Collection](https://www.fertilitydata.org/Country/Country?code=URY) holds Uruguayan rates by birth order
for 1978-2011, but as births per woman of any parity, not per woman at risk.
```
:::

::::

From this it is clear the factors causing the global fertility decline must affect first birth rates, but NOT second birth rates.

Factors that make it less likely for people to form couples, or factors that make it less likely for a couple to have their first child would explain these trends.
