# IVF / ART births by birth order and maternal age — HFD page countries

Scope: the 25 countries on the HFD first-vs-second-birth page (`common/country_names.py`
`COUNTRY_REGIONS`). Researched 2026-11-17.

## Bottom line

- **Birth order is rarely published.** ART registries count treatment *cycles* by the woman's age
  at treatment; they don't record which child the birth is. Birth order appears only where the ART
  register is linked to the birth register (Nordics, US birth certificates) or in one-off studies.
- **Age is widely available** but usually in 3 bands (<35, 35–39, 40+) and by age at
  treatment, not at birth.
- Across every source that splits by parity, **ART births are disproportionately first births**:
  ~60–67% of ART births vs ~37–55% of natural births.

## Best cross-country source with both age and parity

Goisis, Fallesen, Seiz, Salazar, Eremenko, Cozzani (2024), "Educational gradients in the
prevalence of medically assisted reproduction births in a comparative perspective", *Fertility
and Sterility*, [doi:10.1016/j.fertnstert.2024.05.149](https://doi.org/10.1016/j.fertnstert.2024.05.149)
([open PDF](https://discovery.ucl.ac.uk/10192669/1/1-s2.0-S001502822400459X-main.pdf)).
Table 1 gives column % by maternal age and parity for naturally conceived (NC) vs MAR births.
MAR is the **broad** definition (includes IUI/ovulation induction, not just IVF). Samples are
small for ES/UK/FR (survey data; UK n=17,097).

| | DNK | FRA | ESP | UK | USA |
|---|---|---|---|---|---|
| MAR % of all births | 9.1 | 5.5 | 3.8 | 3.4 | 2.0 |
| First-born, % of NC births | 48.3 | 42.1 | 54.5 | 37.2 | 37.4 |
| First-born, % of MAR births | 66.5 | 62.5 | 65.9 | 64.3 | 50.8 |

Derived from Table 1 (my calculation — share of births in each group that are MAR):

| | DNK | FRA | ESP | UK | USA |
|---|---|---|---|---|---|
| First births | 12.1% | 8.0% | 4.6% | 5.7% | 2.7% |
| Second+ births | 6.1% | 3.6% | 2.9% | 2.0% | 1.6% |
| Mother ≤24 | 2.1% | 1.7% | 0.1% | 0.6% | 0.2% |
| 25–29 | 5.4% | 4.6% | 1.0% | 2.7% | 0.9% |
| 30–34 | 9.6% | 6.2% | 3.0% | 3.8% | 2.4% |
| 35–39 | 15.4% | 8.7% | 7.3% | 6.0% | 4.3% |
| 40+ | 27.2% | 11.8% | 15.5% | 8.9% | 9.6% |

So MAR is roughly 1.5–3× as common among first births as later births.

Table 1 samples: Denmark all 2018 births (registers); France perinatal survey 2003/2010/2016
pooled; Spain fertility survey 2018; UK Millennium Cohort Study (births 2000–02, self-report);
US 2019 birth certificates (excl. TN, SC).

### Goisis et al. 2024, Figure 1 — ART share of births, 2000–2019 (digitised)

ART only (in vitro methods), unlike Table 1's broader MAR. Sources per the published caption:
EIM (ART births, Europe), Eurostat (live births), CDC (US). Spain under-reported; Denmark and
Spain include cross-border patients.

UK cross-check against HFEA's own series (2024 trends report, Figure 1 data,
[data/hfea_uk_ivf_births_2014_2024.csv](data/hfea_uk_ivf_births_2014_2024.csv)): 2014 2.52 vs
2.59, 2016 2.74 vs 2.75, 2018 2.99 vs 2.92 — within ~0.1 pp. HFEA continues to 3.24% in 2024
(preliminary). Values extracted from the PDF's vector marker positions, calibrated on
the gridlines, so they are exact to the plot (±0.01 pp), not eyeballed:
[data/goisis2024_fig1_art_share_births.csv](data/goisis2024_fig1_art_share_births.csv).

| Year | Denmark | France | Spain | UK | US |
|---|---|---|---|---|---|
| 2000 | 3.66 | 1.28 | | 1.13 | |
| 2005 | 3.54 | 1.65 | | 1.57 | 1.26 |
| 2010 | 5.87 | 1.98 | 2.76 | 2.11 | 1.54 |
| 2015 | 6.64 | 2.40 | 7.16 | 2.65 | 1.79 |
| 2018 | 5.75 | 2.78 | 9.31 | 2.92 | 2.15 |

Gaps in the series: France 2001, Spain 2000–05 and 2008, US 2000; US also has 2019 (2.24).
Denmark 2018: ART 5.75% vs MAR (incl. IUI) 9.1% in Table 1.

## United States 2024: ART share of births by mother's age and birth order

CDC WONDER, Natality 2016–2024 expanded (D149), 2024 births, grouped by Age of Mother 9 ×
Live Birth Order × Assistive Reproductive Technology × Year. Raw extract (2016–2024):
[data/us_natality_2016_2024_age_order_art.csv](data/us_natality_2016_2024_age_order_art.csv).

- *ART births*: birth-certificate ART = Yes. *Other infertility treatment*: infertility treatment = Yes
  but ART = No (fertility drugs / IUI).
- Denominator: births where the item was reported (ART Yes + No + no infertility treatment).
  Excludes "Not Reported" (~7% of records) and unknown birth order. Cells under 10 are suppressed
  by WONDER and dropped (negligible).
- Birth certificates under-record ART compared with CDC's clinic-based count (NASS), so these
  shares are lower bounds.

**First births**

| Mother's age | ART births | Other infertility tx | Births | ART % | Any infertility tx % |
|---|---|---|---|---|---|
| 15–19 | 10 | 12 | 108,219 | 0.01 | 0.02 |
| 20–24 | 328 | 479 | 326,074 | 0.10 | 0.25 |
| 25–29 | 3,379 | 2,247 | 374,555 | 0.90 | 1.50 |
| 30–34 | 11,918 | 3,754 | 337,133 | 3.54 | 4.65 |
| 35–39 | 12,930 | 2,546 | 141,712 | 9.12 | 10.92 |
| 40–44 | 5,896 | 681 | 28,622 | 20.60 | 22.98 |
| 45–49 | 1,194 | 109 | 2,548 | 46.86 | 51.14 |
| 50+ | 226 | 11 | 390 | 57.95 | 60.77 |
| All ages | 35,881 | 9,839 | 1,320,807 | 2.72 | 3.46 |

**Second and later births**

| Mother's age | ART births | Other infertility tx | Births | ART % | Any infertility tx % |
|---|---|---|---|---|---|
| 15–19 | 0 | 0 | 17,084 | 0.00 | 0.00 |
| 20–24 | 165 | 165 | 235,535 | 0.07 | 0.14 |
| 25–29 | 1,807 | 1,386 | 541,018 | 0.33 | 0.59 |
| 30–34 | 8,287 | 3,126 | 696,420 | 1.19 | 1.64 |
| 35–39 | 13,547 | 2,857 | 438,847 | 3.09 | 3.74 |
| 40–44 | 6,955 | 838 | 103,226 | 6.74 | 7.55 |
| 45–49 | 1,560 | 124 | 6,482 | 24.07 | 25.98 |
| 50+ | 372 | 31 | 697 | 53.37 | 57.82 |
| All ages | 32,693 | 8,527 | 2,039,326 | 1.60 | 2.02 |

At every age from 25 to 44, ART's share of first births is about 3× its share of later births.
Over half of all US ART births in 2024 were first births (35.9k of 68.6k).

### Trend 2016–2024 (ART % of births)

**First births**

| Age | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| <25 | 0.05 | 0.06 | 0.08 | 0.07 | 0.06 | 0.07 | 0.09 | 0.11 | 0.10 |
| 25–29 | 0.64 | 0.68 | 0.71 | 0.67 | 0.64 | 0.70 | 0.79 | 0.83 | 0.90 |
| 30–34 | 2.41 | 2.66 | 2.66 | 2.63 | 2.56 | 2.82 | 3.20 | 3.30 | 3.54 |
| 35–39 | 5.63 | 6.29 | 6.39 | 6.43 | 6.52 | 7.18 | 8.30 | 8.54 | 9.12 |
| 40–44 | 12.74 | 14.27 | 14.92 | 15.34 | 14.94 | 16.50 | 18.68 | 19.49 | 20.60 |
| 45+ | 38.66 | 38.04 | 39.25 | 41.41 | 41.15 | 43.95 | 45.89 | 45.23 | 48.33 |
| All | 1.48 | 1.67 | 1.75 | 1.77 | 1.77 | 2.02 | 2.36 | 2.47 | 2.72 |

**Second and later births**

| Age | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| <25 | 0.03 | 0.04 | 0.04 | 0.05 | 0.05 | 0.05 | 0.06 | 0.08 | 0.07 |
| 25–29 | 0.21 | 0.22 | 0.21 | 0.28 | 0.25 | 0.30 | 0.31 | 0.31 | 0.33 |
| 30–34 | 0.72 | 0.76 | 0.80 | 0.95 | 0.89 | 1.00 | 1.05 | 1.09 | 1.19 |
| 35–39 | 1.62 | 1.76 | 1.87 | 2.19 | 2.16 | 2.42 | 2.71 | 2.79 | 3.09 |
| 40–44 | 3.54 | 3.69 | 4.07 | 4.64 | 4.79 | 5.21 | 5.94 | 6.03 | 6.74 |
| 45+ | 21.31 | 21.49 | 21.92 | 25.28 | 24.54 | 24.53 | 26.29 | 25.97 | 26.91 |
| All | 0.77 | 0.83 | 0.90 | 1.08 | 1.07 | 1.21 | 1.37 | 1.43 | 1.60 |

ART births (count), first / second+: 2016 21.3k / 17.9k; 2019 24.0k / 24.3k; 2024 35.9k / 32.7k.

- ART's share roughly doubled 2016→2024 at every age, for both first and later births. The
  overall share grew partly because mothers got older, but the within-age rise is most of it.
- The first:later ratio is steady at ~3× within ages 30–44, so ART growth isn't concentrated in
  first births.
- Reporting coverage varies: "Not Reported" was ~4% of records in 2016–19, ~0.2% in 2022–23 and
  7.1% in 2024. Which states move in and out of reporting can shift year-to-year values a little,
  so read the 2021→2022 step and the 2024 values with that in mind.

## By country

| Country | Order | Age | What exists | Source |
|---|---|---|---|---|
| Norway | ✔ | ✔ | 1985–2014 register: ART share of births 6.8% at 35–39 vs 1.9% at 25–29 (2010–14). First births = 62.9% of ART births vs 43.1% of natural (2010–14); 73.2% vs 44.1% in 1985–89. Chanfreau et al. (2025) compute ART TFR from 32 years of registers. | [Goisis et al. 2020, Hum Reprod](https://pmc.ncbi.nlm.nih.gov/articles/PMC7316497); [Chanfreau, Goisis, Kravdal 2025, PDR](https://doi.org/10.1111/padr.70009) |
| Denmark | ✔ | ✔ | See five-country table. National IVF register (since 1994) is linked to the Medical Birth Register, so parity×age is possible on request. | Goisis et al. 2024 |
| United States | ✔ (microdata) | ✔ | ART % of births by age, 2017: 30–34 1.37%, 35–39 2.82%, 40–44 5.83%, 45–49 23.2%; <30 under 1%. Birth certificates (since 2016) flag "pregnancy from infertility treatment" (ART vs drugs) alongside age and live-birth order — CDC WONDER natality or NBER microdata can produce the full age×order table. | [Tierney & Cai 2019, Fertil Steril](https://pmc.ncbi.nlm.nih.gov/articles/PMC6986780); [NCHS natality user guide](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/UserGuide2023.pdf) |
| UK (E&W) | ✔ (survey) | ✔ | ~1 in 31 UK births from IVF in 2024 (1 in 65 in 2004); HFEA reports births by patient age. Parity only via Goisis 2024 (survey sample). HFEA anonymised register has previous-treatment-history fields, cycle-level to 2018. | [HFEA trends 2024](https://www.hfea.gov.uk/about-us/publications/research-and-data/fertility-treatment-2024-trends-and-figures); [HFEA anonymised register](https://www.hfea.gov.uk/about-us/data-research) |
| Spain | ✔ (survey) | ✔ | 39,555 babies from 2023 treatments, ~10% of births (12% in 2022 report). SEF registry tabulates by woman's age; parity only via Goisis 2024. | [SEF registry](https://sefertilidad.net/documentos/lyOlT-rkPKvRdGKY_wA1sINHS7Btlw189LVFTlHd5eE.pdf) |
| Japan | ✘ | ✔ | JSOG 2022: 77,206 neonates; live-birth cycles by age at treatment. Divided by HFD births by mother's age 2022 (my calculation): 25–29 3.4%, 30–34 8.9%, 35–39 16.7%, 40–44 26.1%, all ages 9.7% (10.0% using neonates). Age-at-treatment vs age-at-birth mismatch biases this slightly. | [JSOG 2022 summary](https://pmc.ncbi.nlm.nih.gov/articles/PMC11646354/) |
| South Korea | ✘ | partial | HIRA claims analysis: 15.1% of 2024 births after infertility treatment (8.7% in 2019; 36,025 births). Includes IUI. Age/order breakdown not found publicly. | [Newsis/HIRA coverage](https://www.newsis.com/view/NISX20250226_0003079235) |
| Taiwan | ✘ | ✔ (patients) | HPA 2022: 11,549 ART babies; patients 36.1% aged 35–39, 33.3% 40–44; median patient age 38. ART births 0.86% (1998) → 1.44% (2007). | [Focus Taiwan](https://focustaiwan.tw/sci-tech/202501020012); [Taipei Times](https://www.taipeitimes.com/News/front/archives/2025/01/03/2003829569) |
| Czechia | ✘ | ✔ | ÚZIS annual report: IVF/FET deliveries by age at cycle start (<35, 35–39, 40+). Kocourková et al. 2023 link ART register to birth register, giving ART vs non-ART ASFR/TFR; ART <4% of births excluding cross-border patients. | [ÚZIS 2021–23](https://www.uzis.cz/res/f/008464/asistreprodukce2023.pdf); [Kocourková et al. 2023, Sci Rep](https://doi.org/10.1038/s41598-023-37071-7) |
| Canada | ✘ | cycles | 8,870 IVF infants in 2023; IVF 3.0% of Ontario births. CARTR Plus reports by age category of cycle. | [CARTR Plus 2025](https://cfas.ca/_Library/CARTR/2025_CARTR_annual_report_CFAS_2024_Data_.pdf) |
| Finland | ✘ | — | Fertility treatments → 2,336 children, ~4.8% of births (2017). THL MBR records IVF and parity, so tables are possible. | [stat.fi hedhoid](https://stat.fi/til/hedhoid/index_en.html) |
| Sweden | ✘ | — | MFR + Q-IVF; Socialstyrelsen published "Assisterad befruktning 1991–2013" with age/parity sections. | [Socialstyrelsen](https://www.socialstyrelsen.se/statistik-och-data/statistik/statistikamnen/graviditeter-forlossningar-och-nyfodda/) |
| Switzerland | ✘ | cycles | BFS MUF table (pregnancies and births, 2006–); ~2,500 IVF children ≈3% of births. | [BFS](https://www.bfs.admin.ch/asset/en/22164428) |
| Belgium | ✘ | — | Flanders 2010: 5.7% of deliveries after ART (3.6% IVF/ICSI). SPE perinatal reports collect parity and age. | [SPE-based study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5303697) |
| Estonia | ✘ | — | No national ART register; IVF ~2–4% of births. | [Reprod Health 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6083506/) |
| Chile, Lithuania, Netherlands, Ireland, Portugal, Austria, Hungary, Slovenia, Bulgaria, Croatia | ✘ | cycles | Nothing national found beyond the ESHRE/REDLARA registry: EIM reports give ART infants per country and cycles/deliveries by age band; no birth order. | [ESHRE ART in Europe 2020](https://pubmed.ncbi.nlm.nih.gov/40985526/) |

## Gaps / next steps

1. **US is the only country where a full age × birth-order table is publicly computable**
   (birth-certificate infertility-treatment flag, 2016–present). 2024 is tabulated above; earlier
   years can be pulled from the same WONDER query for a trend.
2. Norway/Denmark/Finland/Sweden can produce the same from linked registers, but published tables
   are partial; Chanfreau et al. (2025) is the most likely source of Norwegian ART rates by age
   and parity (not read; paywalled).
3. Definitions differ: IVF-only (HFEA, JSOG, CARTR) vs all MAR incl. IUI (Goisis 2024, Korea
   HIRA). Don't mix them in one chart without saying so.
