# Sources

One YAML file per source (paper, report, book, dataset, survey or web page), tagged with the
factors and measurables in [`_vocab.yaml`](_vocab.yaml). Check with:

```
pixi run sources-check
```

It fails on unknown fields or tags, a missing required field, a DOI written as a URL, a duplicate
DOI, or a `scripts` path that doesn't exist.

## Fields

| field | required | notes |
|---|---|---|
| `id` | yes | Must equal the file name. Kebab-case: `firstauthor-year-keyword` for papers, `publisher-table` for datasets. |
| `type` | yes | `paper`, `report`, `book`, `dataset`, `survey` or `web`. |
| `title` | yes | |
| `doi` / `url` | at least one | DOI bare (`10.4054/...`), not a link. |
| `authors`, `year` | paper, report, book | `"Surname, I."` |
| `publisher` | dataset | |
| `oa` | | `gold`, `green`, `hybrid`, `bronze` or `closed`. |
| `oa_url` | | Free full-text link, if `url`/`doi` is paywalled. Docs link here, never to a local file. |
| `local` | | Repo paths where downloaded data lives (usually a gitignored `data/` folder). |
| `scripts` | | Repo scripts that read this source. |
| `countries` | | HFD population codes (`GBRTENW`, `GBR_NP`, `DEUTE`) where HFD has one, else ISO3; `all` for global. |
| `period` | | `[start_year, end_year]` covered. |
| `factors` | | Factor tags. Exposure measurables already imply their factor, so add a factor only when the source is about it but none of its measurables fits. |
| `measurables` | | Outcome and exposure tags. |
| `findings` | | What the source finds; see below. |
| `notes` | | Free text. |
| `accessed` | | Date accessed, for web pages and data that change. |

Tags are what a source is about. Findings are what it shows, with a direction. Keep the two apart,
so tags don't turn into things like `housing-negative`.

## Findings

Each finding is one cell of the factor table (factor × outcome column) as this source bears on it.

| field | notes |
|---|---|
| `factor` | Required. |
| `measure` | The outcome column, e.g. `cond-asfr-1`. Omitted when the finding covers all columns. |
| `verdict` | Against the cell's tick: `supports`, `mixed`, `contradicts`, or `no-evidence` (examined for this cell but doesn't test it). Omitted for a paper only mentioned in another paper's note. |
| `tick` | The cell's tick when the verdict was made: `yes`, `no` or `?`. A verdict means nothing without it. |
| `direction` | `+`, `-`, `0` or `mixed`: the sign of the factor's effect on the measure. |
| `basis` | `abstract` or `fulltext`: what the verdict was read from. |
| `ref` | Repo file the finding came from. |
| `note` | The finding in words. |

Measurable tags on a paper come from its findings with a real verdict (`supports`, `mixed`,
`contradicts`), not from `no-evidence` ones.

## Importing the factor evidence

`pixi run python sources/import_factor_evidence.py` turns each row of the tables in
`research/factor-evidence/*.md` into findings on the papers it names, resolving "(above)" and
"(lit-review)" references. Metadata (authors, title, year, open-access status and link) comes from
Crossref and OpenAlex and is cached in `sources/.cache/` (gitignored; `--offline` uses only the
cache). Rerunning it replaces the findings it made earlier and leaves hand-written fields alone.
It is a bridge: once findings are edited here, stop rerunning it, or the edits are lost.

## Adding tags

Add a factor or measurable to `_vocab.yaml` when a source needs one; don't reuse a near-miss.
Factors mirror the rows of the table in `docs/factors/index.md`. Measurables stay at the level of the
theory pages (TFR, TMR, CPM, PPR, conditional ASFR, MAB1). Age bands, sex and parity detail go in
`notes`.

## Full texts

PDFs and their text extracts are kept outside the repo, in `$PAPERS_DIR` (default `~/papers`), named
`<id>.pdf` and `<id>.txt`. They are not committed: the repo is public, and most papers can't be
redistributed. A folder inside the repo wouldn't work either, because gitignored files don't reach
new worktrees. Agents read the `.txt`. The check reports how many papers have a local full text, and how
many findings rest on abstracts only.

## Plan

1. Tag list (`_vocab.yaml`). Done.
2. Checker and seed entries for the datasets behind the repo's charts, plus the papers they reproduce.
   Done.
3. Import the papers in `research/factor-evidence/*.md`, each verdict row becoming a `findings`
   item. Done: 129 papers. Two DOIs mentioned only in the files' search notes, not in a table, are
   left out.
4. Download the open-access PDFs (`oa_url`, filled from OpenAlex in phase 3) into `$PAPERS_DIR` and
   extract text. Add paywalled ones by hand.
5. Re-check "abstract truncated" and "mixed" findings against full texts.
6. Sphinx: a generated Sources page filterable by tag, and a directive that lists matching sources on
   a factor page.
7. Optional: generate the factor-evidence tables, or the factor-table ticks, from `findings`.
