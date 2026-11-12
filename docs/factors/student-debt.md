# Student debt

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

**Group:** Education and work. Back to the [factors table](index.md).

## Proposed mechanism

Repayments reduce disposable income during prime childbearing years.

## Where it acts

Ticks from the [factors table](index.md): ✓ where the mechanism is proposed to act, ? where the evidence is mixed or too thin to keep a tick.

| Coupling | PPR 0→1 | First-birth cond. ASFR | Young first births | PPR 1→2+ | Second+ cond. ASFR |
|:-:|:-:|:-:|:-:|:-:|:-:|
| ✓ | ✓ | ✓ | ✓ |  |  |

## Student loan balances

England: average balance per borrower with a loan balance, as at the end of each financial year (the x-axis is the year it ends). US: total student loans outstanding at Q4 each year. Both nominal.

```{raw} html
<iframe src="../_static/ons/student_loan_debt_england_us.html" style="width: 100%; height: 420px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

| | 2007 | 2010 | 2015 | 2020 | 2024 |
|---|--:|--:|--:|--:|--:|
| England: borrowers with a balance (millions) | 1.27 | 1.92 | 3.04 | 4.46 | 5.52 |
| England: average balance (£) | 9,320 | 10,780 | 14,580 | 25,150 | 36,740 |
| US: total outstanding ($ billion) | 589 | 855 | 1,320 | 1,694 | 1,777 |

In England the average balance rose about four-fold and the number of borrowers with a balance about four-fold between 2007 and 2024. US balances tripled between 2007 and 2024 but have been roughly flat since 2021 ($1,733bn in 2021, $1,777bn in 2024). Both series cover all borrowers, not only those of childbearing age, and say nothing about repayments. England's loans are [income-contingent](https://www.gov.uk/government/statistics/student-loans-in-england-2024-to-2025), so a larger balance does not mean proportionally larger repayments. Fertility fell over the same years. The data here has no comparison of borrowers with non-borrowers.

No comparable cross-country series (debt per borrower or share of graduates with debt) was found in a downloadable form, so only England and the US are shown.

Coverage: Student Loans Company, [Student Loans in England: Financial Year 2024-25](https://www.gov.uk/government/statistics/student-loans-in-england-2024-to-2025), Table 5A, income-contingent borrowers who were England-domiciled or EU-domiciled studying in England, 2006-07 to 2023-24 (2024-25 is suppressed). US: Federal Reserve, [Student Loans Owned and Securitized, Outstanding](https://fred.stlouisfed.org/series/SLOAS), 2006–2024.

## Causal evidence

From the [causal analysis](causal-analysis.md), graded by research design (A quasi-experiment, B panel or register, C correlation or simulation, T theory):

C (~): Japanese women at two-year colleges with loans are more likely to delay marriage ([Wang 2024](https://doi.org/10.1080/03075079.2024.2307972)). One country, correlation.

## Studies found

Studies found by searching OpenAlex, read from abstracts only. The verdict says whether the study supports the tick in that column.

| Column | Verdict | Study | Finding |
|---|---|---|---|
| Coupling | mixed | Wang 2024, *Student loan debt and family formation of youth in Japan*, [10.1080/03075079.2024.2307972](https://doi.org/10.1080/03075079.2024.2307972) | Japan, 2017 graduate survey: 2-year-college women with loans more likely to delay marriage. |
| Coupling | no evidence found | Bozick 2014, *Do student loans delay marriage?*, [10.4054/demres.2014.30.69](https://doi.org/10.4054/demres.2014.30.69) | US; abstract truncated before results. Kuperberg 2021 ([10.1111/soin.12416](https://doi.org/10.1111/soin.12416)) find only stated norms (a significant minority say marriage should be delayed). |
| First-birth cond. ASFR | supports | Wang 2024 (above) | Loans negatively correlated with childbearing (count model), stronger for 2-year-college women. Correlation, one country. |
| First-birth cond. ASFR | no evidence found | Yu 2007 (HECS, [10.1007/bf03031879](https://doi.org/10.1007/bf03031879)); Nau et al. 2015 ([10.1016/j.rssm.2015.05.003](https://doi.org/10.1016/j.rssm.2015.05.003)) | Australia/US; abstracts were empty. |

No study found for: PPR 0→1, Young first births, PPR 1→2+, Second+ cond. ASFR.

Source: [`research/factor-evidence/life-course-and-education-work.md`](https://github.com/andrewgsavage/fertility/blob/main/research/factor-evidence/life-course-and-education-work.md).
