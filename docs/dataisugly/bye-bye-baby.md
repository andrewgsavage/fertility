# Bye Bye Baby

The Resolution Foundation produced a report [Bye Bye Baby](https://www.resolutionfoundation.org/publications/bye-bye-baby/) ([PDF](https://www.resolutionfoundation.org/app/uploads/2026/03/Bye-bye-baby.pdf)) that contains several charts. Each chart indivdually is fine, however the line colours and layouts are inconsistent accross charts making it unnecessirly difficult to make conclusions based on multiple charts.

Furthermore, the flipping one percentage (going from X% to 1-X%) yields very different conclusions in one case. Careful when looking at %age trends on % values!

## Colour scheme

Figure 4 colours its age/milestone bands consistently youngest-to-oldest (purple → cyan → yellow → salmon), which makes its two panels easy to read together and easy to compare against each other. Figure 5 doesn't uses different colours to Figure 4 for each age group, and it also uses a different colour ordering (purple → yellow → cyan). Figure 6 uses another convention again, (purple → cyan → salmon → olive)


::::{tab-set}

:::{tab-item} Figure 4
```{image} /_static/resolution/rf_figure4_childless_by_age.png
:alt: Resolution Foundation Figure 4 — proportion of women who haven't had a child, by age, England and Wales
:width: 100%
```
:::

:::{tab-item} Figure 5
```{image} /_static/resolution/rf_figure5.png
:alt: Resolution Foundation Figure 5 — Family size, by age, England and Wales
:width: 100%
```
:::

::: {tab-item} Figure 6

```{image} /_static/resolution/rf_figure6_original.png
:alt: Resolution Foundation Figure 6 — proportion of women who haven't had a biological child, by age and education, UK
:width: 100%
```
:::

::::


## Layout

Figure 6 plots graduates on the left and non-graduates, while Figure 7 plots graduates on the right and non-graduates on the left.

::::{tab-set}

::: {tab-item} Figure 6

```{image} /_static/resolution/rf_figure6_original.png
:alt: Resolution Foundation Figure 6 — proportion of women who haven't had a biological child, by age and education, UK
:width: 100%
```
:::

:::{tab-item} Figure 7
```{image} /_static/resolution/rf_figure7.png
:alt: Resolution Foundation Figure 7 — share of people aged 25-29 cohabiting or married, by education and sex, UK
:width: 100%
```
:::

::::

## Reporting year vs birth cohort

Figure 6 uses reporting year as the x axis, whereas all previous charts used birth cohort as the x axis. Using reporting year as the x axis makes it difficult to track changes in a cohort as the women age - which is what the conclusion for this chart is based on.It also becomes apparent there is something wrong with the underlying data as the childlessness rates increase between 35-39 and 40-44 which is impossible.

Subsequent plots use reporting year as the x axis, however these all show data for 25-29 year olds so there's no issues with comparing cohorts as they age as there is only one age plotted.

::::{tab-set}

::: {tab-item} Figure 6

```{image} /_static/resolution/rf_figure6_original.png
:alt: Resolution Foundation Figure 6 — proportion of women who haven't had a biological child, by age and education, UK
:width: 100%
```
:::

:::{tab-item} Figure 6 Replotted

```{image} /_static/resolution/grads_nongrads_birth_year.png
:alt: Proportion of women without a biological child, by age and education, plotted against mother's birth year
:width: 100%
```
:::

::::


## Shared Axes

It's difficult to compare charts accross multiple pages of a report. When making conclusions that use trends for multiple graphs, it's essential to show them together. When comparing trends against a common variable, eg reporting year, it's helpful to use shared axes or similar.

::::{tab-set}

:::{tab-item} Figure 6a
```{image} /_static/resolution/rf_figure6a.png
:alt: Resolution Foundation Figure 6, non-graduate panel — proportion of non-graduate women who haven't had a biological child, by age, UK
:width: 100%
```
:::

:::{tab-item} Figure 7a
```{image} /_static/resolution/rf_figure7a.png
:alt: Resolution Foundation Figure 7, non-graduate panel — share of non-graduates aged 25-29 cohabiting or married, by sex, UK
:width: 100%
```
:::

:::{tab-item} Figure 8
```{image} /_static/resolution/rf_figure8.png
:alt: Resolution Foundation Figure 8 — share of non-graduates aged 25-29 living in different housing tenures, UK
:width: 100%
```
:::

:::{tab-item} Shared x
```{image} /_static/resolution/mashup.png
:alt: Figures 8, 6a, and 7a stacked on a shared reporting-year x-axis, for non-graduates
:width: 100%
```
:::

::::

See [Bye Bye Baby?](../uk/childlessness-by-education) for what the shared-axis data implies about the report's argument.

```{note}
Figures 4, 5, 6, 7, and 8 (originals, including cropped sub-panels) are reproduced from the Resolution Foundation's [Bye Bye Baby](https://www.resolutionfoundation.org/publications/bye-bye-baby/) report ([PDF](https://www.resolutionfoundation.org/app/uploads/2026/03/Bye-bye-baby.pdf)), included here for commentary and comparison against the recoloured/re-sliced versions above; copyright remains with the Resolution Foundation.

The recoloured charts' data is digitized from Figure 6. See `resolution/scripts/plot_grads_nongrads.py` and `resolution/data/grads.csv` / `resolution/data/nongrads.csv`.

The "Shared x" mashup is redrawn from data digitized off Figures 6a, 7a, and 8 (colour-matched pixel extraction from the source images). See `resolution/scripts/plot_mashup.py` and `resolution/data/fig7a_nongrad.csv` / `resolution/data/fig8_nongrad.csv`.
```
