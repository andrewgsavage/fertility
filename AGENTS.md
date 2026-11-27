Before searching the web, a statistics portal or the literature for data or papers, check the search log: `pixi run searches-check <term>` (a factor tag, country code, dataset code or publisher). Don't repeat an attempt it records as `lacks-it` or `unreliable`; retry a `blocked` one only by the route in its `retry`. After searching, record every place tried, including failures, with the `log-search` skill.

When an agent writes a new docs page (`docs/**/*.md`), put this warning directly under the page title:

````
```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```
````

Don't add it to section index pages, and don't remove an existing warning; only the user decides when a page has been reviewed.

Don't write a caption or description for a chart: no sentence restating what it plots ("Abortions per 100 births, by age"), what the marks are ("Each dot is a country"), or how to use its controls ("Drag the slider", "Use the dropdown", "Hover for values"). The chart's title, axes and legend already say this. Prose next to a chart states findings; coverage and comparability caveats go in its `{note}`.

Cite a chart's or table's data sources in a `{note}` block directly below it: dataset or publication name linked to its URL, then coverage and method caveats, in terse factual sentences. Keep body prose for findings, and link a source inline in prose only where the sentence quotes or discusses that source.

````
```{note}
Eurostat [household composition table](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhindws/default/table) (EU Labour Force Survey), 2006–2024. EU-LFS household data has a methodology break in 2021.
```
````

Put a chart, its data table and its `{note}` in one `tab-set`: a tab per chart, then a `Data` tab with the table(s) and a `Notes` tab with the `{note}`. Leave out `Data` when there's no table. If the chart has variants (by age, ratio vs level), give each its own tab and put all their tables in the one `Data` tab, under a bold label per variant. Findings prose goes outside the tab-set, except findings about one variant, which stay in that variant's tab. Coverage caveats go in the `{note}`, not the chart tab. A table with no chart stays in the body with its `{note}` directly below it.

`````
::::{tab-set}

:::{tab-item} Chart
```{raw} html
<iframe src="../_static/eurostat/abortion_by_age.html" ...></iframe>
```
:::

:::{tab-item} Data
| Country | 2013 | Latest |
|---|--:|--:|
| Spain | 22 | 41 (2024) |
:::

:::{tab-item} Notes
```{note}
Eurostat [demo_fabort](https://ec.europa.eu/eurostat/databrowser/view/demo_fabort/default/table), 2007–2024. ...
```
:::

::::
`````
