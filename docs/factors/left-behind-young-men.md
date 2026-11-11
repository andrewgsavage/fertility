# Left-behind young men

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

**Group:** Education and work. Back to the [factors table](index.md).

## Proposed mechanism

Young men falling behind in education, work and earnings (including NEETs) leave fewer partners seen as able to support a family (young first births: not for low-educated men).

## Where it acts

Ticks from the [factors table](index.md): ✓ where the mechanism is proposed to act, ? where the evidence is mixed or too thin to keep a tick.

| Coupling | PPR 0→1 | First-birth cond. ASFR | Young first births | PPR 1→2+ | Second+ cond. ASFR |
|:-:|:-:|:-:|:-:|:-:|:-:|
| ✓ | ✓ | ✓ | ✓ |  |  |

## Young men's education and NEET rates

Two measures of young men's position: the tertiary-educated share of 25–34s (women minus men) and the NEET rate (not in employment, education or training) of 15–29s by sex. Neither measures partnership prospects directly, and neither shows that a gap reduced births.

```{raw} html
<iframe src="../_static/eurostat/tertiary_gender_gap_europe.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{raw} html
<iframe src="../_static/eurostat/neet_by_sex_europe.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

| Country | Tertiary gap (F−M, pp) 2000 | 2024 | NEET men 2013 | 2024 | NEET women 2013 | 2024 |
|---|--:|--:|--:|--:|--:|--:|
| Spain | 6.1 | 11.2 | 22.8% | 11.9% | 22.1% | 12.1% |
| Italy | 2.7 | 13.5 | 24.1% | 13.8% | 28.3% | 16.6% |
| France | 4.9 | 6.3 | 12.4% | 12.4% | 14.0% | 12.9% |
| Germany | −3.2 | 5.8 | 8.0% | 7.9% | 11.2% | 10.1% |
| Netherlands | 0.5 | 9.5 | 6.9% | 4.5% | 9.4% | 5.4% |
| Poland | 5.9 | 17.9 | 14.2% | 7.4% | 18.8% | 11.5% |
| Sweden | 5.4 | 17.2 | 7.1% | 6.5% | 8.0% | 6.0% |
| Finland | 15.8 | 15.5 | 10.0% | 10.5% | 10.8% | 9.0% |
| Czechia | −0.3 | 15.2 | 8.2% | 3.9% | 17.7% | 13.3% |

Women were ahead of men in tertiary attainment among 25–34s in 29 of 32 countries with data in 2005 and in all 35 in 2024. The gap has widened since 2000 in most countries shown, but not in Finland, where it was already about 16 points. NEET rates tell a different story: in 2024 men's rate was below women's in 30 of 35 countries, and men's rate fell from 2013 in most of those shown. So the data supports an education gap in women's favour, not a rising share of young men outside work and study. It cannot show whether women see the average man as a less suitable partner, nor how the lowest-educated men fare; NEET is not split by education here. Male childlessness and young men's partnership rates were not fetched.

Coverage: Eurostat [attainment by sex and age](https://ec.europa.eu/eurostat/databrowser/view/edat_lfse_03/default/table) (edat_lfse_03; 38 countries, 1992–2025) and [NEET rates](https://ec.europa.eu/eurostat/databrowser/view/lfsi_neet_a/default/table) (lfsi_neet_a; 37 countries, 2003–2025, most from 2013 or later).

## Causal evidence

From the [causal analysis](causal-analysis.md), graded by research design (A quasi-experiment, B panel or register, C correlation or simulation, T theory):

B (+): Norwegian register data link unemployment to fewer births for childless men and women ([Kristensen 2022](https://doi.org/10.4054/demres.2022.46.35)); stable employment promotes parenthood in Finland, more for men ([Jalovaara 2025](https://doi.org/10.1177/00016993251403380)), though that paper's title argues weaker labour status is unlikely to drive the cohort decline.

## Studies found

Studies found by searching OpenAlex, read from abstracts only. The verdict says whether the study supports the tick in that column.

| Column | Verdict | Study | Finding |
|---|---|---|---|
| First-birth cond. ASFR | supports | Kristensen 2022, [10.4054/demres.2022.46.35](https://doi.org/10.4054/demres.2022.46.35) | Norway register 1994-2014: individual unemployment negatively associated with births for childless men and women. |
| First-birth cond. ASFR | supports | Jalovaara 2025, [10.1177/00016993251403380](https://doi.org/10.1177/00016993251403380) | Finland: stable employment promotes entry into parenthood for both sexes, stronger for men; long-term unemployment link intensified in recent cohorts. Title argues weaker labour status is unlikely to drive the cohort decline. |
| Young first births | mixed | Miettinen 2019 (above) | The negative unemployment association does not apply to young, low-educated men. |
| Second+ cond. ASFR | mixed | Kristensen 2022 (above) | Fathers' unemployment link to births faded over time; consistent with blank. |

No study found for: Coupling, PPR 0→1, PPR 1→2+.

Source: [`research/factor-evidence/life-course-and-education-work.md`](https://github.com/andrewgsavage/fertility/blob/main/research/factor-evidence/life-course-and-education-work.md).

## Proposed tick changes

From a second judging pass over the studies above.

| Column | Current | Recommendation | Confidence | Reason |
|---|:-:|---|---|---|
| Young first births | ✓ | qualify (not for low-educated men) | low | Miettinen 2019 only: unemployment–first-birth link absent for young low-educated men |
