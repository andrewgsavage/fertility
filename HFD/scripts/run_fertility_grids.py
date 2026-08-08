import subprocess
import sys

for script in ("scripts/cond_asfr_grid.py", "scripts/cond_asfr_cohort_grid.py", "scripts/cpfr_grid.py"):
    print(f"Running {script}")
    subprocess.run([sys.executable, script], check=True)
