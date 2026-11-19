"""Shared colormap conventions for cohort- and period-colored line charts
across HFD and ONS scripts: cohort-basis charts (one line per birth
cohort) use reversed Viridis, so a plot's first cohort is yellow and later
cohorts fade toward purple; period-basis charts (one line per calendar
year) use Plasma. The colormap itself signals which basis a chart uses.
"""

import plotly.colors as pc

COHORT_COLORSCALE = "Viridis_r"
PERIOD_COLORSCALE = "Plasma"

# Common color axes for long-running charts, so the same color means the
# same cohort (or calendar year) on every such page. Groups outside the
# range clamp to the end color.
COHORT_CAXIS = (1920, 2005)
PERIOD_CAXIS = (1940, 2025)

# A chart covering fewer than this many cohorts/years would show only a
# sliver of the long-term scale (all one hue), so it stretches the full
# scale over its own range instead.
SHORT_SPAN = 30


def cohort_axis(lo, hi):
    return (lo, hi) if hi - lo < SHORT_SPAN else COHORT_CAXIS


def period_axis(lo, hi):
    return (lo, hi) if hi - lo < SHORT_SPAN else PERIOD_CAXIS


def sample_color(colorscale, value, axis):
    lo, hi = axis
    t = 0.0 if hi == lo else min(1.0, max(0.0, (value - lo) / (hi - lo)))
    return pc.sample_colorscale(colorscale, [t])[0]
