import pandas as pd

path = "data/finalisingcohorttables2024finalforupload.xlsx"

df = pd.read_excel(path, sheet_name="Table 2", header=7)
df = df.rename(columns={df.columns[0]: "birth_year"})

col_map = {
    "Age exact years - 16\n[note 4]": 16,
    "Final [note 5]": "final",
    "Proportion of women having \nhad no children [note 8]": "childless",
}
col_map.update({str(a): a for a in range(17, 46)})

df = df.rename(columns=col_map)
df["birth_year"] = df["birth_year"].astype(int)
df = df.set_index("birth_year")

html = (
    df.style
    .background_gradient(cmap="YlOrRd", vmin=0, vmax=1)
    .format(precision=2, na_rep="")
    .to_html()
)

with open("outputs/table2.html", "w") as f:
    f.write(html)

print("Saved outputs/table2.html")

import matplotlib.pyplot as plt

df_plot = df.drop(columns=["final", "childless"])

cmap = plt.colormaps["viridis"]
years = df_plot.index
norm = plt.Normalize(years.min(), years.max())

fig, ax = plt.subplots()
for year, row in df_plot.iterrows():
    ax.plot(row.index, row.values, color=cmap(norm(year)), alpha=0.7)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = fig.colorbar(sm, ax=ax, label="Birth year")
cbar.ax.invert_yaxis()
ax.set_xlabel("Age")
ax.set_ylabel("Proportion with at least one birth")
ax.set_title("Cumulative fertility: Proportion of women who have had\nat least one live birth")
ax.set_xlim(18, 45)
ax.grid(True)
plt.tight_layout()
plt.savefig("outputs/table2_single.png", dpi=150)
plt.close()
print("Saved outputs/table2_single.png")

splits = [
    df_plot[years <= 1973],
    df_plot[(years > 1973) & (years <= 1987)],
    df_plot[years > 1987],
]

fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
for ax, subset in zip(axes, splits):
    for year, row in subset.iterrows():
        ax.plot(row.index, row.values, color=cmap(norm(year)), alpha=0.7)
    ax.set_xlabel("Age")
    ax.set_title(f"Birth years {subset.index.min()}–{subset.index.max()}")
    ax.set_xlim(18, 45)
    ax.grid(True)

axes[0].set_ylabel("Proportion with at least one birth")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = fig.colorbar(sm, ax=axes, label="Birth year")
cbar.ax.invert_yaxis()
fig.suptitle("Cumulative fertility by birth year cohort")
plt.savefig("outputs/table2.png", dpi=150)
print("Saved outputs/table2.png")

middle = df_plot[(years > 1973) & (years <= 1987)]
mean_curve = middle.mean(axis=0)

fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
for ax, subset in zip(axes, splits):
    for year, row in subset.iterrows():
        ax.plot(row.index, row.values - mean_curve, color=cmap(norm(year)), alpha=0.7)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Age")
    ax.set_title(f"Birth years {subset.index.min()}–{subset.index.max()}")
    ax.set_xlim(18, 45)
    ax.grid(True)

axes[0].set_ylabel("Deviation from 1974–1987 average")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = fig.colorbar(sm, ax=axes, label="Birth year")
cbar.ax.invert_yaxis()
fig.suptitle("Cumulative fertility relative to 1974–1987 cohort average")
plt.savefig("outputs/table2_deviation.png", dpi=150)
print("Saved outputs/table2_deviation.png")

import numpy as np

trendline_rows = []

subset = splits[2]
fig, ax = plt.subplots(figsize=(8, 5))
for year, row in subset.iterrows():
    diff = (row - mean_curve).dropna()
    if len(diff) < 3:
        continue
    color = cmap(norm(year))
    ax.plot(diff.index, diff.values, color=color, alpha=0.2)
    fit_data = diff.iloc[-10:]
    if len(fit_data) < 3:
        continue
    x = fit_data.index.astype(float).values
    coeffs = np.polyfit(x, fit_data.values, 2)
    x_fit = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_fit, np.polyval(coeffs, x_fit), color=color, alpha=0.8)
    min_age = -coeffs[1] / (2 * coeffs[0])
    min_val = np.polyval(coeffs, min_age)
    x_ext = np.linspace(x.max(), min(min_age, 40, x.max() + 5), 100)
    y_ext = np.polyval(coeffs, x_ext)
    mask = y_ext <= 0
    if mask.any():
        ax.plot(x_ext[mask], y_ext[mask], color=color, alpha=0.8, linestyle=":")
    if min_age <= 40 and min_val <= 0:
        ax.plot(min_age, min_val, marker="x", color=color, markersize=6, markeredgewidth=1.5)
    trendline_rows.append({"birth_year": year, "min_age": round(min_age, 2), "min_value": round(min_val, 4), "x2": round(coeffs[0] * 1e4, 0)})

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.axvline(33, color="black", linewidth=0.8, linestyle="--")
ax.grid(True)
ax.set_xlabel("Age")
ax.set_title(f"Birth years {subset.index.min()}–{subset.index.max()}")
ax.set_xlim(18, 45)

ax.set_ylabel("Deviation from 1974–1987 average")

sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
cbar = fig.colorbar(sm, ax=ax, label="Birth year")
cbar.ax.invert_yaxis()
ax.set_title(f"Birth years {subset.index.min()}–{subset.index.max()} — deviation with quadratic trendlines")
plt.tight_layout()
plt.savefig("outputs/table2_quadratic.png", dpi=150)
print("Saved outputs/table2_quadratic.png")

# Euler trendlines: extend each cohort's data by one step using slope from ±1 neighbours
diff_curves = {year: (row - mean_curve).dropna() for year, row in subset.iterrows()}

fig, ax = plt.subplots(figsize=(8, 5))
for year, diff in diff_curves.items():
    if len(diff) < 3:
        continue
    color = cmap(norm(year))
    ax.plot(diff.index, diff.values, color=color, alpha=0.2)

    # Midpoint method: estimate slope at last age (k1), half-step, then slope at midpoint (k2)
    last_age = diff.index[-1]
    euler_data = diff.copy()
    prev_diff = diff_curves.get(year - 1)
    next_diff = diff_curves.get(year + 1)

    def neighbour_slope(age):
        slopes = []
        if prev_diff is not None and age in prev_diff.index and age - 1 in prev_diff.index:
            slopes.append(prev_diff[age] - prev_diff[age - 1])
        if next_diff is not None and age in next_diff.index and age - 1 in next_diff.index:
            slopes.append(next_diff[age] - next_diff[age - 1])
        return np.mean(slopes) if slopes else None

    k1 = neighbour_slope(last_age)
    if k1 is not None:
        y_mid = diff[last_age] + 0.5 * k1
        # slope at midpoint: interpolate neighbour slopes between A and A+1
        k_next = neighbour_slope(last_age + 1)
        k2 = np.mean([s for s in [k1, k_next] if s is not None])
        midpoint_val = diff[last_age] + k2
        euler_data = pd.concat([euler_data, pd.Series([midpoint_val], index=[last_age + 1])])

    fit_data = euler_data.iloc[-10:]
    if len(fit_data) < 3:
        continue
    x = fit_data.index.astype(float).values
    coeffs = np.polyfit(x, fit_data.values, 2)
    x_fit = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_fit, np.polyval(coeffs, x_fit), color=color, alpha=0.8)
    min_age = -coeffs[1] / (2 * coeffs[0])
    min_val = np.polyval(coeffs, min_age)
    x_ext = np.linspace(x.max(), min(min_age, 40, x.max() + 5), 100)
    y_ext = np.polyval(coeffs, x_ext)
    mask = y_ext <= 0
    if mask.any():
        ax.plot(x_ext[mask], y_ext[mask], color=color, alpha=0.8, linestyle=":")
    if min_age <= 40 and min_val <= 0:
        ax.plot(min_age, min_val, marker="x", color=color, markersize=6, markeredgewidth=1.5)

    # add midpoint min values to existing trendline rows
    for r in trendline_rows:
        if r["birth_year"] == year:
            r["midpoint_min_age"] = round(min_age, 2)
            r["midpoint_min_value"] = round(min_val, 4)
            r["midpoint_x2"] = round(coeffs[0] * 1e4, 0)
            break

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.axvline(33, color="black", linewidth=0.8, linestyle="--")
ax.grid(True)
ax.set_xlabel("Age")
ax.set_ylabel("Deviation from 1974–1987 average")
ax.set_title(f"Birth years {subset.index.min()}–{subset.index.max()} — midpoint method trendlines (±1 cohort)")
ax.set_xlim(18, 45)

cbar.ax.invert_yaxis()
plt.tight_layout()
plt.savefig("outputs/table2_midpoint.png", dpi=150)
print("Saved outputs/table2_midpoint.png")

pd.DataFrame(trendline_rows).to_csv("outputs/table2_trendlines.csv", index=False)
print("Saved outputs/table2_trendlines.csv")
