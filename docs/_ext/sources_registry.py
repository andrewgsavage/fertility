"""`{sources}` directive: render entries from the sources/ registry (sources/*.yaml).

Options (all optional; values are comma-separated tags from sources/_vocab.yaml):

    :factor:      sources tagged with, or with findings on, any of these factors
    :measurable:  sources tagged with any of these measurables
    :type:        paper, report, book, dataset, survey, web
    :filter:      flag: add type/factor/measurable dropdowns above the table

With `:factor:` the directive renders that factor's findings (one row per finding, grouped by
outcome column) followed by the other matching sources. Without it, it renders one row per
source. Every registry file is a build dependency of the page, so editing a YAML rebuilds it.
"""

from __future__ import annotations

import importlib.util
import pathlib

from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_SOURCES_DIR = _REPO_ROOT / "sources"


def _registry():
    spec = importlib.util.spec_from_file_location("sources_registry_lib", _SOURCES_DIR / "sources.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_LIB = _registry()
_VOCAB = _LIB.load_vocab()
_FACTOR_LABELS = {k: v["label"] for k, v in _VOCAB["factors"].items()}
_MEASURE_LABELS = {k: v["label"] for k, v in _VOCAB["measurables"].items()}
_MEASURE_ORDER = list(_VOCAB["measurables"])
_TICK = {"yes": "✓", "no": "blank", "?": "?"}
_VERDICT_ORDER = {"contradicts": 0, "supports": 1, "mixed": 2, "no-evidence": 3, None: 4}


def _cell(text) -> str:
    return " ".join(str(text or "").split()).replace("|", "\\|")


def _short_authors(src: dict) -> str:
    authors = src.get("authors") or []
    names = [a.split(",")[0].strip() for a in authors]
    if not names:
        return src.get("publisher", "")
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    return f"{names[0]} et al."


def _link(src: dict) -> str:
    if src.get("doi"):
        return f"https://doi.org/{src['doi']}"
    return src.get("url", "")


def _cite(src: dict, with_title: bool = True) -> str:
    who = _short_authors(src)
    year = src.get("year") or "n.d."
    label = f"{who} {year}" if src.get("type") in {"paper", "report", "book"} else src["title"]
    url = _link(src)
    out = f"[{_cell(label)}]({url})" if url else _cell(label)
    if with_title and src.get("type") in {"paper", "report", "book"}:
        out += f", *{_cell(src.get('title'))}*"
    if src.get("oa_url") and src.get("oa") != "closed" and src.get("oa_url") != url:
        out += f" ([free copy]({src['oa_url']}))"
    return out


def _split(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


class SourcesDirective(SphinxDirective):
    has_content = False
    option_spec = {
        "factor": directives.unchanged,
        "measurable": directives.unchanged,
        "type": directives.unchanged,
        "filter": directives.flag,
    }

    def run(self):
        for p in _LIB.source_paths():
            self.env.note_dependency(str(p))
        self.env.note_dependency(str(_SOURCES_DIR / "_vocab.yaml"))
        srcs = _LIB.load()

        factors, measures, types = (_split(self.options.get(k)) for k in ("factor", "measurable", "type"))
        for f in factors:
            if f not in _FACTOR_LABELS:
                raise self.error(f"unknown factor {f!r} (see sources/_vocab.yaml)")
        for m in measures:
            if m not in _MEASURE_LABELS:
                raise self.error(f"unknown measurable {m!r} (see sources/_vocab.yaml)")

        def keep(s):
            if types and s.get("type") not in types:
                return False
            if factors and not (set(factors) & set(s["all_factors"])
                                or any(fd.get("factor") in factors for fd in s.get("findings") or [])):
                return False
            if measures and not set(measures) & set(s.get("measurables") or []):
                return False
            return True

        chosen = sorted((s for s in srcs if keep(s)), key=lambda s: (_short_authors(s).lower(), s.get("year") or 0))
        md = self._findings_md(chosen, factors) if factors else self._sources_md(chosen, "filter" in self.options)
        return self.parse_text_to_nodes(md)

    def _findings_md(self, chosen: list[dict], factors: list[str]) -> str:
        rows = []
        for s in chosen:
            for fd in s.get("findings") or []:
                if fd.get("factor") in factors:
                    rows.append((s, fd))
        rows.sort(key=lambda r: (
            _MEASURE_ORDER.index(r[1]["measure"]) if r[1].get("measure") in _MEASURE_ORDER else 99,
            _VERDICT_ORDER.get(r[1].get("verdict"), 9), _short_authors(r[0]).lower()))
        out = []
        if rows:
            many = len(factors) > 1
            head = "| " + ("Factor | " if many else "") + "Column | Tick | Verdict | Read | Source | Finding |"
            out += [head, "|" + "---|" * (7 if many else 6)]
            for s, fd in rows:
                verdict = fd.get("verdict") or "mentioned"
                if verdict == "contradicts":
                    verdict = "**contradicts**"
                read = "full text" if fd.get("basis") == "fulltext" else "abstract"
                col = _MEASURE_LABELS.get(fd.get("measure"), "all columns")
                fac = f"{_FACTOR_LABELS[fd['factor']]} | " if many else ""
                out.append(f"| {fac}{_cell(col)} | {_TICK.get(fd.get('tick'), '')} | {verdict} | {read} | "
                           f"{_cite(s, with_title=False)} | {_cell(fd.get('note'))} |")
        others = [s for s in chosen if not any(fd.get("factor") in factors for fd in s.get("findings") or [])]
        if others:
            out += ["", "Other sources tagged with this factor:", ""]
            out += [f"- {_cite(s)}" for s in others]
        if not out:
            out = ["No sources in the registry for this factor yet."]
        return "\n".join(out) + "\n"

    def _sources_md(self, chosen: list[dict], with_filter: bool) -> str:
        out = []
        if with_filter:
            out.append(self._filter_html(chosen))
        out += ["", ":::{container} sources-table", "",
                "| Source | Type | Factors | Measurables | Findings |", "|---|---|---|---|---|"]
        for s in chosen:
            fds = s.get("findings") or []
            ft = sum(1 for f in fds if f.get("basis") == "fulltext")
            find = f"{len(fds)} ({ft} full text)" if fds else ""
            out.append(
                f"| {_cite(s)} | {s.get('type')} | "
                f"{_cell('; '.join(_FACTOR_LABELS[f] for f in sorted(set(s['all_factors']))))} | "
                f"{_cell('; '.join(_MEASURE_LABELS[m] for m in s.get('measurables') or []))} | {find} |")
        out += ["", ":::", ""]
        return "\n".join(out)

    def _filter_html(self, chosen: list[dict]) -> str:
        def options(values):
            return "".join(f'<option value="{v}">{v}</option>' for v in values)

        types = sorted({s.get("type") for s in chosen})
        facs = sorted({_FACTOR_LABELS[f] for s in chosen for f in s["all_factors"]})
        meas = sorted({_MEASURE_LABELS[m] for s in chosen for m in s.get("measurables") or []})
        return f"""```{{raw}} html
<div class="sources-filter">
  <label>Type <select data-col="1"><option value="">all</option>{options(types)}</select></label>
  <label>Factor <select data-col="2"><option value="">all</option>{options(facs)}</select></label>
  <label>Measurable <select data-col="3"><option value="">all</option>{options(meas)}</select></label>
  <span class="sources-filter-count"></span>
</div>
<style>
  .sources-filter {{ display: flex; flex-wrap: wrap; gap: 0.4em 1em; font-size: 0.9em; margin-bottom: 0.5em; }}
  .sources-filter select {{ margin-left: 0.2em; max-width: 16em; }}
  .sources-filter-count {{ color: var(--color-foreground-secondary); }}
  .sources-table td {{ vertical-align: top; }}
</style>
<script>
document.addEventListener("DOMContentLoaded", () => {{
  const box = document.querySelector(".sources-filter");
  const rows = [...document.querySelectorAll(".sources-table tbody tr")];
  const count = box.querySelector(".sources-filter-count");
  const apply = () => {{
    const sel = [...box.querySelectorAll("select")].filter(s => s.value);
    let n = 0;
    rows.forEach(r => {{
      const ok = sel.every(s => {{
        const text = r.cells[+s.dataset.col].textContent;
        return s.dataset.col === "1" ? text.trim() === s.value : text.split("; ").map(t => t.trim()).includes(s.value);
      }});
      r.style.display = ok ? "" : "none";
      n += ok;
    }});
    count.textContent = n + " of " + rows.length + " sources";
  }};
  box.addEventListener("change", apply);
  apply();
}});
</script>
```
"""


def setup(app: Sphinx):
    app.add_directive("sources", SourcesDirective)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
