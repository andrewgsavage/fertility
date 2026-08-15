import matplotlib.pyplot as plt
import pandas as pd

AGE_GROUPS = ["25-29", "30-34", "35-39", "40-44"]
MEDIAN_AGE = {"25-29": 27, "30-34": 32, "35-39": 37, "40-44": 42}
# Youngest -> oldest: purple, cyan, yellow, red, so the same age group always
# gets the same colour across charts (grads/nongrads panels, year/birth-year axes).
AGE_COLORS = {"25-29": "#6A3D9A", "30-34": "#1F9E9E", "35-39": "#D4A017", "40-44": "#E31A1C"}


def load_series(path):
    header = pd.read_csv(path, header=None, nrows=2)
    top = header.iloc[0].ffill()
    columns = pd.MultiIndex.from_arrays([top, header.iloc[1]])
    df = pd.read_csv(path, header=None, skiprows=2, names=columns)

    series = {}
    for group in AGE_GROUPS:
        sub = df[group].dropna()
        series[group] = sub.sort_values("X")
    return series


def save(fig, path):
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def plot_all(datasets, xlabel, suptitle, out_path, birth_year=False):
    fig, axes = plt.subplots(1, len(datasets), figsize=(8 * len(datasets), 6), sharey=True)
    for ax, (name, series) in zip(axes, datasets.items()):
        for group in AGE_GROUPS:
            x = series[group]["X"]
            if birth_year:
                x = x - MEDIAN_AGE[group]
            ax.plot(x, series[group]["Y"], label=f"{group} year olds", linewidth=1.5, color=AGE_COLORS[group])

        ax.set_xlabel(xlabel)
        ax.set_title(name, fontsize=13)
        ax.grid(True, linewidth=0.4)
        ax.legend()

    axes[0].set_ylabel("Proportion childless")
    fig.suptitle(suptitle, fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, 0.94))

    save(fig, out_path)


if __name__ == "__main__":
    datasets = {
        "Graduates": load_series("data/grads.csv"),
        "Non-graduates": load_series("data/nongrads.csv"),
    }
    plot_all(
        datasets,
        "Year",
        "Proportion of women without a biological child, by age and education",
        "outputs/grads_nongrads.png",
    )
    plot_all(
        datasets,
        "Mother's birth year",
        "Proportion of women without a biological child, by age and education",
        "outputs/grads_nongrads_birth_year.png",
        birth_year=True,
    )
