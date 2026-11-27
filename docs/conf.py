import filecmp
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "_ext"))

project = "Fertility"
copyright = "2026, Andrew Savage"
author = "Andrew Savage"

extensions = [
    "myst_parser",
    "sphinx_design",
    "scatter_controls",
    "sources_registry",
    "search_log",
]

myst_enable_extensions = [
    "colon_fence",
]

html_theme = "furo"
html_title = "Fertility"
html_static_path = ["_static"]

# --- Copy generated outputs into _static so pages can reference them ---
#
# Each top-level <SOURCE>/outputs folder (HFD, ONS, OWID, eurostat, ...) holds
# the git-tracked, canonical outputs of that source's analysis scripts. At
# build time every one is mirrored into docs/_static/<source, lowercased>/
# (e.g. HFD/outputs -> _static/hfd/) so pages can reference the files as
# ordinary static assets. The copies are gitignored, not duplicated in git.
# A new source folder with an outputs/ dir is picked up automatically.
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_OUTPUT_DIRS = {
    src.parent.name.lower(): src
    for src in sorted(_REPO_ROOT.glob("*/outputs"))
    if src.is_dir()
    and src.parent.name != "docs"
    and not src.parent.name.startswith((".", "_"))
}


def _sync_dir(src, dest):
    """Mirror src into dest, touching only files whose content differs.

    Rewriting unchanged files would look like an edit to sphinx-autobuild
    (which watches docs/), triggering an endless rebuild/reload loop.
    """
    wanted = set()
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        wanted.add(rel)
        target = dest / rel
        if target.exists() and filecmp.cmp(path, target, shallow=False):
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    if dest.exists():
        for path in dest.rglob("*"):
            if path.is_file() and path.relative_to(dest) not in wanted:
                path.unlink()


def _copy_outputs(app, config):
    static_dir = pathlib.Path(app.confdir) / "_static"
    for name, src in _OUTPUT_DIRS.items():
        _sync_dir(src, static_dir / name)


def setup(app):
    app.connect("config-inited", _copy_outputs)
