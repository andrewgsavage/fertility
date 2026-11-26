"""Check headline comparisons in the FT's "Why birth rates are falling everywhere all at
once" (16 May 2026) against UN World Population Prospects 2024 (via Our World in Data).

- "In more than two-thirds of the world's 195 countries" TFR is below 2.1, and "in 66
  countries" it is closer to one than to two (below 1.5).
- "In 2023 Mexico's birth rate fell below that of the US for the first time."

Inputs: OWID/data/fertility-rate-with-projections.csv (estimates to 2023, medium-variant
projections after), OWID/data/population.csv, FT/outputs/ft_birth_rates_everywhere.csv.
Outputs: FT/outputs/ft_headline_counts.csv, FT/outputs/ft_mexico_vs_us.csv.
"""

import pandas as pd

from common.paths import data_dir, outputs_dir

OWID = data_dir("OWID")
OUT = outputs_dir("FT")
EST = "fertility_rate__sex_all__age_all__variant_estimates"
PROJ = "fertility_rate__sex_all__age_all__variant_medium__projected"


def counts():
    d = pd.read_csv(OWID / "fertility-rate-with-projections.csv")
    d = d[d.code.str.fullmatch(r"[A-Z]{3}", na=False)]  # countries and territories, no aggregates
    d["tfr"] = d[EST].fillna(d[PROJ])
    pop = pd.read_csv(OWID / "population.csv")
    pop = pop[pop.year == 2023].set_index("code").population_historical
    d["pop"] = d.code.map(pop)
    rows = []
    for year in [2023, 2025]:
        for min_pop, label in [(0, "All 236 countries and territories"), (90_000, "Population 90,000+")]:
            s = d[(d.year == year) & (d["pop"] >= min_pop)]
            rows.append({"year": year, "set": label, "n": len(s),
                         "below_2.1": int((s.tfr < 2.1).sum()), "share_below_2.1": round((s.tfr < 2.1).mean(), 3),
                         "below_1.5": int((s.tfr < 1.5).sum()),
                         "basis": "estimate" if year <= 2023 else "medium-variant projection"})
    return pd.DataFrame(rows)


def mexico_vs_us():
    ft = pd.read_csv(OUT / "ft_birth_rates_everywhere.csv")
    ft = ft[ft.chart == "mexico_vs_us"].pivot(index="year", columns="series", values="value").add_prefix("FT ")
    w = pd.read_csv(OWID / "children-born-per-woman.csv")
    w = w[w.entity.isin(["Mexico", "United States"])].pivot(index="year", columns="entity",
                                                              values="fertility_rate_hist")
    w.columns = ["WPP Mexico", "WPP US"]
    return ft.join(w, how="left").loc[2005:].round(2)


if __name__ == "__main__":
    c = counts()
    c.to_csv(OUT / "ft_headline_counts.csv", index=False)
    print(c.to_string(index=False))
    m = mexico_vs_us()
    m.to_csv(OUT / "ft_mexico_vs_us.csv")
    print(m.loc[2018:].to_string())
