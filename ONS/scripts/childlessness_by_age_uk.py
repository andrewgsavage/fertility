"""Childlessness by exact age, England & Wales (ONS cohort table 3), plotted
against year of birth, on the same axis as a UK higher-education
participation-rate series -- for a rough visual comparison of education
expansion against delayed/foregone childbearing, generation by generation.

No single official source publishes a UK HE participation rate for
1950-present -- the measure has changed repeatedly (Age Participation Index
-> HEIPR -> CHEP-25) -- so the education series below is compiled from
several sources and split into two segments with different confidence: see
APPROX_EDUCATION/OFFICIAL_EDUCATION. Both are recorded by participation
(calendar) year and converted to an estimated birth cohort by subtracting
ENTRY_AGE, since these participation-rate measures don't carry a birth year
of their own.
"""

import bisect
import pathlib

import plotly.colors as pc
import plotly.graph_objects as go

from cond_asfr_uk_ons import load_table3

_SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT = "outputs/childlessness_by_age_uk.html"

AGES = [20, 25, 30, 35, 40, 45]

# Modal HE entry age -- used to convert participation (calendar) year to an
# estimated birth cohort below. 18-year-olds are "the largest contributing
# age group" and have "the highest [rate] in the series" per DfE, "Participation
# Rates in Higher Education: Academic Years 2006/07-2017/18 (Provisional)",
# Sept 2019 (see OFFICIAL_EDUCATION's source) -- so cohort = year - 18 is a
# reasonable single-age approximation for both segments below, even though
# HEIPR itself sums participation across ages 17-30.
ENTRY_AGE = 18

# 1950-2001: Age Participation Index (API, Great Britain, under-21
# entrants) -- discontinued in 2001 and replaced by HEIPR, so this is the
# whole API series end to end. 1961-1997 is digitized from a published
# chart (not an original data table, so still approximate) -- Greenaway &
# Haynes (2000), "Age Participation Index: Funding Universities to Meet
# National and International Challenges", University of Nottingham, Figure
# 2 "Age Participation Index (API), 1961-1997"
# (researchgate.net/publication/246275720), digitized points in
# university/Age Participation Index.csv. 1950 (pre-1961, no chart
# coverage) is from Times Higher Education, "Participation rates: now we
# are 50" (timeshighereducation.com/features/participation-rates-now-we-are-50/2005873.article).
# 1999 and 2001 are read off a second, independent chart of the same
# series -- Whitty, Hayton & Tang (2015), "Who You Know, What You Know and
# Knowing the Ropes", Review of Education 3(1), Figure 1 "Participation
# rate (API) for Great Britain (1950-2001)" (doi.org/10.1002/rev3.3038),
# sourced there to Broeke & Hamed (2008) -- and agree closely with the
# Greenaway & Haynes-derived points through 1997, a useful cross-check.
# Note this means API (ending 2001) and OFFICIAL_EDUCATION's HEIPR
# (starting 1999/00) genuinely overlap for two years, reflecting the real
# transition between measures, rather than needing an artificial bridge.
APPROX_EDUCATION = [
    (1950, 3.4),
    (1961, 5.5), (1963, 6.7), (1965, 8.8), (1967, 10.6), (1969, 12.7),
    (1971, 14.0), (1973, 14.1), (1975, 13.5), (1977, 12.8), (1979, 12.3),
    (1981, 13.1), (1983, 13.1), (1985, 13.8), (1987, 14.6), (1989, 17.1),
    (1991, 23.3), (1993, 29.9), (1995, 32.4), (1997, 33.3),
    (1999, 35), (2001, 37),
]

# 1999/00-2017/18: Higher Education Initial Participation Rate (HEIPR),
# England, 17-30 year olds -- annual, official. Discontinued after 2017/18
# here: later years switched to a different, cohort-based measure (CHEP-25)
# that isn't directly comparable.
# 1999/00-2005/06 (old methodology): SN/SG/2630 (see above).
# 2006/07-2017/18 (new methodology): DfE, "Participation Rates in Higher
# Education: Academic Years 2006/07-2017/18 (Provisional)", Sept 2019
# (assets.publishing.service.gov.uk/government/uploads/system/uploads/
# attachment_data/file/834341/HEIPR_publication_2019.pdf).
OFFICIAL_EDUCATION = [
    (1999, 39), (2000, 40), (2001, 40), (2002, 41), (2003, 40), (2004, 40), (2005, 42),
    (2006, 41.8), (2007, 43.1), (2008, 45.1), (2009, 45.9), (2010, 46.0), (2011, 49.1),
    (2012, 42.6), (2013, 46.5), (2014, 47.9), (2015, 49.2), (2016, 49.9), (2017, 50.2),
]

AGE_COLORS = pc.qualitative.Safe
X_RANGE = [1920, 2005]


def childlessness_by_age():
    """{age: [(birth_year, pct_childless), ...]} for AGES, from ONS Table 3
    (already cohort-indexed, so no calendar-year reslicing needed)."""
    by_cohort = load_table3()
    result = {age: [] for age in AGES}
    for birth_year, ages in by_cohort.items():
        for age in AGES:
            if age in ages:
                p1, _p2 = ages[age]
                result[age].append((birth_year, 100 - p1))
    for age in AGES:
        result[age].sort()
    return result


def _to_cohort(series):
    return [(year - ENTRY_AGE, pct) for year, pct in series]


ARROW_YEARS = (1968, 1975)


def _interp(series, x):
    """Linearly interpolate y at x from a sorted [(x, y), ...] series --
    the digitized API series is only at ~2-year resolution, so ARROW_YEARS
    won't always land on an exact digitized point."""
    exact = dict(series)
    if x in exact:
        return exact[x]
    xs = [px for px, _ in series]
    i = bisect.bisect_left(xs, x)
    (x0, y0), (x1, y1) = series[i - 1], series[i]
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def _add_trend_arrow(fig, series, x0, x1, color, label, y_offset=0, label_before=True):
    """Annotation arrow from (x0, y at x0) to (x1, y at x1) on a single
    trace's data (mirrors the era call-outs in historic_trends_uk.py,
    simplified for this figure's single, non-subplot axes). y_offset shifts
    both ends vertically by the same amount, to keep overlapping arrows
    (e.g. the childless-at-N series) visually separated; color matches the
    underlying trace's line color rather than a flat black, so each arrow
    reads as belonging to its trace. label is a format string taking the
    real (un-offset) percentage-point change as {pp}. label_before puts the
    label to the left of the arrow (right-anchored text ending at the
    arrow's tail) when True, or to the right (left-anchored text starting
    at the arrow's head) when False -- so the label sits clear of the
    arrow rather than straddling it."""
    y0_real, y1_real = _interp(series, x0), _interp(series, x1)
    y0, y1 = y0_real + y_offset, y1_real + y_offset
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2, arrowcolor=color,
        text="",
    )
    label_x, label_y, xanchor = (x0, y0, "right") if label_before else (x1, y1, "left")
    fig.add_annotation(
        x=label_x, y=label_y, xref="x", yref="y", xanchor=xanchor, yanchor="bottom",
        showarrow=False, text=label.format(pp=y1_real - y0_real),
        font=dict(size=11, color=color), bgcolor="rgba(255,255,255,0.75)",
    )


def plot(childless_by_age):
    fig = go.Figure()

    for i, age in enumerate(AGES):
        years, pct = zip(*childless_by_age[age])
        fig.add_trace(
            go.Scatter(
                x=years, y=pct, mode="lines", name=f"Childless at {age}",
                line=dict(width=2, color=AGE_COLORS[i % len(AGE_COLORS)]),
                hovertemplate=f"Age {age}<br>Born %{{x}}<br>%{{y:.1f}}% childless<extra></extra>",
            ),
        )

    approx_cohort = _to_cohort(APPROX_EDUCATION)
    official_cohort = _to_cohort(OFFICIAL_EDUCATION)
    approx_years, approx_pct = zip(*approx_cohort)
    official_years, official_pct = zip(*official_cohort)

    # No bridging connector needed: API (ending 2001) and HEIPR (starting
    # 1999/00) genuinely overlap for two years -- both measures were
    # published side by side during the transition -- so the two lines are
    # left to overlap on the chart rather than being artificially joined.
    fig.add_trace(
        go.Scatter(
            x=approx_years, y=approx_pct, mode="lines+markers",
            name="HE — API",
            line=dict(width=2, color="#999999", dash="dot"), marker=dict(size=4),
            hovertemplate=f"Born %{{x}} (participated ~%{{x}}+{ENTRY_AGE})<br>%{{y:.1f}}% (API, digitized/approx.)<extra></extra>",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=official_years, y=official_pct, mode="lines",
            name="HE — HEIPR",
            line=dict(width=2, color="#333333"),
            hovertemplate=f"Born %{{x}} (participated ~%{{x}}+{ENTRY_AGE})<br>%{{y:.1f}}% (HEIPR)<extra></extra>",
        ),
    )

    for year in ARROW_YEARS:
        fig.add_vline(x=year, line=dict(width=1, color="#999999", dash="dash"))

    _add_trend_arrow(
        fig, approx_cohort, *ARROW_YEARS, color="#999999", y_offset=-6,
        label="{pp:.1f}pp rise in HE participation", label_before=False,
    )
    CHILDLESS_ARROWS = {
        30: ("Rise ({pp:.1f}pp) in Childless at 30", 3),
        35: ("Small rise ({pp:.1f}pp) in Childless at 35", 3),
        40: ("Static ({pp:.1f}pp) in Childless at 40", 0),
    }
    for age, (label, y_offset) in CHILDLESS_ARROWS.items():
        color = AGE_COLORS[AGES.index(age) % len(AGE_COLORS)]
        _add_trend_arrow(fig, childless_by_age[age], *ARROW_YEARS, color=color, label=label, y_offset=y_offset)

    fig.update_xaxes(title_text="Estimated year of birth", range=X_RANGE)
    fig.update_yaxes(title_text="%", range=[0, 100])
    fig.update_layout(
        title=f"Childlessness by age vs HE participation (entry age {ENTRY_AGE}), by estimated birth cohort",
        template="plotly_white", autosize=True,
        legend=dict(orientation="v", x=1.02, xanchor="left", y=1, yanchor="top"),
        margin=dict(r=140),
    )
    return fig


if __name__ == "__main__":
    fig = plot(childlessness_by_age())
    fig.write_html(
        OUTPUT,
        include_plotlyjs="cdn",
        full_html=True,
        default_width="100%",
        default_height="100%",
        config={"responsive": True},
    )
    html = open(OUTPUT, "r", encoding="utf-8").read()
    html = html.replace("<head>", "<head>\n<style>html, body { height: 100%; margin: 0; }</style>", 1)
    open(OUTPUT, "w", encoding="utf-8").write(html)
    print(f"Saved {OUTPUT}")
