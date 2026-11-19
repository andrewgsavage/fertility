"""Download open-access full texts for papers in sources/ and extract their text.

Writes $PAPERS_DIR/<id>.pdf and <id>.txt (PAPERS_DIR defaults to ~/papers; outside the
repo, never committed). Candidate links come from the cached OpenAlex record
(sources/.cache/, filled by import_factor_evidence.py): each open-access location's
PDF link, then its landing page's `citation_pdf_url` meta tag, then the entry's
`oa_url`. A download counts only if the bytes start with %PDF.

Results go to $PAPERS_DIR/_fetch_log.json: per id, the status, the URL used and the
version (publishedVersion / acceptedVersion / submittedVersion). Papers with a PDF
already present are skipped, but still get a .txt if missing, so hand-added PDFs
(paywalled papers) only need dropping into the folder as <id>.pdf.

    pixi run python sources/fetch_fulltexts.py [--retry-failed] [--only ID ...]
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
import yaml
from pypdf import PdfReader

from import_factor_evidence import CACHE, cached_get, slug
from sources import papers_dir, source_paths

UA = {"User-Agent": "fertility-docs-sources/0.1 (open-access full-text fetch)"}
MAX_BYTES = 60 * 1024 * 1024
META_PDF = re.compile(
    r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)["\']'
    r'|<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
    re.I,
)


def openalex(src: dict) -> dict | None:
    doi = str(src["doi"])
    return cached_get(f"openalex-{doi}", f"https://api.openalex.org/works/doi:{doi}", offline=False)


def pmcid(src: dict) -> str | None:
    oa = openalex(src) or {}
    m = re.search(r"(\d+)/?$", str((oa.get("ids") or {}).get("pmcid") or ""))
    if m:
        return f"PMC{m.group(1)}"
    for url, _ in candidates(src):
        m = re.search(r"/(PMC\d+)", url)
        if m:
            return m.group(1)
    return None


def europepmc_text(pmc: str) -> tuple[str, str] | None:
    """Full text from the Europe PMC REST API (JATS XML), for PMC-hosted papers."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
    r = get(url)
    if r is None or not r.ok or b"<article" not in r.content[:5000]:
        return None
    root = ET.fromstring(r.content)
    blocks = []
    for el in root.iter():
        if el.tag in {"article-title", "title"}:
            blocks.append("\n## " + " ".join("".join(el.itertext()).split()))
        elif el.tag == "p":
            blocks.append(" ".join("".join(el.itertext()).split()))
    return r.content.decode("utf-8", "ignore"), "\n\n".join(b for b in blocks if b.strip()) + "\n"


def candidates(src: dict) -> list[tuple[str, str | None]]:
    """(url, version) pairs, best first: direct PDF links, then landing pages."""
    pdfs, pages = [], []
    oa = openalex(src)
    if oa:
        locs = [oa.get("best_oa_location")] + list(oa.get("locations") or [])
        for loc in locs:
            if not loc or not loc.get("is_oa"):
                continue
            if loc.get("pdf_url"):
                pdfs.append((loc["pdf_url"], loc.get("version")))
            if loc.get("landing_page_url"):
                pages.append((loc["landing_page_url"], loc.get("version")))
    if src.get("oa_url"):
        pdfs.append((src["oa_url"], None))
    pages.append((f"https://doi.org/{src['doi']}", None))  # publisher page's citation_pdf_url
    seen, out = set(), []
    for url, ver in pdfs + pages:
        if url not in seen:
            seen.add(url)
            out.append((url, ver))
    return out


def get(url: str) -> requests.Response | None:
    try:
        r = requests.get(url, headers=UA, timeout=45, stream=True, allow_redirects=True)
        body = r.raw.read(MAX_BYTES + 1, decode_content=True)
        r._content = body
        return r
    except requests.RequestException:
        return None


def fetch_pdf(src: dict) -> tuple[bytes | None, dict]:
    tried = []
    for url, version in candidates(src):
        r = get(url)
        if r is None:
            tried.append(f"{url}: error")
            continue
        body = r.content
        if r.ok and body[:5] == b"%PDF-" and len(body) <= MAX_BYTES:
            return body, {"url": url, "version": version}
        if r.ok and b"<html" in body[:2000].lower():
            m = META_PDF.search(body.decode("utf-8", "ignore"))
            if m:
                pdf_url = urljoin(r.url, m.group(1) or m.group(2))
                r2 = get(pdf_url)
                if r2 is not None and r2.ok and r2.content[:5] == b"%PDF-":
                    return r2.content, {"url": pdf_url, "version": version}
                tried.append(f"{pdf_url}: {getattr(r2, 'status_code', 'error')} via meta tag")
                continue
        tried.append(f"{url}: {r.status_code} {r.headers.get('content-type', '')[:30]}")
        time.sleep(0.5)
    return None, {"tried": tried}


def extract_text(pdf: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf))
    pages = []
    for i, page in enumerate(reader.pages, 1):
        try:
            pages.append(f"\n\n--- page {i} ---\n\n" + (page.extract_text() or ""))
        except Exception as e:  # malformed pages shouldn't lose the rest
            pages.append(f"\n\n--- page {i}: extraction failed ({type(e).__name__}) ---\n\n")
    return "".join(pages).strip() + "\n"


def write_missing(pdir, papers: list[dict], log: dict) -> None:
    """Checklist of papers with no local text, for downloading by hand as <id>.pdf."""
    rows = []
    for s in sorted(papers, key=lambda s: s["id"]):
        if (pdir / f"{s['id']}.txt").exists():
            continue
        status = log.get(s["id"], {}).get("status") or ("no doi" if not s.get("doi") else "not tried")
        link = f"https://doi.org/{s['doi']}" if s.get("doi") else s.get("url", "")
        alt = s.get("oa_url") if s.get("oa_url") and s.get("oa_url") != link else ""
        n = len(s.get("findings") or [])
        rows.append(f"| `{s['id']}.pdf` | {s.get('title', '')} | {status} | {n} | {link} | {alt} |")
    (pdir / "_missing.md").write_text(
        "# Papers with no local full text\n\n"
        "Save each as the file name shown, in this folder, then run `pixi run sources-fetch` to extract text.\n"
        "Findings = how many factor-table findings rest on this paper's abstract.\n\n"
        "| save as | title | status | findings | link | open-access link |\n|---|---|---|---|---|---|\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    retry = "--retry-failed" in args
    only = set(args[args.index("--only") + 1:]) if "--only" in args else None
    pdir = papers_dir()
    pdir.mkdir(parents=True, exist_ok=True)
    log_path = pdir / "_fetch_log.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}

    srcs = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in source_paths()]
    papers = [s for s in srcs if s.get("type") in {"paper", "report", "book"}]
    if only:
        papers = [s for s in papers if s["id"] in only]

    counts = {"have": 0, "fetched": 0, "failed": 0, "closed": 0, "no-doi": 0, "skipped": 0}
    for src in papers:
        sid = src["id"]
        pdf_path, txt_path = pdir / f"{sid}.pdf", pdir / f"{sid}.txt"
        if txt_path.exists() and not pdf_path.exists():
            counts["have"] += 1
            continue
        if pdf_path.exists():
            if not txt_path.exists():
                txt_path.write_text(extract_text(pdf_path.read_bytes()), encoding="utf-8")
            counts["have"] += 1
            continue
        if not src.get("doi"):
            counts["no-doi"] += 1
            continue
        if src.get("oa") == "closed" or not src.get("oa"):
            counts["closed"] += 1
            log.setdefault(sid, {"status": "closed"})
            continue
        if log.get(sid, {}).get("status") == "failed" and not retry:
            counts["skipped"] += 1
            continue
        pdf, info = fetch_pdf(src)
        pmc = None if pdf else pmcid(src)
        epmc = europepmc_text(pmc) if pmc else None
        if epmc:
            (pdir / f"{sid}.xml").write_text(epmc[0], encoding="utf-8")
            txt_path.write_text(epmc[1], encoding="utf-8")
            log[sid] = {"status": "fetched", "url": f"europepmc:{pmc}", "version": "publishedVersion"}
            counts["fetched"] += 1
            print(f"ok    {sid}  (Europe PMC XML)")
        elif pdf:
            pdf_path.write_bytes(pdf)
            txt_path.write_text(extract_text(pdf), encoding="utf-8")
            log[sid] = {"status": "fetched", **info}
            counts["fetched"] += 1
            print(f"ok    {sid}  ({info.get('version') or 'version unknown'})")
        else:
            log[sid] = {"status": "failed", **info}
            counts["failed"] += 1
            print(f"fail  {sid}")
        log_path.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
        time.sleep(1)

    log_path.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
    write_missing(pdir, [s for s in srcs if s.get("type") in {"paper", "report", "book"}], log)
    print("\n" + ", ".join(f"{k}: {v}" for k, v in counts.items()) + f"  ->  {pdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
