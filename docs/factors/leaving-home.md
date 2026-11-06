# Leaving Home

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Childbearing almost always happens after young adults leave their parental home, so a later move-out could delay or reduce childbearing. Billari & Kohler (2002) found a clear negative association across Europe between the median age women born in 1960 left home and their completed fertility: every country with "latest-late" home-leaving (Italy, Spain) also had lowest-low fertility, while Sweden, the earliest leaver, was among the highest.

Eurostat's annual estimates of the average age young people leave home show this relationship held through the 2000s, then broke down. In 2005, each extra year of women's leaving age went with 0.065 fewer children per woman (r = -0.75). By 2024 the slope was zero (r = -0.02). Holding the country set fixed to the 28 countries with data in every year from 2010 to 2024 gives the same picture: r went from -0.71 to -0.07.

::::{tab-set}

:::{tab-item} Leaving age vs TFR
```{raw} html
<iframe src="../_static/eurostat/leaving_home_vs_tfr.html" style="width: 100%; aspect-ratio: 1 / 1; max-height: 720px; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
Drag the slider to change year.
:::

:::{tab-item} Correlation by year
| Year | Countries | r |
|---|---|---|
| 2000 | 11 | -0.57 |
| 2002 | 17 | -0.60 |
| 2004 | 25 | -0.72 |
| 2005 | 25 | -0.75 |
| 2006 | 27 | -0.75 |
| 2008 | 28 | -0.64 |
| 2010 | 30 | -0.70 |
| 2012 | 31 | -0.63 |
| 2014 | 32 | -0.57 |
| 2016 | 32 | -0.54 |
| 2018 | 32 | -0.42 |
| 2019 | 31 | -0.31 |
| 2020 | 30 | -0.29 |
| 2021 | 30 | -0.32 |
| 2022 | 31 | -0.12 |
| 2023 | 31 | -0.02 |
| 2024 | 31 | -0.02 |

Pearson correlation between women's average leaving age and TFR across countries with both values that year. The country set grows over the 2000s.
:::

:::{tab-item} Leaving age over time
```{raw} html
<iframe src="../_static/eurostat/leaving_home_trend.html" style="width: 100%; aspect-ratio: 3 / 2; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

::::

The collapse comes from fertility falling in the early-leaving countries, not from leaving ages converging. Between 2010 and 2024, for the same 28 countries:

| Region | Countries | Change in TFR | Change in women's leaving age (years) |
|---|---|---|---|
| Nordic | 3 | -0.52 | +0.7 |
| Western | 7 | -0.33 | +0.7 |
| Southern | 6 | -0.19 | +0.7 |
| Central & Eastern | 11 | -0.13 | -1.0 |

Finland, Denmark, France and the Netherlands kept leaving home at 21-23 but lost 0.36-0.62 children per woman. Southern Europe left home later still and fell by less. Much of Central and Eastern Europe left home earlier, with smaller falls in fertility. Late home-leaving still goes with low fertility in Southern Europe, but early home-leaving no longer goes with high fertility.

## Leaving age and age at first birth

If leaving home late delayed families, countries where women leave later would also have later first births. They don't. Across countries, women's leaving age has almost no relation to mothers' mean age at first birth: r stayed between -0.25 and +0.17 from 2002 to 2024, and was +0.01 in 2024. Leaving ages span 9 years (20.8 in Finland to 29.8 in Croatia), while mean age at first birth spans 5 (26.9 in Bulgaria to 31.9 in Italy).

::::{tab-set}

:::{tab-item} Leaving age vs age at first birth
```{raw} html
<iframe src="../_static/eurostat/leaving_home_vs_mab1.html" style="width: 100%; aspect-ratio: 1 / 1; max-height: 720px; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
Drag the slider to change year.
:::

:::{tab-item} By region, 2024
| Region | Leaving age | Age at first birth | Gap (years) |
|---|---|---|---|
| Nordic | 21.5 | 30.2 | 8.7 |
| Western | 24.5 | 30.3 | 5.8 |
| Southern | 28.3 | 30.8 | 2.5 |
| Central & Eastern | 25.9 | 28.4 | 2.5 |
| Balkans & Türkiye | 27.5 | 27.9 | 0.4 |

Unweighted country means. The gap is between two averages, not the time between leaving home and first birth for individual women.
:::

::::

Nordic women leave home almost 9 years before the average first birth; Southern European women leave about 2.5 years before it. First births everywhere cluster around 27-32, regardless of when women leave home. Leaving home late shortens the gap between moving out and having a first child, rather than pushing the first child later.

```{note}
Data: Eurostat, [Estimated average age of young people leaving the parental household by sex](https://ec.europa.eu/eurostat/databrowser/view/yth_demo_030/default/table) (yth_demo_030), women; [Fertility indicators](https://ec.europa.eu/eurostat/databrowser/view/demo_find/default/table) (demo_find), total fertility rate and mean age of women at birth of first child. Leaving age is estimated from the Labour Force Survey and has series breaks in some countries; Sweden's series is noisy, dropping to about 17.6 in 2019-20. Leaving-age series start in 2009 for Sweden, 2010 for Denmark and 2021 for Norway, and the UK series ends in 2019 (2018 for the scatter).

Billari, F.C. and Kohler, H.-P. (2002), [*Patterns of Lowest-Low Fertility in Europe*](https://www.demogr.mpg.de/papers/working/wp-2002-040.pdf), MPIDR Working Paper WP-2002-040, Figure 6.
```
