"""Load and check the source registry in sources/*.yaml against sources/_vocab.yaml.

Run `pixi run sources-check`. Exits 1 if any source has an error; warnings are
printed but do not fail. `load()` is importable (e.g. by a Sphinx extension) and
returns each source with an extra `all_factors` key: its own factor tags plus the
factors implied by its exposure measurables.

Full texts live outside the repo (they are not redistributable and gitignored
files would not reach worktrees): $PAPERS_DIR, default ~/papers, holding
<id>.pdf and <id>.txt. The check reports which papers have a local full text.
"""

from __future__ import annotations

import os
import pathlib
import re
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
VOCAB_PATH = HERE / "_vocab.yaml"

TYPES = {"paper", "report", "book", "dataset", "web", "survey"}
CITED_TYPES = {"paper", "report", "book"}  # need authors and a year
OA = {"gold", "green", "hybrid", "bronze", "closed"}
DIRECTIONS = {"+", "-", "0", "mixed"}
VERDICTS = {"supports", "mixed", "contradicts"}
FIELDS = {
    "id", "type", "title", "authors", "publisher", "year", "doi", "url", "oa", "oa_url",
    "local", "scripts", "countries", "period", "factors", "measurables", "findings",
    "notes", "accessed",
}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COUNTRY_RE = re.compile(r"^[A-Z]{3}[A-Z_]{0,6}$")  # ISO3, or HFD codes: GBRTENW, GBR_NP, DEUTE
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")


def papers_dir() -> pathlib.Path:
    return pathlib.Path(os.environ.get("PAPERS_DIR", pathlib.Path.home() / "papers"))


def load_vocab() -> dict:
    return yaml.safe_load(VOCAB_PATH.read_text(encoding="utf-8"))


def source_paths() -> list[pathlib.Path]:
    return sorted(p for p in HERE.glob("*.yaml") if not p.name.startswith("_"))


def load() -> list[dict]:
    vocab = load_vocab()
    implied = {k: v.get("factor") for k, v in vocab["measurables"].items()}
    out = []
    for path in source_paths():
        src = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        factors = list(src.get("factors") or [])
        for m in src.get("measurables") or []:
            f = implied.get(m)
            if f and f not in factors:
                factors.append(f)
        src["all_factors"] = factors
        out.append(src)
    return out


def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def check_source(path: pathlib.Path, src: dict, vocab: dict) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    factors, measurables = vocab["factors"], vocab["measurables"]

    unknown = set(src) - FIELDS
    if unknown:
        errors.append(f"unknown fields: {sorted(unknown)}")

    sid = src.get("id")
    if sid != path.stem:
        errors.append(f"id {sid!r} must equal file name {path.stem!r}")
    elif not ID_RE.match(sid):
        errors.append(f"id {sid!r} must be lowercase kebab-case")

    stype = src.get("type")
    if stype not in TYPES:
        errors.append(f"type must be one of {sorted(TYPES)}")
    if not src.get("title"):
        errors.append("title is required")
    if not (src.get("doi") or src.get("url")):
        errors.append("doi or url is required")
    if stype in CITED_TYPES:
        if not src.get("authors"):
            errors.append(f"authors required for type {stype}")
        if not isinstance(src.get("year"), int):
            errors.append(f"year (int) required for type {stype}")
    if stype == "dataset" and not src.get("publisher"):
        errors.append("publisher required for type dataset")

    doi = src.get("doi")
    if doi and not DOI_RE.match(str(doi)):
        errors.append(f"doi {doi!r} should be bare (10.xxxx/...), not a URL")
    if src.get("oa") is not None and src["oa"] not in OA:
        errors.append(f"oa must be one of {sorted(OA)}")

    for c in _as_list(src.get("countries")):
        if c != "all" and not COUNTRY_RE.match(str(c)):
            errors.append(f"country {c!r} is not an HFD code, ISO3 code or 'all'")

    period = src.get("period")
    if period is not None and not (
        isinstance(period, list) and len(period) == 2 and all(isinstance(y, int) for y in period)
        and period[0] <= period[1]
    ):
        errors.append("period must be [start_year, end_year]")

    for f in _as_list(src.get("factors")):
        if f not in factors:
            errors.append(f"unknown factor {f!r}")
    for m in _as_list(src.get("measurables")):
        if m not in measurables:
            errors.append(f"unknown measurable {m!r}")

    for i, fd in enumerate(_as_list(src.get("findings"))):
        where = f"findings[{i}]"
        if not isinstance(fd, dict):
            errors.append(f"{where} must be a mapping")
            continue
        if fd.get("factor") not in factors:
            errors.append(f"{where}: unknown factor {fd.get('factor')!r}")
        if fd.get("measure") is not None and fd["measure"] not in measurables:
            errors.append(f"{where}: unknown measurable {fd['measure']!r}")
        if fd.get("direction") is not None and str(fd["direction"]) not in DIRECTIONS:
            errors.append(f"{where}: direction must be one of {sorted(DIRECTIONS)}")
        if fd.get("verdict") is not None and fd["verdict"] not in VERDICTS:
            errors.append(f"{where}: verdict must be one of {sorted(VERDICTS)}")

    for s in _as_list(src.get("scripts")):
        if not (REPO / s).is_file():
            errors.append(f"script {s!r} not found")
    # `local` paths are usually gitignored data folders, so absent in a fresh worktree.
    for p in _as_list(src.get("local")):
        if not (REPO / p).exists() and not (REPO / p).parent.exists():
            warnings.append(f"local path {p!r}: parent folder not found")

    if not (src.get("factors") or src.get("measurables")):
        warnings.append("no factor or measurable tags")
    return errors, warnings


def main() -> int:
    vocab = load_vocab()
    for name, m in vocab["measurables"].items():
        if m.get("kind") == "exposure" and m.get("factor") not in vocab["factors"]:
            print(f"_vocab.yaml: measurable {name!r} names unknown factor {m.get('factor')!r}")
            return 1

    n_err = 0
    seen_doi: dict[str, str] = {}
    papers = []
    paths = source_paths()
    for path in paths:
        try:
            src = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            print(f"ERROR {path.name}: YAML parse error: {e}")
            n_err += 1
            continue
        errors, warnings = check_source(path, src, vocab)
        doi = str(src.get("doi") or "").lower()
        if doi:
            if doi in seen_doi:
                errors.append(f"duplicate doi, also in {seen_doi[doi]}")
            seen_doi[doi] = path.name
        for e in errors:
            print(f"ERROR {path.name}: {e}")
        for w in warnings:
            print(f"warn  {path.name}: {w}")
        n_err += bool(errors)
        if src.get("type") in CITED_TYPES:
            papers.append(src)

    pdir = papers_dir()
    have_text = [p for p in papers if (pdir / f"{p.get('id')}.txt").is_file()]
    with_findings = [p for p in papers if p.get("findings")]
    findings_no_text = [p for p in with_findings if p not in have_text]
    print(
        f"\n{len(paths)} sources, {n_err} with errors. "
        f"{len(papers)} papers/reports/books: {len(have_text)} with full text in {pdir}; "
        f"{len(findings_no_text)} of {len(with_findings)} with findings rest on no local full text."
    )
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
