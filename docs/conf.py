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
    "region_tabs",
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
# HFD/outputs, ONS/outputs, and resolution/outputs are the git-tracked,
# canonical outputs of the analysis scripts. They are copied into
# docs/_static/<name> at build time (not duplicated in git) so pages can
# reference them as ordinary static assets.
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_OUTPUT_DIRS = {
    "hfd": _REPO_ROOT / "HFD" / "outputs",
    "ons": _REPO_ROOT / "ONS" / "outputs",
    "resolution": _REPO_ROOT / "resolution" / "outputs",
    "democracy": _REPO_ROOT / "democracy" / "outputs",
}


def _copy_outputs(app, config):
    static_dir = pathlib.Path(app.confdir) / "_static"
    for name, src in _OUTPUT_DIRS.items():
        if not src.exists():
            continue
        dest = static_dir / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)


def setup(app):
    app.connect("config-inited", _copy_outputs)
