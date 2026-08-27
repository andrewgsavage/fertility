"""Data table: for each TFR threshold, per-country stats on the trajectory
after first dropping below it.

For every major country (population over 1 million) that has ever dropped
below a given threshold: the year it first crossed below, the average TFR
from that year onwards, the trough (min) TFR and year, the peak TFR reached
anywhere in the plotted series (from the crossing year onwards — the same
window tfr_threshold_year.py plots), and the average TFR over the years
following the trough.
"""

import pandas as pd
import re

INPUT = "data/children-born-per-woman.csv"
POPULATION_INPUT = "data/population.csv"
OUTPUT = "outputs/tfr_threshold_table.csv"

THRESHOLDS = [1.1, 1.2, 1.3, 1.4, 1.5]
MIN_POPULATION = 1_000_000
ISO3_RE = re.compile(r"^[A-Z]{3}$")

df = pd.read_csv(INPUT).sort_values(["entity", "year"])

series = {}
for entity, rows in df.groupby("entity"):
    series[entity] = {
        "years": rows["year"].to_numpy(),
        "tfr": rows["fertility_rate_hist"].to_numpy(),
    }

pop_df = pd.read_csv(POPULATION_INPUT).sort_values(["entity", "year"])
latest_pop = pop_df.groupby("entity").last()
major_entities = {
    entity
    for entity, row in latest_pop.iterrows()
    if isinstance(row["code"], str) and ISO3_RE.match(row["code"]) and row["population_historical"] > MIN_POPULATION
}

entities = sorted(e for e in series if e in major_entities)

rows = []
for threshold in THRESHOLDS:
    for entity in entities:
        years = series[entity]["years"]
        tfr = series[entity]["tfr"]

        below = tfr < threshold
        if not below.any():
            continue
        cross_idx = below.argmax()
        cross_year = int(years[cross_idx])
        tail_years = years[cross_idx:]
        tail_tfr = tfr[cross_idx:]
        avg_after_cross = float(tail_tfr.mean())

        # Peak: the highest point anywhere in the plotted series (from the
        # crossing year onwards), matching what tfr_threshold_year.py draws.
        peak_idx_rel = tail_tfr.argmax()
        peak_tfr = float(tail_tfr[peak_idx_rel])
        peak_year = int(tail_years[peak_idx_rel])

        # Trough: minimum TFR from the crossing year onwards.
        min_idx_rel = tail_tfr.argmin()
        min_idx = cross_idx + min_idx_rel
        min_tfr = float(tfr[min_idx])
        min_year = int(years[min_idx])

        after = slice(min_idx + 1, None)
        after_years = years[after]
        after_tfr = tfr[after]

        if len(after_tfr) > 0:
            avg_tfr = float(after_tfr.mean())
            avg_period = f"{int(after_years[0])}-{int(after_years[-1])}"
        else:
            avg_tfr = None
            avg_period = ""

        rows.append({
            "threshold": threshold,
            "country": entity,
            "year_dropped_below": cross_year,
            "avg_tfr_after_cross": round(avg_after_cross, 3),
            "min_tfr": round(min_tfr, 3),
            "min_tfr_year": min_year,
            "subsequent_peak_tfr": round(peak_tfr, 3),
            "subsequent_peak_tfr_year": peak_year,
            "avg_tfr_after_min": round(avg_tfr, 3) if avg_tfr is not None else "",
            "avg_tfr_period": avg_period,
        })

out_df = pd.DataFrame(rows)
out_df.to_csv(OUTPUT, index=False)

print(f"Wrote {OUTPUT} ({len(out_df)} rows across {len(THRESHOLDS)} thresholds)")
