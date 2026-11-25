# Unused plots

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Charts taken off their pages and kept here for reference.

## Coupling against first-birth rates, by country (dropdowns)

From [Coupling and motherhood](#with-child-15-24-25-34), where a 2x2 grid of fixed age pairs replaced it. Every country with both a coupling series and conditional first-birth rates: 13 countries. Each arrow is a country's straight-line trend from its first to its latest year, labelled with its country code; faint points are every year. The y dropdown also offers the share of women with a child by 25, 30, 35 or 40. The coupling dropdown also has 5-year groups, which exist only for the register countries (Denmark, Finland, Netherlands); the US, Spain, Poland and the UK have 25–34 only.

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/ilo/coupling_vs_cond_asfr.html" style="width: 100%; height: 600px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
First births per childless woman from the [Human Fertility Database](https://www.humanfertility.org/) (conditional fertility rates `mi`, pooled over the chosen ages with childless-women exposures `exposRRpa` as weights; % with a child = 100 minus childless women's share of all female exposure at that age and year, from `exposRRpa`); UK from the ONS England and Wales reconstruction (ages 21 and over only; % with a child from cohort table 3). Coupling from ILOSTAT where it records cohabitation, from national registers for Denmark, Finland and the Netherlands, the CPS for the US, otherwise from the FT. Country sources and years are in the Sources tab on [Coupling and motherhood](#with-child-15-24-25-34).
```
:::

::::

## Young adults in a couple against first-birth rates (dropdowns)

From [Coupling and motherhood](#with-child-eurostat-18-24), which now shows women 18–24 in a couple against % with a child by 21 and by 25. The dropdowns offer other coupling ages and sexes, and first-birth rates or % with a child at other ages.

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/eurostat/coupling_vs_cond_asfr_eurostat_trends.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Notes
```{note}
Eurostat [household composition table](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhindws/default/table) (EU Labour Force Survey), adults living in a couple (married or cohabiting, in their own couple household) over all persons in the group; people living with their parents are not counted as in a couple. First-birth rates and % with a child from the Human Fertility Database as on Coupling and motherhood; UK births are England and Wales (ONS reconstruction, ages 21 and over, so no first-birth rate at 20–24). 20 countries have both. EU-LFS household data has a methodology break in 2021. Denmark, Sweden and Norway start hidden (click their names to show them): Denmark and Sweden jump 15–25 points between years at 25–49 and Denmark falls to 1% at 18–24, which look like series breaks; Norway has data only from 2021, at about 3%.
```
:::

::::

(coupling-un-first-birth)=
## Coupling by 5-year age against first-birth rates, UN data

From [Partnership formation](../factors/partnership-formation.md), removed from that page. Coupling from the UN series, women married or in a union, by 5-year age group, against first births per childless woman. 17 countries; one point per census or survey year, so most lines have 3–6 points. Each arrow is a country's straight-line trend from its first to its latest year, labelled with its country code; faint points are every year. The y dropdown also offers the share of women with a child by 25, 30, 35 or 40.

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/un/coupling_vs_cond_asfr_un.html" style="width: 100%; height: 600px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Notes

```{note}
Coupling from UN World Marriage Data 2019 ([Coupling over time](../factors/coupling-trends.md), women); first-birth rates from the Human Fertility Database, pooled over the chosen single ages with childless-women exposures as weights. Countries: Austria, Belarus, Bulgaria, Canada, Chile, Czechia, Denmark, Estonia, Hungary, Japan, S Korea, Lithuania, Norway, Poland, Russia, Sweden, Ukraine. Finland, Iceland, Ireland and Taiwan have UN and HFD data but fewer than two years in common.
```

:::

::::
