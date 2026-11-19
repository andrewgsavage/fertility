---
name: add-source
description: Add a paper, dataset, report or web page to the sources/ registry, tagged with factors and measurables. Use when citing a source in docs or scripts, or when asked to add, tag or record findings for one.
---

# Add a source

The registry is `sources/`: one YAML file per source. Fields, finding rules and tagging rules
live in [`sources/README.md`](../../../sources/README.md); the allowed tags in
[`sources/_vocab.yaml`](../../../sources/_vocab.yaml). Read both before writing an entry. Run
commands from the repo root.

## Steps

1. **Find any existing entry.** Search `sources/*.yaml` for the DOI, URL and first author's
   surname. If one exists, extend it (new tags, findings, `scripts`) and skip to step 5.
   Done when you know whether you are creating or extending.

2. **Get the metadata from the record, not memory.** For a DOI:

   ```
   cd sources && pixi run python -c "from import_factor_evidence import metadata; print(metadata('10.xxxx/yyyy', offline=False))"
   ```

   This returns title, authors, year, journal and open-access status and link from Crossref and
   OpenAlex. For a dataset or web page, read the publisher's page. A field you cannot confirm stays
   out, and the gap goes in `notes` ("year unknown", "check authors"). Done when every field you
   write has a source.

3. **Write `sources/<id>.yaml`.** Use the `id` scheme in the README. Tag with `factors` and
   `measurables` for what the source is about. Fill `countries`, `period` and `scripts` when known.
   Done when the file has every field the README marks required for its `type`.

4. **Record findings from what you read.** One finding per factor-table cell the source bears on,
   with `basis: fulltext` or `basis: abstract` matching what you actually read, `ref` pointing at the
   repo file that cites it, and the `tick` that cell had. A source you only skimmed gets tags and no
   findings. Done when each finding's `note` states the result and its sample (country, years, data).

5. **Fetch the full text** for papers with an open-access link:

   ```
   pixi run sources-fetch --only <id>
   ```

   If it reports `fail`, tell the user: the paper is listed in `$PAPERS_DIR/_missing.md` for a manual
   download.

6. **Check.** `pixi run sources-check` passes with 0 errors and prints no warning for your file.

## Tags

- **Measurable missing:** add it to `_vocab.yaml` at theory-page level (`kind: outcome`, or
  `kind: exposure` with its `factor`), then use it.
- **Factor missing:** factors mirror the rows of the table in `docs/factors/index.md`, so a new one
  is the user's call. Ask before adding it, and tag with the nearest existing factor meanwhile only
  if it genuinely fits.

## Hand-written findings

The YAML is the record of findings; `research/factor-evidence/*.md` was only its starting point.
When you correct an imported finding (e.g. after reading the full text), edit it in place: set
`basis: fulltext`, and point `ref` at the repo file where the correction is cited, such as the docs
page. Corrections live only in the YAML, so `sources/import_factor_evidence.py` stays unrun from
then on.
