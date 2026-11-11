# Explaining the 2010s Drop

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

How much of the fall in UK fertility since 2010 can be explained by applying effect sizes from earlier studies to what actually changed? Each row below takes a published effect, multiplies it by the measured change in England & Wales, and gives the implied change in TFR.

## The drop to explain

England & Wales TFR fell from 1.94 in 2010 to 1.49 in 2022, a drop of 0.45 ([HFD](https://www.humanfertility.org), GBRTENW). ONS reports 1.44 for 2023 and 1.41 for 2024.

| Age | ASFR sum 2010 | ASFR sum 2022 | Change | Share of drop |
|---|--:|--:|--:|--:|
| Under 25 | 0.483 | 0.247 | −0.236 | 52% |
| 25–29 | 0.521 | 0.396 | −0.125 | 28% |
| 30–34 | 0.561 | 0.479 | −0.082 | 18% |
| 35+ | 0.374 | 0.367 | −0.007 | 2% |
| **TFR** | **1.939** | **1.489** | **−0.450** | |

Half the drop is in births under 25. Births at 35+ did not rise to make up for it, so this is not only postponement, at least not yet.

## Pregnancies and abortions

Births can fall because fewer pregnancies happen or because more pregnancies end in abortion. Abortions to England & Wales residents rose from 189,574 in 2010 to 251,377 in 2022 ([DHSC abortion statistics](https://www.gov.uk/government/collections/abortion-statistics-for-england-and-wales)). Births fell from 723,165 to 605,479 ([ONS](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/livebirths); HFD gives the same counts).

| | 2010 | 2022 | Change |
|---|--:|--:|--:|
| Births | 723,165 | 605,479 | −117,686 |
| Abortions | 189,574 | 251,377 | +61,803 |
| Births + abortions | 912,739 | 856,856 | −55,883 |
| Abortions as share of births + abortions | 20.8% | 29.3% | +8.6 points |

About half of the fall in births appears as a rise in abortions, and half as fewer pregnancies in the first place. Miscarriages aren't counted.

As a ceiling: if abortions had stayed at 20.8% of births + abortions, and every extra abortion would otherwise have been a birth, 2022 would have had about 73,000 more births, roughly 0.18 on TFR. The real effect is smaller, since some of those births would have happened later instead. This is the route by which births were lost, not a cause: it says people who became pregnant were more often deciding not to have a child.

## Applying published effects

| Factor | Published effect | UK change, 2010→2022 | Implied change in TFR |
|---|---|---|--:|
| Unemployment | +1 point of unemployment lowers birth rates at every age, most at the youngest: about 0.2% at 15–19 and 0.1% at 20–24 ([Goldstein et al. 2013](https://www.demographic-research.org/volumes/vol29/4/29-4.pdf), Europe 2001–10) | 7.9% → 3.8% (−4.1 points; [ONS MGSX](https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/unemployment/timeseries/mgsx/lms)) | ≈ +0.002 |
| House prices | +$10,000 prices: births +5% among owners, −2.4% among non-owners, net +0.8% at the US average ownership rate, in the current period ([Dettling & Kearney 2014](https://econpapers.repec.org/RePEc:eee:pubeco:v:110:y:2014:i:c:p:82-100), US; the [working paper](https://www.nber.org/papers/w17485) gives +4.5% and −1% per 10% rise). In England & Wales, +2.4% among owners per 10% rise, fading within two years; no positive effect for renters ([Washbrook](https://www.bristol.ac.uk/cmm/research/housing/publications/do-high-prices-deter-fertility.html)) | Median local price-to-earnings ratio 6.6 → 9.0 (+36%) | 0 to +0.1 |
| Two-child limit | Little to no decline in third and later births among low-income families; at most small effects ([Reader, Portes & Patrick 2025](https://doi.org/10.1007/s11113-025-09935-5)) | Introduced April 2017 (about £3,000 a year less per third or later child) | ≈ 0 |
| Child benefit | The average subsidy for an extra child raised fertility 7.8%, with no effect at high incomes ([Cohen, Dehejia & Romanov 2013](https://www.nber.org/papers/w13700), Israel 1999–2005) | Frozen 2011–14 and 2016–20, 1% rises between; eldest-child rate £20.30 → £21.80 a week, a 20% fall in real value ([CPAG](https://cpag.org.uk/sites/default/files/2023-10/Money%20Well%20Spent.pdf)). Withdrawn from families with an earner over £50,000 from 2013 | ≈ −0.03 |
| Childcare and parental leave | Expansions raise births slightly, often only by bringing them forward | 30 funded hours (2017), Shared Parental Leave (2015): both expansions | ≥ 0 |
| **Sum of quantified causes** | | | **−0.03 to +0.1** |

Notes on the rows:

- **Unemployment** explains the dip in birth rates during the 2008–12 recession in harder-hit countries. In the UK, unemployment then fell to its lowest level since the 1970s while fertility kept falling.
- **House prices**: the house-price calculation uses the working-paper figures per 10% rise and assumes half of births are to owners (an assumption, not a measured share): 3.6 × (0.5 × 4.5% − 0.5 × 1%) ≈ +6% births, about +0.1 TFR. The published per-$10,000 figures also give a net rise. Both studies measure short-run effects, which mostly shift timing, so +0.1 overstates the effect. Neither measures the long-run effect of young adults buying later or not at all, which is the more plausible route to fewer births. That effect is unquantified.
- **Two-child limit**: third and later births did fall, but the study finds the policy explains almost none of that.
- **Child benefit**: losing 20% of the subsidy's value, scaled linearly from the Israeli estimate, gives 0.2 × 7.8% ≈ 1.6% fewer births, about −0.03 TFR. This is an upper end: Israeli subsidies were larger relative to income, and the UK withdrawal hit high earners, where the study finds no effect. Cuts to child tax credits and Universal Credit over the same years are not included.
- **Childcare and leave** became more generous over the period, so published effects predict a small rise.

Real wages stagnated over the period, but published income effects on fertility have both signs, so no row is given for income.

## What's left

Applied to what changed in England & Wales, the quantified evidence explains at most about 0.03 of the 0.45 drop, through the cut in child benefit. The other measured factors either moved in the direction that should raise births, or have effects too small to matter.

This matches the US. [Kearney, Levine & Pardue (2022)](https://www.nber.org/papers/w29286) tested state-level economic and policy measures previously shown to affect birth rates and found that none accounted for much of the US decline after 2007. They suggest shifting priorities of more recent cohorts as the explanation.

The candidates left are mostly factors with no published effect size:

- fewer and later partnerships, and what drives them: [left-behind young men](index.md), [dating apps](index.md), the political divide between young men and women;
- smartphones and social media;
- perceived uncertainty about the future, as distinct from measured economic conditions;
- [intensive parenting norms](index.md) and a lower ideal family size;
- long-run housing effects through delayed home ownership.

The two facts above narrow it down. Any explanation has to account for a fall concentrated under 25, with no catch-up at 35+, and for a rising share of pregnancies ending in abortion. Both point to people choosing not to have children now, rather than being unable to.
