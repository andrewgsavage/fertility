"""Data behind the charts in the FT's "Why birth rates are falling everywhere all at once"
(John Burn-Murdoch, 16 May 2026), read out of the article's Flourish embeds.

Input (not tracked in git): FT/data/birth_rates_2026/v<id>.html, each saved from
https://flo.uri.sh/visualisation/<id>/embed for the ids in CHARTS. The housing
counterfactual chart (visualisation 28976312, in story 3678740) is private and returns 403.

Output: FT/outputs/ft_birth_rates_everywhere.csv, one long table
(chart, title, facet, year, series, value).
"""

import pandas as pd

from common.flourish import flourish, flourish_settings
from common.paths import data_dir, outputs_dir

DATA = data_dir("FT") / "birth_rates_2026"
OUTPUT = outputs_dir("FT") / "ft_birth_rates_everywhere.csv"

# Flourish visualisation id -> short name, in article order.
CHARTS = {
    28957389: "tfr_by_region",
    28970599: "mexico_vs_us",
    28974152: "japan_productivity",
    28974495: "ideal_vs_actual",
    28955750: "coupling_25_34",
    28994739: "children_per_mother",
    28959991: "coupling_by_education",
    28957217: "coupling_vs_tfr",
    28989486: "earnings_gap",
    # Smartphone story (3679769), slide by slide.
    28990445: "smartphone_tfr_slide1",
    28990469: "smartphone_tfr_slide2",
    28990485: "smartphone_tfr_slide3",
    28990534: "smartphone_tfr_aligned",
    28990605: "smartphone_tfr_vs_trend",
    28973302: "socialising",
    28989105: "left_right_by_sex",
}


def load():
    frames = []
    for vid, name in CHARTS.items():
        path = DATA / f"v{vid}.html"
        d = flourish(path)
        d.insert(0, "title", flourish_settings(path).get("layout.title"))
        d.insert(0, "chart", name)
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    d = load()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUTPUT, index=False)
    print(f"wrote {OUTPUT}: {len(d)} rows, {d.chart.nunique()} charts")
