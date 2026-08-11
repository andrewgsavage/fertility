import csv
import json
import re

INPUT = "data/359847807070781.csv"
OUTPUT = "outputs/fertility_by_lad.json"

METRIC_KEYS = [
    "live_births",
    "crude_birth_rate",
    "gfr",
    "tfr",
    "asfr_under18",
    "asfr_under20",
    "asfr_20_24",
    "asfr_25_29",
    "asfr_30_34",
    "asfr_35_39",
    "asfr_40_44",
    "asfr_45plus",
    "mean_age_mother",
]

ASFR_KEYS = [k for k in METRIC_KEYS if k.startswith("asfr_")]
BASELINE_YEAR = "2013"
REL_METRIC_KEYS = [f"{k}_rel2013" for k in ASFR_KEYS]

LAD_CODE_RE = re.compile(r"^[EWSN]\d{8}$")

# ONS retired and reissued these two GSS codes; the Nomis fertility export
# still uses the old ones, while the LAD boundary file uses the new ones.
LAD_CODE_REMAP = {
    "E08000016": "E08000038",  # Barnsley
    "E08000019": "E08000039",  # Sheffield
}

years = {}
lad_names = {}
current_year = None

with open(INPUT, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        cells = [c.strip() for c in row]
        if not any(cells):
            continue
        if cells[0].startswith("Date"):
            current_year = cells[1]
            years.setdefault(current_year, {})
            continue
        if current_year is None or len(cells) < 15:
            continue
        code = cells[14]
        if not LAD_CODE_RE.match(code):
            continue
        code = LAD_CODE_REMAP.get(code, code)
        name = cells[13]
        values = cells[:13]
        try:
            record = {k: (float(v) if v not in ("", "-", "..") else None) for k, v in zip(METRIC_KEYS, values)}
        except ValueError:
            continue
        years[current_year][code] = record
        lad_names[code] = name

baseline_year_data = years.get(BASELINE_YEAR, {})
for year, rows in years.items():
    for code, record in rows.items():
        baseline_record = baseline_year_data.get(code)
        for asfr_key, rel_key in zip(ASFR_KEYS, REL_METRIC_KEYS):
            value = record.get(asfr_key)
            baseline = baseline_record.get(asfr_key) if baseline_record else None
            if value is None or baseline is None or baseline == 0:
                record[rel_key] = None
            else:
                record[rel_key] = (value - baseline) / baseline

out = {
    "years": sorted(years.keys()),
    "metrics": METRIC_KEYS + REL_METRIC_KEYS,
    "baseline_year": BASELINE_YEAR,
    "lad_names": lad_names,
    "data": years,
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))

n_lads = len(lad_names)
n_years = len(years)
print(f"Wrote {OUTPUT} ({n_lads} LADs x {n_years} years)")
