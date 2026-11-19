# Plotting conventions (for agents)

Colors for every Plotly chart that colors lines by birth cohort or calendar year. All of it lives in `common/plot_colors.py` (`from common.plot_colors import ...`) — import from there, never hardcode a colorscale name or a year range in a chart script.

## Colormaps

| Lines colored by | Colormap | Constant |
|---|---|---|
| Birth cohort | Viridis, reversed — first cohort **yellow**, later cohorts fade to purple | `COHORT_COLORSCALE` (`"Viridis_r"`) |
| Calendar (period) year | Plasma | `PERIOD_COLORSCALE` |

The colormap tells the reader which basis a chart uses, so don't swap them or use Turbo for either. Colormaps for anything else (maps, scatter, projection rounds, categorical groups) are out of scope.

## Common color axis

Long-running charts share one axis, so the same color means the same cohort/year on every page:

- `COHORT_CAXIS = (1920, 2005)`
- `PERIOD_CAXIS = (1940, 2025)`

Groups outside the axis clamp to the end color (clip `t` to `[0, 1]` — `pc.sample_colorscale` raises on values outside it).

## Short charts do not use the long-term axis

A chart covering fewer than `SHORT_SPAN` (30) cohorts or years would show only a sliver of the scale (one hue), so it stretches the full colormap over its own range: first cohort/year yellow (cohort) or dark (period), last at the other end. Use `cohort_axis(lo, hi)` / `period_axis(lo, hi)`, which return `(lo, hi)` for short charts and the common axis otherwise. Examples: the fixed-era copies of the historic-trends chart; the 2005–2025 conditional-ASFR grid.

Use the real range of the data. If an era has an open-ended upper bound or right-censored (empty) trailing cohorts, take the last group that actually has data.

## Rules

- Pass the axis to both the line colors and the colorbar (`cmin`/`cmax` on the dummy trace), so the bar matches the lines.
- A slider/range filter only hides traces; it never changes colors.
- After changing colors, regenerate the affected `outputs/*.html` (they are tracked) and check them in a browser with the cache bypassed — the docs build copies outputs into `docs/_static`, and a stale tab looks like a failed change.
