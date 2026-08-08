import math

import matplotlib.pyplot as plt
import pandas as pd

from country_names import country_title

mi = pd.read_csv(
    "data/HFD/mi.txt",
    sep=r"\s+",
    skiprows=3,
    names=["code", "year", "age", "m1x", "m2x", "m3x", "m4x", "m5px"],
    na_values=".",
)
mi["age_num"] = mi["age"].astype(str).str.replace("-", "", regex=False).str.replace("+", "", regex=False).astype(int)
mi = mi.sort_values(["code", "year", "age_num"])

orders = ["m1x", "m2x", "m3x", "m4x", "m5px"]


def build_life_table(group):
    l = [1.0, 0.0, 0.0, 0.0, 0.0]  # survivors at parity 0,1,2,3,4+
    total_births = 0.0
    for _, row in group.iterrows():
        b = [0.0, 0.0, 0.0, 0.0, 0.0]
        for i, col in enumerate(orders):
            m = row[col]
            if pd.isna(m):
                continue
            q = m / (1 + 0.5 * m)
            pool = l[i] + (0.5 * b[i - 1] if i > 0 else 0.0)
            b[i] = pool * q
        total_births += sum(b)
        l[0] -= b[0]
        for i in range(1, 5):
            l[i] += b[i - 1] - b[i]
    return pd.Series({"avg_per_woman": total_births, "childless_share": l[0]})


results = mi.groupby(["code", "year"]).apply(build_life_table, include_groups=False).reset_index()
results["avg_per_mother"] = results["avg_per_woman"] / (1 - results["childless_share"])
results = results[results["code"] != "UKR"]

countries = sorted(results["code"].unique())
n = len(countries)
ncols = 6
nrows = math.ceil(n / ncols)

fig, axes = plt.subplots(nrows, ncols, figsize=(3 * ncols, 2.5 * nrows), sharex=True, sharey=True)
axes = axes.flatten()

for ax, country in zip(axes, countries):
    subset = results[results["code"] == country].sort_values("year")
    title = country_title(country, subset["year"].min(), subset["year"].max())
    ax.plot(subset["year"], subset["avg_per_mother"], color="tab:red", linewidth=1.2)
    ax.set_title(title, fontsize=9)
    ax.grid(True, linewidth=0.4)

for ax in axes[n:]:
    ax.set_visible(False)

fig.supxlabel("Year")
fig.supylabel("Average number of children per mother")
fig.suptitle("Average children per mother, built from mi.txt life table, by country")

plt.savefig("outputs/avg_children_per_mother_mi.png", dpi=150)
print("Saved outputs/avg_children_per_mother_mi.png")
