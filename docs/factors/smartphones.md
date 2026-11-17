# Smartphones

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

**Group:** Social and cultural. Back to the [factors table](index.md).

## Proposed mechanism

Screen time displaces in-person socialising, so young adults meet fewer potential partners.

## Where it acts

Ticks from the [factors table](index.md): ✓ where the mechanism is proposed to act, ? where the evidence is mixed or too thin to keep a tick.

| Coupling | PPR 0→1 | First-birth cond. ASFR | Young first births | PPR 1→2+ | Second+ cond. ASFR |
|:-:|:-:|:-:|:-:|:-:|:-:|
| ✓ | ✓ | ✓ | ✓ |  |  |

## Mobile internet use and young fertility

Share of 16–24-year-olds using a mobile phone or smartphone to access the internet away from home or work (last 3 months), beside births per woman across ages 20–29 (5 × (ASFR 20–24 + ASFR 25–29)). This tests timing only: if smartphones cut young fertility, the fall should start or steepen as adoption passes a threshold. It can't separate smartphones from other changes in the same years.

```{raw} html
<iframe src="../_static/eurostat/smartphone_adoption_timeline.html" style="width: 100%; height: 480px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

| Country | Mobile internet use, 16–24: 2011 | 2013 | 2015 | 2019 | First year ≥50% | Births per woman at 20–29: 2011 | 2019 | Peak year (1985 on) |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| Germany | 30% | 74% | 89% | 95% | 2012 | 0.59 | 0.58 | 2001 |
| France | 42% | 74% | 86% | 94% | 2012 | 0.97 | 0.81 | 2001 |
| Spain | 38% | 81% | 91% | 98% | 2012 | 0.45 | 0.37 | ≤1985 |
| Italy | 24% | 46% | 66% | 80% | 2014 | 0.54 | 0.42 | ≤1985 |
| Sweden | 56% | 84% | 89% | 97% | ≤2011 | 0.80 | 0.69 | 1990 |
| Netherlands | 69% | 89% | 90% | 97% | ≤2011 | 0.72 | 0.57 | ≤1985 |
| Poland | 24% | 47% | 76% | 93% | 2014 | 0.72 | 0.72 | 1991 |
| Hungary | 21% | 47% | 80% | 92% | 2014 | 0.54 | 0.67 | 1990 |
| Czechia | 17% | 49% | 77% | 97% | 2014 | 0.68 | 0.79 | ≤1985 |
| Romania | 6% | 22% | 62% | 92% | 2015 | 0.81 | 0.91 | 1986 |

Peak year is the maximum of the 3-year average of 20–29 fertility from 1985; "≤1985" means the series was already falling at the start of that window.

Adoption was fast and nearly universal: among 28 countries with both years, use by 16–24s was 6–69% in 2011 and 80–98% in 2019. Fertility at 20–29 had peaked before 2000 in all 26 countries with data back to 1985, so the fall predates smartphones. Among those, in the 19 where use passed 50% by 2013, the latest 20–29 peak was 1993. The timing is consistent with a long decline that smartphones joined late, not with a decline that started when they spread.

```{raw} html
<iframe src="../_static/eurostat/smartphone_vs_young_fertility.html" style="width: 100%; height: 520px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

Across 28 countries, a larger rise in mobile internet use between 2011 and 2019 goes with a smaller fall in 20–29 fertility (r = 0.51), the opposite sign to the proposed mechanism. The late adopters (Romania, Bulgaria, Czechia, Hungary) are also where 20–29 fertility recovered after earlier postponement, so adoption speed mostly tracks a catch-up in fertility.

Coverage: Eurostat [isoc_ci_im_i](https://ec.europa.eu/eurostat/databrowser/view/isoc_ci_im_i/default/table) (mobile internet, 2011–2019) and [demo_frate](https://ec.europa.eu/eurostat/databrowser/view/demo_frate/default/table) (fertility rates by age; the UK ends in 2018 and Germany's 2023 value is missing). This series ends in 2019 and measures mobile internet use, not smartphone ownership. Not included: ITU/World Bank mobile subscriptions (phones, not smartphones), Pew ownership surveys, and time-use data on in-person socialising (ATUS, HETUS), which have no consistent multi-country annual series.

## Causal evidence

No study with a readable causal test was found for this factor. See the [causal analysis](causal-analysis.md).

## Studies found

Studies found by searching OpenAlex, read from abstracts only. The verdict says whether the study supports the tick in that column.

| Column | Verdict | Study | Finding |
|---|---|---|---|
| First-birth cond. ASFR | no evidence found | Billari et al. 2019, *Does broadband Internet affect fertility?*, [10.1080/00324728.2019.1584327](https://doi.org/10.1080/00324728.2019.1584327) | Adjacent evidence only (broadband, not smartphones): German panel IV design finds positive effects of broadband availability on fertility of the highly educated (rest truncated). |
| Young first births | no evidence found | Guldi & Herbst 2016, *impact of broadband diffusion on teen fertility decisions*, [10.1007/s00148-016-0605-0](https://doi.org/10.1007/s00148-016-0605-0) | Abstract empty; title only. Broadband, not smartphones. |
| PPR 1→2+ | no evidence found | Kalabikhina 2020, [10.38050/01300105202065](https://doi.org/10.38050/01300105202065) | Adjacent: Russia RLMS 2014-18, broadband use raises fertility of women 25-49 and second+ births are more affected. |
| Second+ cond. ASFR | no evidence found | Kalabikhina 2020 (above) | As above. |

No study found for: Coupling, PPR 0→1.

Source: [`research/factor-evidence/social-cultural-and-population.md`](https://github.com/andrewgsavage/fertility/blob/main/research/factor-evidence/social-cultural-and-population.md).
