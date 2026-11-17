# Microdemographic Framework

The Total Fertility Rate (TFR) is the product of two independent components: TFR = TMR × CPM.

- **Total Maternal Rate (TMR)**: A societal measure of the proportion of women who would become mothers over their reproductive lifetime, assuming current age-specific fertility rates persist.
- **Total Childlessness Rate (TCR)**: A societal measure indicating the proportion of women who would remain childless over their reproductive lifetime, assuming current age-specific fertility rates persist. As the complement of TMR (i.e., TCR = 1 – TMR). The term societal childlessness encompasses voluntary, medically and biologically involuntary, as well as circumstantial forms of childlessness.
- **Children per Mother (CPM)**: A societal measure representing the average number of children born to women who become mothers, based on current age-specific fertility rates. This period-based metric captures trends in family size independently of childlessness.

```{raw} html
<iframe src="../_static/hfd/mdf_facet.html" style="width: 100%; height: 1060px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

## Summary of Traditional & Proposed Fertility Measures

**Table S1.1.** Microdemographic Framework (MDF) measures.

| Metric | Definition | Type | Strengths | Reporting Lag | Data Requirement | Limitations |
|---|---|---|---|---|---|---|
| Total Maternal Rate (TMR) | Proportion of women who would become mothers (15–49) if current age-specific fertility rates remained constant; equivalent to First-Order TFR (TFR1) but expressed as a likelihood of motherhood rather than births per woman. | Period | Intuitive reframing of TFR1; enhances policy relevance by focusing on motherhood incidence. | Most recent year. | Moderate. Requires birth order data (e.g., HFD). | Tempo effects may inflate or deflate rates (e.g., values >1); relies on birth order accuracy. |
| Total Childlessness Rate (TCR) | Proportion of women who would remain childless if current age-specific fertility rates remained constant; 1 − TMR. | Period | Timely childlessness indicator; reveals shocks (e.g., 1970s, 2008). | Most recent year. | Moderate. Requires birth order data (e.g., HFD). | Tempo effects may yield negative values temporarily; depends on TMR's data quality. |
| Children per Mother (CPM) | Avg. number of children born to mothers (15–49) if current age-specific fertility rates remained constant; TFR / TMR. | Period | Isolates family size trends among mothers; stable over decades. | Most recent year. | Moderate. Requires birth order data and TFR (e.g., HFD). | Sensitive to TMR fluctuations; assumes consistent fertility patterns. |

**Table S1.2.** Traditional fertility measures.

| Metric | Definition | Type | Strengths | Reporting Lag | Data Requirement | Limitations |
|---|---|---|---|---|---|---|
| Total Fertility Rate (TFR) | Avg. number of children per woman if current fertility rates remain constant. | Period | Simple, widely used, allows international comparisons. | Most recent year. | Low. Uses birth registries and population estimates. | Over-aggregates childlessness and family size; masks tempo effects and underlying dynamics. |
| First-Order TFR (TFR1) | Avg. number of first births per woman if current age-specific fertility rates remain constant. | Period | Measures entry into motherhood; available in datasets like HFD. | Most recent year. | Moderate. Requires birth order data. | Less intuitive for non-specialists; still subject to tempo effects; doesn't isolate childlessness or family size. |
| Parity Progression Ratio (PPR) (0→1) | Probability that a childless woman transitions to motherhood. | Period / Cohort | Tracks likelihood of first births across populations. | Decades (Cohort), Recent (Period). | Moderate. Requires birth order data. | Tempo effects distort period estimates; cohort data lags significantly. |
| Children Ever Born (CEB) | Total number of children born to a cohort of women. | Cohort | Reflects true completed fertility. | Decades. | High. Requires long-term surveys. | Highly lagged; misses real-time trends. |
| Cohort Fertility Rate (CFR) | Avg. number of children per woman by the end of reproductive years. | Cohort | Removes tempo distortions; accurate for completed fertility. | Decades. | High. Requires decades of tracking. | Not suitable for timely policy analysis. |
| Tempo-Adjusted TFR | Adjusted TFR correcting for birth postponement. | Period | Mitigates tempo distortions in fertility timing. | Most recent year. | High. Requires statistical adjustments and detailed data. | Still aggregates childlessness and family size; complex to compute. |
| Completed Childlessness Rate (CCR) | Proportion of women in a cohort who never had children. | Cohort | Precise measure of lifetime childlessness. | Decades. | High. Requires surveys or longitudinal studies. | Delayed reporting; no real-time insights. |
| Sibship Size | Avg. number of siblings per child within a cohort. | Cohort | Tracks family size trends from children's perspective. | Decades. | High. Requires detailed household surveys. | Highly lagged; indirect measure of fertility behavior. |

```{note}
Shaw, S. J. (2025), ["On a microdemographic framework for decomposing contemporary fertility dynamics"](https://doi.org/10.1038/s41598-025-11522-9), *Scientific Reports* 15, 30726.

HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).
```
