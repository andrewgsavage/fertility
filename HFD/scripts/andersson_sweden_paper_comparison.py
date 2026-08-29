"""Reproduce the completed-fertility-by-age-at-first-birth curves for
Swedish women born 1935-39 and 1950-54, from Andersson (2008: 49, Table
12d), as reprinted in Schmidt, Sobotka, Bentzen & Nyboe Andersen (2012,
Hum Reprod Update 18(1):29-43, Fig. 4) -- digitized by eye from that
figure.

No HFD overlay here: HFD's own Swedish parity-progression data (cft.txt)
only starts at the 1955 birth cohort, so there's no cohort in common with
this figure's much older 1935-39/1950-54 cohorts to compare against. Kept
as a standalone historical data point instead -- the same measure as the
rest of this page's "Comparison to published research" section, just
predating HFD's own coverage.
"""

import plotly.graph_objects as go

OUTPUT = "outputs/andersson_sweden_paper_comparison.html"

# Digitized by eye, one point per age year, from Fig. 4 of Schmidt et al.
# 2012 (originally Andersson 2008, Table 12d).
AGES = list(range(15, 45))
COHORT_1935_39 = [
    3.65, 3.22, 3.08, 2.92, 2.76, 2.62, 2.55, 2.44, 2.38, 2.32,
    2.20, 2.15, 2.06, 2.00, 1.92, 1.86, 1.78, 1.70, 1.62, 1.58,
    1.49, 1.46, 1.33, 1.28, 1.22, 1.16, 1.13, 1.11, 1.08, 1.00,
]
COHORT_1950_54 = [
    2.80, 2.78, 2.67, 2.64, 2.58, 2.47, 2.45, 2.39, 2.36, 2.33,
    2.30, 2.26, 2.20, 2.17, 2.12, 2.06, 2.02, 1.95, 1.89, 1.80,
    1.75, 1.60, 1.56, 1.47, 1.35, 1.28, 1.20, 1.15, 1.12, 1.02,
]


def plot():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=AGES, y=COHORT_1935_39, mode="lines+markers",
        line=dict(width=1.8, color="navy"), marker=dict(size=5, symbol="diamond"),
        name="Cohorts 1935-39",
        hovertemplate="Cohorts 1935-39<br>Age %{x}<br>%{y:.2f} children<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=AGES, y=COHORT_1950_54, mode="lines+markers",
        line=dict(width=1.8, color="black"), marker=dict(size=5, symbol="square"),
        name="Cohorts 1950-54",
        hovertemplate="Cohorts 1950-54<br>Age %{x}<br>%{y:.2f} children<extra></extra>",
    ))

    fig.update_xaxes(range=[15, 44], title="Age at first birth")
    fig.update_yaxes(range=[1.0, 4.0], title="Completed fertility rate")
    fig.update_layout(
        title="Sweden: Andersson (2008) via Schmidt et al. 2012",
        template="plotly_white",
        height=500,
    )
    return fig


if __name__ == "__main__":
    fig = plot()
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height=f"{fig.layout.height}px",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
