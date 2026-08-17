# Historic Trends

On this page, the ONS period data [from Conditional ASFR](cond-asfr) is converted to birth cohorts and plotted, and key trends between cohorts are examined. Three types of metrics are plotted:

The Age Specific Fertility Rate (ASFR) gives the probability any woman of a given age in a birth cohort will have a child. This is shown but not commented on as it's more instructive to look at the first and second birth metrics.

The Conditional Age Specific Fertility Rate (Cond. N), by birth order, gives the probability any woman with n-1 children goes on to have their nth child.

The Cumulative fertility rates (Cum. N), by birth order, give the cumulative probability of a woman having >=n children.

Cohorts have been grouped together based on where these trends change and plotted to show these changes. These groups do not necessarily correspond to social generations!

## Cohort Plots

Let's start with the baby boomers. This generation is characterised by first birth fertility rates reducing up to age 32, then increasing later in life. Second births followed a similar trend. These trends gave fewer births at the end of motherhood.


```{raw} html
<iframe src="../_static/ons/historic_trends_uk_1945_1965.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```

The 1965-79 cohorts saw a slightly different trend in first birth fertility; first birth fertility rates reducing up to age 30 and later ages. This caused the peak in the Cond. 1st rate to shift later AND increase in magnitude (likelihood), resulting in more first births overall. Second birth fertility rates fell at ages below 35, and stayed stable at later ages. Combined with the later first births this led to fewer second births.

```{raw} html
<iframe src="../_static/ons/historic_trends_uk_1965_1979.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border); margin-top: 8px;" loading="lazy"></iframe>
```

The 1979-1989 cohorts saw very stable fertility rates compared to other cohorts.

```{raw} html
<iframe src="../_static/ons/historic_trends_uk_1979_1989.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border); margin-top: 8px;" loading="lazy"></iframe>
```

Post-1989 cohorts have seen a significant reduction in fertility in their early years, and the trend shows no sign of slowing; At every age each successive cohort has fewer children than the previous cohort. There are no signs that the peak of the Cond. 1st rate will shift to a later year thus far.

```{raw} html
<iframe src="../_static/ons/historic_trends_uk_1989_.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border); margin-top: 8px;" loading="lazy"></iframe>
```


## All Cohorts



```{raw} html
<style>
  .range-slider-wrap { position: relative; height: 32px; max-width: 500px; }
  .range-slider-wrap input[type="range"] { position: absolute; width: 100%; pointer-events: none; }
  .range-slider-wrap input[type="range"]::-webkit-slider-thumb { pointer-events: auto; }
  .range-slider-wrap input[type="range"]::-moz-range-thumb { pointer-events: auto; }
</style>
<p>
  <label style="font: inherit;">
    Cohort: <b id="historic-trends-range-label">1883–2010</b>
    <div class="range-slider-wrap">
      <input id="historic-trends-min" type="range" min="1883" max="2010" value="1883">
      <input id="historic-trends-max" type="range" min="1883" max="2010" value="2010">
    </div>
  </label>
</p>
<iframe id="historic-trends-frame" src="../_static/ons/historic_trends_uk.html" style="width: 100%; height: 400px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
<script>
  (function () {
    var minInput = document.getElementById("historic-trends-min");
    var maxInput = document.getElementById("historic-trends-max");
    var label = document.getElementById("historic-trends-range-label");

    function applyRange() {
      var lo = Math.min(parseInt(minInput.value), parseInt(maxInput.value));
      var hi = Math.max(parseInt(minInput.value), parseInt(maxInput.value));
      label.textContent = lo + "–" + hi;
      var win = document.getElementById("historic-trends-frame").contentWindow;
      if (win && win.setRange) win.setRange(lo, hi);
    }

    minInput.addEventListener("input", applyRange);
    maxInput.addEventListener("input", applyRange);
  })();
</script>
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13.

Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

See `ONS/scripts/historic_trends_uk.py`.
```
