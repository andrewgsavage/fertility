# Education vs Fertility

The ONS and the resolution foundation both mention a 

Did the expansion of UK higher education line up with women having children later — or
not having them at all? 

```{raw} html
<iframe src="../_static/ons/childlessness_by_age_uk.html" style="width: 100%; aspect-ratio: 11 / 6; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```


```{note}
Age Participation Index (API) and Higher Education Initial Participation Rate (HEIPR) are measures of entry to full-time higher education. HEIPR replaced API. These values have been plotted assuming students enter univeristy at 18.
```
## 1965–79 birth cohorts

The dashed vertical lines above mark the 1968 and 1975 birth cohorts, bracketing the
steepest rise in HE participation. For those same cohorts, here's the ASFR / conditional
first- and second-birth / cumulative-birth panel from [Historic Trends](historic-trends).

```{raw} html
<iframe src="../_static/ons/historic_trends_uk_1965_1979.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Childlessness: Office for National Statistics, "Childbearing for women born in different
years, England and Wales", Table 3 (percentage of women by number of live-born children,
by age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

Education, 1950: Times Higher Education, ["Participation rates: now we are
50"](https://www.timeshighereducation.com/features/participation-rates-now-we-are-50/2005873.article).

Education, 1961–1997 (API): digitized from Greenaway & Haynes (2000), ["Age Participation
Index: Funding Universities to Meet National and International
Challenges"](https://www.researchgate.net/publication/246275720), University of
Nottingham, Figure 2 "Age Participation Index (API), 1961-1997".

Education, 1999 and 2001 (API): read from a second, independent chart of the same series
— Whitty, Hayton & Tang (2015), ["Who You Know, What You Know and Knowing the
Ropes"](https://doi.org/10.1002/rev3.3038), *Review of Education* 3(1), Figure 1
"Participation rate (API) for Great Britain (1950-2001)", sourced there to Broeke &
Hamed (2008) — and closely matching the Greenaway & Haynes-derived points through 1997,
a useful cross-check between the two charts.

Education, the 1999/00–2005/06 HEIPR (old methodology): House of Commons Library,
[SN/SG/2630 "Participation in higher
education"](https://dera.ioe.ac.uk/id/eprint/22740/1/SN02630.pdf) (Paul Bolton).

Education, 2006/07–2017/18 HEIPR (new methodology): Department for Education,
["Participation Rates in Higher Education: Academic Years 2006/07–2017/18
(Provisional)"](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/834341/HEIPR_publication_2019.pdf),
September 2019.

The participation measure changed definition twice across the approx./HEIPR range — Age
Participation Index (Great Britain, under-21 entrants) to 2001, then HEIPR (England,
17–30 year olds, old then new methodology) from 1999/00 — so treat that line as
indicative of the overall trend rather than a single consistent metric. It's also
discontinued after 2017/18 here: later years moved to a cohort-based measure (CHEP-25)
not directly comparable to HEIPR — the two segments aren't directly splice-able into
one continuous series. See `ONS/scripts/childlessness_by_age_uk.py` for the full
per-point sourcing.
```
