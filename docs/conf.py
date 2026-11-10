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
]

myst_enable_extensions = [
    "colon_fence",
]

html_theme = "furo"
html_title = "Fertility"
html_static_path = ["_static"]

# --- Copy generated outputs into _static so pages can reference them ---
#
# HFD/outputs, ONS/outputs, resolution/outputs, and OWID/outputs are the
# git-tracked, canonical outputs of the analysis scripts. They are copied
# into docs/_static/<name> at build time (not duplicated in git) so pages
# can reference them as ordinary static assets.
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_OUTPUT_DIRS = {
    "hfd": _REPO_ROOT / "HFD" / "outputs",
    "ons": _REPO_ROOT / "ONS" / "outputs",
    "resolution": _REPO_ROOT / "resolution" / "outputs",
    "owid": _REPO_ROOT / "OWID" / "outputs",
    "democracy": _REPO_ROOT / "democracy" / "outputs",
    "eurostat": _REPO_ROOT / "eurostat" / "outputs",
    "housing": _REPO_ROOT / "housing" / "outputs",
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
        if src.exists():
            _sync_dir(src, static_dir / name)


def setup(app):
    app.connect("config-inited", _copy_outputs)
