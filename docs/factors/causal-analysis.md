# Causal analysis of the factors

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

The [factors table](index.md) lists what has been proposed. This page asks a harder question: for each factor, is there evidence that it *causes* lower fertility, and at which stage? It is based on abstract-level reading of the studies collected for the table (full texts were not read), so treat the grades as a first pass.

## Why correlation is not enough here

Four problems recur across the factors.

1. **Timing versus quantum.** Most studies measure period birth rates or hazards. A factor that delays births lowers those rates without lowering completed family size. Only the parity progression columns (PPR 0→1, PPR 1→2+) are about final levels, and they are rarely tested directly.
2. **Reverse causation.** People who want children soon choose housing, partners and jobs differently. Fertility intentions can cause the factor, not the reverse.
3. **Selection and confounding.** Education, region, cohort and cultural background all shift both the factor and fertility. Urbanisation, secularisation and female employment move together over the same decades.
4. **Feedback.** Low fertility feeds back into [politics](../democracy/index.md) and into [ideal family size](../owid/the-low-fertility-trap.md), so some "causes" are also consequences.

## Causal structure

The graph in the [factor influence graph](../_static/factor-graph.html) implies three layers:

- **Upstream factors** (planning rules, urbanisation, secularisation, technology, welfare state) act mostly through other factors.
- **Mediating factors** (house prices, education, employment, partnership formation, age at first birth) act on the two conditional rates.
- **Outcomes**: first-birth and second+ conditional ASFR, which combine into TFR.

Mediation matters for interpretation. A study that controls for income when estimating the effect of house prices removes part of the causal path, and a study that does not control for it mixes in the effect of whatever drives both. Neither estimate is "the" effect of housing.

## Strength of evidence

Grades describe the research design, not the size of the effect. Every study found for a factor is listed below, including weak designs and studies that cut against the tick, because a factor with one quasi-experiment and five correlations reads differently from one with only the quasi-experiment.

- **A**: quasi-experiment or natural experiment (policy reform, birth-date cut-off, law change).
- **B**: panel or register data with fixed effects or a potential-outcomes design. Controls for stable confounders but not for reverse causation.
- **C**: correlation, aggregate time series, cross-country comparison or simulation.
- **T**: theory, review or commentary with no test of its own.

Direction: **+** supports the factor lowering fertility, **−** contradicts it, **~** mixed or conditional. It is read against the tick for that factor in the table, so "+" for parental leave means leave raises second births.

| Factor | Grades found | Net reading |
|---|---|---|
| Education | A, C | Delays first birth; no effect on completed fertility in the one quasi-experiment. |
| Parental leave | A, T | Raises second births in Austria; weaker or temporary elsewhere. |
| Child benefits | A, B | Cuts lower births; benefits raise higher-order births. |
| Childcare provision | A, C | Positive for first births in Germany; limited elsewhere. |
| Contraception, abortion | A, C | Access lowers young births; permanence not read. |
| Sex education, teen campaigns | C | Weak or wrong-signed. |
| Job insecurity | A, B | Delays first births; one contrary quasi-experiment. |
| House prices | B, C | Lower young first births; sign depends on tenure. |
| Economic uncertainty | B, C | Fertility falls with unemployment and uncertainty; not uniform across measures. |
| Female employment | C | Negative in aggregate; depends on country. |
| Intensive parenting | B, C, T | Inconsistent. |
| Income, rents, home size, childcare costs, cost of raising children | B, C | Mixed or model-based. |
| Female age-related infertility | C | Simulation only. |
| Pensions | A, C | Quasi-experiment is in Namibia, a high-fertility setting. |
| Urbanisation, child mortality | C | Developing-country evidence, not the housing-cost mechanism. |
| Leaving home, partnership formation, student debt, sperm counts, social media, smartphones, political divide, planning rules | none readable | No causal test found, or abstracts were truncated. |

### Life course and education

- **Education.** A (+, timing only): in a Swedish school cut-off, an 11-month later graduation delays first birth by about 5 months and does not change completed fertility ([Skirbekk 2004](https://doi.org/10.1353/dem.2004.0028)). C (+): cohort childlessness is higher among the more educated in every UK country ([Kuang 2024](https://doi.org/10.4054/demres.2024.51.36)); 40–50% of the fall in cumulated fertility at 25 in Belgian cohorts is attributable to rising education ([Neels 2010](https://doi.org/10.1553/populationyearbook2010s77)). C (~): the childlessness gradient is narrowing or reversing in Finland and Sweden ([Jalovaara 2021](https://doi.org/10.1080/00324728.2021.1887506)), and second-birth risks are higher for educated women in West Germany and France ([Köppen 2006](https://doi.org/10.4054/demres.2006.14.14)).
- **Age at first birth.** A (−): the same Swedish cut-off finds the delay persists into second births but completed fertility is unaffected. C (~): the effect on second births is mediated by education and childcare enrolment across 23 countries ([Van Bavel 2010](https://doi.org/10.1553/populationyearbook2010s107)).
- **Partnership stability.** C (~): French microsimulation shows smaller families after first-union dissolution, largely closed by repartnering ([Thomson 2012](https://doi.org/10.1007/s13524-011-0085-5)). The Finnish and Austrian studies had no readable result.
- **Female age-related infertility.** C (+): a Monte Carlo model puts live birth within a year of trying at 75% at 30, 66% at 35 and 44% at 40 ([Léridon 2004](https://doi.org/10.1093/humrep/deh304)). Observed fecundability cohorts were not readable.
- **Falling sperm counts.** C (~): declines are reported in some places and contested elsewhere ([Mendiola 2013](https://doi.org/10.1111/j.2047-2927.2012.00058.x), [Jouannet 2001](https://doi.org/10.1034/j.1600-0463.2001.090502.x)). No study found links them to birth rates.
- **Student debt.** C (~): Japanese women at two-year colleges with loans are more likely to delay marriage ([Wang 2024](https://doi.org/10.1080/03075079.2024.2307972)). One country, correlation.

### Education and work

- **Job insecurity.** B (+): casual and fixed-term work lower first-birth likelihood, with lower wages mediating much of it ([Laß 2025](https://doi.org/10.1215/00703370-12234731)); uncertain first jobs account for about 7% of Italian women's first-birth postponement ([Vignoli 2019](https://doi.org/10.1016/j.alcr.2019.100308)); Spanish temporary contracts correlate with fewer first births ([Guner 2024](https://doi.org/10.1111/iere.12708)). B (~): Finnish unemployment delays first births, but not for young low-educated women or men ([Miettinen 2019](https://doi.org/10.1016/j.alcr.2019.100320)). A (−): Swedish vocational-school women graduating into a deep recession married and had children earlier ([Engdahl 2022](https://doi.org/10.3368/jhr.1220-11387r1)).
- **Left-behind young men.** B (+): Norwegian register data link unemployment to fewer births for childless men and women ([Kristensen 2022](https://doi.org/10.4054/demres.2022.46.35)); stable employment promotes parenthood in Finland, more for men ([Jalovaara 2025](https://doi.org/10.1177/00016993251403380)), though that paper's title argues weaker labour status is unlikely to drive the cohort decline.
- **Female employment.** C (+): negatively correlated with TFR in every region of a global panel ([Behrman 2020](https://doi.org/10.4054/demres.2020.43.25)). C (~): employment conflicts with childbearing in Italy but not Poland ([Matysiak 2013](https://doi.org/10.1007/s10680-013-9287-4)); the cross-country link turned positive in developed countries in the mid-1980s, and whether that is spurious is debated.
- **Motherhood earnings penalty.** B (~): Austrian administrative data show delaying motherhood changes earnings only a little ([Bíró 2026](https://doi.org/10.1007/s00148-026-01189-5)), so postponing buys little.
- **Long working hours.** B: French fixed-effects data show nonstandard schedules, especially night work, lower the chance of a first child ([Lambert 2023](https://doi.org/10.1177/0192513x221150975)). That is a different exposure from long hours, but it hints that the first-birth cell in the table may be missing a tick.

### Costs and housing

- **House prices and ownership.** B (+): Belgian municipality fixed effects show lower first-birth hazards at 18–34 ([Wood & Maes 2026](https://doi.org/10.4054/demres.2026.55.19)); Dutch register data show lower conception risk and widening tenure gaps ([van Wijk & Feijten 2025](https://doi.org/10.1007/s10680-025-09754-6)). B (~): English owners' fertility rises 2.4% per 10% price rise while renters do not respond ([Washbrook](https://www.bristol.ac.uk/cmm/research/housing/publications/do-high-prices-deter-fertility.html)); a Canadian panel's theory is negative for renters and ambiguous for owners ([Clark & Ferrer 2019](https://doi.org/10.5018/economics-ejournal.ja.2019-38)). C (+): a Hong Kong aggregate series ([Yi & Zhang 2010](https://doi.org/10.1111/j.1465-7295.2009.00213.x)). C (−): a US aggregate VAR finds a positive effect ([Affuso 2022](https://doi.org/10.3390/jrfm15090403)).
- **Rents.** B (~): no clear relation between housing spending and births among UK renters ([Buh 2026](https://doi.org/10.1007/s10680-026-09778-6)); renters show delayed negative responses in the English data above.
- **Home size.** B/C (~): UK owners' higher housing expenditure is linked to second and third births, but that is expenditure, not size; Finnish fertility varies by housing type ([Kulu & Vikat 2007](https://doi.org/10.4054/demres.2007.17.26)).
- **Childcare costs.** C (~): higher US childcare costs lower births for non-employed women but not employed women ([Blau & Robins 1989](https://doi.org/10.2307/2061526)).
- **Cost of raising children.** C (~): a birth lowers subjective economic wellbeing, mainly via direct costs ([Spitzer 2021](https://doi.org/10.1553/0x003ccd30)); rising income prerequisites for a first child, rather than uncertainty, may explain postponement ([van Wijk & Billari 2024](https://doi.org/10.1111/padr.12624)).
- **Income level.** C (~): a calibrated model puts about 2.5% of US women childless from poverty and 8.1% from the opportunity cost of childrearing ([Baudin 2015](https://doi.org/10.1257/aer.20120926)); theory predicts a negative aggregate link via education but a positive link within an education level ([Strulik 2024](https://doi.org/10.1007/s00148-024-01017-8)). C (−): US data for 1850–2000 show no robust income link, with schooling explaining about 60% of the decline ([Hansen 2017](https://doi.org/10.1017/s136510051600081x)).
- **Economic uncertainty.** B (+): in 251 EU regions the fertility decline is strongly related to the rise in unemployment ([Matysiak 2020](https://doi.org/10.1553/0x003ccd44)); age-, parity- and education-specific rates respond in 31 countries plus the US ([Comolli 2017](https://doi.org/10.4054/demres.2017.36.51)). C (+): in 126 countries a higher World Uncertainty Index lowers fertility ([Gözgör 2021](https://doi.org/10.1086/715020)). C (~): perceived uncertainty is not consistently associated with postponement (van Wijk & Billari 2024); labour-market polarisation prolongs the decline ([Seltzer 2019](https://doi.org/10.1007/s13524-019-00790-6)).

### Policy and the state

- **Parental leave.** A (+): the Austrian 1990 extension from 1 to 2 years raised second births ([Lalive & Zweimüller 2009](https://doi.org/10.1162/qjec.2009.124.3.1363)). A (~): Estonia's reform accelerated second and third births, with the quantum result not read ([Puur & Abdullayev 2023](https://doi.org/10.1007/s10680-023-09669-0)); a fathers' quota had no effect in Norway and a temporary third-birth effect for lower-income Swedish couples ([Duvander & Lappegård 2020](https://doi.org/10.1007/s11113-020-09574-y)). T: a review frames the policy effect as limited ([Gauthier & Gietel-Basten 2024](https://doi.org/10.1111/padr.12691)).
- **Child benefits.** A/B (+): an 18% household income cut for German welfare families lowered births 6.8% ([Sandner & Wiynck 2023](https://doi.org/10.1007/s11113-023-09757-3)); a cash benefit for families with 4+ children raised births in a quasi-experiment ([Lyssiotou 2021](https://doi.org/10.1515/bejeap-2020-0165)).
- **Childcare provision.** A (+): county-level childcare expansion raised first-birth transitions 11.9% among native childless couples in the labour force ([Schuß & Azaouagh 2022](https://doi.org/10.1111/boer.12367)). C (~): limited, positive short-term effects in Italian regions, plus a review ([Scherer & Pavolini 2023](https://doi.org/10.1186/s41118-023-00208-7)); childcare services matter for the second-child transition across Europe ([d'Albis & Gobbi 2017](https://doi.org/10.1017/dem.2017.2)).
- **Pensions and welfare state.** A (+): Namibian social pensions substantially reduced fertility, mostly late in reproductive life ([Rossi & Godard 2022](https://doi.org/10.1257/pol.20200466)). C (+): a strong cross-country correlation between government pensions and lower fertility ([Boldrín & De Nardi 2005](https://doi.org/10.1017/dem.2014.14)).

### Social, cultural and population

- **Contraception.** A (+): Swedish teen fertility responds strongly to pill access ([Ragan 2025](https://doi.org/10.1093/ej/ueaf017)). A (~): US state laws on marital pill access raised the nonmarital birth rate 15–18% ([Beauchamp 2019](https://doi.org/10.1111/ecin.12757)). T: the Finnish history calls the pill's significance "ambiguous" ([Pasila 2011](https://doi.org/10.23979/fypr.45065)).
- **Abortion.** A (+): US legalisation lowered fertility about 4% ([Levine 1996](https://doi.org/10.2105/ajph.89.2.199)); 19th-century restrictions raised birth rates 4–12% ([Lahey 2014](https://doi.org/10.1007/s13524-014-0293-x)); legalisation contributed to lower teen out-of-wedlock births ([Donohue 2009](https://doi.org/10.1093/aler/ahp006)). A (~): the delay-versus-permanence question was posed but the result not read ([Ananat 2007](https://doi.org/10.3368/jhr.xlii.2.375)). T: a world time series sets out two opposing predictions ([Fernández 2023](https://doi.org/10.1007/s10680-023-09687-y)).
- **Sex education and teen campaigns.** C (−): a cross-country panel links mandates to higher teen fertility, with opt-out laws possibly limiting this ([Paton 2020](https://doi.org/10.1002/hec.4021)). C (~): promotion of long-acting contraception has a negative but small and insignificant effect on teen pregnancy in English regions ([Girma 2015](https://doi.org/10.1016/j.socscimed.2015.02.040)); England's rates fell more than 50% from 1998 to 2014, with attribution not read ([Baxter 2021](https://doi.org/10.1016/j.socscimed.2021.113685)).
- **Low fertility awareness.** C (~): an online tool raised knowledge and shifted ideal timing, with no birth outcomes ([Daniluk 2014](https://doi.org/10.1093/humrep/deu328)); childless people in Portugal were poorly informed, with the link to intentions not read.
- **Secularisation.** B (+): Finnish registers show a self-reinforcing negative effect via church membership ([Schubert 2026](https://doi.org/10.1016/j.ssresearch.2026.103371)).
- **Gender equality at home.** C (~): Spanish and Nordic studies test attitudes and intentions, not completed births, and both abstracts were truncated before results.
- **Ideal family size.** C (~): ideals remain centred on two children, and the gap is between ideals and intentions ([Brinton 2018](https://doi.org/10.1111/padr.12128)); the intended-versus-completed gap was not read ([Beaujouan 2019](https://doi.org/10.1007/s11113-019-09516-3)).
- **Intensive parenting norms.** B (+): fatherhood norms lower the transition to a first birth among German childless men ([Ruckdeschel 2024](https://doi.org/10.1177/0192513x241227872)). T (+): a theory of comparison motives ([Mahler 2025](https://doi.org/10.1353/eca.2025.a994511)). C (−): US women who breastfeed for 5+ months, a proxy for intensive parenting, have more children, with selection into the behaviour ([Maralani 2018](https://doi.org/10.1007/s13524-018-0710-7)).
- **Dating apps.** C (−): meeting online does not predict breakup and predicts faster transitions to marriage, but only among couples that form ([Rosenfeld 2017](https://doi.org/10.15195/v4.a20)).
- **Urbanisation.** C (+): lower urban fertility in 60 developing countries ([Lerch 2018](https://doi.org/10.1111/padr.12220)), coastal Ghana ([White 2008](https://doi.org/10.1353/dem.0.0035)) and The Gambia ([Adebowale 2024](https://doi.org/10.25133/jpssv332025.011)). All developing-country evidence, not the housing-cost mechanism.
- **Child mortality decline.** C (~): a health innovation that cut mortality led to delayed childbearing and lower fertility and marriage ([Bhalotra 2023](https://doi.org/10.1093/jeea/jvac072)); a review finds mixed evidence for a fertility–survival trade-off ([Lawson 2012](https://doi.org/10.1098/rspb.2012.1635)).
- **Population ageing and politics.** C/T (~): older respondents are less supportive of family transfers, and ageing electorates favour pensions, but the effect on births is not tested.

## What the evidence supports

**Well identified, but mostly about timing.** The best designs (education cut-offs, leave reforms, benefit cuts, contraception and abortion law) show that policies and institutions move births. The education result is the clearest example of a delay with no change in completed fertility.

**Few designs reach completed fertility.** Almost no study in the set tests whether a factor lowers the proportion of women who ever become mothers or who have a second child. That is where the final TFR is decided, so the strongest causal claims in the table are about the wrong quantity for a long-run decline.

**Postponement is the linking mechanism, not a cause on its own.** The chain is: a factor delays first births (well supported for education, job insecurity and house prices), and biological decline with age converts some of the delay into permanent childlessness or smaller families (supported by simulation, not by observed cohorts). This predicts that factors acting at young ages matter most when recovery at older ages is weakest. The table's "Young first births" column marks these factors, but the recovery question is open.

**The weakest-evidenced factors are the most talked about.** Technology and social-media explanations have the least causal evidence in the set, since they have no policy or institutional variation to exploit.

## Gaps

- Link each factor to **completed cohort outcomes** (childlessness, second births by age 45), not only to rates. Cohort data from the [Human Fertility Database](../hfd/index.md) and UK administrative data could do this for factors with regional or cohort variation, such as housing and education.
- Separate the **tenure effect in housing**: owners and renters respond with opposite signs, so a pooled estimate hides both.
- Test **mediation explicitly** (for example, how much of the education effect runs through partnership formation versus age at first birth).
- Quantify **how much postponement becomes permanent**, by factor, using cohorts old enough to have finished childbearing.
- Check the abstract-only readings against full texts, especially the "mixed" and "no evidence found" verdicts, many of which come from truncated abstracts.
