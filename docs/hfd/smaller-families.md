# Smaller Families?

In many countries the average family size is decreasing; there are increasingly more single child families. This is often described as a preference for fewer children. However this does not account for the first child being born later.

If there was a preference for fewer children, the total number of children should decrease when controlling for the age of her first birth. This is not seen when plotting the expected number of children against the age of first birth. This suggests women who desire multiple children are having their first child later.

```{warning}
These charts show estimations, not real data. However they still show overall trends. Comparisons to published data follow.

Most countries do not collect or make data available that shows this. The plots below have been calculated using the conditional probabilities of each birth without information on birth year. This distorts the plot, however the overarching trends remain. 

```



```{raw} html
<iframe src="../_static/hfd/births_per_mother_facet.html" style="width: 100%; height: 870px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Backward recursion over each cohort's own parity-progression hazards (cft.txt: q2x-q5px),
giving expected total children for a woman at parity 1 at each age. 5th-or-higher order
approximated as exactly 5. Only cohorts whose tracked data reaches age 40 are shown.
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

### Europe, Beaujouan, Zeman & Nathan (2023) 

The estimation and published data both show fewer children born to older mothers and give similar numbers. The trends accross cohorts is similar, with the estimation and published data both showing increasing family sizes for older mothers.


```{raw} html
<iframe src="../_static/hfd/beaujouan_paper_comparison.html" style="width: 100%; height: 1350px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Beaujouan É, Zeman K, Nathan M. "Delayed first births and completed fertility across the
1940–1969 birth cohorts." Demographic Research 2023;48(15):387-420. Available at
[demographic-research.org](https://www.demographic-research.org/volumes/vol48/15/). Values
for the seven countries shown are taken directly from the paper's supplementary Excel file
(one sheet per country), not digitized from Figure 3 — France, Italy and Switzerland are
also in the paper but aren't in HFD's cft.txt. Age bins (15-19 .. 40-44) plotted at their
midpoint.
```

Andersson (2008), reprinted in Schmidt et al. (2012)'s review of postponement research, shows the same pattern going back further for Sweden — cohorts born 1935-39 and 1950-54, predating HFD's own Swedish coverage (which starts at the 1955 cohort), so there's no HFD line to overlay here.

```{raw} html
<iframe src="../_static/hfd/andersson_sweden_paper_comparison.html" style="width: 100%; height: 520px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Schmidt L, Sobotka T, Bentzen JG, Nyboe Andersen A. "Demographic and medical consequences
of the postponement of parenthood." Human Reproduction Update 2012;18(1):29-43. Original
data source: Andersson G (2008), Table 12d. Digitized by eye from Figure 4.
```

## Estimated across all countries, period basis

Using calendar periods give similar trends to birth cohorts.

```{raw} html
<iframe src="../_static/hfd/births_per_mother_estimated_facet.html" style="width: 100%; height: 870px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

UK excluded: no HFD period fertility table exists for it.
```


## Comparison to published research

### Finland, Roustaei et al. (2019)

The estimation and published data both show fewer children born to older mothers and give similar numbers. The trends accross periods is similar, with the estimation and published data both showing increasing family sizes for older mothers.

```{raw} html
<iframe src="../_static/hfd/finland_paper_comparison.html" style="width: 100%; height: 480px; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Roustaei Z, Räisänen S, Gissler M, Heinonen S. "Fertility rates and the postponement of
first births: a descriptive study with Finnish population data." BMJ Open 2019;9:e026336.
Available at [bmjopen.bmj.com](https://bmjopen.bmj.com/content/9/1/e026336). Four periods
digitized from panel B of the paper's [online supplementary
figure](https://pmc.ncbi.nlm.nih.gov/articles/instance/6340426/bin/bmjopen-2018-026336supp001.pdf),
which extends the main text's Figure 2B (1987-91 and 1992-96 only) to two further 5-year
periods. The paper groups by first-birth calendar period, so the HFD line for each period
is averaged from HFD's own period-basis recursion (pft.txt) over those same calendar years,
rather than from a birth-cohort grouping that has no real correspondence to it.

The two curves still aren't the same kind of measurement. HFD's is a modeled expected
value: it chains each calendar year's own age-specific parity-progression hazards together,
assuming a woman's chance of a 2nd birth, 3rd birth, etc. can be treated as independent
probabilities at each age. The paper's, from Finland's individually-linked Medical Birth
Register, is presumably a direct empirical average — the actual completed number of
children real women had, tracked to today via personal identifiers, no chaining of rates
required. That a rate-based model and a direct headcount land on the same shape and range
is itself a useful check on the hazard-independence assumption the recursion relies on.
```
