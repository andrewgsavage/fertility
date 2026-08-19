# Bye Bye Baby?

The Resolution Foundation's report [Bye Bye Baby](https://www.resolutionfoundation.org/publications/bye-bye-baby/) ([PDF](https://www.resolutionfoundation.org/app/uploads/2026/03/Bye-bye-baby.pdf)) has a few conclusions that appear to be artefacts of how the data has been presented. [Reanalysing the data](../dataisugly/bye-bye-baby) gives other conclusions.


**Since 2011 there has been a sharp rise in the proportion of nongraduates aged 25-29 who haven’t had a child**

This is correct but misleading. It is an artefact of using childlessness rates rather than fertility or motherhood rates. First birth fertility rates in both graduates and non-graduates have declined similarly. The proportion of 25-29 year olds with a child fell by practically the same amount for graduates (-33%) as for non-graduates (-30%) over 2011-2023:

::::{tab-set}

:::{tab-item} Table
| | Graduate: childless | Graduate: with child | | Non-graduate: childless | Non-graduate: with child |
|---|---|---|---|---|---|
| 2011 | 77% | 23% | | 33% | 67% |
| 2023 | 85% | 15% | | 53% | 47% |
| Relative change in "with child" | | -33% | | | -30% |
:::

:::{tab-item} Figure 6

```{image} /_static/resolution/grads_nongrads_birth_year.png
:alt: Proportion of women without a biological child, by age and education, plotted against mother's birth year
:width: 100%
```
:::

::::

**Graduate women set the trend for delay; now non-graduate women appear to be following suit**



> A larger share of women belonged to a group – graduates – that have tended to have children later. But behaviour also changed within this group, with graduates postponing motherhood further over time. As a result, the median age at first birth among graduate women rose from 28 for those born in the early-1950s to 32 for those born in the 1970s. Among women who didn’t make it to or through higher education, there was very little change in childbearing behaviour for a long time – the typical age at which non-graduate women had their first child remained at around 25-26 years across cohorts.

This appears to be the same data as plotted in Figure 6. However Figure 6 only plots childlessness rates for the 1950s cohorts at 40-44 so it is not possible to verify. Furthermore the data plotted in Figure 6 shows some errors; A cohort's childless share can only fall or stay flat as it ages - a woman who has had a child by 35-39 is still a mother at 40-44. Similarly it is not realistic that there are no new mothers as the cohort ages from 30-34 to 34-39. The trends seen in graduates, the peaks and troughs between 1965 and 1975, don't occur in successive age groupings for the same cohort. These factors make this data questionable.


::::{tab-set}

:::{tab-item} Figure 6, by birth year

```{image} /_static/resolution/grads_nongrads_birth_year.png
:alt: Proportion of women without a biological child, by age and education, plotted against mother's birth year
:width: 100%
```
:::

:::{tab-item} Figure 6, by cohort
```{image} /_static/resolution/grads_nongrads.png
:alt: Proportion of women without a biological child, by age and education, plotted against reporting year
:width: 100%
```
:::

::::

The decline visible in the non-graduate 25-29 group for mothers born from ~1984 onwards (reporting years from 2011) reappears when they are 30-34 as expected. It is odd that this is the only place where a trend in one age group is seen in the subsequent age group as the mothers age, suggesting a large amount of noise in this data.

Graduate fertility rates were static until 2014, so it's too early to tell whether graduate childless rates will show the same follow-through, since those cohorts haven't reached 30-34 yet.


**The rise in childlessness among non-graduates is likely related to the decline in partnership rates and changes to housing tenure**

The report's narrative links the non-graduate childlessness rise to two other trends it shows separately: falling coresidential partnership (Figure 7) and worsening housing tenure (Figure 8). Plotting all three on a shared year axis for the group the report focuses on — non-graduates aged 25-29 — with a dotted line at 2011, the year the report's own title marks as when the "sharp rise" began, tests whether the timing actually lines up:

::::{tab-set}

:::{tab-item} Figures 6, 7 & 8
```{image} /_static/resolution/mashup_analysis.png
:alt: Childlessness, coresidential partnership, and housing tenure (as lines) for non-graduates aged 25-29, on a shared year axis, with a marker at 2011
:width: 100%
```
:::

:::{tab-item} Figures 6, 7 & 8, table
| Series | 2009 | 2011 | 2022 |
|---|---|---|---|
| Childless (Figure 6) | 38% | 33% | 53% |
| Cohabiting or married, Women (Figure 7) | 63% | 62% | 59% |
| Cohabiting or married, All (Figure 7) | 58% | 57% | 55% |
| Cohabiting or married, Men (Figure 7) | 53% | 53% | 51% |
| Homeowner (Figure 8) | 33% | 27% | 25% |
| Social rent (Figure 8) | 16% | 17% | 14% |
| Private rent (Figure 8) | 29% | 34% | 33% |
| Other (Figure 8) | 2% | 3% | 3% |
| Living with parents (Figure 8) | 19% | 19% | 26% |
:::

:::{tab-item} Figure 9
```{image} /_static/resolution/rf_figure9.png
:alt: Resolution Foundation Figure 9 — proportion of non-graduate women aged 25-29 without a dependent child, by tenure and relationship status, UK, 2009-2013 vs 2020-2024
:width: 100%
```
:::

:::{tab-item} Figure 9, table
| Category | 2009-2013 | 2020-2024 | Change |
|---|---|---|---|
| Living with parents | 86% | 85% | -1pp |
| Other | 74% | 77% | +3pp |
| Homeowner | 45% | 56% | +11pp |
| Private rent | 40% | 47% | +7pp |
| Social rent | 17% | 19% | +2pp |
| Coupled | 38% | 44% | +6pp |
| Single | 51% | 59% | +8pp |
| All | 45% | 54% | +9pp |
:::

::::

Childlessness fell from 42% in 1999 to 33% in 2011, a 10pp decline. It then rose from 33% in 2011 to 53% in 2022, a 20pp increase. The report asserts that coupling and housing costs are driving the change. However it does not directly compare rates during the decline and increase in childnlessness, so let's do that.

- **Partnership** Cohabiting or married rates for women were steady pre-2011. Post-2011 they declined 4pp, and couples are shown to have approx a 13pp decrease in likelihood of childlessness in Figure 9, so explains 0.5pp of the 20pp of the decline in childlessness.
- **Housing costs** Homeowner rates declined fastest the pre-2011 with private renting increasing as childlessness rates fell, going *against* the paper's arguement that higher housing costs lead to increased childlessness. Post-2011 homeowner and private renting rates pleateaued while childlessness rates increased sharply, again going against the paper's arguement. Furthermore, Private rent and Homeship childlessnesss rates are shown to be fairly similar in Figure 9. Living with parents increased by 6.3pp post-2011 and has a 38pp increase in the likelihood of childlessness compared to private rent, so can explain 2.4pp of the 20pp of the decline in childlessness.


**The decline in coupling and increase in living with parents contribute to the increase in childlessness. Housing costs show limited relation to the decline in childlessness.**

```{note}
Data digitized from the Resolution Foundation's [Bye Bye Baby](https://www.resolutionfoundation.org/publications/bye-bye-baby/) report, Figure 6.

The shared-axis chart and slope table use the digitized Figures 6a, 7a, and 8 data described in [Bye Bye Baby](../dataisugly/bye-bye-baby).
```
