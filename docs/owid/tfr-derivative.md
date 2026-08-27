# Rate of change of TFR

The total fertility rate (TFR) itself only shows the level in a given year.
Its year-on-year derivative, d(TFR)/d(year), shows how fast that level is
rising or falling. Plotting the derivative against the TFR level itself
(rather than against year) traces out each country's trajectory through
TFR-vs-rate-of-change space — useful for spotting whether decline
accelerates or slows as TFR approaches a given level, and whether a country
is currently rising or falling at its current level. Tick countries or
regions in the sidebar to add/remove them; hover a point to see its year.

```{raw} html
<iframe src="../_static/owid/tfr_derivative.html" style="width: 100%; height: 650px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

```{note}
Data: Human Fertility Database (2025); UN, World Population Prospects (2024)
— with major processing by Our World in Data. Source:
[Fertility rate: births per woman](https://ourworldindata.org/grapher/children-born-per-woman),
Our World in Data.

The derivative is computed as a simple year-on-year central difference of
the reported TFR series (one-sided at each series' first and last year).
```
