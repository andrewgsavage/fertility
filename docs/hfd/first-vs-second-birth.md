# First vs Second Birth

The global drop in fertility since the 2000s is almost entirely down to the drop in fertility of first time mothers. The drop is strongest in younger women and reduces with age. By age 30-32 fertility rates return to their historic values. This can be seen by comparing the [conditional age specific fertility rates (ASFR)](https://www.humanfertility.org/Data/ExplanatoryNotes) for first and second births.

The conditional ASFR gives the probability that a woman will give birth to their next child in a given year. The charts below show that a 30 year old woman in South Korea in 2005 had approximately a 15% chance of having a child, and in 2024 that dropped to 4%.

This reduction in first birth fertility rates can be seen in almost all countries the [Human Fertility Database](https://www.humanfertility.org/) has data on. In contrast, the second birth fertility rates do not show the same trend; in most countries the second birth rates are fairly static.

Uruguay, which is not in the Human Fertility Database, shows the same first-birth pattern in [Cabella et al. (2024)](https://www.demographic-research.org/articles/volume/50/16): between 2016 and 2021 the first-birth rate of childless women fell 36% at age 20, 29% at 30 and 12% at 35.

Brazil, estimated here from birth records, shows first-birth rates falling most at young ages, as elsewhere: from 2010 to 2024 the rate fell 50% at 16, 41% at 18 and 25% at 20, and from 2015 to 2024 it fell 9% at 25 and 5% at 28. Unlike most HFD countries, its second-birth rates fell too, by 20–32% at every age from 18 to 29 between 2015 and 2024.

Greece, estimated here from births by order since 1960, follows the HFD pattern closely. From 2010 to 2024 the first-birth rate fell 59% at 20, 50% at 25 and 27% at 30, was flat at 35 and rose 49% at 40. The second-birth rate rose 9% at 20 and fell 5–12% between 25 and 32.

Mauritius, estimated from Human Fertility Collection rates by birth order since 2005, also shows first-birth rates falling most at young ages: 40% at 20 and 55% at 22 from 2010 to 2024, and 41% at 25 from 2015. Its second-birth rates at the same ages roughly doubled. They come from small numbers of young mothers of one, estimated from rates published by 5-year age group, so they are less reliable than the first-birth rates.

::::{tab-set}

:::{tab-item} Linear

```{raw} html
<iframe src="../_static/hfd/cond_asfr_facet.html" style="width: 100%; height: 1640px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
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

```{note}
Brazil is not in HFD. Births by mother's age and order are from the Ministry of Health's [SINASC](https://datasus.saude.gov.br/nascidos-vivos-desde-1994) live-birth declarations (DATASUS FTP national files), 2000–2024, order being the mother's previous live-born children plus one; women by single year of age are from [UN WPP 2024](https://population.un.org/wpp/downloads). Women by parity are not observed: they are estimated by summing each cohort's order-specific birth rates over its earlier ages, ignoring mortality and migration differences by parity. A cohort's years before 2000 take 2000's rates, and a rate is drawn only where those years hold at most 10% of the cohort's first births (first and second births for the second-birth rate), which is up to age 20 in 2005 and 40 in 2024. Years are drawn from 2005, as for the HFD countries. 2009–2011 has ages up to about 25, so Brazil is not in the change since 2009-11 chart. Order is not stated for 13% of births in 2000, 6% in 2010 and 1% in 2024; these are spread over the order mix at the same age, which understates first births if most of them are first births. SINASC counts 5–8% fewer births than WPP in 2000–2004. Mexico's birth registrations were tried the same way but count more than one first birth per woman over a cohort's lifetime, so they give no usable childless population.
```

```{note}
Greece is not in HFD. Rates by birth order and single year of age are [Human Fertility Collection](https://www.fertilitydata.org/Country/Country?code=GRC) European Demographic Observatory estimates for 1960–1991 and, from 1992, Eurostat live births by mother's age and birth order ([demo_fordagec](https://ec.europa.eu/eurostat/databrowser/view/demo_fordagec/default/table)) over women on 1 January ([demo_pjan](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table)), mean of this year and next. Where both exist (1992–2008) their TFRs differ by at most 0.03. Women by parity are estimated as for Brazil, by summing each cohort's rates from 1960, so every age passes the 10% rule from 1990.
```

```{note}
Mauritius is not in HFD. Rates by birth order are from the [Human Fertility Collection](https://www.fertilitydata.org/Country/Country?code=MUS) (Ministry of Health demographic yearbooks and Statistics Mauritius digests), published by 5-year age group and split into single ages by HFC. The split by order breaks in 2005, so the series starts there. Women by parity are estimated as for Brazil, with a cohort's years before 2005 taking 2005's rates and the same 10% rule, which reaches age 22 in 2010 and 33 in 2020. Its change since 2009-11 panel covers those young ages only. Excludes Agalega and St Brandon from 2015.
```
:::

::::

From this it is clear the factors causing the global fertility decline must affect first birth rates, but NOT second birth rates.

Factors that make it less likely for people to form couples, or factors that make it less likely for a couple to have their first child would explain these trends.
