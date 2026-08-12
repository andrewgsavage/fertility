# Historic Trends

The same charts as on [Later Births](later-births) — plain ASFR, conditional first/second-birth ASFR, and cumulative first/second-birth % — consolidated into a single figure, one row of panels sharing a y-axis wherever the underlying scale matches (ASFR and the two conditional panels share 0–25%; the two cumulative panels share 0–100%). Drag either handle to narrow the cohorts shown.

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
<iframe id="historic-trends-frame" src="../_static/ons/historic_trends_uk.html" style="width: 100%; height: 550px; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
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
