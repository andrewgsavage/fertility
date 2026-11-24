# Coupling and motherhood

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Part of [Partnership formation](partnership-formation.md). The share of women with at least one child against the share living in a couple (married or cohabiting), by age group and by single year of age.

**Reading the arrows.** Each arrow runs from a country's first year to its latest. Both axes are shares of all women at that age, drawn at the same scale, so the direction of an arrow says which share moved.

```{raw} html
<svg viewBox="0 0 360 250" role="img" aria-label="Arrow directions on a chart of % in a couple (x) against % with a child (y)" style="max-width: 360px; width: 100%; display: block; margin: 0.5em auto; color: var(--color-foreground-primary);">
<defs>
<marker id="ah-a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#d95f02"/></marker>
<marker id="ah-b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1b9e77"/></marker>
<marker id="ah-c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7570b3"/></marker>
<marker id="ah-d" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#e7298a"/></marker>
</defs>
<line x1="40" y1="215" x2="340" y2="215" stroke="currentColor" stroke-width="1.2"/>
<line x1="40" y1="215" x2="40" y2="15" stroke="currentColor" stroke-width="1.2"/>
<text x="340" y="235" text-anchor="end" font-size="12" fill="currentColor">% in a couple &#8594;</text>
<text x="16" y="215" font-size="12" fill="currentColor" transform="rotate(-90 16 215)">% with a child &#8594;</text>
<circle cx="190" cy="115" r="3.5" fill="currentColor"/>
<line x1="190" y1="115" x2="190" y2="195" stroke="#d95f02" stroke-width="2.5" marker-end="url(#ah-a)"/>
<text x="200" y="178" font-size="13" font-weight="bold" fill="#d95f02">A</text>
<line x1="190" y1="115" x2="133" y2="172" stroke="#1b9e77" stroke-width="2.5" marker-end="url(#ah-b)"/>
<text x="116" y="186" font-size="13" font-weight="bold" fill="#1b9e77">B</text>
<line x1="190" y1="115" x2="110" y2="115" stroke="#7570b3" stroke-width="2.5" marker-end="url(#ah-c)"/>
<text x="92" y="119" font-size="13" font-weight="bold" fill="#7570b3">C</text>
<line x1="190" y1="115" x2="247" y2="58" stroke="#e7298a" stroke-width="2.5" marker-end="url(#ah-d)"/>
<text x="252" y="54" font-size="13" font-weight="bold" fill="#e7298a">D</text>
</svg>
```

- **A, straight down:** the share in a couple stays the same while the share with a child falls: couples form at a constant rate but fewer go on to have a child by that age.
- **B, diagonal down and left (45°):** both shares fall by the same number of points: every woman who no longer forms a couple is one fewer mother, as if each lost couple would have had a child.
- **C, straight left:** fewer couples, but the same share with a child: the women who no longer form couples were not the ones having children (or have them outside a couple).
- **D, diagonal up and right:** more couples and more mothers, point for point.

An arrow pointing straight at the origin (0%, 0%) means fewer couples with the same share of them having a child; since fewer than all couples have a child, that line is shallower than 45° when the share with a child is below the share in a couple. Arrows steeper than that mean the share of couples having a child fell as well. Shares of all women do not say whether the mothers are the women in couples; the lines above are the simplest reading, not the only one.

Each chart has a *middle of age range* panel (with a child by the middle of the coupling age range) and an *end of age range* panel (by its end). The measured lag from coupling to a first birth, on [Couple to first birth](union-to-first-birth.md), is 2–5 years, which favours the end-of-range panels.

The **Ratio over time** tab on each chart plots % with a child divided by % in a couple, year by year. A flat line is an arrow aimed at the origin; a falling line is an arrow steeper than that. It is mothers per coupled woman, not the share of couples with a child: mothers outside a couple raise it, and it can exceed 1. The y axis is logarithmic, so a halving and a doubling are the same distance from the dotted line at 1.

## HFD

\% with a child from the [Human Fertility Database](https://www.humanfertility.org/), at single years of age.

(with-child-eurostat-18-24)=
### Eurostat

Eurostat provides data on % living in a couple for 18-24 and 25-49 year olds. The 25-49 year bucket is too big to be useful. 

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/eurostat/coupling_vs_cond_asfr_eurostat_default.html" style="width: 100%; height: 700px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/eurostat/coupling_vs_cond_asfr_eurostat_ratio.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
Eurostat [household composition table](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhindws/default/table) (EU Labour Force Survey), adults living in a couple (married or cohabiting, in their own couple household) over all persons in the group. A couple sharing a home with parents or other adults counts as "another type of household", not as a couple, so the share is low where young couples live with family: in Croatia in 2020, 1.1k of 138k women 18–24 were in a couple household and 135.9k in another type. First-birth rates and % with a child from the Human Fertility Database as in the charts below; UK births are England and Wales (ONS reconstruction, ages 21 and over, so no first-birth rate at 20–24). 20 countries have both. EU-LFS household data has a methodology break in 2021. Denmark, Sweden and Norway start hidden (click their names to show them): Denmark and Sweden jump 15–25 points between years at 25–49 and Denmark falls to 1% at 18–24, which look like series breaks; Norway has data only from 2021, at about 3%. Values Eurostat flags u (low reliability) are drawn but left out of the trend arrows, are marked on hover, and are dashed on the ratio lines: Croatia in every year but 2022, Bulgaria 2015–2016 and 2019–2023, Denmark, Ireland, Slovakia and Slovenia from 2020–2021, Lithuania 2006–2008, Norway 2021 and 2023. End-of-range ratios divide % with a child by the end age by the coupling share averaged over the whole age range, youngest ages included, so they run above the middle-of-range ratios even if every mother is in a couple.
```

:::

::::

(with-child-15-24-25-34)=
### ILO, FT & National registers

Other sources provide data on  % living in a couple for 18-24 and 25-34 year olds.

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/ilo/coupling_vs_mothers_grid.html" style="width: 100%; height: 800px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/ilo/coupling_vs_mothers_grid_ratio.html" style="width: 100%; height: 800px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

| Country | Coupling source | Years |
|---|---|---|
| Canada, Japan, S Korea | ILO, women | 2000–2023/24 |
| Chile, Russia, Belarus | ILO, women | 2010–2020, 2010–2018, 2016–2018 |
| Denmark, Finland, Netherlands | National registers, women, any age | 1990–2025, 1992–2024, 1995–2023 |
| US | CPS (Census AD-3), women, 25–34 | 1990–2023 |
| Spain | FT, both sexes, 25–34 | 1991–2022 |
| Poland | FT, both sexes, 25–34 | 2001–2017 |
| UK | FT, both sexes, 25–34; births England and Wales | 1992–2019 |

```{note}
First births per childless woman from the [Human Fertility Database](https://www.humanfertility.org/) (conditional fertility rates `mi`, pooled over the chosen ages with childless-women exposures `exposRRpa` as weights; % with a child = 100 minus childless women's share of all female exposure at that age and year, from `exposRRpa`); UK from the ONS England and Wales reconstruction (% with a child from cohort table 3; see [England and Wales](#coupling-ew-ons) below). Coupling from ILOSTAT where it records cohabitation, from the national sources on [Coupling over time](coupling-trends.md) for Denmark, Finland, the Netherlands and the US, otherwise from the FT. HFD countries with no coupling series (e.g. France, Germany, Sweden) are left out. End-of-range ratios divide % with a child by the end age by the coupling share averaged over the whole age range, youngest ages included, so they run above the middle-of-range ratios even if every mother is in a couple.
```

:::

::::

### National registers: Not aggregated by age


::::{tab-set}

:::{tab-item} Denmark, Finland, Netherlands
```{raw} html
<iframe src="../_static/nso/coupling_mothers_trends.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} US
```{raw} html
<iframe src="../_static/nso/coupling_mothers_trends_us.html" style="width: 100%; height: 640px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/nso/coupling_mothers_trends_ratio.html" style="width: 100%; height: 750px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
Couples: women living with a spouse or partner (married, registered or cohabiting) over all women of that age, from national registers: [CBS StatLine 37620](https://opendata.cbs.nl/statline/#/CBS/nl/dataset/37620/table) (Netherlands), Statistics Denmark [FAM100N](https://www.statbank.dk/FAM100N) over [BEFOLK1](https://www.statbank.dk/BEFOLK1), Statistics Finland [12c6](https://pxdata.stat.fi/PxWeb/pxweb/en/StatFin/StatFin__perh/statfin_perh_pxt_12c6.px/); US Census Bureau [Table AD-3](https://www.census.gov/data/tables/time-series/demo/families/adults.html) (CPS ASEC), which gives only 18–24 and 25–34. % with a child: 100 minus childless women's share of all women at that age and year, from the [Human Fertility Database](https://www.humanfertility.org/) (`exposRRpa`), pooled over the same ages for the US. More by age and year on [Coupling over time](coupling-trends.md).
```

:::

::::

(with-child-un-5-year)=
### UN: 5-year age groups

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/un/coupling_vs_mothers_grid_un.html" style="width: 100%; height: 1500px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/un/coupling_vs_mothers_grid_un_ratio.html" style="width: 100%; height: 1500px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
Coupling from UN World Marriage Data 2019 ([Coupling over time](coupling-trends.md), women married or in a union), one point per census or survey year; the same countries and coupling series as on [Unused plots](#coupling-un-first-birth). % with a child at single ages from the [Human Fertility Database](https://www.humanfertility.org/) (100 minus childless women's share of all female exposure at that age and year, from `exposRRpa`). End-of-range ratios divide % with a child by the end age by the coupling share averaged over the whole age range, youngest ages included, so they run above the middle-of-range ratios even if every mother is in a couple.
```

:::

::::

## ONS

\% with a child and coupling from the Office for National Statistics, England and Wales.

(coupling-ew-ons)=
### England and Wales

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/ons/coupling_vs_mothers_ew.html" style="width: 100%; height: 560px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/ons/coupling_vs_mothers_ew_ratio.html" style="width: 100%; height: 450px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
\% with a child by 30: ONS [childbearing for women born in different years](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable), table 3 (parity distribution by age and year of birth), 100 minus the share of each cohort still childless at 30, plotted at year = birth cohort + 30. In a couple at 16–29: ONS [population estimates by marital status and living arrangements](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesbymaritalstatusandlivingarrangements) (Labour Force Survey weighted to mid-year population estimates), women living as a married, civil partnered or cohabiting couple over all women 16–29. England and Wales, 2002–2025. ONS publishes living arrangements under 30 only as one 16–29 group, 18–29 in 2025 after the minimum marriage age rose to 18. ONS suspended the accredited status of LFS-based estimates in November 2023 over falling response; the 2023–2024 dip in coupling may reflect that.
```

:::

::::

## DHS

\% with a child from [Demographic and Health Surveys](https://dhsprogram.com/), by 5-year age group, for countries not in the Human Fertility Database.

(with-child-un-dhs)=
### UN: 5-year age groups

DHS countries: the share of women in a 5-year age group with at least one child against the share of the same age group married or in a union. Each arrow is a country's straight-line trend from its first to its latest survey year, labelled with its country code. All panels run 0–100% on both axes.

::::{tab-set}

:::{tab-item} Chart

```{raw} html
<iframe src="../_static/dhs/coupling_vs_mothers_un_grid.html" style="width: 100%; height: 850px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/dhs/coupling_vs_mothers_un_grid_ratio.html" style="width: 100%; height: 850px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
\% with a child from the [DHS Program API](https://api.dhsprogram.com/) (indicator `FE_CEBA_W_CH0`, women with no children ever born, by 5-year age group), DHS surveys of all women only. Coupling from UN World Marriage Data 2019 ([Coupling over time](coupling-trends.md), women married or in a union), one point per survey year, usually from the same DHS survey. 30 countries with at least two such years.
```

:::

::::

### ILO, FT & UN

Share of women in a 5-year age group with at least one child against the coupling rate, for countries with Demographic and Health Surveys (DHS), which are not in the Human Fertility Database. The left dropdown picks the coupling age group; the right one picks the motherhood age group (20–24 to 35–39). Markers grow with the year.

::::{tab-set}

:::{tab-item} ILO, national and FT coupling
```{raw} html
<iframe src="../_static/dhs/coupling_vs_mothers.html" style="width: 100%; height: 600px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} UN coupling, 5-year ages
```{raw} html
<iframe src="../_static/dhs/coupling_vs_mothers_un.html" style="width: 100%; height: 600px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Ratio over time

```{raw} html
<iframe src="../_static/dhs/coupling_vs_mothers_ratio.html" style="width: 100%; height: 850px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

:::

:::{tab-item} Sources

```{note}
\% with a child from the [DHS Program API](https://api.dhsprogram.com/) (indicator `FE_CEBA_W_CH0`, women with no children ever born, by 5-year age group), DHS surveys of all women only; surveys of ever-married women (most of Egypt, Jordan, Pakistan and Bangladesh) are left out. HFD rows of the table: childless women's share of all women in the age group, from the [Human Fertility Database](https://www.humanfertility.org/) (`exposRRpa`). Coupling from ILOSTAT (women) for 14 DHS countries, FT (both sexes, 25–34) for Angola, Cambodia, Ghana, India, Kenya and Nigeria; UN tab: UN World Marriage Data ([Coupling over time](coupling-trends.md)), 30 DHS countries, one point per survey year, usually from the same DHS survey.
```

:::

::::

| Latest survey, women aged 25–29 | Married or in a union | With a child |
|---|--:|--:|
| South Africa 2016 | 35.7% | 84.7% |
| Namibia 2013 | 37.5% | 82.7% |
| Colombia 2010 | 60.2% | 75.2% |
| Philippines 2017 | 70.7% | 70.4% |
| Ukraine 2012 (HFD) | 70.0% | 61.2% |
| Sweden 2012 (HFD) | 73.3% | 35.0% |
| Japan 2015 (HFD) | 38.0% | 25.2% |

At the same coupling rate, DHS countries have far more mothers than HFD countries. In South Africa and Namibia at least 45% of women aged 25–29 are mothers who are not married or in a union (mothers minus coupled), so coupling there says little about first births.
