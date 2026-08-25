# Births per Mother vs Age of First Birth

[First vs Second Birth](first-vs-second-birth) shows that the global fertility decline is driven almost entirely by falling first-birth rates in younger women, while later first births and second-birth rates have stayed comparatively stable. That raises an obvious follow-up: for a woman who does become a mother, does having that first child later mean going on to have fewer children overall?

The charts below answer that directly: for each age X, what is the expected total number of children for a woman whose *first* birth happens at exactly that age? This is a conditional expectation, not a cohort average — it isolates the effect of first-birth timing itself from everything else that differs between cohorts. Each line is one birth cohort (women born in a given year); it's computed by taking that cohort's own age-specific parity-progression rates (the probability of having a 2nd, 3rd, 4th, ... child at a given age, given the number of children she has so far) and working backwards from the end of the fertile window: at each age, folding in the chance of moving up one more parity before running out of childbearing years. A woman whose first child arrives young has many more years left in which a second, third, or fourth might follow — which is exactly why every line below slopes downward.

```{region-tabs} births_per_mother_region Expected total children given first birth at that age, {region}
```

In almost every country, the lines slope down steeply and consistently — a first birth at 20 implies roughly twice the eventual family size of a first birth at 35, in cohort after cohort. This holds whether cohorts are compared to each other (older, greener lines vs. younger, redder ones sit at similar levels almost everywhere) or looked at individually: the shape isn't a cross-cohort average effect, it's there within essentially every single cohort's own data.

Belgium, Croatia, and South Korea show no lines at all, and Switzerland only one: HFD's birth-order-specific data for those countries only starts in the mid-to-late 2000s, so none of their tracked cohorts are old enough yet for this page's terminal-age assumption (see the note below) to be safe.

This still doesn't establish that delay itself *causes* smaller families — a woman's fertility intentions, partner situation, and biology at the time of her first birth plausibly shape both when it happens and how many children follow. But it does mean that, mechanically, later first births leave less runway for the additional children that would otherwise have followed — and the data confirms that runway is not being fully made up for elsewhere in the fertile window.

## How accurate is this estimate?

HFD only publishes *estimated* cohort parity-progression hazards (cft.txt), so there's no measured cohort data to check the chart above against directly. But the same recursion can run on HFD's *period* fertility tables instead, which come in two versions: one built the same estimated way as cft.txt (pft.txt), and one measured directly from each country's population register (pftc.txt — the processed output of the underlying age-and-parity data). Comparing the two, year by year, isolates the estimation method itself.

Only five HFD countries have continuous, multi-decade register coverage in pftc.txt rather than isolated census years: Denmark, Finland, Hungary, Norway, and Sweden. For all five, the estimated and register-measured curves are nearly indistinguishable at every age:

```{image} /_static/hfd/births_per_mother_validation.png
:alt: Estimated (pft.txt) vs register-measured (pftc.txt) expected children by age of first birth, for Denmark, Finland, Hungary, Norway, and Sweden
:width: 100%
```

```{note}
Dashed = HFD's estimation method (pft.txt), applied per calendar year rather than per cohort. Solid = the same recursion run on register-measured parity data (pftc.txt). Every 10th available year shown per country.

Mean absolute error across every (year, age) cell, ages 18-39: 0.006-0.010 children, against a range of roughly 1.0-3.0 — noise-level given the underlying rates are estimates to begin with. Hungary's lines look noisier above only because its fertility swung more over 1970-2020 than the Nordic countries', spreading its year-to-year lines further apart; its estimation error (MAE 0.008) is in the same range as the others. The single largest discrepancy in any country/year/age cell is 0.12 children (Sweden, 2018, age 18), a low-birth-count cell — few Swedish women have a first child at 18 — where noise in the rarer 4th/5th-birth hazards compounds through the recursion.
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Each line uses HFD's cohort fertility tables (cft.txt), which give, for a cohort at each age, the discrete probability of a 2nd/3rd/4th/5th+ birth conditional on already having exactly 1/2/3/4 children. Starting from the oldest tracked age and working down to each age X, a backward recursion folds in that age's chance of progressing one more parity, giving the expected total number of children for a woman at parity 1 (i.e. who just had her first birth) at that age. A woman who reaches "5th or higher order" is approximated as ending on exactly 5 — a small undercount for the shrinking few who go on to a 6th+.

Since a cohort with no data past some age is otherwise indistinguishable from one that has genuinely finished having children, only cohorts whose tracked data reaches age 40 are shown — younger cohorts are excluded rather than silently understating their eventual family size.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

HFD has no cohort parity-progression life tables for the UK, so the UK data is
reconstructed from this data: at each age, the cumulative % of the cohort with >=1 / >=2
/ >=3 / >=4 children is differenced against the previous age to get the same kind of
discrete parity-progression hazard used for the HFD countries, up to fourth birth (Table
3's top bucket is "4 or more", approximated as exactly 4 — a coarser cutoff than HFD's
5+, since ONS's source table doesn't split any further).
```
