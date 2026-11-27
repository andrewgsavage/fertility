"""Regenerate every output: run each <SOURCE>/scripts/*.py entry point in dependency order.

    pixi run outputs            # every source folder
    pixi run outputs ONS HFD    # only these source folders

A script whose input data isn't downloaded is skipped with a "missing data" note
rather than stopping the run: either its own <SOURCE>/data folder is absent, or it
fails with FileNotFoundError on a path under some */data/ folder. Downloads are
separate (see README.md); nothing here fetches data.
"""

import os
import re
import subprocess
import sys
import time

from common.paths import REPO, data_dir

# Modules other scripts import, or that only print a sample: they write nothing.
NOT_ENTRY_POINTS = {
    "eurostat/scripts/_common.py",
    "eurostat/scripts/abortion_by_age_national.py",
    "eurostat/scripts/scatter_chart.py",
    "eurostat/scripts/timeline_chart.py",
    "eurostat/scripts/young_fertility.py",
    "HFD/scripts/births_per_mother_period_grid.py",
    "HFD/scripts/births_per_mother_region_grid.py",
    "ONS/scripts/metrics.py",
    "ONS/scripts/pupils_leaving_age_uk.py",
    "ONS/scripts/births_per_mother_uk_ons.py",  # prints a sample from common/ons_births_per_mother.py
    "ONS/scripts/mdf_uk_ons.py",  # prints a sample from common/ons_mdf.py
    "NSO/scripts/download.py",  # downloads data; not part of regenerating outputs
    "NSO/scripts/births_by_order_download.py",  # downloads data; not part of regenerating outputs
    "FT/scripts/google_trends_app_stores.py",  # downloads data; not part of regenerating outputs
}

# Scripts whose outputs other scripts read, in the order they must run. Everything
# else runs after these, alphabetically.
RUN_FIRST = [
    "ONS/scripts/dhsc_parity_by_age.py",  # -> eurostat/scripts/abortion_parity.py
    "NSO/scripts/births_by_order_rates.py",  # -> HFD/scripts/cond_asfr_facet.py, eurostat/scripts/change_matrix.py
    "ILO/scripts/coupling_ilo.py",  # -> common/coupling_hfd.py
    "FT/scripts/ft_birth_rates_everywhere.py",  # -> FT/scripts/ft_birth_rates_charts.py, ft_headline_checks.py
    "FT/scripts/ft_coupling.py",  # -> common/coupling_hfd.py
    "NSO/scripts/coupling_nso.py",  # -> common/coupling_hfd.py
    "UN/scripts/coupling_un.py",  # -> UN, DHS coupling charts
    "DHS/scripts/dhs_mothers.py",  # -> DHS/scripts/coupling_vs_mothers.py
    "ONS/scripts/parse_csv.py",  # -> build_plotly_map.py, build_plotly_scatter.py
    "ONS/scripts/parse_housing_csv.py",  # -> build_plotly_scatter.py
    "ONS/scripts/parse_population_csv.py",  # -> build_plotly_scatter.py
    "ONS/scripts/simplify_geojson.py",  # -> build_plotly_map.py
    "ILO/scripts/separated_ilo.py",  # -> ILO/scripts/separation_vs_second_birth.py
    "eurostat/scripts/lone_parents_divorce_europe.py",  # -> ILO/scripts/separation_vs_second_birth.py
    "ONS/scripts/coupling_by_age_ew.py",  # -> ONS/scripts/births_by_union_ew.py
    "ONS/scripts/births_by_union_ew.py",  # -> HFD/scripts/couples_vs_births_per_couple.py
    "ACS/scripts/acs_births_by_union.py",  # -> HFD/scripts/couples_vs_births_per_couple.py
    "GGS/scripts/young_ideals_europe.py",  # -> eurostat/scripts/change_matrix.py
    "GSS/scripts/ideal_by_cohort_us.py",  # -> eurostat/scripts/change_matrix.py
]

# A script that reads its own source's data folder this way is skipped up front
# when that folder is absent.
OWN_DATA_RE = re.compile(r'data_dir\(\s*"(?P<src>[^"]+)"\s*\)|ROOT\s*/\s*"data"')
TIMEOUT = 600  # seconds per script; the slowest takes well under a minute
MISSING_DATA_RE =re.compile(r"FileNotFoundError: .*[\\/]data[\\/][^\n]*")


def entry_points(sources=None):
    scripts = sorted(
        (p.relative_to(REPO).as_posix() for p in REPO.glob("*/scripts/*.py")),
        key=str.lower,
    )
    scripts = [s for s in scripts if s not in NOT_ENTRY_POINTS]
    first = [s for s in RUN_FIRST if s in scripts]
    ordered = first + [s for s in scripts if s not in first]
    if sources:
        wanted = {s.strip("/\\").lower() for s in sources}
        ordered = [s for s in ordered if s.split("/")[0].lower() in wanted]
    return ordered


def own_data_missing(script):
    source = script.split("/")[0]
    text = (REPO / script).read_text(encoding="utf-8")
    if OWN_DATA_RE.search(text) and not data_dir(source).exists():
        return data_dir(source).relative_to(REPO).as_posix() + "/"
    return None


def run(script):
    """(status, detail) for one script: status is ran / skipped / failed."""
    missing = own_data_missing(script)
    if missing:
        return "skipped", f"missing data: {missing} not found"
    try:
        proc = subprocess.run(
            [sys.executable, str(REPO / script)],
            cwd=REPO,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return "failed", f"timed out after {TIMEOUT}s (a hung kaleido PNG export, if it writes PNGs; rerun it)"
    if proc.returncode == 0:
        return "ran", ""
    missing = MISSING_DATA_RE.search(proc.stderr)
    if missing:
        detail = missing.group(0).removeprefix("FileNotFoundError: ")
        for prefix in (str(REPO).replace("\\", "\\\\") + "\\\\", str(REPO) + os.sep):
            detail = detail.replace(prefix, "")
        return "skipped", "missing data: " + detail
    lines = [line for line in proc.stderr.strip().splitlines() if line.strip()]
    return "failed", (lines[-1] if lines else f"exit code {proc.returncode}"), proc.stderr


def main(argv):
    scripts = entry_points(argv)
    if not scripts:
        print(f"No scripts found for {argv}", file=sys.stderr)
        return 2
    results = {"ran": [], "skipped": [], "failed": []}
    for i, script in enumerate(scripts, 1):
        start = time.perf_counter()
        status, detail, *stderr = run(script)
        took = time.perf_counter() - start
        print(f"[{i}/{len(scripts)}] {status:7} {script} ({took:.1f}s){'  ' + detail if detail else ''}", flush=True)
        if stderr:
            tail = stderr[0].strip().splitlines()[-12:]  # end of the traceback
            print("    " + "\n    ".join(tail), flush=True)
        results[status].append((script, detail))

    print(f"\nSummary: {len(results['ran'])} ran, {len(results['skipped'])} skipped, {len(results['failed'])} failed")
    for status in ("skipped", "failed"):
        for script, detail in results[status]:
            print(f"  {status}: {script}: {detail}")
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
