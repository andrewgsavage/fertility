# Coupling by local authority

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Share of women living in a couple (married, civil partnership or cohabiting) in each local authority district (LAD) of England and Wales at the 2021 Census, set against the same LAD's age-specific fertility rate (ASFR) for 2021. National trends are on [Coupling over time](../factors/coupling-trends.md) and [Coupling and motherhood](../factors/coupling-vs-mothers.md); the LAD fertility data is the same as on the [map](fertility-map.md) and [scatter](scatter.md) pages.

## Findings

- Across 317 LADs, coupling share explains 26% of the variation in ASFR at 25–29 (r = 0.51) and 34% at 30–34 (r = 0.58). Each extra point of coupling goes with about 1.5 more births per 1,000 women at both ages.
- At 25–29 the link is mostly inner London. Leaving out the 33 London boroughs, r falls to 0.23 (n = 284) and the rank correlation to 0.16. At 30–34 it holds outside London (r = 0.56, n = 284).
- Births per coupled woman (ASFR divided by coupling share) is barely more uniform than ASFR. Its coefficient of variation across LADs is 0.217 against 0.222 for ASFR at 25–29, and 0.123 against 0.151 at 30–34. In log terms, coupling share accounts for 20% of the variance in ASFR at 25–29 and 38% at 30–34; births per coupled woman accounts for 70% and 65% (the rest is their covariance).
- Births per coupled woman at 25–29 ranges from 55 per 1,000 in Wandsworth and 68 in Cambridge to 267 in Oldham and 266 in Barking and Dagenham (10th–90th percentile 127–209). Inner London has both the fewest couples and the fewest births per couple at that age.
- Between the 2011 and 2021 censuses the share of women in a couple fell in 297 of 317 LADs at 25–29 (pooled 53.9% to 49.6%) and in 282 at 30–34 (66.4% to 64.3%). The largest falls at 25–29 were Slough (−14.0 points), Sandwell (−11.5), Broxbourne and Thurrock (−11.4 each). LADs where coupling fell more did not see bigger falls in ASFR from 2013 to 2021 (r = 0.09 at 25–29, 0.04 at 30–34).

## Coupling vs ASFR, 2021

```{raw} html
<iframe src="../_static/ons/coupling_vs_asfr_lad_ew.html" style="width: 100%; height: 560px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

Outliers (more than 2.5 standard deviations from the fitted line) at 25–29: City of London (ASFR 8.7, 556 women in the age group in households), Wandsworth, Warwick and Cambridge below the line, Oldham above. At 30–34 the outliers are all above the line, in the commuter belt around London (Tandridge, Epping Forest, Brentwood, Hertsmere, Elmbridge, Sevenoaks). Dropping them changes r by less than 0.02.

University towns are low on both axes at 25–29 but do not drive the fit. Oxford (38% coupled) and Cambridge (40%) have the lowest coupling outside London; Cambridge and Warwick (ASFR 51 at 57% coupled) are below the line, likely from postgraduate students, and Oxford's residual is −1.8. At 30–34 none of the three is an outlier.

```{note}
Coupling: ONS [Census 2021 create-a-custom-dataset API](https://developer.ons.gov.uk/createyourowndataset/), usual residents, living arrangements (11 categories) × age (12 categories) × sex, by lower-tier local authority. In a couple = every "living in a couple" category, including separated people living with a new partner. Household residents only (communal establishments excluded, to match 2011). Census 2021 counts are perturbed for disclosure control; Isles of Scilly is withheld. LADs merged since 2021 (Cumberland, Westmorland and Furness, North Yorkshire, Somerset) are summed to April 2023 boundaries.

Fertility: ONS [births and fertility rates by local authority](https://www.nomisweb.co.uk/datasets/lebirthrates) (Nomis), 2021, births per 1,000 women using mid-year population estimates. Unweighted: each LAD counts once.
```

## Births per coupled woman

```{raw} html
<iframe src="../_static/ons/births_per_coupled_lad_ew.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Same sources as above. Births per coupled woman = 2021 ASFR ÷ Census 2021 share of women in a couple; it assumes all births are to women in a couple, so it overstates within-couple fertility where births outside co-residential couples are common.
```

## Change, 2011 to 2021

```{raw} html
<iframe src="../_static/ons/coupling_change_lad_ew.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

LAD shares are stable relative to each other (r between 2011 and 2021 is 0.90 at 25–29 and 0.94 at 30–34).

```{note}
2011: ONS Census 2011 [DC1108EW living arrangements by sex by age](https://www.nomisweb.co.uk/census/2011/dc1108ew) (Nomis), women in households, local authorities before April 2015, summed to April 2023 boundaries. In a couple = married, civil partnership or cohabiting. 2021: as above. LAD ASFRs start in 2013, so the fertility change compared is 2013–2021, not 2011–2021.
```
