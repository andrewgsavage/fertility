# TFR trajectories after crossing a threshold

Rather than picking countries by hand, this chart selects them by a TFR
threshold: every country whose TFR has ever dropped below the chosen level
is plotted from the year it first crosses below that level through to its
most recent year — even if it later recovers back above the threshold,
which does not cut the line short. Limited to major countries (population
over 1 million; OWID's continent/income-group aggregates like "World" and
small states like Andorra are excluded) so the chart stays legible. As on
the
[rate of change of TFR](tfr-derivative) page, x is the TFR level and y is
its year-on-year derivative, with markers fading from light (the crossing
year) to full opacity (most recent year).

Drag the threshold slider to change which countries qualify; hover a point
to see its country and year.

```{raw} html
<iframe src="../_static/owid/tfr_threshold_derivative.html" style="width: 100%; height: 650px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Data: Human Fertility Database (2025); UN, World Population Prospects (2024)
— with major processing by Our World in Data. Source:
[Fertility rate: births per woman](https://ourworldindata.org/grapher/children-born-per-woman),
Our World in Data.

The derivative is a simple year-on-year central difference of the reported
TFR series (one-sided at each series' first and last year). The default
threshold, 2.1, is the commonly cited replacement rate.
```
