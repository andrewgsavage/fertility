When an agent writes a new docs page (`docs/**/*.md`), put this warning directly under the page title:

````
```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```
````

Don't add it to section index pages, and don't remove an existing warning; only the user decides when a page has been reviewed.

Cite a chart's or table's data sources in a `{note}` block directly below it: dataset or publication name linked to its URL, then coverage and method caveats, in terse factual sentences. Keep body prose for findings, and link a source inline in prose only where the sentence quotes or discusses that source.

````
```{note}
Eurostat [household composition table](https://ec.europa.eu/eurostat/databrowser/view/lfst_hhindws/default/table) (EU Labour Force Survey), 2006–2024. EU-LFS household data has a methodology break in 2021.
```
````
