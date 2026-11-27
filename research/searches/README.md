# Search log

What has been looked for, where, and what came of it, including the searches that failed. It is
there so the next agent doesn't repeat a dead end, and does retry a source whose block it can get
past. `sources/` records the sources that were used; this records the searches.

One YAML file per **question**: the thing someone was trying to find, not the place they looked.
Each place tried is one attempt under it.

Before searching the web, a statistics portal or the literature, look here first:

```
pixi run searches-check <term> [<term> ...]
```

Terms are matched case-insensitively against the whole entry, so a factor tag, country code, dataset
code or publisher name all work. With no terms it checks every entry, and fails on unknown fields or
tags, a missing required field, or a `sources` id or `pages` path that doesn't exist.

The docs site renders the log on its Searches page (`docs/searches.md`, the `{searches}` directive
in `docs/_ext/search_log.py`).

## Fields

| field | required | notes |
|---|---|---|
| `id` | yes | Equals the file name. Kebab-case, naming the question: `coupling-by-narrow-age`. |
| `question` | yes | What was wanted, specific enough to tell whether a new search is the same one: measure, ages, years, countries. |
| `status` | yes | `answered`, `partial`, `dead-end` (every lead tried, none worked) or `open` (leads left in `next`). |
| `answer` | if answered or partial | What was found and where it is used. |
| `factors`, `measurables` | | Tags from [`sources/_vocab.yaml`](../../sources/_vocab.yaml). |
| `countries` | | HFD codes or ISO3, or `all`, as in `sources/`. |
| `pages` | | Repo paths of the docs pages that use the answer or list the gap. |
| `sources` | | `sources/` ids of what was used. |
| `attempts` | yes | One per place tried; see below. |
| `next` | | Leads not yet tried. |
| `notes` | | Anything else a later agent needs, such as a technique that worked. |

## Attempts

| field | required | notes |
|---|---|---|
| `date` | yes | `YYYY-MM-DD`. |
| `tried` | yes | The dataset code, table, paper, site or search query. |
| `url` | | |
| `outcome` | yes | See below. |
| `why` | unless found | What was wrong, specific enough to judge whether it still holds. |
| `retry` | | What would change the outcome: a manual browser download, a registration, the user's login, a new release. |

| outcome | meaning | retry? |
|---|---|---|
| `found` | Had what was wanted. | |
| `partial` | Had some of it (some countries, wider age bands, fewer years). | For the missing part only. |
| `lacks-it` | The source exists and was read, but doesn't have it. | No, unless a new release adds it. |
| `unreliable` | Has it, but the coding or definitions make it wrong for this use. | No. |
| `blocked` | Couldn't be read: HTTP 403, paywall, login, registration, application, host outage, unreadable format. | Yes, by the route in `retry`. |
| `nothing-found` | A search query or literature search turned up nothing relevant. | With different terms. |

`blocked` is the outcome that changes. Say how it was blocked: a 403 to scripts may open in a
browser, and a registration the user can do in a minute.

Papers that couldn't be downloaded are listed in `$PAPERS_DIR/_missing.md` by
`pixi run sources-fetch`. Don't copy them here. Log a paper here only when the search for it, or
for what it would have shown, was the work.
