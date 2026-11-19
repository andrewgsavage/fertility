"""Repo-root-anchored paths, so scripts give the same files whatever the working directory."""

import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent


def data_dir(folder):
    """<repo>/<folder>/data (downloaded inputs, not tracked in git)."""
    return REPO / folder / "data"


def outputs_dir(folder):
    """<repo>/<folder>/outputs (generated charts and tables, tracked in git)."""
    return REPO / folder / "outputs"


def intermediate_dir(folder):
    """<repo>/<folder>/intermediate (derived inputs shared between scripts, tracked in git
    but not published into the docs' _static like outputs/)."""
    return REPO / folder / "intermediate"
