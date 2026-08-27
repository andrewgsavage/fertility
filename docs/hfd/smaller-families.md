# Smaller Families?

In many countries the average family size is decreasing; there are increasingly more single child families. This is often described as a preference for fewer children. However this does not account for the first child being born later.

If there was a preference for fewer children, the total number of children should decrease when controlling for the age of her first birth. This is not seen when plotting the expected number of children against the age of first birth.

This suggests women who desire multiple children are having their first child later.

```{region-tabs} births_per_mother_region Expected total children given first birth at that age, {region}
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Backward recursion over each cohort's own parity-progression hazards (cft.txt: q2x-q5px),
giving expected total children for a woman at parity 1 at each age. 5th-or-higher order
approximated as exactly 5. Only cohorts whose tracked data reaches age 45 are shown.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

UK column reconstructed from Table 3 (HFD has no UK parity-progression tables): cumulative
% of the cohort with >=1/2/3/4 children, differenced by age into the same kind of discrete
hazard, capped at 4+ (coarser than HFD's 5+).
```

## Comparison to published research

Roustaei et al. (2019) found the same pattern in Finnish population-register data: completed fertility around 3 children for a first birth before age 21, falling to about 2 (replacement level) by age 30.

```{image} /_static/hfd/finland_paper_comparison.png
:alt: HFD-derived expected children by age of first birth for Finland (1967-1978 birth cohorts) overlaid on Roustaei et al. 2019's completed fertility curves for women whose first birth was in 1987-91, 1992-96, 1997-01, or 2002-06
:width: 60%
```

```{note}
Roustaei Z, Räisänen S, Gissler M, Heinonen S. "Fertility rates and the postponement of
first births: a descriptive study with Finnish population data." BMJ Open 2019;9:e026336.
Available at [bmjopen.bmj.com](https://bmjopen.bmj.com/content/9/1/e026336). Four periods
digitized from panel B of the paper's [online supplementary
figure](https://pmc.ncbi.nlm.nih.gov/articles/instance/6340426/bin/bmjopen-2018-026336supp001.pdf),
which extends the main text's Figure 2B (1987-91 and 1992-96 only) to two further 5-year
periods.

The two curves aren't the same kind of measurement. HFD's is a modeled expected value: it
chains each cohort's own age-specific parity-progression hazards together, assuming a
woman's chance of a 2nd birth, 3rd birth, etc. can be treated as independent probabilities
at each age. The paper's, from Finland's individually-linked Medical Birth Register, is
presumably a direct empirical average — the actual completed number of children real women
had, tracked to today via personal identifiers, no chaining of rates required. The two also
group cohorts differently (HFD by the mother's own birth year, the paper by the calendar
year her first birth occurred). That a rate-based model and a direct headcount land on the
same shape and range is itself a useful check on the hazard-independence assumption the
recursion relies on.
```

Beaujouan, Zeman & Nathan (2023) found the same pattern directly from survey and census birth histories across ten high-income countries, for mothers' completed fertility conditional on age at first birth.

```{image} /_static/hfd/beaujouan_paper_comparison.png
:alt: HFD-derived expected children by age of first birth overlaid on Beaujouan, Zeman & Nathan 2023's completed cohort fertility by age at first birth, for Austria, Netherlands, Norway, Poland, Sweden, United States and Great Britain
:width: 100%
```

```{note}
Beaujouan É, Zeman K, Nathan M. "Delayed first births and completed fertility across the
1940–1969 birth cohorts." Demographic Research 2023;48(15):387-420. Available at
[demographic-research.org](https://www.demographic-research.org/volumes/vol48/15/). Values
for the seven countries shown are taken directly from the paper's supplementary Excel file
(one sheet per country), not digitized from Figure 3 — France, Italy and Switzerland are
also in the paper but aren't in HFD's cft.txt. Age bins (15-19 .. 35-39) plotted at their
midpoint; the paper's own 40-44 bin is dropped, as its completed fertility mostly sits at
its definitional floor of 1 child and adds noise rather than signal.
```

Andersson (2008), reprinted in Schmidt et al. (2012)'s review of postponement research, shows the same pattern going back further for Sweden — cohorts born 1935-39 and 1950-54, predating HFD's own Swedish coverage (which starts at the 1955 cohort), so there's no HFD line to overlay here.

```{image} /_static/hfd/andersson_sweden_paper_comparison.png
:alt: Completed fertility rate by age at first birth for Swedish women born 1935-39 and 1950-54, digitized from Schmidt et al. 2012's Figure 4
:width: 60%
```

```{note}
Schmidt L, Sobotka T, Bentzen JG, Nyboe Andersen A. "Demographic and medical consequences
of the postponement of parenthood." Human Reproduction Update 2012;18(1):29-43. Original
data source: Andersson G (2008), Table 12d. Digitized by eye from Figure 4.
```

## Estimated across all countries, period basis

Same recursion applied to HFD's period fertility tables (pft.txt: q2x-q5px) per calendar year instead of per birth cohort, for every HFD country.

```{region-tabs} births_per_mother_estimated_region Estimated expected total children given first birth at that age (period basis), {region}
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

UK excluded: no HFD period fertility table exists for it.
```

## How accurate is this estimate?

Same recursion run per calendar year on HFD's period fertility tables: an estimated version (pft.txt) and, for the five countries with continuous population-register coverage, a version measured directly from register data (pftc.txt).

```{image} /_static/hfd/births_per_mother_accuracy.png
:alt: Estimated (pft.txt, dashed) vs register-measured (pftc.txt, solid) expected children by age of first birth, for Denmark, Finland, Hungary, Norway, and Sweden
:width: 100%
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Mean absolute error across every (year, age 18-44) cell: 0.005-0.008 children, against a range of roughly 1.0-3.0.
```
