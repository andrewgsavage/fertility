import csv
import json
import re

INPUT = "data/2820211563520880.csv"
OUTPUT = "outputs/population_by_lad.json"

# Female population estimates by 5-year age band (Nomis export). Unlike the
# births CSV (one "Date:" block per year, wide by metric), this file has one
# "Age:" block per age band, wide by year.
AGE_BAND_KEYS = {
    "Total": "pop_total",
    "Aged 15 - 19 years": "pop_15_19",
    "Aged 20 - 24 years": "pop_20_24",
    "Aged 25 - 29 years": "pop_25_29",
    "Aged 30 - 34 years": "pop_30_34",
    "Aged 35 - 39 years": "pop_35_39",
    "Aged 40 - 44 years": "pop_40_44",
    "Aged 45 - 49 years": "pop_45_49",
}

LAD_CODE_RE = re.compile(r"^[EWSN]\d{8}$")
# Same GSS code reissue as the births CSV — see parse_csv.py.
LAD_CODE_REMAP = {
    "E08000016": "E08000038",  # Barnsley
    "E08000019": "E08000039",  # Sheffield
}

data = {}
lad_names = {}
years = None
current_metric = None
header_seen = False

with open(INPUT, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        cells = [c.strip() for c in row]
        if not any(cells):
            continue
        # Each of the 8 age-band sections repeats the title/copyright lines
        # (single-cell rows), not just the first — skip anything too short
        # to be a real header or data row.
        if len(cells) < 2:
            continue
        if cells[0].startswith("Age"):
            current_metric = AGE_BAND_KEYS.get(cells[1])
            header_seen = False
            continue
        if current_metric is None:
            continue
        if cells[0].startswith("local authority"):
            years = cells[2:]
            for y in years:
                data.setdefault(y, {})
            header_seen = True
            continue
        if not header_seen:
            continue
        code = cells[1]
        if not LAD_CODE_RE.match(code):
            continue
        code = LAD_CODE_REMAP.get(code, code)
        lad_names[code] = cells[0]
        for year, raw in zip(years, cells[2:]):
            try:
                value = float(raw) if raw not in ("", "-", "..") else None
            except ValueError:
                value = None
            data[year].setdefault(code, {})[current_metric] = value

out = {
    "years": sorted(data.keys()),
    "metrics": list(AGE_BAND_KEYS.values()),
    "lad_names": lad_names,
    "data": data,
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))

print(f"Wrote {OUTPUT} ({len(lad_names)} LADs x {len(out['years'])} years x {len(AGE_BAND_KEYS)} age bands)")
