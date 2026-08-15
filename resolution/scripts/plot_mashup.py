import matplotlib.pyplot as plt
import pandas as pd

TENURES = ["homeowner", "social_rent", "private_rent", "other", "living_with_parents"]
TENURE_COLORS = {
    "homeowner": "#6A3D9A",
    "social_rent": "#00BFBF",
    "private_rent": "#B0FFFF",
    "other": "#FFD33D",
    "living_with_parents": "#CFDC72",
}
TENURE_LABELS = {
    "homeowner": "Homeowner",
    "social_rent": "Social rent",
    "private_rent": "Private rent",
    "other": "Other",
    "living_with_parents": "Living with parents",
}


def load_childless_25_29():
    header = pd.read_csv("data/nongrads.csv", header=None, nrows=2)
    top = header.iloc[0].ffill()
    columns = pd.MultiIndex.from_arrays([top, header.iloc[1]])
    df = pd.read_csv("data/nongrads.csv", header=None, skiprows=2, names=columns)
    sub = df["25-29"].dropna().sort_values("X")
    return sub["X"], sub["Y"] * 100


def plot_mashup(out_path, stacked_tenure=True, mark_2011=False):
    fig8 = pd.read_csv("data/fig8_nongrad.csv")
    fig7a = pd.read_csv("data/fig7a_nongrad.csv")
    childless_x, childless_y = load_childless_25_29()

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True, gridspec_kw={"hspace": 0})

    ax = axes[0]
    ax.plot(childless_x, childless_y, color="#6A3D9A", linewidth=1.5)
    ax.set_ylabel("Childless (%)")
    ax.grid(True, linewidth=0.4)

    ax = axes[1]
    ax.plot(fig7a["year"], fig7a["women"], color="#1F9E9E", label="Women", linewidth=1.5)
    ax.plot(fig7a["year"], fig7a["all"], color="#777777", label="All", linewidth=1.5)
    ax.plot(fig7a["year"], fig7a["men"], color="#6A3D9A", label="Men", linewidth=1.5)
    ax.set_ylabel("Cohabiting or married (%)")
    ax.grid(True, linewidth=0.4)
    ax.legend()

    ax = axes[2]
    if stacked_tenure:
        ax.stackplot(
            fig8["year"],
            [fig8[t] for t in TENURES],
            colors=[TENURE_COLORS[t] for t in TENURES],
            labels=[TENURE_LABELS[t] for t in TENURES],
        )
        ax.grid(True, axis="y", linewidth=0.5, color="white", alpha=0.6, zorder=3)
    else:
        for t in TENURES:
            ax.plot(fig8["year"], fig8[t], color=TENURE_COLORS[t], label=TENURE_LABELS[t], linewidth=1.5)
        ax.grid(True, linewidth=0.4)
    ax.set_ylabel("Housing tenure (%)")
    ax.set_xlabel("Year")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=8)

    if mark_2011:
        for ax in axes:
            ax.axvline(2011, color="black", linewidth=1, linestyle=":", zorder=4)

    axes[0].set_xlim(1999, 2023)
    fig.suptitle("Non-graduates aged 25-29: childlessness, partnership, and housing tenure")
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    plot_mashup("outputs/mashup.png", stacked_tenure=True, mark_2011=False)
    plot_mashup("outputs/mashup_analysis.png", stacked_tenure=False, mark_2011=True)
