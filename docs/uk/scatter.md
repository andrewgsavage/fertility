# Explore

Following from first-vs-second-birth, it would be ideal to find data on first births to integorgate the causes for the drop in fertility. The UK does not publish first birth data at town level. It does publish Age Specific Fertility Rates (ASFR) in 5 year buckets for towns, which is presented here. 

The reduction in fertility can be seen clearly in the 20-24 and 25-29 age groups as expected based on the reduction in global first birth rates. The fertility decline in 30-34 year olds is much less severe.

In the 20-24 and 25-29 age groups, the sharpest declines in fertility (drops larger than 50% since 2013) occur mostly in the areas that alraedy saw low fertility rates in 2013. These are generally university towns and cities, and areas in and around London. These are the areas young people migrate to, see [Centre for Cities: The great British "brain drain"](https://www.centreforcities.org/reader/great-british-brain-drain/nature-migration-within-england-wales/).

::::{tab-set}

:::{tab-item} 20–24
```{image} /_static/ons/scatter_asfr_20_24.png
:alt: ASFR 20-24 (2013) vs (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 25–29
:selected:
```{image} /_static/ons/scatter_asfr_25_29.png
:alt: ASFR 25-29 (2013) vs (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 30–34
```{image} /_static/ons/scatter_asfr_30_34.png
:alt: ASFR 30-34 (2013) vs (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 35–39
```{image} /_static/ons/scatter_asfr_35_39.png
:alt: ASFR 35-39 (2013) vs (2024), by local authority
:width: 100%
```
:::
::::

# Housing

High housing costs correlate with lower fertility rates. This is most clearly seen when looking at 25-29 year olds. This correlation is also seen in the 20-24 age bracket, though university students distort this as they have much lower fertility rates, brining down the fertility in university towns and cities. In the 35-39 age bracket this trend reverses, however the ASFRs in the expensive areas are low (approx 80) compared to the highs (approx 120) seen in cheaper areas in other age brackets. The population of 35-39 year olds in these areas is lower than 25-29 year olds resulting in some of the lowest overall fertility rates in the country.

::::{tab-set}

:::{tab-item} 20–24
```{image} /_static/ons/scatter_housing_asfr_20_24.png
:alt: Average house price vs ASFR 20-24 (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 25–29
:selected:
```{image} /_static/ons/scatter_housing_asfr_25_29.png
:alt: Average house price vs ASFR 25-29 (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 30–34
```{image} /_static/ons/scatter_housing_asfr_30_34.png
:alt: Average house price vs ASFR 30-34 (2024), by local authority
:width: 100%
```
:::

:::{tab-item} 35–39
```{image} /_static/ons/scatter_housing_asfr_35_39.png
:alt: Average house price vs ASFR 35-39 (2024), by local authority
:width: 100%
```
:::
::::

The Resolution Foundation's report [Bye Bye Baby](https://www.resolutionfoundation.org/publications/bye-bye-baby/) ([PDF](https://www.resolutionfoundation.org/app/uploads/2026/03/Bye-bye-baby.pdf)) has a few interesting points. 

also 

why does fig6 show increasing childlessness 2012 onwards, but comparatively static cohabitation ratios in fig7?
how can housing costs be a driver, if they've risen in tandem with wage increases? ditto proportions are relatively constant since 2010s
why isn't there a drop in second births if house prices are an issue?



```{scatter-controls}
```

```{note}
Fertility: Office for National Statistics, "Live births in England and Wales: birth rates down to local authority areas". Available at [nomisweb.co.uk/datasets/lebirthrates](https://www.nomisweb.co.uk/datasets/lebirthrates).

Population: Office for National Statistics, "Population estimates - local authority based by five year age band". Available at [nomisweb.co.uk/datasets/pestnew](https://www.nomisweb.co.uk/datasets/pestnew).

Housing: Office for National Statistics, "Average house price" and "Housing affordability ratio (residence-based)". Available at [ons.gov.uk/explore-local-statistics/indicators](https://www.ons.gov.uk/explore-local-statistics/indicators).
```
