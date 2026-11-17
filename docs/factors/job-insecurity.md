# Job insecurity

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

**Group:** Education and work. Back to the [factors table](index.md).

## Proposed mechanism

Temporary contracts and unstable early careers delay partnership and first births (young first births: not for low-educated groups).

## Where it acts

Ticks from the [factors table](index.md): ✓ where the mechanism is proposed to act, ? where the evidence is mixed or too thin to keep a tick.

| Coupling | PPR 0→1 | First-birth cond. ASFR | Young first births | PPR 1→2+ | Second+ cond. ASFR |
|:-:|:-:|:-:|:-:|:-:|:-:|
| ✓ | ✓ | ✓ | ✓ |  |  |

## Temporary contracts among young employees

Temporary employees as a share of all employees aged 15–29, 1995–2025, and against each country's mean age at first birth (slider: year). A high share means more young workers are on fixed-term or agency contracts. It doesn't show that contract type delayed births: countries and years also differ in housing, education length and norms.

```{raw} html
<iframe src="../_static/eurostat/temp_contracts_youth_europe.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{raw} html
<iframe src="../_static/eurostat/temp_contracts_vs_first_birth_age.html" style="width: 100%; height: 540px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

| Country | Temp. share 2000 | 2010 | 2025 | Mean age at first birth 2010 | 2023 |
|---|--:|--:|--:|--:|--:|
| Spain | 55.6% | 45.1% | 33.7% | 29.8 | 31.5 |
| Italy | 19.6% | 33.1% | 36.6% | 30.3 | 31.8 |
| France | 36.3% | 36.3% | 39.2% | | 29.1 |
| Germany | 35.2% | 41.4% | 34.6% | 28.9 | 29.8 |
| Netherlands | 26.3% | 39.4% | 51.1% | 29.2 | 30.4 |
| Poland | 9.4% | 48.0% | 39.1% | 26.5 | 28.4 |
| Portugal | 34.3% | 46.0% | 36.7% | 28.1 | 30.2 |
| Sweden | 32.3% | 42.4% | 34.6% | 28.9 | 30.0 |
| Hungary | 10.4% | 17.6% | 7.5% | 27.7 | 28.8 |

Across countries the two are positively related: correlation 0.63 in 2005 (25 countries), 0.48 in 2015 and 0.50 in 2023 (33 each). Over time within countries the link is weak. Poland's share rose from 9% to 48% between 2000 and 2010 as first-birth age rose from 24.5 to 26.5. But Spain's share fell from 54% in 2015 to 34% in 2025 while its first-birth age rose from 29.8 in 2010 to 31.5 in 2023. The cross-country link may reflect other differences, such as long education or late home-leaving in southern Europe. The 15–29 group includes students working part-time, which inflates the share.

Coverage: Eurostat [temporary employees by age](https://ec.europa.eu/eurostat/databrowser/view/lfsa_etpgan/default/table) (38 countries, 1995–2025, many series start later) and [mean age at first birth](https://ec.europa.eu/eurostat/databrowser/view/demo_find/default/table) (34 countries in the scatter, 1995–2024). Youth unemployment is not shown.

## Causal evidence

From the [causal analysis](causal-analysis.md), graded by research design (A quasi-experiment, B panel or register, C correlation or simulation, T theory):

B (+): casual and fixed-term work lower first-birth likelihood, with lower wages mediating much of it ([Laß 2025](https://doi.org/10.1215/00703370-12234731)); uncertain first jobs account for about 7% of Italian women's first-birth postponement ([Vignoli 2019](https://doi.org/10.1016/j.alcr.2019.100308)); Spanish temporary contracts correlate with fewer first births ([Guner 2024](https://doi.org/10.1111/iere.12708)). B (~): Finnish unemployment delays first births, but not for young low-educated women or men ([Miettinen 2019](https://doi.org/10.1016/j.alcr.2019.100320)). A (−): Swedish vocational-school women graduating into a deep recession married and had children earlier ([Engdahl 2022](https://doi.org/10.3368/jhr.1220-11387r1)).

## Studies found

Studies found by searching OpenAlex, read from abstracts only. The verdict says whether the study supports the tick in that column.

| Column | Verdict | Study | Finding |
|---|---|---|---|
| First-birth cond. ASFR | supports | Laß 2025, [10.1215/00703370-12234731](https://doi.org/10.1215/00703370-12234731) | Panels (HILDA, SOEP, 19 years): casual work (Australia, both sexes) and fixed-term contracts (Germany, women) lower first-birth likelihood; lower wages mediate much of it. |
| First-birth cond. ASFR | supports | Vignoli 2019, *The impact of job uncertainty on first-birth postponement*, [10.1016/j.alcr.2019.100308](https://doi.org/10.1016/j.alcr.2019.100308) | Italy, potential-outcome design: 7% of women's and 5% of men's potential first-birth postponement due to uncertain first jobs. |
| First-birth cond. ASFR | supports | Guner et al. 2024, *Labor market institutions and fertility*, [10.1111/iere.12708](https://doi.org/10.1111/iere.12708) | Spain admin data: temporary contracts correlate with lower first-birth rates; model says reform of duality raises fertility. |
| Young first births | mixed | Miettinen 2019, [10.1016/j.alcr.2019.100320](https://doi.org/10.1016/j.alcr.2019.100320) | Finland register 1988-2009: unemployment delays first births, but not for young low-educated women or men. |
| Young first births | contradicts | Engdahl 2022, *Early Labor Market Prospects and Family Formation*, [10.3368/jhr.1220-11387r1](https://doi.org/10.3368/jhr.1220-11387r1) | Sweden: vocational-school women graduating into a deep recession married and had children earlier, especially low-GPA women (quasi-random). |

No study found for: Coupling, PPR 0→1, PPR 1→2+, Second+ cond. ASFR.

Source: [`research/factor-evidence/life-course-and-education-work.md`](https://github.com/andrewgsavage/fertility/blob/main/research/factor-evidence/life-course-and-education-work.md).

## Proposed tick changes

From a second judging pass over the studies above.

| Column | Current | Recommendation | Confidence | Reason |
|---|:-:|---|---|---|
| Young first births | ✓ | qualify (not for low-educated) | medium | Miettinen 2019 (Finland) and Engdahl 2022 (Sweden): no delay, or earlier births, among young low-educated / vocational women |
