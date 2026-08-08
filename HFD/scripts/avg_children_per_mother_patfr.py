import math

import matplotlib.pyplot as plt
import pandas as pd

from country_names import country_title

patfr = pd.read_csv(
    "data/HFD/patfr.txt",
    sep=r"\s+",
    skiprows=3,
    names=["code", "year", "patfr", "patfr1", "patfr2", "patfr3", "patfr4", "patfr5p"],
    na_values=".",
)

pft = pd.read_csv(
    "data/HFD/pft.txt",
    sep=r"\s+",
    skiprows=3,
    names=[
        "code", "year", "age", "w0x", "m1x", "q1x", "l0x", "b1x", "L0x", "Sb1x",
        "w1x", "m2x", "q2x", "l1x", "b2x", "L1x", "Sb2x",
        "w2x", "m3x", "q3x", "l2x", "b3x", "L2x", "Sb3x",
        "w3x", "m4x", "q4x", "l3x", "b4x", "L3x", "Sb4x",
        "w4x", "m5px", "q5px", "l4x", "b5px", "L4x", "Sb5px",
    ],
    na_values=".",
)
final_l0x = pft[pft["age"] == "55+"][["code", "year", "l0x"]].rename(columns={"l0x": "l0x_final"})

df = patfr.merge(final_l0x, on=["code", "year"])
df["childless_share"] = df["l0x_final"] / 10000
df["avg_per_mother"] = df["patfr"] / (1 - df["childless_share"])
df = df[df["code"] != "UKR"]

countries = sorted(df["code"].unique())
n = len(countries)
ncols = 6
nrows = math.ceil(n / ncols)

fig, axes = plt.subplots(nrows, ncols, figsize=(3 * ncols, 2.5 * nrows), sharex=True, sharey=True)
axes = axes.flatten()

for ax, country in zip(axes, countries):
    subset = df[df["code"] == country].sort_values("year")
    title = country_title(country, subset["year"].min(), subset["year"].max())
    ax.plot(subset["year"], subset["avg_per_mother"], color="tab:blue", linewidth=1.2)
    ax.set_title(title, fontsize=9)
    ax.grid(True, linewidth=0.4)

for ax in axes[n:]:
    ax.set_visible(False)

fig.supxlabel("Year")
fig.supylabel("Average number of children per mother")
fig.suptitle("Average children per mother (PATFR / (1 - childless share)), by country")

plt.savefig("outputs/avg_children_per_mother_patfr.png", dpi=150)
print("Saved outputs/avg_children_per_mother_patfr.png")
