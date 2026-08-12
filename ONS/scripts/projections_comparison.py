"""Combine each NPP round's own TFR/CFS/ASFR projection chart into one
comparison figure per metric, so the shifting principal-projection
trajectory across rounds is visible at a glance instead of split across
six separate ONS charts (one per round's own methodology page, linked
from docs/uk/projections.md's closing note).

Source CSVs are ONS's own "Download as csv" data for each chart,
saved to ONS/data/projection_rounds/ (gitignored, not redistributed):
- {round}_tfr_cfs.csv (2012/2014/2016/2018): that round's own chart of
  actual+assumed UK TFR and completed family size (CFS) by year.
- {round}_tfr_multiround.csv (2022/2024): ONS's own multi-round TFR
  comparison chart -- only that round's own column is used here, since
  earlier rounds are already covered by their own _tfr_cfs.csv.
- {round}_asfr.csv (2018/2022/2024): that round's own assumed
  age-specific fertility rate by year, split by age band.
"""

import csv
import pathlib

import plotly.colors as pc
import plotly.graph_objects as go

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = _SCRIPT_DIR.parent / "data" / "projection_rounds"

ROUNDS = ["2012", "2014", "2016", "2018", "2022", "2024"]

# Canonical age-band labels -> the column header substring used by each
# round's own ASFR chart (they don't all use the same wording/boundaries
# for the youngest and oldest bands).
ASFR_BANDS = {
    "Under 20": {"2018": "under 20", "2022": "15 to 19", "2024": "15 to 19"},
    "20-24": {"2018": "20 to 24", "2022": "20 to 24", "2024": "20 to 24"},
    "25-29": {"2018": "25 to 29", "2022": "25 to 29", "2024": "25 to 29"},
    "30-34": {"2018": "30 to 34", "2022": "30 to 34", "2024": "30 to 34"},
    "35-39": {"2018": "35 to 39", "2022": "35 to 39", "2024": "35 to 39"},
    "40+": {"2018": "40 and over", "2022": "40 to 46", "2024": "40 to 46"},
}


OBSERVED_COLOR = "#333333"

# Fixed categorical order/hues for the six age bands (dataviz skill's
# validated default palette, slots 1-6 -- adjacent-pair safe for a line
# chart with this many series). Kept as one dict so color assignment
# never depends on which bands happen to be present.
BAND_COLORS = {
    "Under 20": "#2a78d6",
    "20-24": "#eb6834",
    "25-29": "#1baf7a",
    "30-34": "#eda100",
    "35-39": "#e87ba4",
    "40+": "#008300",
}

# Line style distinguishes observed vs. which round's projection, so
# color is free to carry age-band identity when every band is overlaid
# on one axis instead of faceted.
ASFR_ROUND_DASH = {"2018": "dash", "2022": "dot", "2024": "dashdot"}


def _round_color(round_label):
    i = ROUNDS.index(round_label)
    t = i / (len(ROUNDS) - 1)
    return pc.sample_colorscale("Turbo", [t])[0]


def _split_observed_projected(series_by_round):
    """Split {round: {year: value}} into a single reconciled "observed"
    series (years up to that round's own base year, later rounds' revised
    figures winning over earlier rounds' for the same year) and each
    round's own projected-only series (years from its base year onward)."""
    observed = {}
    for round_label in sorted(series_by_round, key=int):
        base_year = int(round_label)
        for year, value in series_by_round[round_label].items():
            if year <= base_year:
                observed[year] = value
    projected = {
        round_label: {y: v for y, v in series.items() if y >= int(round_label)}
        for round_label, series in series_by_round.items()
    }
    return observed, projected


def _read_rows(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def _is_year(cell):
    return cell.strip().isdigit() and len(cell.strip()) == 4


def load_tfr_cfs(round_label):
    """year -> (tfr, cfs), from that round's own actual+assumed chart.
    Column order (CFS then TFR) and header wording both vary by round,
    so this locates columns by position relative to the first data row
    rather than by header text."""
    rows = _read_rows(DATA_DIR / f"{round_label}_tfr_cfs.csv")
    tfr, cfs = {}, {}
    for row in rows:
        if len(row) < 3 or not _is_year(row[0]):
            continue
        year = int(row[0])
        if row[1]:
            cfs[year] = float(row[1])
        if row[2]:
            tfr[year] = float(row[2])
    return tfr, cfs


def load_tfr_multiround(round_label):
    """year -> tfr for just this round's own column out of a multi-round
    comparison chart (2022/2024-based split observed/projected values
    across two columns for the same round; merged here)."""
    rows = _read_rows(DATA_DIR / f"{round_label}_tfr_multiround.csv")
    header = next(r for r in rows if r and r[0].strip() == "Year")
    cols = [i for i, h in enumerate(header) if h.startswith(f"{round_label}-based principal projection")]
    tfr = {}
    for row in rows:
        if not row or not _is_year(row[0]):
            continue
        year = int(row[0])
        for i in cols:
            if i < len(row) and row[i]:
                tfr[year] = float(row[i])
                break
    return tfr


def load_asfr(round_label):
    """canonical band -> {year: rate}, from that round's own assumed-ASFR chart."""
    rows = _read_rows(DATA_DIR / f"{round_label}_asfr.csv")
    header = next(r for r in rows if r and r[0].strip().rstrip() == "Year")
    header = [h.strip() for h in header]
    by_band = {}
    for band, col_by_round in ASFR_BANDS.items():
        wanted = col_by_round[round_label]
        col = next((i for i, h in enumerate(header) if h == wanted), None)
        if col is None:
            continue
        series = {}
        for row in rows:
            if not row or not _is_year(row[0]):
                continue
            year = int(row[0])
            if col < len(row) and row[col]:
                series[year] = float(row[col])
        by_band[band] = series
    return by_band


def build_tfr_figure():
    tfr_by_round = {
        round_label: (load_tfr_multiround(round_label) if round_label in ("2022", "2024")
                      else load_tfr_cfs(round_label)[0])
        for round_label in ROUNDS
    }
    observed, projected = _split_observed_projected(tfr_by_round)

    fig = go.Figure()
    years = sorted(observed)
    fig.add_trace(go.Scatter(
        x=years, y=[observed[y] for y in years],
        mode="lines", name="Observed",
        line=dict(color=OBSERVED_COLOR, width=2.5),
        hovertemplate=f"Observed<br>%{{x}}: %{{y:.2f}}<extra></extra>",
    ))
    for round_label in ROUNDS:
        years = sorted(projected[round_label])
        fig.add_trace(go.Scatter(
            x=years, y=[projected[round_label][y] for y in years],
            mode="lines", name=f"{round_label}-based",
            line=dict(color=_round_color(round_label), width=2),
            hovertemplate=f"{round_label}-based<br>%{{x}}: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin=dict(t=30, r=20, l=50, b=40),
        xaxis_title="Year",
        yaxis_title="Total fertility rate (children per woman)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    return fig


def build_cfs_figure():
    cfs_rounds = ["2012", "2014", "2016", "2018"]
    cfs_by_round = {round_label: load_tfr_cfs(round_label)[1] for round_label in cfs_rounds}
    observed, projected = _split_observed_projected(cfs_by_round)

    fig = go.Figure()
    years = sorted(observed)
    fig.add_trace(go.Scatter(
        x=years, y=[observed[y] for y in years],
        mode="lines", name="Observed",
        line=dict(color=OBSERVED_COLOR, width=2.5),
        hovertemplate=f"Observed<br>%{{x}}: %{{y:.2f}}<extra></extra>",
    ))
    for round_label in cfs_rounds:
        years = sorted(projected[round_label])
        fig.add_trace(go.Scatter(
            x=years, y=[projected[round_label][y] for y in years],
            mode="lines", name=f"{round_label}-based",
            line=dict(color=_round_color(round_label), width=2),
            hovertemplate=f"{round_label}-based<br>%{{x}}: %{{y:.2f}}<extra></extra>",
        ))
    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin=dict(t=30, r=20, l=50, b=40),
        xaxis_title="Cohort's approximate birth year (CFS plotted at cohort + 30)",
        yaxis_title="Completed family size (children per woman)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )
    return fig


def build_asfr_figure():
    bands = list(ASFR_BANDS)
    asfr_rounds = ["2018", "2022", "2024"]
    asfr_by_round = {r: load_asfr(r) for r in asfr_rounds}

    fig = go.Figure()
    for band in bands:
        color = BAND_COLORS[band]
        observed, projected = _split_observed_projected(
            {r: asfr_by_round[r].get(band, {}) for r in asfr_rounds}
        )
        years = sorted(observed)
        fig.add_trace(go.Scatter(
            x=years, y=[observed[y] for y in years],
            mode="lines", name=band,
            legendgroup=band,
            legend="legend",
            line=dict(color=color, width=2.5, dash="solid"),
            hovertemplate=f"{band}, observed<br>%{{x}}: %{{y:.1f}}<extra></extra>",
        ))
        for round_label in asfr_rounds:
            years = sorted(projected[round_label])
            fig.add_trace(go.Scatter(
                x=years, y=[projected[round_label][y] for y in years],
                mode="lines", name=f"{band} ({round_label}-based)",
                legendgroup=band,
                showlegend=False,
                line=dict(color=color, width=1.8, dash=ASFR_ROUND_DASH[round_label]),
                hovertemplate=f"{band}, {round_label}-based<br>%{{x}}: %{{y:.1f}}<extra></extra>",
            ))

    # A second legend, purely for line style, using invisible dummy
    # traces -- color already carries age-band identity above, so this
    # is the only way to explain what solid/dash/dot/dashdot mean.
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", name="Observed",
        line=dict(color=OBSERVED_COLOR, width=2.5, dash="solid"),
        legend="legend2", showlegend=True, hoverinfo="skip",
    ))
    for round_label, dash in ASFR_ROUND_DASH.items():
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="lines", name=f"{round_label}-based (projected)",
            line=dict(color=OBSERVED_COLOR, width=1.8, dash=dash),
            legend="legend2", showlegend=True, hoverinfo="skip",
        ))

    fig.update_layout(
        template="plotly_white",
        autosize=True,
        margin=dict(t=30, r=170, l=50, b=40),
        xaxis_title="Year",
        yaxis_title="Births per 1,000 women",
        legend=dict(title="Age band", x=1.02, y=1, xanchor="left", yanchor="top"),
        legend2=dict(title="Line style", x=1.02, y=0.55, xanchor="left", yanchor="top"),
        hovermode="x unified",
    )
    return fig


def _write(fig, output_path):
    fig.write_html(
        output_path,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = open(output_path, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(output_path, "w", encoding="utf-8").write(html)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    _write(build_tfr_figure(), "outputs/projections_tfr.html")
    _write(build_cfs_figure(), "outputs/projections_cfs.html")
    _write(build_asfr_figure(), "outputs/projections_asfr.html")
