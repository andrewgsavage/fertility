# FT: Why birth rates are falling everywhere all at once

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

The FT's [Why birth rates are falling everywhere all at once](https://www.ft.com/content/fba35eca-df3a-4ad6-b42d-eb08eb7c9ad3) (John Burn-Murdoch, 16 May 2026) argues that the post-2010 fall in fertility is tied to smartphones. Its evidence is a chart that dates smartphone take-off in each country from app-store Google searches and adoption surveys, then shows TFR dropping below its pre-smartphone trend. This page rebuilds that chart from the FT's own data, redoes the search dating, runs the comparison for 65 countries, and checks two headline numbers against UN World Population Prospects (WPP) 2024.

## Bottom line

- **The FT's trend comparison reproduces exactly.** A linear trend fitted to TFR over the 10 years up to take-off gives every value in the FT's chart, to within 0.001 percentage points.
- **The take-off date is not where the break is.** On the FT's own data, moving each country's take-off date 1–3 years later makes the gap after it bigger (median −17% to −18%, against −13.7% at the FT dates). Moving it 3+ years earlier puts TFR *above* trend. The chart shows a decline that sped up through the 2010s, measured against a straight line. It doesn't show a break at take-off.
- **App-store searches date take-off to 2010–2013 almost everywhere.** That is true from Sweden to Ethiopia, so searches can't produce the FT's spread of dates (US 2007, Iran 2015). The FT's early dates for the US, UK and Australia come from adoption surveys.
- **With search dates the effect is about half the size.** Across 65 countries, the median gap 5–7 years after the search-dated take-off is −6%, against −13.7% for the FT's eight countries. A third of countries are at or above trend.
- **Mexico's fall depends on the data source.** WPP 2024 has Mexico's TFR at 1.91 in 2023, still above the US (1.62). The FT's series (national estimates) has 1.52. On WPP, Mexico is 2% below trend 8 years after take-off. On the FT's series it is 17.6% below.
- **"More than two-thirds of 195 countries below 2.1" is not in WPP.** WPP has 52–57% below 2.1, depending on the year and which territories count.

## The smartphone chart

The FT chart has five slides. Three show TFR by calendar year for eight countries. One re-indexes them to years since smartphone take-off. The last shows the % gap from a linear trend over the 10 years up to take-off. The take-off years below come from matching the re-indexed slide back to calendar years. Every series ends in 2023, so each match is exact.

::::{tab-set}

:::{tab-item} By year
```{raw} html
<iframe src="../_static/ft/ft_br_smartphone_tfr_calendar.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Since take-off
```{raw} html
<iframe src="../_static/ft/ft_br_smartphone_tfr_aligned.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} vs trend
```{raw} html
<iframe src="../_static/ft/ft_br_smartphone_tfr_vs_trend.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
Redrawn from the data in the FT's Flourish charts (visualisations 28990485, 28990534, 28990605). FT sources: UN World Population Prospects, national statistics agencies, Birth Gauge; take-off from Hudson and Moscoso Boedo (2026), Google Trends, Pew Research Center and Newzoo. The FT's first two slides show the same series for fewer countries and are left out.
```
:::

::::

| Country | FT take-off | Search take-off | % vs trend, year 5: FT | Year 5: WPP TFR | Year 8: FT | Year 8: WPP TFR |
|---|--:|--:|--:|--:|--:|--:|
| US | 2007 | 2011 | −13.0 | −13.0 | −15.8 | −15.8 |
| Australia | 2008 | 2011 | −9.4 | −9.4 | −16.8 | −16.8 |
| UK | 2009 | 2011 | −11.5 | −11.5 | −18.7 | −18.7 |
| Indonesia | 2012 | 2012 | −11.3 | −11.3 | −14.6 | −14.6 |
| Mexico | 2013 | 2012 | −6.9 | −3.4 | −17.6 | −2.0 |
| Senegal | 2013 | 2013 | −13.6 | −13.6 | −20.2 | −20.2 |
| Egypt | 2014 | 2012 | −19.5 | −19.5 | −24.1 | −24.4 |
| Iran | 2015 | 2011 | −18.7 | −18.6 | −24.4 | −21.9 |

```{note}
FT chart data read from the article's Flourish embeds (visualisations 28990445–28990605). TFR: [UN World Population Prospects 2024](https://population.un.org/wpp/) via [Our World in Data](https://ourworldindata.org/grapher/children-born-per-woman), estimates to 2023. The "WPP TFR" columns use the FT's take-off years. Search take-off: first year the annual mean of Google Trends interest in "app store", "play store", "google play" and "android market" (summed) reaches 25% of its 2004–2024 peak year.
```

### Searches

App-store searches rise, peak and then decline as phone owners stop needing to look up the store. That makes their rise a usable adoption marker. But the rise happens at nearly the same time everywhere: 63 of 65 countries cross the threshold between 2010 and 2013, with Japan, South Korea, Taiwan and Sweden first, in 2010. The exceptions are China in 2014, where Google is blocked, and Ethiopia in 2016. In 2012 Android Market was renamed Google Play, so "play store" and "google play" searches jump that year in every country. That pushes dates towards 2012.

Trends scales each country's series to its own peak, so the search index shows when searches grew relative to that country's later level. It doesn't show what share of people had a smartphone. In poorer countries, early searches come from the minority online, so the index rises before most people have a phone.

### Trend gap across 65 countries

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/smartphone_vs_trend.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
| Years since take-off | −10 | −5 | 0 | 2 | 4 | 6 | 8 | 10 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Median % gap, 65 countries (search dates, WPP TFR) | 0.6 | −0.2 | −0.3 | −0.7 | −2.9 | −5.8 | −8.5 | −11.1 |
| Countries | 65 | 65 | 65 | 65 | 65 | 65 | 64 | 63 |

Per-country series: `FT/outputs/smartphone_vs_trend.csv`.
:::

:::{tab-item} Notes
```{note}
TFR: [UN WPP 2024](https://population.un.org/wpp/) via [Our World in Data](https://ourworldindata.org/grapher/children-born-per-woman), estimates to 2023, so countries with later take-off have shorter series. Take-off: [Google Trends](https://trends.google.com/) app-store searches, as in the table above. The FT median line uses the FT's eight countries, dates and TFR. Countries: the FT's eight plus 57 others, mostly with population over 10 million, with enough search volume. The y-axis is cut at ±50%: Taiwan (to +168%, a trend fitted through its 2010 low heads towards zero), Nepal and Bangladesh go above it, Ukraine (−54%, war) below.
```
:::

::::

With search dates, the gap opens 3–4 years after take-off and grows steadily, with no sharp break. It stays well below the FT's median gap: −5.8% against −14.4% six years after take-off. The FT's eight countries are among the steeper fallers.

### Placebo dates

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/smartphone_placebo.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
| Take-off date moved by (years) | −6 | −4 | −2 | −1 | 0 | +1 | +2 | +3 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| FT's 8 countries, FT dates and TFR (median %) | 18.5 | 7.4 | −5.0 | −11.1 | −13.7 | −16.9 | −18.0 | −17.5 |
| 65 countries, search dates, WPP TFR (median %) | 9.9 | 3.3 | −2.2 | −3.4 | −6.1 | −5.6 | −4.5 | −5.8 |

Per-country values: `FT/outputs/smartphone_placebo.csv`.
:::

:::{tab-item} Notes
```{note}
Gap = mean % difference between TFR and a linear trend over the 10 years up to the moved date, 5–7 years after that date. TFR: FT chart data (FT's eight) and [UN WPP 2024](https://population.un.org/wpp/) via [Our World in Data](https://ourworldindata.org/grapher/children-born-per-woman) (65 countries). Moving dates later shortens the post-period before 2023, so the +3 and +4 points cover fewer countries.
```
:::

::::

If smartphones caused a break at take-off, the gap should be largest at the true date and shrink as the date moves away from it. Instead, for the FT's countries the gap keeps growing for later dates, and for the 65 countries it is flat from 0 to +3. Anchoring a straight line anywhere in the late 2000s or early 2010s gives a large gap. This is because the decline sped up across the 2010s everywhere, whatever the local smartphone date. The early anchors give large positive gaps because a 10-year line through the steeper falls of earlier decades overshoots downward.

The test can't rule smartphones out. It only shows that the chart can't separate them from anything else that sped up the decline after about 2010. It also doesn't test the FT's other claim, that the fall is steeper at younger ages. [Hudson and Moscoso Boedo](https://papers.ssrn.com/abstract=6676839), the paper the FT cites, use variation across US counties in when fast broadband arrived, which is a stronger design. The FT describes it as a 4G study; in the October 2026 version, 4G coverage is only a control and comes out near zero. Their outcome is teen births: 3.5% lower four to six years after a cable upgrade, with no response at ages 25–34.

## Mexico vs the US

| Year | Mexico, FT | US, FT | Mexico, WPP | US, WPP |
|---|--:|--:|--:|--:|
| 2018 | 1.91 | 1.71 | 2.03 | 1.72 |
| 2020 | 1.75 | 1.62 | 1.99 | 1.62 |
| 2021 | 1.63 | 1.63 | 1.97 | 1.63 |
| 2022 | 1.57 | 1.65 | 1.94 | 1.66 |
| 2023 | 1.52 | 1.60 | 1.91 | 1.62 |
| 2025 | 1.38 | 1.57 | | |

```{note}
FT chart data from the article's Flourish embed (visualisation 28970599); its footer cites UN WPP, national statistics agencies and Birth Gauge. [UN WPP 2024](https://population.un.org/wpp/) via [Our World in Data](https://ourworldindata.org/grapher/children-born-per-woman), estimates to 2023.
```

In the FT's series, Mexico first falls below the US in 2022, and the two are level in 2021. The article says 2023. WPP 2024 has Mexico 0.29 above the US in 2023, with a much slower decline after 2018. The two sources agree on the US to within 0.02.

## Countries below replacement

| Year | Set | Countries | Below 2.1 | Share | Below 1.5 |
|---|---|--:|--:|--:|--:|
| 2023 | All countries and territories | 236 | 129 | 55% | 65 |
| 2023 | Population 90,000+ | 200 | 103 | 52% | 50 |
| 2025 | All countries and territories | 236 | 134 | 57% | 68 |
| 2025 | Population 90,000+ | 200 | 107 | 54% | 53 |

```{note}
[UN WPP 2024](https://population.un.org/wpp/) via [Our World in Data](https://ourworldindata.org/grapher/fertility-rate-with-projections): estimates for 2023, medium-variant projection for 2025. Population 90,000+ approximates the 195 UN members and observers. The FT counts use national statistics and Birth Gauge where newer, which are often lower than WPP.
```

The FT's "66 countries closer to one than to two" matches WPP only when territories such as Hong Kong, Macao and Puerto Rico are counted. "More than two-thirds of 195 countries" below 2.1 would need about 25 more countries below 2.1 than WPP has. That gap is the same kind of difference as Mexico's: recent national data running below WPP.

## South Korea by birth order

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/hfc/kor_tfr_by_order.html" style="width: 100%; height: 460px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
| Year | TFR | First | Second | Third+ | Source |
|---|--:|--:|--:|--:|---|
| 1980 | 2.88 | 1.00 | 0.88 | 0.99 | ODE |
| 1984 | 1.75 | 0.83 | 0.66 | 0.26 | ODE |
| 1992 | 1.77 | 0.92 | 0.71 | 0.14 | ODE |
| 1999 | 1.48 | 0.74 | 0.59 | 0.15 | ODE |
| 2000 | 1.48 | 0.71 | 0.62 | 0.15 | HFD |
| 2015 | 1.24 | 0.67 | 0.46 | 0.11 | HFD |
| 2023 | 0.72 | 0.43 | 0.23 | 0.05 | HFD |
| 2024 | 0.75 | 0.46 | 0.24 | 0.05 | HFD |
:::

:::{tab-item} Notes
```{note}
[Human Fertility Collection](https://www.fertilitydata.org/), South Korea, period TFR by birth order, age in completed years. 1980–1999: European Demographic Observatory (ODE) research estimates; 2000–2024: Human Fertility Database vital statistics. In 2000–2007, when both exist, ODE's TFR is 0.03–0.05 above HFD's, so part of the 1999–2000 step is the change of source. A third series in HFC, Kye (2012), runs 0.01–0.03 above HFD over 2000–2015.
```
:::

::::

Korea's first fall, from 2.88 in 1980 to 1.75 in 1984, was mostly third and later births: they dropped from 0.99 to 0.26, 0.73 of the 1.13 fall. First births stayed at 0.8–0.9 per woman until the early 1990s. Since 2015 the fall has been at first and second births almost equally. From 2015 to 2023 TFR fell by 0.52: 0.23 of that was first births, 0.22 second and 0.06 third and later. First births in 2023 (0.43) were less than half their 1992 level (0.92).

## Uruguay by birth order

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/hfc/ury_tfr_by_order.html" style="width: 100%; height: 460px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
| Year | TFR | First | Second | Third+ | Source |
|---|--:|--:|--:|--:|---|
| 1978 | 2.91 | 0.90 | 0.79 | 1.23 | HFC |
| 1988 | 2.58 | 0.92 | 0.72 | 0.94 | HFC |
| 1996 | 2.51 | 0.88 | 0.68 | 0.95 | HFC |
| 2005 | 1.99 | 0.80 | 0.56 | 0.64 | HFC |
| 2011 | 1.90 | 0.80 | 0.57 | 0.53 | HFC |
| 2013 | 1.96 | 0.85 | 0.60 | 0.51 | Estimate |
| 2021 | 1.38 | 0.62 | 0.45 | 0.31 | Estimate |

**Check of the estimate's denominators: TFR from MSP births and INE population vs HFC**

| Year | MSP/INE | HFC | Gap |
|---|--:|--:|--:|
| 1996 | 2.45 | 2.51 | −0.05 |
| 2000 | 2.15 | 2.21 | −0.06 |
| 2005 | 1.95 | 1.99 | −0.04 |
| 2008 | 1.96 | 1.97 | −0.01 |
| 2011 | 1.90 | 1.90 | 0.00 |

**Check of the estimate's order split: share of the fall in TFR by birth order**

| | First | Second | Third+ |
|---|--:|--:|--:|
| Estimate, 2013–2021 | 40% | 26% | 35% |
| Cabella et al. (2024), 2015–2021 | 41% | 31% | 29% |
:::

:::{tab-item} Notes
```{note}
1978–2011: [Human Fertility Collection](https://www.fertilitydata.org/), Uruguay, from the Latin American Fertility Database. 1978–1988 and 1993: Nathan's rates from official birth counts by 5-year age group and order, unknowns spread pro rata, births raised 2.5% for under-registration. 1996–2011: Cabella, Nathan and Pardo, [Nathan, Pardo and Cabella (2016)](https://www.demographic-research.org/articles/volume/34/20): Live Birth Certificate records, linked to the Perinatal Information System for 2008–2011, weighted for under-coverage, over INE 2013-revision population. No data for 1989–1992, 1994–1995 and 1998.

2013 and 2021 are estimates made here. Age-specific rates by 5-year group: Ministry of Public Health (MSP) [live births by mother's age](https://web.archive.org/web/20230215183142/https://uins.msp.gub.uy/materiales/2021/cuadro3natalidad.rar) over INE's [female population at 30 June](https://www.gub.uy/instituto-nacional-estadistica/estimaciones2025) (Revision 2025, based on the 2023 census). Each group's rate is split by the share of births of each order in that group in MSP's public [Perinatal Information System microdata](https://web.archive.org/web/20230215183142/https://uins.msp.gub.uy/materiales/perinatal/Base_de_datos_SIP_2021.rar) (2013 and 2021 are the only years archived), order being previous deliveries plus one. SIP covers 97% of births in 2013 and 94% in 2021, and records age in 5-year groups at the first prenatal visit. MSP's files are read from Internet Archive copies; the ministry's site refuses access from outside Uruguay. The estimate's 2021 TFR (1.38) matches the 1.37 in [Cabella et al. (2024)](https://www.demographic-research.org/articles/volume/50/16). Their Table A-1 splits the 2015–2021 fall by age and order using linked birth-certificate and SIP microdata with exposures by parity; it gives no levels by order. TFR was 1.96 in 2013 and 1.95 in 2015 on the MSP/INE basis, so the 2013–2021 split is comparable. The estimate puts about 5 points less of the fall on second births and 6 more on third and later births than the paper. Its births-over-population TFR runs 0.04–0.06 below HFC's in 1996–2006, when HFC raised births for under-registration and used the older population revision, and within 0.02 in 2007–2011.
```
:::

::::

Uruguay's TFR fell in two stages, and the orders behind them differ. Between 1996 and 2011 it fell by 0.61, and 0.42 of that was third and later births; first births only went from 0.88 to 0.80. Between 2013 and 2021 it fell by 0.58: first births by 0.23, third and later by 0.20 and second births by 0.15. Cabella et al.'s 2015–2021 breakdown, from fuller data, also puts about 40% of the fall on first births, but ranks second births (31%) above third and later (29%). First births held at 0.80–0.92 per woman from 1978 to 2013, then fell to 0.62 by 2021.

### Uruguay first births by age, 2016–2021

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/hfc/ury_first_births_fig5.html" style="width: 100%; height: 460px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
**First births per childless woman, selected ages**

| Age | 2016 | 2019 | 2021 |
|--:|--:|--:|--:|
| 16 | 0.037 | 0.021 | 0.017 |
| 19 | 0.072 | 0.051 | 0.044 |
| 22 | 0.061 | 0.049 | 0.043 |
| 25 | 0.062 | 0.048 | 0.048 |
| 28 | 0.080 | 0.062 | 0.056 |
| 32 | 0.107 | 0.086 | 0.079 |
| 36 | 0.077 | 0.072 | 0.069 |
| 40 | 0.037 | 0.037 | 0.034 |

**Period first-birth table built from these rates**

| Year | First birth by 25 | By 30 | By 50 | Mean age at first birth |
|---|--:|--:|--:|--:|
| 2016 | 44% | 62% | 86% | 25.5 |
| 2017 | 40% | 57% | 83% | 26.1 |
| 2018 | 39% | 55% | 81% | 26.2 |
| 2019 | 34% | 50% | 78% | 26.9 |
| 2020 | 34% | 50% | 77% | 26.7 |
| 2021 | 31% | 47% | 76% | 27.5 |
:::

:::{tab-item} Notes
```{note}
Digitised from Figure 5 of [Cabella et al. (2024)](https://www.demographic-research.org/articles/volume/50/16) (conditional age-specific first-birth rates: first births at each age over childless women of that age), single years of age 13–49. Their sources: Live Birth Certificate and Perinatal Information System (MSP), with INE 2013-revision population and women by parity carried forward from the 2011 census. The paper publishes no data file; values are traced from the figure's image, about ±0.002, and 11 of 206 points where lines overlap were read by eye (flagged in `research/data/cabella2024_fig5_ury_casfr1.csv`). The first-birth table applies each year's rates to a hypothetical cohort of childless women; it is a period measure, not the share of any real cohort who will have children. Its mean age at first birth rises 2.0 years from 2016 to 2021, matching the "nearly two years" in the paper's abstract.
```
:::

::::

The fall in first births was steepest at the youngest ages. Between 2016 and 2021 the rate fell by 55% at 16, 40% at 19 and 26% at 32, but by 10–11% at 36 and 40. The early peak around 19–20, which made Uruguay's first-birth curve two-humped, has nearly gone. At 2021 rates, 31% of women would have a first child by 25, against 44% at 2016 rates, and 76% by 50, against 86%.

## The article's other charts

These are redrawn from the data in the article's Flourish charts, in article order. The data for all of them is in `FT/outputs/ft_birth_rates_everywhere.csv`. The FT drew children per mother and the share of women who are mothers on two y-axes. Here they are two rows of panels instead.

### TFR by region

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_tfr_by_region.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28957389. FT sources: UN World Population Prospects, national statistics agencies, Birth Gauge. Regional groupings and weights are the FT's and aren't documented.
```
:::

::::

Eastern Asia goes from 1.65 in 2010 to 0.96 in 2025. Latin America goes from 2.06 to 1.39 over the same years and is now level with Northern Europe and the high-income average (1.39–1.40). The FT's Latin America series drops 0.18 in one year, 2023 to 2024.

### Mexico vs the US, FT series

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_mexico_vs_us.html" style="width: 100%; height: 440px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28970599. FT sources: UN World Population Prospects, national statistics agencies, Birth Gauge. WPP's own figures are in the Mexico vs the US table above.
```
:::

::::

### Japan's working-age population

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_japan_productivity.html" style="width: 100%; height: 460px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28974152, 1995–2019. FT sources: World Bank, UN, and The Wealth of Working Nations (Fernández-Villaverde et al., 2024).
```
:::

::::

By 2019, GDP per working-age adult in Japan was 142 (1995 = 100), within the 139–146 range of the other five countries. Its working-age share of the population fell to 85, against 94–100 elsewhere. That puts its GDP per capita at 120, against 132–144.

### Ideal vs actual family size

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_ideal_vs_actual.html" style="width: 100%; height: 440px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28974495. "Actual" is the tempo-adjusted TFR. FT sources: Eurobarometer, Generations and Gender Survey, and South Korea's National Fertility and Family Health and Welfare Surveys. Survey years differ by country.
```
:::

::::

Ideal family size barely moved: 2.3–2.5 in the UK, France and Finland in every survey year. South Korea's fell from 2.22 to 1.96. The gap widened because actual fertility fell. Between 2011 and 2022 it fell from 1.98 to 1.39 in Finland and from 1.92 to 1.63 in the UK. In South Korea it went from 1.52 in 2015 to 1.00 in 2021.

### Coupling at 25–34

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_coupling_25_34.html" style="width: 100%; height: 740px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28955750. FT sources: International Labour Organization, Arab Barometer, Demographic and Health Surveys, national statistics agencies. Some countries count only legal marriage; see [coupling trends](../factors/coupling-trends.md) for the ILO and UN series.
```
:::

::::

The region averages fell between 2015 and 2023 in East Asia (54% to 48%), Latin America (57% to 52%) and most steeply in the Middle East and north Africa (58% to 46%). South Asia stayed at 83–85% and Sub-Saharan Africa at 63–64%.

### Children per mother

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_children_per_mother.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28994739. FT sources: Human Fertility Database and Shaw (2025), On a microdemographic framework for decomposing contemporary fertility dynamics. The chart doesn't say what age range the share of women who are mothers covers. Years differ by country.
```
:::

::::

In the US, children per mother rose from 2.33 in 1995 to 2.58 in 2022, while the share of women who have children fell from 85% to 64%. Chile's share fell from 94% to 65% (1995–2020), with children per mother down only from 2.46 to 2.26.

### Coupling by education

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_coupling_by_education.html" style="width: 100%; height: 440px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28959991. FT sources: UK Household Longitudinal Study, UK Family Resources Survey, US Current Population Survey. UK 1992–2019, US 1980–2024.
```
:::

::::

Graduates used to be the less likely group to be in a couple, and are now the more likely. In the US, coupling at 25–34 fell from 70% to 49% among non-graduates (1980–2024) and from 67% to 58% among graduates. In the UK it fell from 71% to 56% and from 66% to 61% (1992–2019).

### Coupling vs TFR

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_coupling_vs_tfr.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28957217. Both series are indexed to 2010 = 100. Coupling rate is marriage or any co-residential union, depending on the country's data. FT sources: OECD, Our World in Data, Demographic and Health Surveys, Arab Barometer, national statistics agencies.
```
:::

::::

The two indices end close together in most countries. In the latest year, coupling and TFR were 74 and 73 in Finland, 80 and 82 in Mexico, and 79 and 73 in Türkiye. South Korea was 72 and 65, and the US 90 and 85. Matching indices don't separate fewer couples from fewer births per couple; the [couples vs births per couple](../factors/couples-vs-births-per-couple.md) page does that split.

### Earnings of young women vs men

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_earnings_gap.html" style="width: 100%; height: 440px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28989486. Women's average earnings as a % of men's at ages 24–28. FT sources: UK Household Longitudinal Study, US Current Population Survey.
```
:::

::::

In the bottom half of the earnings distribution, women's earnings rose from 66% to 94% of men's in the UK and from 40% to 68% in the US (1994–2021). In the top half they rose from 77–79% to 87% in both countries (1994–2023).

### Socialising

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_socialising.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28973302: the FT's smoothed lines for 15–29-year-olds. Each panel uses a different measure and y-axis range, both taken from the FT. FT sources: American Time Use Survey, Korean Time Use Survey, European Social Survey.
```
:::

::::

Korean 15–29s spent 42 minutes a day socialising in person in 1999 and 20 in 2024. US 15–29s spent 66% of their free time with other people in 2003 and 52% in 2024. The share socialising at least weekly fell from 88% to 72% in the UK and from 88% to 78% across Europe (2002–2023).

### Left–right placement

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ft/ft_br_left_right_by_sex.html" style="width: 100%; height: 440px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
FT chart data, Flourish visualisation 28989105. Average self-placement on a 0–10 left–right scale, under-30s. FT source: European Social Survey; the countries pooled and the weighting aren't stated.
```
:::

::::

Among under-30s without a degree, the gap between men and women grew from 0.54 points in 2002 to 0.90 in 2023. Among graduates it stayed at 0.63–0.65. Both sexes without a degree moved left, women by 0.79 points and men by 0.43. The article says men "have not" moved; on its own data they moved about half as far as women.
