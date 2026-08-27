"""Population half-life (years for the population to halve) as a function
of TFR, for docs/democracy/stability.md.

Each generation multiplies the population by TFR / REPLACEMENT_TFR, so
after n generations the population is (TFR / REPLACEMENT_TFR) ** n of its
starting size. Solving for the n at which that ratio reaches 0.5, and
converting generations to years via GENERATION_YEARS, gives:

    half_life_years = GENERATION_YEARS * ln(0.5) / ln(TFR / REPLACEMENT_TFR)

This reproduces the worked example in stability.md directly: a TFR of 1.05
is exactly half of replacement (1.05 / 2.1 = 0.5), so ln(0.5)/ln(0.5) = 1
and half_life_years = GENERATION_YEARS = 30.
"""

import math
import pathlib

import plotly.graph_objects as go

OUTPUT_DIR = pathlib.Path("outputs")

REPLACEMENT_TFR = 2.1
GENERATION_YEARS = 30  # mean age of childbirth, per stability.md

# 0.50 up to (not including) REPLACEMENT_TFR in 0.01 steps -- half-life
# diverges to infinity at replacement, so 2.1 itself isn't plottable.
_N_STEPS = round((REPLACEMENT_TFR - 0.50) / 0.01)
TFR_VALUES = [round(0.50 + i * 0.01, 2) for i in range(_N_STEPS)]

def half_life_years(tfr):
    return GENERATION_YEARS * math.log(0.5) / math.log(tfr / REPLACEMENT_TFR)


# Points called out in the surrounding text, so the reader can match a
# specific claim to a specific point on the curve.
CALLOUTS = {
    1.05: "1.05: halves every generation (30 years)",
    1.40: "1.40: the \"point of no return\"",
    1.70: f"1.70: {half_life_years(1.70):.0f}-year half-life",
}


def _figure(log_y):
    half_lives = [half_life_years(tfr) for tfr in TFR_VALUES]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=TFR_VALUES, y=half_lives, mode="lines+markers",
            line=dict(width=2, color="#2a78d6"), marker=dict(size=4),
            hovertemplate="TFR %{x:.2f}<br>%{y:.0f}-year half-life<extra></extra>",
        ),
    )
    for tfr, label in CALLOUTS.items():
        y = half_life_years(tfr)
        fig.add_trace(
            go.Scatter(
                x=[tfr], y=[y], mode="markers", marker=dict(size=9, color="#eb6834"),
                showlegend=False, hoverinfo="skip",
            ),
        )
        fig.add_annotation(
            x=tfr, y=y, text=label, showarrow=True, arrowhead=2, ax=40, ay=-30,
            font=dict(size=11, color="#eb6834"), bgcolor="rgba(255,255,255,0.75)",
        )
    fig.add_vline(
        x=REPLACEMENT_TFR, line=dict(width=1, color="#999999", dash="dash"),
        annotation_text="Replacement (2.1)", annotation_position="top",
    )
    fig.update_xaxes(title_text="Total fertility rate (TFR)", range=[REPLACEMENT_TFR + 0.02, 0.50])
    if log_y:
        # Explicit range: letting plotly.js auto-range a log axis here (with
        # arrow annotations present) blows the range out to ~1e60 instead of
        # fitting the ~14-4400 data span.
        fig.update_yaxes(
            title_text="Half-life (years, log scale)", type="log",
            range=[math.log10(10), math.log10(6000)],
        )
    else:
        fig.update_yaxes(title_text="Half-life (years)", range=[0, 200])
    fig.update_layout(
        title="Population half-life vs TFR",
        template="plotly_white", autosize=True, showlegend=False,
    )
    return fig


def _table_markdown(n_cols=4):
    """The same TFR/half-life pairs as the chart, as a markdown table --
    wrapped into n_cols side-by-side (TFR, Half-life) column pairs so 160
    rows of data fit in a reasonable number of table rows."""
    rows_per_col = -(-len(TFR_VALUES) // n_cols)  # ceil
    header = "| " + " | ".join(["TFR", "Half-life (yrs)"] * n_cols) + " |"
    sep = "|" + "---|" * (2 * n_cols)
    lines = [header, sep]
    for r in range(rows_per_col):
        cells = []
        for c in range(n_cols):
            i = c * rows_per_col + r
            if i < len(TFR_VALUES):
                tfr = TFR_VALUES[i]
                cells += [f"{tfr:.2f}", f"{half_life_years(tfr):.1f}"]
            else:
                cells += ["", ""]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def _save(fig, name):
    output = OUTPUT_DIR / name
    fig.write_html(
        output, include_plotlyjs="cdn", full_html=True,
        default_width="100%", default_height="100%",
        config={"responsive": True},
    )
    html = output.read_text(encoding="utf-8")
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    output.write_text(html, encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(exist_ok=True)
    _save(_figure(log_y=False), "half_life_tfr_linear.html")
    _save(_figure(log_y=True), "half_life_tfr_log.html")
    # .txt, not .md -- outputs/ is copied into docs/_static/democracy at
    # build time, and myst_parser treats any .md file under the source
    # tree (static assets included) as a page to build.
    table_output = OUTPUT_DIR / "half_life_tfr_table.txt"
    table_output.write_text(_table_markdown(), encoding="utf-8")
    print(f"Saved {table_output}")
