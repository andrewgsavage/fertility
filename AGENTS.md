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
