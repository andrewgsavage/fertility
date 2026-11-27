# Chance a Childless Woman Becomes a Mother

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

If a childless woman of a given age lived through the rest of her childbearing years at one calendar year's [conditional first-birth rates](first-vs-second-birth.md) (first births per childless woman at each age), the chance she has a first child before 45 is

```{math}
P(\text{mother before 45} \mid \text{childless at } a) = 1 - \exp\Big(-\sum_{x=a}^{44} m_1(x)\Big)
```

where {math}`m_1(x)` is the year's first-birth rate per person-year lived childless at age {math}`x`.

Since 2005 the chance has fallen for childless women of 25 in most countries: from 75% to 54% in South Korea, 66% to 50% in Taiwan (2006), 71% to 59% in Finland, 73% to 62% in Spain and 77% to 67% in the United States. For childless women of 35 it has risen in most countries, from 22% to 34% in Austria and 41% to 54% in Portugal, as more first births happen in the late 30s. At 30 the change is mixed: down 6 to 10 points in South Korea, Taiwan, Spain, Sweden, Finland and the United States, and up in most of Central Europe.

::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/hfd/motherhood_probability.html" style="width: 100%; height: 1970px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
:::

:::{tab-item} Data
| Country | 25, 2005 | 25, latest | 30, 2005 | 30, latest | 35, 2005 | 35, latest | Latest year |
|---|--:|--:|--:|--:|--:|--:|--:|
| Canada | 71% | 63% | 57% | 54% | 26% | 30% | 2023 |
| United States | 77% | 67% | 62% | 56% | 32% | 34% | 2024 |
| Chile | 79% | 82% | 64% | 73% | 34% | 54% | 2020 |
| Japan | 61% | 59% | 45% | 48% | 20% | 26% | 2024 |
| South Korea | 75% | 54% | 60% | 51% | 27% | 31% | 2024 |
| Taiwan (2006) | 66% | 50% | 52% | 42% | 22% | 25% | 2024 |
| Denmark | 80% | 76% | 64% | 65% | 30% | 38% | 2025 |
| Finland | 71% | 59% | 55% | 49% | 26% | 27% | 2024 |
| Norway | 80% | 73% | 66% | 64% | 33% | 38% | 2024 |
| Sweden | 81% | 72% | 69% | 62% | 38% | 36% | 2024 |
| Estonia | 71% | 62% | 48% | 49% | 23% | 28% | 2024 |
| Lithuania | 61% | 78% | 33% | 66% | 11% | 34% | 2020 |
| Belgium | 72% | 73% | 52% | 60% | 22% | 32% | 2022 |
| Ireland | 73% | 74% | 64% | 69% | 36% | 49% | 2022 |
| Netherlands | 77% | 73% | 64% | 64% | 31% | 37% | 2023 |
| Spain | 73% | 62% | 64% | 56% | 37% | 38% | 2023 |
| Portugal | 84% | 81% | 73% | 74% | 41% | 54% | 2024 |
| Greece | 65% | 64% | 52% | 56% | 28% | 37% | 2024 |
| England & Wales | 71% | 70% | 60% | 62% | 35% | 42% | 2025 |
| Austria | 65% | 69% | 49% | 58% | 22% | 34% | 2023 |
| Switzerland | 72% | 71% | 59% | 64% | 31% | 42% | 2024 |
| Czechia | 74% | 82% | 55% | 69% | 22% | 38% | 2021 |
| Hungary | 70% | 66% | 53% | 53% | 25% | 28% | 2020 |
| Slovenia | 73% | 76% | 57% | 61% | 26% | 34% | 2019 |
| Bulgaria | 81% | 82% | 64% | 69% | 35% | 47% | 2021 |
| Croatia | 69% | 72% | 50% | 60% | 22% | 34% | 2024 |
:::

:::{tab-item} Notes
```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Conditional first-birth rates by single age (`mi.txt`). Data downloaded on 2026-07-13.
Ages 45 and over are left out because many countries have no rate there for a ten-year stretch; first births after 45 would add well under one percentage point.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3. Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).
HFD has no conditional rates for England and Wales; they are reconstructed from this table as yearly hazards of a first birth among childless women,
re-sliced from cohort to calendar year, and combined as {math}`1 - \prod_{x=a}^{44}(1 - h_x)`.
```

```{note}
Greece is not in HFD. Its first-birth rates per childless woman are estimated from births by order: [Human Fertility Collection](https://www.fertilitydata.org/Country/Country?code=GRC) estimates for 1960–1991 and Eurostat [demo_fordagec](https://ec.europa.eu/eurostat/databrowser/view/demo_fordagec/default/table) over [demo_pjan](https://ec.europa.eu/eurostat/databrowser/view/demo_pjan/default/table) from 1992, with childless women from each cohort's summed first-birth rates since 1960. Mauritius, estimated the same way from Human Fertility Collection rates, starts in 2005 and doesn't yet cover every age to 44, so it has no panel.
```
:::

::::
