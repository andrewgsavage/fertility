"""Check the search log in research/searches/*.yaml.

Run `pixi run searches-check`. Exits 1 if any entry has an error. Tags are checked
against sources/_vocab.yaml, `sources` against the ids in sources/*.yaml, and
`pages` against repo paths. See research/searches/README.md for the fields.

With arguments, prints the entries whose text matches every term instead, e.g.
`pixi run searches-check statcan` or `pixi run searches-check partnership GBR`.
"""

from __future__ import annotations

import datetime as dt
import pathlib
import sys

import yaml

from sources import COUNTRY_RE, ID_RE, REPO, load_vocab, source_paths

LOG = REPO / "research" / "searches"

STATUSES = {"answered", "partial", "dead-end", "open"}
OUTCOMES = {"found", "partial", "lacks-it", "blocked", "unreliable", "nothing-found"}
FIELDS = {
    "id", "question", "status", "factors", "measurables", "countries", "answer", "pages",
    "sources", "attempts", "next", "notes",
}
ATTEMPT_FIELDS = {"date", "tried", "url", "outcome", "why", "retry"}


def log_paths() -> list[pathlib.Path]:
    return sorted(p for p in LOG.glob("*.yaml") if not p.name.startswith("_"))


def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def check_entry(path: pathlib.Path, e: dict, vocab: dict, source_ids: set[str]) -> list[str]:
    errors = []
    unknown = set(e) - FIELDS
    if unknown:
        errors.append(f"unknown fields: {sorted(unknown)}")
    eid = e.get("id")
    if eid != path.stem:
        errors.append(f"id {eid!r} must equal file name {path.stem!r}")
    elif not ID_RE.match(eid):
        errors.append(f"id {eid!r} must be lowercase kebab-case")
    if not e.get("question"):
        errors.append("question is required")
    if e.get("status") not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    if e.get("status") in {"answered", "partial"} and not e.get("answer"):
        errors.append(f"answer is required when status is {e.get('status')}")

    for f in _as_list(e.get("factors")):
        if f not in vocab["factors"]:
            errors.append(f"unknown factor {f!r}")
    for m in _as_list(e.get("measurables")):
        if m not in vocab["measurables"]:
            errors.append(f"unknown measurable {m!r}")
    for c in _as_list(e.get("countries")):
        if c != "all" and not COUNTRY_RE.match(str(c)):
            errors.append(f"country {c!r} is not an HFD code, ISO3 code or 'all'")
    for s in _as_list(e.get("sources")):
        if s not in source_ids:
            errors.append(f"source {s!r} not in sources/")
    for p in _as_list(e.get("pages")):
        if not (REPO / p).is_file():
            errors.append(f"page {p!r} not found")

    attempts = _as_list(e.get("attempts"))
    if not attempts:
        errors.append("attempts must list at least one attempt")
    for i, a in enumerate(attempts):
        where = f"attempts[{i}]"
        if not isinstance(a, dict):
            errors.append(f"{where} must be a mapping")
            continue
        if set(a) - ATTEMPT_FIELDS:
            errors.append(f"{where}: unknown fields {sorted(set(a) - ATTEMPT_FIELDS)}")
        if not a.get("tried"):
            errors.append(f"{where}: tried is required")
        if a.get("outcome") not in OUTCOMES:
            errors.append(f"{where}: outcome must be one of {sorted(OUTCOMES)}")
        if a.get("outcome") not in {"found", None} and not a.get("why"):
            errors.append(f"{where}: why is required unless outcome is found")
        if not isinstance(a.get("date"), dt.date):
            errors.append(f"{where}: date must be YYYY-MM-DD")
    return errors


def search(terms: list[str]) -> int:
    terms = [t.lower() for t in terms]
    hits = 0
    for path in log_paths():
        text = path.read_text(encoding="utf-8")
        if all(t in text.lower() for t in terms):
            hits += 1
            e = yaml.safe_load(text) or {}
            print(f"{path.relative_to(REPO).as_posix()}  [{e.get('status')}]  {e.get('question')}")
            for a in _as_list(e.get("attempts")):
                line = f"  {a.get('date')}  {a.get('outcome'):<13} {a.get('tried')}"
                if a.get("why"):
                    line += f": {a['why']}"
                print(line.strip("\n"))
    print(f"{hits} matching entr{'y' if hits == 1 else 'ies'}")
    return 0


def main() -> int:
    if len(sys.argv) > 1:
        return search(sys.argv[1:])
    vocab = load_vocab()
    source_ids = {p.stem for p in source_paths()}
    n_err = 0
    paths = log_paths()
    for path in paths:
        try:
            e = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as err:
            print(f"ERROR {path.name}: YAML parse error: {err}")
            n_err += 1
            continue
        errors = check_entry(path, e, vocab, source_ids)
        for msg in errors:
            print(f"ERROR {path.name}: {msg}")
        n_err += bool(errors)
    print(f"{len(paths)} searches, {n_err} with errors")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
