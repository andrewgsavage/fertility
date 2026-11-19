"""Import the papers cited in research/factor-evidence/*.md into sources/*.yaml.

Each row of an evidence table (Factor | Column | Tick | Verdict | Paper | Finding)
becomes a `findings` item on every paper named in its Paper cell. "(above)" and
"(lit-review)" references are resolved to the paper's first full citation in the
evidence files, or to its row in docs/literature-review.md.

Metadata comes from Crossref (authors, title) and OpenAlex (year, open-access
status and link), cached in sources/.cache/ (gitignored). An existing source with
the same DOI keeps its fields; its factor-evidence findings are replaced and its
tags extended.

    pixi run python sources/import_factor_evidence.py [--offline]
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata

import requests
import yaml

from sources import HERE, REPO, load_vocab

EVIDENCE = [
    "research/factor-evidence/costs-and-housing.md",
    "research/factor-evidence/life-course-and-education-work.md",
    "research/factor-evidence/policy-and-the-state.md",
    "research/factor-evidence/social-cultural-and-population.md",
]
LIT_REVIEW = REPO / "docs/literature-review.md"
CACHE = HERE / ".cache"
UA = {"User-Agent": "fertility-docs-sources/0.1"}

COLUMNS = {
    "Coupling": "share-in-couple",
    "PPR 0→1": "ppr-0-1",
    "First-birth cond. ASFR": "cond-asfr-1",
    "Young first births": "young-first-births",
    "PPR 1→2+": "ppr-1-2plus",
    "Second+ cond. ASFR": "cond-asfr-2plus",
    "all six columns": None,
}
FACTOR_ALIASES = {
    "House prices & ownership": "house-prices",
    "Political divide": "political-divide",
    "Sex education & teen pregnancy campaigns": "sex-education",
}
TICKS = {"✓": "yes", "blank": "no", "blank/✓": "?", "?": "?"}
VERDICTS = {
    "supports": "supports", "mixed": "mixed", "contradicts": "contradicts",
    "contradicts (the blank)": "contradicts", "no evidence found": "no-evidence",
}
# Names whose Crossref and OpenAlex records both carry mojibake.
NAME_FIXES = {"K�gel": "Kögel"}
STOP = set("""a an the of and or in on for to from with by at as is are do does did how what why
when who its it their this that between across among into over under after before than
evidence effect effects impact impacts role new study analysis case using via toward towards""".split())

DOI_RE = re.compile(r"10\.\d{4,9}/(?:[^\s()\]]|\([^\s()]*\))+")
LINK_RE = re.compile(r"\[([^\]]*)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
YEAR_RE = re.compile(r"^(.*?)\b((?:1[89]|20)\d{2})[a-z]?\b")


def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text.replace("ß", "ss")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def cite_key(chunk: str) -> str:
    """'van Wijk & Billari 2024 (above), ...' -> 'van wijk & billari 2024'."""
    text = LINK_RE.sub("", chunk)
    m = YEAR_RE.match(text)
    if m:
        authors = m.group(1)
        year = m.group(2)
    else:
        authors, year = re.split(r"[(,]", text)[0], ""
    authors = re.sub(r"\(.*?\)|,", " ", authors).replace("*", "")
    return " ".join((authors + " " + year).lower().split())


def split_cell(cell: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in cell:
        depth += ch in "([" and 1 or ch in ")]" and -1 or 0
        if ch == ";" and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip() and p.strip() not in {"–", "-"}]


def parse_chunk(chunk: str) -> dict:
    out = {"key": cite_key(chunk), "cite": chunk}
    title = re.search(r"\*([^*]+)\*", LINK_RE.sub("", chunk))
    if title:
        out["title"] = title.group(1).strip()
    for text, url in LINK_RE.findall(chunk):
        d = DOI_RE.search(url) or DOI_RE.search(text)
        if d:
            out["doi"] = d.group(0).lower().rstrip(".")
        else:
            out["url"] = url
    return out


def evidence_rows():
    for rel in EVIDENCE:
        lines = (REPO / rel).read_text(encoding="utf-8").splitlines()
        start = next(i for i, l in enumerate(lines) if l.startswith("| Factor | Column |"))
        factor = column = tick = None
        for line in lines[start + 2:]:
            if not line.startswith("|"):
                break
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            f, c, t, v, paper, finding = cells[:6]
            factor, column, tick = f or factor, c or column, t or tick
            yield dict(ref=rel, factor=factor, column=column, tick=tick,
                       verdict=v, paper=paper, finding=finding)


def lit_review_index() -> dict:
    idx = {}
    for line in LIT_REVIEW.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(.+?)\s*(?:\((\d{4})\))?,\s*\[\*?(.+?)\*?\]\((\S+?)\)", line)
        if not m:
            continue
        authors_raw, year, title, url = m.groups()
        authors_raw = authors_raw.rstrip(",")
        authors = [a.strip() for a in re.split(r",? and |(?<=\.), (?=[A-Z])", authors_raw) if a.strip()]
        first = authors[0].split(",")[0].strip().lower()
        entry = dict(authors=authors, year=int(year) if year else None, title=title.strip("*"), url=url)
        d = DOI_RE.search(url)
        if d:
            entry["doi"] = d.group(0).lower()
        idx.setdefault(first, []).append(entry)
    return idx


def cached_get(name: str, url: str, offline: bool):
    path = CACHE / f"{slug(name)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    if offline:
        return None
    for attempt in range(4):
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code in (429, 503):
            time.sleep(2 ** attempt)
            continue
        data = r.json() if r.ok else None
        CACHE.mkdir(exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        time.sleep(0.15)
        return data
    return None


def metadata(doi: str, offline: bool) -> dict:
    out = {}
    cr = cached_get(f"crossref-{doi}", f"https://api.crossref.org/works/{doi}", offline)
    if cr and cr.get("message"):
        m = cr["message"]
        out["title"] = (m.get("title") or [None])[0]
        authors = []
        for a in m.get("author", []):
            if a.get("family"):
                family = a["family"].title() if a["family"].isupper() else a["family"]
                initials = " ".join(p[0].upper() + "." for p in re.split(r"[\s.-]+", a.get("given", "")) if p)
                authors.append(f"{family}, {initials}".strip(", "))
            elif a.get("name"):
                authors.append(a["name"])
        out["authors"] = authors
        out["family"] = next((a["family"] for a in m.get("author", []) if a.get("family")), None)
        if out["family"] and out["family"].isupper():
            out["family"] = out["family"].title()
        out["container"] = (m.get("container-title") or [None])[0]
    oa = cached_get(f"openalex-{doi}", f"https://api.openalex.org/works/doi:{doi}", offline)
    if oa and oa.get("id"):
        out["year"] = oa.get("publication_year")
        out.setdefault("title", oa.get("title"))
        out["title"] = out["title"] or oa.get("title")
        names = [a["author"]["display_name"] for a in oa.get("authorships", [])]
        # Crossref sometimes carries mojibake (e.g. "K�gel"); fall back to OpenAlex names.
        if names and (not out.get("authors") or any("�" in a for a in out["authors"])):
            out["authors"] = [f"{n.split()[-1]}, " + " ".join(w[0] + "." for w in n.split()[:-1]) for n in names]
            out["family"] = names[0].split()[-1]
        acc = oa.get("open_access") or {}
        status = acc.get("oa_status")
        out["oa"] = status if status in {"gold", "green", "hybrid", "bronze", "closed"} else (
            "gold" if status == "diamond" else None)
        if acc.get("oa_url"):
            out["oa_url"] = acc["oa_url"]
    for bad, good in NAME_FIXES.items():
        out["authors"] = [x.replace(bad, good) for x in out.get("authors") or []]
        if out.get("family"):
            out["family"] = out["family"].replace(bad, good)
    return out


def make_id(family: str, year, title: str, taken: set) -> str:
    words = [w for w in slug(title or "").split("-") if w not in STOP and len(w) > 2]
    base = f"{slug(family or 'unknown')}-{year or 'nd'}"
    for n in (2, 3, 4):
        cand = "-".join([base] + words[:n])
        if cand not in taken:
            return cand
    i = 2
    while f"{base}-{i}" in taken:
        i += 1
    return f"{base}-{i}"


def main(offline: bool) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    vocab = load_vocab()
    labels = {slug(v["label"]): k for k, v in vocab["factors"].items()}

    def factor_slug(name):
        return FACTOR_ALIASES.get(name) or labels.get(slug(name))

    rows = list(evidence_rows())
    papers: dict[str, dict] = {}  # cite key -> parsed citation with doi/url
    for row in rows:
        for chunk in split_cell(row["paper"]):
            p = parse_chunk(chunk)
            if (p.get("doi") or p.get("url")) and p["key"] not in papers:
                papers[p["key"]] = p
    lit = lit_review_index()

    def resolve(chunk):
        p = parse_chunk(chunk)
        if p.get("doi") or p.get("url"):
            p = papers.get(p["key"], p)
            if not p.get("doi"):
                hit = next((h for hs in lit.values() for h in hs if h["url"] == p.get("url")), None)
                if hit:
                    p = dict(p, lit=hit)
            return p
        if p["key"] in papers:
            return resolve(papers[p["key"]]["cite"])
        # same first author and year, cited with a different co-author string
        first, year = p["key"].split()[0], p["key"].split()[-1]
        for k, q in papers.items():
            if k.split()[0] == first and k.split()[-1] == year:
                return q
        for k, q in papers.items():
            if k.split()[0] == first and not year.isdigit():
                return q
        hits = lit.get(first, [])
        hits = [h for h in hits if not year.isdigit() or h["year"] == int(year)] or hits
        if hits:
            return dict(key=p["key"], lit=hits[0], **{k: hits[0][k] for k in ("doi", "url") if k in hits[0]})
        return None

    unresolved, unknown_factors = [], set()
    by_ref: dict[str, dict] = {}  # doi or url -> {"cite": parsed, "findings": [...]}
    for row in rows:
        f = factor_slug(row["factor"])
        if not f:
            unknown_factors.add(row["factor"])
            continue
        cited = []
        for chunk in split_cell(row["paper"]):
            p = resolve(chunk)
            if not p:
                unresolved.append(f"{row['ref']}: {chunk}")
                continue
            cited.append((p, VERDICTS[row["verdict"]]))
        # Papers named only inside the Finding text: the row's verdict belongs to the cited
        # paper, so these get no verdict unless the row is "no evidence found".
        cited_dois = {p.get("doi") for p, _ in cited}
        for d in DOI_RE.findall(row["finding"]):
            d = d.lower().rstrip(".")
            if d not in cited_dois:
                cited_dois.add(d)
                verdict = "no-evidence" if row["verdict"] == "no evidence found" else None
                cited.append(({"key": d, "doi": d, "cite": d, "mentioned": True}, verdict))
        for p, verdict in cited:
            key = p.get("doi") or p.get("url")
            rec = by_ref.setdefault(key, {"cite": p, "findings": []})
            fd = {"factor": f}
            measure = COLUMNS[row["column"]]
            if measure:
                fd["measure"] = measure
            if verdict:
                fd["verdict"] = verdict
            fd["tick"] = TICKS[row["tick"]]
            fd["basis"] = "abstract"
            fd["ref"] = row["ref"]
            fd["note"] = row["finding"]
            if fd not in rec["findings"]:
                rec["findings"].append(fd)

    existing = {}
    for path in HERE.glob("*.yaml"):
        if path.name.startswith("_"):
            continue
        src = yaml.safe_load(path.read_text(encoding="utf-8"))
        for k in ("doi", "url"):
            if src.get(k):
                existing[str(src[k]).lower()] = (path, src)
    taken = {p.stem for p in HERE.glob("*.yaml")}

    written = updated = 0
    for key, rec in sorted(by_ref.items()):
        findings = rec["findings"]
        factors = sorted({fd["factor"] for fd in findings})
        measures = sorted({fd["measure"] for fd in findings
                           if fd.get("measure") and fd.get("verdict") in {"supports", "mixed", "contradicts"}})
        if key.lower() in existing:
            path, src = existing[key.lower()]
            src["findings"] = [x for x in src.get("findings") or []
                               if not str(x.get("ref", "")).startswith("research/factor-evidence/")] + findings
            src["factors"] = sorted(set(src.get("factors") or []) | set(factors))
            src["measurables"] = list(dict.fromkeys((src.get("measurables") or []) + measures))
            src = {k: v for k, v in src.items() if v not in (None, [], "")}
            path.write_text(yaml.safe_dump(src, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
            updated += 1
            continue

        cite = rec["cite"]
        notes = ["Imported from research/factor-evidence; findings are from abstracts only (AI-generated, not reviewed)."]
        if cite.get("doi"):
            meta = metadata(cite["doi"], offline)
            authors = meta.get("authors") or []
            family = meta.get("family") or (authors[0].split(",")[0] if authors else cite["key"].split()[0])
            year = meta.get("year")
            title = re.sub(r"<[^>]+>", "", meta.get("title") or cite.get("title") or "").strip() or None
            cited_year = cite["key"].split()[-1]
            if year and cited_year.isdigit() and int(cited_year) != year:
                notes.append(f"Evidence file cites it as {cited_year}; OpenAlex gives {year}.")
            src = dict(id=None, type="paper", title=title, authors=authors, year=year, doi=cite["doi"])
            if meta.get("container"):
                notes.append(f"Published in {meta['container']}.")
            if meta.get("oa"):
                src["oa"] = meta["oa"]
            if meta.get("oa_url") and meta.get("oa") != "closed":
                src["oa_url"] = meta["oa_url"]
        elif cite.get("lit"):
            lit_e = cite["lit"]
            family = lit_e["authors"][0].split(",")[0]
            year, title = lit_e["year"], lit_e["title"]
            src = dict(id=None, type="paper", title=title, authors=lit_e["authors"], year=year, url=lit_e["url"])
        else:
            family = cite["key"].split()[0]
            year = int(cite["key"].split()[-1]) if cite["key"].split()[-1].isdigit() else None
            title = cite.get("title")
            src = dict(id=None, type="paper", title=title, authors=[family.title()], year=year, url=cite["url"])
            notes.append("Metadata from the evidence file only; check title, authors and year.")
        src["id"] = make_id(family, year, title, taken)
        taken.add(src["id"])
        src["factors"] = factors
        src["measurables"] = measures
        src["findings"] = findings
        src["notes"] = " ".join(notes)
        src = {k: v for k, v in src.items() if v not in (None, [], "")}
        (HERE / f"{src['id']}.yaml").write_text(
            yaml.safe_dump(src, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
        written += 1

    print(f"{len(rows)} evidence rows, {len(by_ref)} papers: {written} new, {updated} updated.")
    for u in unresolved:
        print("unresolved:", u)
    for f in sorted(unknown_factors):
        print("unknown factor:", f)
    return 1 if unresolved or unknown_factors else 0


if __name__ == "__main__":
    sys.exit(main(offline="--offline" in sys.argv))
