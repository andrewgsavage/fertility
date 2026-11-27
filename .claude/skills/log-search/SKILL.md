---
name: log-search
description: Record a search for data or papers in research/searches/, including the places that failed (403, paywall, login, wrong age bands, bad coding). Use after any search of the web, a statistics portal or the literature, and before starting one to check what was already tried.
---

# Log a search

The log is `research/searches/`: one YAML file per question, one attempt per place tried. Fields and
the `outcome` values are in [`research/searches/README.md`](../../../research/searches/README.md).
Read it before writing an entry. Run commands from the repo root.

## Before searching

1. **Look for the question.** Run `pixi run searches-check <term> ...` with the factor tag, country
   code, dataset code or publisher. Read each matching file. Skip attempts marked `lacks-it` or
   `unreliable`, and retry a `blocked` one only by the route in its `retry`. Done when you know
   which places are left to try.

## After searching

2. **Find or start the entry.** If a file asks the same question, add to it. If yours is narrower or
   wider (different ages, countries or measure), start a new file and mention the other in `notes`.
   Done when you know which file you are writing.

3. **Add one attempt per place tried**, with today's date, including those that worked. `tried`
   names the dataset code, table, paper or search query. `why` says what was wrong specifically
   enough for a later agent to judge whether it still holds ("16-29 is one band", not "no good").
   For `blocked`, say how (HTTP 403 to scripts, paywall, login, registration) and put in `retry`
   what would get past it. Done when every place you looked at is listed.

4. **Update the summary fields**: `status`, `answer`, `pages`, `sources` (ids of the `sources/`
   entries you added with the `add-source` skill) and `next` for leads you didn't get to. Done when
   `status` matches the attempts.

5. **Check**: `pixi run searches-check`. Done when it reports no errors.

Papers that `sources-fetch` couldn't download are already in `$PAPERS_DIR/_missing.md`; don't copy
them here.
