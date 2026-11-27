"""Repo-root-anchored paths, so scripts give the same files whatever the working directory."""

import os
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent


def _main_checkout(repo):
    """The main checkout of a git worktree (repo itself if it isn't a worktree)."""
    git = repo / ".git"
    if not git.is_file():  # main checkout: .git is a folder
        return repo
    gitdir = pathlib.Path(git.read_text(encoding="utf-8").split("gitdir:", 1)[1].strip())
    common = gitdir / "commondir"  # .git/worktrees/<name>/commondir -> ../..
    common = (gitdir / common.read_text(encoding="utf-8").strip()).resolve() if common.exists() else gitdir.parents[1]
    return common.parent


# Raw downloads live in one place shared by the main checkout and all its worktrees, so they
# are downloaded once and survive worktree cleanup. Set FERTILITY_DATA to keep them elsewhere.
DATA_ROOT = pathlib.Path(os.environ["FERTILITY_DATA"]) if os.environ.get("FERTILITY_DATA") else _main_checkout(REPO)


def data_dir(folder):
    """<main checkout>/<folder>/data (downloaded inputs, not tracked in git)."""
    return DATA_ROOT / folder / "data"


def outputs_dir(folder):
    """<repo>/<folder>/outputs (generated charts and tables, tracked in git)."""
    return REPO / folder / "outputs"


def intermediate_dir(folder):
    """<repo>/<folder>/intermediate (derived inputs shared between scripts, tracked in git
    but not published into the docs' _static like outputs/)."""
    return REPO / folder / "intermediate"
