import csv
import json
import re

HOUSE_PRICE_IN = "data/average-house-price-line.csv"
AFFORDABILITY_IN = "data/housing-affordability-ratio-line.csv"
OUTPUT = "outputs/housing_by_lad.json"

# Both are simple long-format ONS "Explore Local Statistics" exports
# (areacd, areanm, period, value) rather than the wide Nomis layout used
# elsewhere — house price is monthly, affordability is already annual
# (dated each April), so both are read at the April row for a given year to
# get one comparable value per year. Codes are already the current GSS
# codes (post Barnsley/Sheffield reissue), unlike the older Nomis exports.
LAD_CODE_RE = re.compile(r"^[EW]\d{8}$")


def read_april_values(path):
    """{year: {code: value}} from the April row of each year, plus
    {code: name} for rows seen."""
    values = {}
    names = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = row["areacd"]
            if not LAD_CODE_RE.match(code):
                continue
            period = row["period"]
            if period[4:10] != "-04-01":
                continue
            year = period[:4]
            raw = row["value"]
            try:
                value = float(raw) if raw not in ("", "-", "..") else None
            except ValueError:
                value = None
            values.setdefault(year, {})[code] = value
            names[code] = row["areanm"]
    return values, names


house_price, house_price_names = read_april_values(HOUSE_PRICE_IN)
affordability, affordability_names = read_april_values(AFFORDABILITY_IN)

lad_names = {**house_price_names, **affordability_names}
years = sorted(set(house_price) | set(affordability))
data = {year: {} for year in years}
for year in years:
    for code, name in lad_names.items():
        record = {}
        if code in house_price.get(year, {}):
            record["house_price"] = house_price[year][code]
        if code in affordability.get(year, {}):
            record["affordability_ratio"] = affordability[year][code]
        if record:
            data[year][code] = record

# Same "% change vs 2013" convention as parse_csv.py's ASFR rel2013 fields:
# (value - baseline) / baseline, stored as a fraction (e.g. -0.15 for -15%).
BASELINE_YEAR = "2013"
METRIC_KEYS = ["house_price", "affordability_ratio"]
REL_METRIC_KEYS = [f"{k}_rel2013" for k in METRIC_KEYS]
baseline_year_data = data.get(BASELINE_YEAR, {})
for year, rows in data.items():
    for code, record in rows.items():
        baseline_record = baseline_year_data.get(code)
        for metric, rel_key in zip(METRIC_KEYS, REL_METRIC_KEYS):
            value = record.get(metric)
            baseline = baseline_record.get(metric) if baseline_record else None
            if value is None or baseline is None or baseline == 0:
                record[rel_key] = None
            else:
                record[rel_key] = (value - baseline) / baseline

out = {
    "years": years,
    "metrics": METRIC_KEYS + REL_METRIC_KEYS,
    "baseline_year": BASELINE_YEAR,
    "lad_names": lad_names,
    "data": data,
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))

print(f"Wrote {OUTPUT} ({len(lad_names)} LADs x {len(years)} years)")
