"""Staying-on rates (pupils aged 15/16/17/18 in full-time education beyond
the leaving age) and higher-education participation, UK, by estimated
birth cohort. A trace-building library, not a standalone script -- rendered
as the bottom panel of childlessness_by_age_uk.py's combined, shared-x-axis
figure (see that module's plot()).

All four staying-on series -- "% of the age group in full-time education"
-- are from House of Commons Library Standard Note SN/SG/4252, "Education:
Historical statistics" (Paul Bolton, 27 November 2012):
https://researchbriefings.files.parliament.uk/documents/SN04252/SN04252.pdf

Aged 16 and 17 are digitized at annual resolution directly from the pixels
of the chart "Pupils in full-time education beyond the leaving age" (p.11)
-- not just read off Table 5's own sparser rows -- using the chart image's
own axis tick pixel positions for calibration (bottom axis: 1953 at x=144,
2008 at x=1717, 28.6px/year; left axis: 100% at y=15, 0% at y=943, 9.28px/%;
colors (0,128,0) for Aged 16, (132,224,98) for Aged 17). Table 5's own
numbers for these two ages agree with the digitized points at every year
Table 5 covers (typically within 0.5pp), a useful cross-check.

Aged 15 and 18 aren't plotted in the p.11 chart at all -- schools-only
"18+" for 1953-1970, then "18"/"15" for 1971/72-1995/96 -- so these come
only from Table 5 "Enrolment and post-compulsory staying-on rates, UK"
(p.18), read directly off its rows; blank ".." cells are omitted rather
than interpolated. Aged 15 stops being published after 1976/77 (no later
source found).

Every series' underlying measurement basis changes twice, per the note's
own text -- REF below assigns each a distinct id and REF_DASH a distinct
line style, consistently across every age that uses it, so the line style
identifies the basis wherever it appears rather than being a per-trace
flourish:
- 1953-1970 (REF 1 chart / REF 4 Table 5): "pupils at school beyond the
  statutory leaving age" (schools only), % of the equivalent 13-year-old
  cohort three years earlier, age at the preceding Christmas.
- 1971-1979 (REF 2 chart / REF 5 Table 5): "% of the population in
  full-time education" (schools and colleges), a broader base -- hence the
  jump between 1970 and 1971/72 -- age still at the preceding Christmas.
- 1980 onwards (REF 3 chart / REF 6 Table 5): same broad "all full-time
  education" base, but age is now measured as at the *start* of the school
  year (31 August) -- this alone causes Table 5 to show a fall in the
  16-year-old rate between 1976/77 and 1980/81, not a real decline.
Rather than draw one connected line across these incompatible bases (which
would show a misleading dip-then-recover, as the original chart does), each
is its own trace (STAYING_ON_PERIODS) -- no line is drawn between them, and
the docs page's own note explains what the gaps mean. Within a period,
small further gaps (e.g. the chart's own 1976 and 2008) are gaps in the
source, not omissions here. Academic-year rows ("1971-72" etc.) are
recorded at their second (spring) calendar year, which is where Table 5's
own numbers land when cross-checked against the p.11 chart's actual pixel
positions (e.g. "1976-77"'s Aged-16 value of 61 sits at x=1977 in the
chart, not x=1976).

SN04252 is a one-off 2012 note with no ongoing update, so it stops at
2009/10 (Aged 15/16/17) or 1995/96 (Aged 18). DfE's own ongoing
"Participation in education, training and employment age 16 to 18" series
(National Statistics, England only), category "Full-time education (FTE)",
sex=Total, labour_market_status=Total (REF 7), picks up from there -- full
range 1994-2024 for every age it covers (16/17/18), from its Headlines
data file:
https://explore-education-statistics.service.gov.uk/find-statistics/participation-in-education-training-and-employment-age-16-to-18
This is a genuinely different measure from SN04252's (England-only here vs
UK there; a different definition of "full-time education" -- their
overlapping years typically differ by 2-4pp, not a small rounding gap).
For Aged 18, DfE's 1994 start doesn't overlap SN04252's own span (which
ends 1991), so it's simply a separate, later trace. For Aged 16/17, DfE's
1994 start *does* overlap SN04252's own digitized (REF 3) span (which runs
to 2010) -- rather than truncate DfE's data to avoid the overlap, or splice
the two incompatible measures into one misleadingly continuous line, all
of DfE's Aged 16/17 data is plotted as its own trace that overlaps REF 3's
-- the same treatment already used for API vs HEIPR below.

HE participation series (Age Participation Index and its successor,
HEIPR). No single official source publishes a UK HE participation rate for
1950-present -- the measure has changed repeatedly (API -> HEIPR -> CHEP-25)
-- so it's compiled from several sources and split into two segments with
different confidence: see APPROX_EDUCATION/OFFICIAL_EDUCATION. Both are
recorded by participation (calendar) year and converted to an estimated
birth cohort by subtracting ENTRY_AGE, since these participation-rate
measures don't carry a birth year of their own. Not further split by
sub-source/line-style like the staying-on series above -- API's own
1950/1961-97/1999+2001 sub-sources are too sparse (the 1950 point in
particular is a single value, with no line of its own to style) for a
per-sub-source style to read as anything but noise.
"""

import plotly.graph_objects as go

# Sentinel marking a gap: no line is drawn between the points either side
# of it (see module docstring for what each gap means).
BREAK = None

# One id per methodology/source, shared with the numbering in the docs
# page's "Data" tab -- see module docstring for what each id is. 1-3: p.11
# chart pixels, by period. 4-6: Table 5, by period. 7: DfE. Dash style
# tracks *methodology period*, not the finer 7-way source split above --
# refs 1/4, 2/5 and 3/6 are the same period read from two different
# sources (chart vs Table 5), so they share a style; only the period (and
# DfE) is what the line style legend distinguishes (see
# add_staying_on_style_legend). The 7-way split still matters for
# citations (the docs page's Data tab), just not for the chart's own
# legend.
REF_DASH = {
    1: "solid", 4: "solid",
    2: "dash", 5: "dash",
    3: "dot", 6: "dot",
    7: "dashdot",
}

# (label, dash) for the line-style legend (see add_staying_on_style_legend)
# -- one entry per distinct REF_DASH value, i.e. per methodology period, or
# DfE; not per individual ref/source (see REF_DASH's comment for why).
STYLE_LEGEND = [
    ("School only, excludes college", "solid"),
    ("All FTE, age at Christmas", "dash"),
    ("All FTE, age in Sept", "dot"),
    ("DfE", "dashdot"),
]

# Digitized at annual resolution from the p.11 chart's own pixels (see
# module docstring for the calibration used). The chart's own line has
# gaps at 1976 (within REF 2) and 2008 (within REF 3) -- kept here rather
# than bridged, since they're gaps in the source, not omissions.
STAYING_ON_16_P1 = [
    (1953, 17.9), (1954, 18.9), (1955, 19.3), (1956, 20.7), (1957, 21.7),
    (1958, 22.3), (1959, 23.0), (1960, 21.2), (1961, 21.7), (1962, 22.3),
    (1963, 24.0), (1964, 24.6), (1965, 26.3), (1966, 28.0), (1967, 29.6),
    (1968, 32.1), (1969, 33.9), (1970, 35.1),
]
STAYING_ON_16_P2 = [
    (1972, 43.2), (1973, 44.0), (1974, 54.8), (1975, 56.9), BREAK,
    (1977, 61.0), (1978, 60.5), (1979, 60.2),
]
STAYING_ON_16_P3 = [
    (1981, 42.2), (1982, 48.2), (1983, 51.8), (1984, 49.3), (1985, 48.4),
    (1986, 49.1), (1987, 49.8), (1988, 51.2), (1989, 54.7), (1990, 57.2),
    (1991, 61.9), (1992, 67.5), (1993, 71.2), (1994, 73.6), (1995, 72.8),
    (1996, 69.7), (1997, 70.3), (1998, 69.3), (1999, 70.5), (2000, 72.1),
    (2001, 73.1), (2002, 72.1), (2003, 72.2), (2004, 72.1), (2005, 72.9),
    (2006, 75.6), (2007, 77.0), BREAK,
    (2009, 81.9), (2010, 84.8),
]

# DfE "Participation..." Headlines data, category "Full-time education
# (FTE)", age 16, sex/labour_market_status "Total" -- see module docstring.
# Plotted in full (1994-2024) as its own overlapping trace rather than
# joined onto STAYING_ON_16_P3 above, since it genuinely overlaps that
# series' own 1994-2010 span -- same treatment as API/HEIPR below.
STAYING_ON_16_DFE = [
    (1994, 71.8), (1995, 71.1), (1996, 70.6), (1997, 70.2), (1998, 70.2),
    (1999, 71.8), (2000, 71.0), (2001, 71.0), (2002, 72.6), (2003, 73.2),
    (2004, 74.9), (2005, 76.7), (2006, 78.5), (2007, 78.4), (2008, 81.2),
    (2009, 83.8), (2010, 84.4), (2011, 83.3), (2012, 83.8), (2013, 86.3),
    (2014, 88.1), (2015, 87.7), (2016, 88.1), (2017, 87.7), (2018, 86.5),
    (2019, 86.9), (2020, 87.5), (2021, 86.7), (2022, 87.8), (2023, 87.5),
    (2024, 87.8),
]

STAYING_ON_17_P1 = [
    (1953, 9.3), (1954, 10.1), (1955, 10.5), (1956, 11.1), (1957, 11.9),
    (1958, 12.3), (1959, 12.9), (1960, 11.2), (1961, 11.9), (1962, 12.3),
    (1963, 12.9), (1964, 13.5), (1965, 13.9), (1966, 15.0), (1967, 16.4),
    (1968, 17.9), (1969, 19.1), (1970, 20.3),
]
STAYING_ON_17_P2 = [
    (1972, 28.0), (1973, 28.7), (1974, 28.1), (1975, 27.8), BREAK,
    (1977, 31.4), (1978, 31.9), (1979, 31.4),
]
STAYING_ON_17_P3 = [
    (1981, 26.8), (1982, 30.1), (1983, 32.3), (1984, 31.6), (1985, 31.6),
    (1986, 31.9), (1987, 33.1), (1988, 33.8), (1989, 35.9), (1990, 39.7),
    (1991, 43.5), (1992, 49.2), (1993, 54.3), (1994, 57.4), (1995, 59.2),
    (1996, 59.0), (1997, 58.0), (1998, 57.2), (1999, 58.2), (2000, 57.4),
    (2001, 58.0), (2002, 58.0), (2003, 57.8), (2004, 59.0), (2005, 58.5),
    (2006, 61.2), (2007, 63.0), BREAK,
    (2009, 66.1), (2010, 70.9),
]

# DfE "Participation..." Headlines data, category "Full-time education
# (FTE)", age 17, sex/labour_market_status "Total" -- see module docstring.
# Plotted in full (1994-2024) as its own overlapping trace, same reasoning
# as STAYING_ON_16_DFE above.
STAYING_ON_17_DFE = [
    (1994, 59.8), (1995, 59.6), (1996, 59.3), (1997, 58.7), (1998, 58.5),
    (1999, 59.7), (2000, 60.0), (2001, 58.7), (2002, 59.4), (2003, 60.6),
    (2004, 61.8), (2005, 64.0), (2006, 65.9), (2007, 66.8), (2008, 67.8),
    (2009, 72.9), (2010, 73.8), (2011, 72.9), (2012, 74.4), (2013, 74.1),
    (2014, 76.7), (2015, 77.0), (2016, 77.4), (2017, 77.9), (2018, 78.1),
    (2019, 77.5), (2020, 79.2), (2021, 78.4), (2022, 77.8), (2023, 78.5),
    (2024, 79.3),
]

# Table 5 only -- not in the p.11 chart -- so far sparser; blank ".." cells
# in the table are simply absent here rather than interpolated.
STAYING_ON_15_P1 = [(1953, 32.4), (1955, 34.5), (1960, 38.4), (1965, 43.8), (1970, 57.3)]
STAYING_ON_15_P2 = [(1972, 73), (1977, 100)]

STAYING_ON_18_P1 = [(1953, 3.9), (1955, 4.1), (1965, 5.0), (1970, 6.9)]
STAYING_ON_18_P2 = [(1972, 18), (1977, 19)]
STAYING_ON_18_P3 = [(1981, 15), (1986, 18), (1991, 25)]

# DfE "Participation..." Headlines data, category "Full-time education
# (FTE)", age 18, sex/labour_market_status "Total" -- see module docstring.
# Starts 1994, so this doesn't reuse Table 5's own 1996 point (41 vs Table
# 5's 40 for the same year -- close, but the two aren't the same series).
# Doesn't overlap STAYING_ON_18_P3 above (which ends 1991), unlike the Aged
# 16/17 DfE series, but is still kept as its own trace/style rather than
# merged, for the same reason: it's a different source.
STAYING_ON_18_DFE = [
    (1994, 39.6), (1995, 41.2), (1996, 41.3), (1997, 40.0), (1998, 39.1),
    (1999, 39.2), (2000, 39.3), (2001, 38.2), (2002, 38.5), (2003, 38.5),
    (2004, 39.5), (2005, 41.7), (2006, 42.4), (2007, 43.5), (2008, 43.9),
    (2009, 46.6), (2010, 48.6), (2011, 50.4), (2012, 48.0), (2013, 49.5),
    (2014, 49.9), (2015, 50.0), (2016, 49.8), (2017, 49.3), (2018, 49.9),
    (2019, 50.7), (2020, 52.0), (2021, 50.3), (2022, 48.8), (2023, 47.6),
    (2024, 48.5),
]

STAYING_ON_COLORS = {15: "#2ca02c", 16: "#1f77b4", 17: "#ff7f0e", 18: "#9467bd"}

# [(ref, period_pairs), ...] per age -- see module docstring for what each
# ref id/period means. Order matters: the first entry carries the age's
# single legend swatch (see add_staying_on_traces).
STAYING_ON_PERIODS = {
    15: [(4, STAYING_ON_15_P1), (5, STAYING_ON_15_P2)],
    16: [(1, STAYING_ON_16_P1), (2, STAYING_ON_16_P2), (3, STAYING_ON_16_P3)],
    17: [(1, STAYING_ON_17_P1), (2, STAYING_ON_17_P2), (3, STAYING_ON_17_P3)],
    18: [(4, STAYING_ON_18_P1), (5, STAYING_ON_18_P2), (6, STAYING_ON_18_P3)],
}

# The DfE series (see module docstring) for each age it covers -- always a
# separate trace/ref (7), whether or not it overlaps its age's periods
# above in time (it does for 16/17, not for 18).
STAYING_ON_DFE = {16: STAYING_ON_16_DFE, 17: STAYING_ON_17_DFE, 18: STAYING_ON_18_DFE}

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
# 1999/00-2005/06 (old methodology): SN/SG/2630 (see childlessness_by_age_uk.py).
# 2006/07-2017/18 (new methodology): DfE, "Participation Rates in Higher
# Education: Academic Years 2006/07-2017/18 (Provisional)", Sept 2019
# (assets.publishing.service.gov.uk/government/uploads/system/uploads/
# attachment_data/file/834341/HEIPR_publication_2019.pdf).
OFFICIAL_EDUCATION = [
    (1999, 39), (2000, 40), (2001, 40), (2002, 41), (2003, 40), (2004, 40), (2005, 42),
    (2006, 41.8), (2007, 43.1), (2008, 45.1), (2009, 45.9), (2010, 46.0), (2011, 49.1),
    (2012, 42.6), (2013, 46.5), (2014, 47.9), (2015, 49.2), (2016, 49.9), (2017, 50.2),
]


def _to_cohort(series):
    return [(year - ENTRY_AGE, pct) for year, pct in series]


def staying_on_cohort_series(age):
    """Flat, sorted [(birth_year, pct), ...] for one age, combining every
    STAYING_ON_PERIODS period plus the DfE continuation (breaks dropped) --
    for interpolating an approximate value at an arbitrary birth year across
    period/source boundaries (e.g. education-vs-fertility.md's cohort-gap
    callouts), the same cross-source bridging already used for HE
    participation (see he_cohort_series)."""
    out = []
    for _ref, pairs in STAYING_ON_PERIODS[age]:
        for item in pairs:
            if item is BREAK:
                continue
            year, pct = item
            out.append((year - age, pct))
    for year, pct in STAYING_ON_DFE.get(age, []):
        out.append((year - age, pct))
    return sorted(out)


def he_cohort_series():
    """Flat, sorted [(birth_year, pct), ...] bridging APPROX_EDUCATION (API)
    and OFFICIAL_EDUCATION (HEIPR) -- same use as staying_on_cohort_series."""
    return sorted(_to_cohort(APPROX_EDUCATION) + _to_cohort(OFFICIAL_EDUCATION))


def _cohort_series(age_col, pairs):
    """[(birth_year, pct), ...] for one age, converting participation year
    to birth year and turning each inline BREAK marker into a None-valued
    point (at the midpoint year of its neighbors) so Plotly leaves a
    visual gap there instead of connecting across it."""
    out = []
    for i, item in enumerate(pairs):
        if item is BREAK:
            prev_year = pairs[i - 1][0]
            next_year = next(y for y, _ in pairs[i + 1:])
            out.append(((prev_year + next_year) / 2 - age_col, None))
        else:
            year, pct = item
            out.append((year - age_col, pct))
    return out


def add_staying_on_traces(fig, row=None, col=None, legend="legend"):
    """Aged 15/16/17/18 staying-on lines, one trace per (age, period) --
    see STAYING_ON_PERIODS/REF_DASH -- so line style identifies the
    measurement basis, plus one further trace per age for the DfE
    continuation (STAYING_ON_DFE, ref 7), left to overlap the last period
    rather than truncated or joined where it overlaps in time (Aged
    16/17) -- same treatment as HE -- API/HEIPR in add_he_traces below.
    Each age gets a single legend entry (its first period)."""
    for age, color in STAYING_ON_COLORS.items():
        for i, (ref, pairs) in enumerate(STAYING_ON_PERIODS[age]):
            birth_years, pct = zip(*_cohort_series(age, pairs))
            observed_years = [by + age for by in birth_years]
            fig.add_trace(
                go.Scatter(
                    x=birth_years, y=pct, mode="lines",
                    name=f"Aged {age}", legend=legend, legendgroup=f"age{age}",
                    showlegend=(i == 0), connectgaps=False,
                    customdata=observed_years,
                    line=dict(width=2, color=color, dash=REF_DASH[ref]),
                    hovertemplate=f"Born %{{x}}, observed %{{customdata}}<br>%{{y:.1f}}% of {age}-year-olds in full-time education<extra></extra>",
                ),
                row=row, col=col,
            )

    for age, dfe_pairs in STAYING_ON_DFE.items():
        birth_years, pct = zip(*_cohort_series(age, dfe_pairs))
        observed_years = [by + age for by in birth_years]
        fig.add_trace(
            go.Scatter(
                x=birth_years, y=pct, mode="lines",
                name=f"Aged {age} (DfE)", legend=legend, showlegend=False,
                customdata=observed_years,
                line=dict(width=2, color=STAYING_ON_COLORS[age], dash=REF_DASH[7]),
                hovertemplate=f"Born %{{x}}, observed %{{customdata}}<br>%{{y:.1f}}% of {age}-year-olds in full-time education (DfE)<extra></extra>",
            ),
            row=row, col=col,
        )


def add_staying_on_style_legend(fig, legend="legend3"):
    """Dummy no-data traces, one per STYLE_LEGEND entry, so line style
    (methodology period, or DfE) has its own legend, separate from
    add_staying_on_traces' per-age color legend -- same dummy-trace
    approach used for ASFR_ROUND_DASH in projections_comparison.py."""
    for label, dash in STYLE_LEGEND:
        fig.add_trace(
            go.Scatter(
                x=[None], y=[None], mode="lines", name=label,
                line=dict(width=2, color="#555555", dash=dash),
                legend=legend, showlegend=True, hoverinfo="skip",
            ),
        )


def add_he_traces(fig, row=None, col=None, legend="legend"):
    """HE — API / HE — HEIPR lines."""
    approx_cohort = _to_cohort(APPROX_EDUCATION)
    official_cohort = _to_cohort(OFFICIAL_EDUCATION)
    approx_years, approx_pct = zip(*approx_cohort)
    official_years, official_pct = zip(*official_cohort)
    approx_observed = [y + ENTRY_AGE for y in approx_years]
    official_observed = [y + ENTRY_AGE for y in official_years]

    # No bridging connector needed: API (ending 2001) and HEIPR (starting
    # 1999/00) genuinely overlap for two years -- both measures were
    # published side by side during the transition -- so the two lines are
    # left to overlap on the chart rather than being artificially joined.
    fig.add_trace(
        go.Scatter(
            x=approx_years, y=approx_pct, mode="lines",
            name="HE — API", legend=legend, customdata=approx_observed,
            line=dict(width=2, color="#555555", dash="dot"),
            hovertemplate="Born %{x}, participated ~%{customdata}<br>%{y:.1f}% (API, digitized/approx.)<extra></extra>",
        ),
        row=row, col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=official_years, y=official_pct, mode="lines",
            name="HE — HEIPR", legend=legend, customdata=official_observed,
            line=dict(width=2, color="#555555", dash="solid"),
            hovertemplate="Born %{x}, participated ~%{customdata}<br>%{y:.1f}% (HEIPR)<extra></extra>",
        ),
        row=row, col=col,
    )
