"""`{searches}` directive: render the search log in research/searches/*.yaml.

Options (optional): `:factor:` comma-separated factor tags from sources/_vocab.yaml; only
entries tagged with one of them are shown. The directive must be used on a page at the top of
docs/, so that links to `docs/...` pages resolve.
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

import yaml
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_SOURCES_DIR = _REPO_ROOT / "sources"


def _lib():
    sys.path.insert(0, str(_SOURCES_DIR))  # searches.py imports sources.py
    try:
        spec = importlib.util.spec_from_file_location("search_log_lib", _SOURCES_DIR / "searches.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.pop(0)


_LIB = _lib()
_STATUS_ORDER = {"open": 0, "partial": 1, "dead-end": 2, "answered": 3}


def _cell(text) -> str:
    return " ".join(str(text or "").split()).replace("|", "\\|")


def _page_link(path: str) -> str:
    if path.startswith("docs/") and path.endswith(".md"):
        return f"[{path[5:-3]}]({path[5:]})"
    return f"`{path}`"


class SearchesDirective(SphinxDirective):
    has_content = False
    option_spec = {"factor": directives.unchanged}

    def run(self):
        paths = _LIB.log_paths()
        for p in paths:
            self.env.note_dependency(str(p))
        factors = [f.strip() for f in (self.options.get("factor") or "").split(",") if f.strip()]
        entries = [yaml.safe_load(p.read_text(encoding="utf-8")) or {} for p in paths]
        if factors:
            entries = [e for e in entries if set(factors) & set(e.get("factors") or [])]
        entries.sort(key=lambda e: (_STATUS_ORDER.get(e.get("status"), 9), e.get("id", "")))
        return self.parse_text_to_nodes("\n\n".join(self._entry_md(e) for e in entries))

    def _entry_md(self, e: dict) -> str:
        out = [f"**{_cell(e.get('question'))}** ({e.get('status')}, `{e.get('id')}`)"]
        if e.get("answer"):
            out.append(f"Answer: {_cell(e['answer'])}")
        if e.get("pages"):
            out.append("Pages: " + ", ".join(_page_link(p) for p in e["pages"]))
        rows = ["| Date | Tried | Outcome | Why | Retry |", "|---|---|---|---|---|"]
        for a in e.get("attempts") or []:
            tried = _cell(a.get("tried"))
            if a.get("url"):
                tried = f"[{tried}]({a['url']})"
            rows.append(f"| {a.get('date')} | {tried} | {a.get('outcome')} | {_cell(a.get('why'))} | {_cell(a.get('retry'))} |")
        out.append("\n".join(rows))
        if e.get("next"):
            out.append(f"Next: {_cell(e['next'])}")
        if e.get("notes"):
            out.append(f"Notes: {_cell(e['notes'])}")
        return "\n\n".join(out)


def _outdated_on_new_files(app, env, added, changed, removed):
    """Rebuild pages using {searches} when a log file is added or deleted."""
    files = sorted(p.name for p in _LIB.log_paths())
    previous = getattr(env, "search_log_files", None)
    env.search_log_files = files
    if previous == files:
        return []
    return [d for d in env.found_docs
            if "{searches}" in pathlib.Path(env.doc2path(d)).read_text(encoding="utf-8")]


def setup(app: Sphinx):
    app.add_directive("searches", SearchesDirective)
    app.connect("env-get-outdated", _outdated_on_new_files)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
