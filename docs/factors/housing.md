# Housing

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Housing can hold back fertility in two ways: through its cost (prices, rents, mortgage payments) and through its size (bedrooms and floor space). The evidence is stronger for size than for cost, and cost effects show up within countries more clearly than between them.

## House prices across countries

The Netherlands is often cited as the case where house prices and fertility moved most clearly in opposite directions: real house prices rose 52% between 2013 and 2024 and TFR fell from 1.68 to 1.43. Across 40 OECD and EU countries, though, it is mid-table on both: 14th for real house price growth and 21st for the fall in TFR. Across countries, the change in real house prices over 2013-2024 is uncorrelated with the change in TFR (r = +0.07). Real rents (r = -0.16) and the price-to-income ratio (r = -0.10) do little better.

Some of the largest fertility falls came where real house prices fell. Finland's real house prices fell 17% and its TFR fell by 0.50, one of the largest falls in Europe. Italy (-16%) and South Korea (-6%) followed the same pattern. Hungary and Portugal, with two of the largest price rises (+111% and +91%), are among the four countries where TFR rose.

::::{tab-set}

:::{tab-item} Price change vs TFR change
```{raw} html
<iframe src="../_static/housing/price_change_vs_tfr_change.html" style="width: 100%; aspect-ratio: 1 / 1; max-height: 720px; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
Use the dropdown to switch between real house prices, real rents and price-to-income.
:::

:::{tab-item} Over time, by country
```{raw} html
<iframe src="../_static/housing/country_prices_tfr.html" style="width: 100%; aspect-ratio: 4 / 3; max-height: 760px; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

::::

Within the Netherlands the relationship is clearer. Van Wijk (2024) finds that after 2010, fertility fell more in Dutch regions where house prices rose more, enough to account for a substantial part of the national decline; before 2010 the regional link ran slightly the other way. Feijten and van Wijk (2025) split this by tenure for 2012-2022: a €100,000 higher regional house price goes with a 3.1 percentage point lower chance of having a child, partly because fewer young people in expensive regions own their home. For renters, high prices go with fewer births; for owners, with more. This matches UK survey evidence that rising prices raise births among owners and not among renters (Washbrook; Buh 2026). Cross-country comparisons mix owners and renters and can't separate the two.

## The UK since 2022

UK real house prices peaked in early 2022 and by mid-2026 were 10% lower, back to their 2007 level. The house price to income ratio fell 14% from its 2022 peak. Over the same period England and Wales TFR fell from 1.55 (2021) to 1.39 (2025), a record low.

The fall in fertility started earlier, in 2013, when real house prices were at their post-crisis low. TFR fell from 1.93 in 2012 to 1.59 in 2019 while real prices recovered to around their 2007 level, then kept falling after prices turned down in 2022. Before that, TFR rose from 1.63 in 2001 to 1.94 in 2010 while real house prices rose 71% to their 2007 peak. In none of these periods does TFR track house prices.

Falling real prices since 2022 don't mean housing got cheaper to buy or rent:

- Bank Rate rose from 0.1% in December 2021 to 5.25% in August 2023, so monthly mortgage payments on a new loan rose even as prices fell.
- Rents rose 6% in real terms between the third quarter of 2022 and the second quarter of 2026, while real house prices fell 9%.

So the UK since 2022 rules out house *prices* as the main driver but not housing *costs*.

## House size

Bedroom count is the housing variable most strongly associated with fertility in the studies below. Most of this evidence is cross-sectional, so it can't rule out that couples who plan children move to bigger homes first.

- **United States.** Stone (2024), using about 12 million women in the American Community Survey 2006-2022 with controls for income, education, tenure and other factors, finds women in 1- or 2-bedroom homes have a TFR of 1.2-1.35, against 1.9-2.0 in 3-bedroom homes and 1.7-1.95 in larger ones. Bedroom count mattered more than building type (single-family 1.9 vs apartments 1.8) or area population density (1.65-1.85 in the densest areas vs 1.85-1.95 in the least dense). Women in apartments with 3+ bedrooms had the same fertility as those in single-family houses with 3+ bedrooms.
- **New US apartments are shrinking.** Stone and Fijan (2025) report the average new multifamily unit fell from about 1,300 sq ft in 2007 to 1,043 sq ft in 2024, and 3+ bedroom units fell from 7-11% of construction in the 1990s-2000s to about 5%.
- **Large-unit supply.** Couillard (2026) estimates an elasticity of US births to average rents of -0.3, and that adding large units yields 3.4 times as many births as adding small units at the same cost, because it lowers the price of the larger homes families move into.
- **Finland.** A City of Helsinki study (2025) found higher birth rates in areas with more family-sized homes; fewer than one in five homes in Helsinki, Tampere and Turku have four or more rooms. The authors caution that building more family homes may not raise fertility directly. Using Finnish register data, Kulu and Vikat (2007) found fertility highest among couples in single-family houses and lowest in apartments, but attributed much of the gap to selective moves: couples planning children move to houses.

```{note}
Data: OECD, [Analytical house price indicators](https://data-explorer.oecd.org/vis?df[ds]=dsDisseminateFinalDMZ&df[id]=DSD_AN_HOUSE_PRICES%40DF_HOUSE_PRICES&df[ag]=OECD.ECO.MPD) (real house prices; price-to-income; rents, deflated with the real house price index's deflator). TFR: Eurostat [demo_find](https://ec.europa.eu/eurostat/databrowser/view/demo_find/default/table) for European countries; ONS [Births in England and Wales](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths/datasets/birthsinenglandandwalesbirthregistrations) for the UK; World Bank [SP.DYN.TFRT.IN](https://data.worldbank.org/indicator/SP.DYN.TFRT.IN) otherwise. UK TFR is for England and Wales. Non-OECD economies in the OECD file (Brazil, China, India, Indonesia, Russia, Saudi Arabia, South Africa) are excluded. See also [Ration Analytics, UK house prices adjusted for inflation](https://rationanalytics.com/uk/house-prices-inflation-adjusted).

van Wijk, D. (2024), [*House prices and fertility: Can the Dutch housing crisis explain the post-2010 fertility decline?*](https://doi.org/10.1002/psp.2787), *Population, Space and Place* 30(7).
Feijten, P. and van Wijk, D. (2025), [*Stijgende woningprijzen, minder geboorten*](https://www.cbs.nl/nl-nl/longread/statistische-trends/2025/stijgende-woningprijzen-minder-geboorten), CBS Statistische Trends.
Stone, L. (2024), [*More Crowding, Fewer Babies: The Effects of Housing Density on Fertility*](https://ifstudies.org/ifs-admin/resources/research/lymanstonefertilityhousingbrief-june.pdf), Institute for Family Studies.
Stone, L. and Fijan, B. (2025), [*Homes for Young Families, Part 2*](https://ifstudies.org/report-brief/homes-for-young-families-part-2), Institute for Family Studies.
Couillard, B.K. (2026), [*Build, Baby, Build: How Housing Shapes Fertility*](https://sites.google.com/view/ben-couillard/home), job market paper, University of Toronto.
City of Helsinki (2025), [*Study: Birth rate higher in areas with more family homes*](https://www.hel.fi/en/news/study-birth-rate-higher-in-areas-with-more-family-homes).
Kulu, H. and Vikat, A. (2007), [*Fertility differences by housing type: The effect of housing conditions or of selective moves?*](https://www.demographic-research.org/volumes/vol17/26/17-26.pdf), *Demographic Research* 17(26).
```
