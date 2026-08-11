# Conditional ASFR

The [First vs Second Birth](../hfd/first-vs-second-birth) page compares the conditional age specific fertility rate (ASFR) — the probability a woman has her next child in a given year — for first and second births across countries, including a UK column reconstructed from ONS cohort data (HFD itself has no conditional-ASFR tables for the UK).

This page shows that same UK reconstruction on its own, colored by period (calendar) year, with every available year plotted and a slider to narrow the range shown. See [Later Births](later-births) for the same chart colored by birth cohort instead, alongside the underlying cumulative data.

```{raw} html
<style>
  .range-slider-wrap { position: relative; height: 32px; max-width: 500px; }
  .range-slider-wrap input[type="range"] { position: absolute; width: 100%; pointer-events: none; }
  .range-slider-wrap input[type="range"]::-webkit-slider-thumb { pointer-events: auto; }
  .range-slider-wrap input[type="range"]::-moz-range-thumb { pointer-events: auto; }
</style>
<p>
  <label style="font: inherit;">
    Year: <b id="cond-asfr-range-label">1941–2025</b>
    <div class="range-slider-wrap">
      <input id="cond-asfr-min" type="range" min="1941" max="2025" value="1941">
      <input id="cond-asfr-max" type="range" min="1941" max="2025" value="2025">
    </div>
  </label>
</p>
<iframe id="cond-asfr-frame" src="../_static/ons/cond_asfr_uk_ons.html" style="width: 100%; aspect-ratio: 11 / 6; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
<script>
  (function () {
    var minInput = document.getElementById("cond-asfr-min");
    var maxInput = document.getElementById("cond-asfr-max");
    var label = document.getElementById("cond-asfr-range-label");

    function applyRange() {
      var lo = Math.min(parseInt(minInput.value), parseInt(maxInput.value));
      var hi = Math.max(parseInt(minInput.value), parseInt(maxInput.value));
      label.textContent = lo + "–" + hi;
      var win = document.getElementById("cond-asfr-frame").contentWindow;
      if (win && win.setRange) win.setRange(lo, hi);
    }

    minInput.addEventListener("input", applyRange);
    maxInput.addEventListener("input", applyRange);
  })();
</script>
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).

HFD has no conditional-ASFR tables for the UK, so this is reconstructed from that data:
at each age, the conditional (parity-progression) rate is estimated as a discrete
hazard on the cumulative % of the cohort with at least 1 / at least 2 children, then
re-sliced from cohort into period (calendar) year to match HFD's chart convention. See
`ONS/scripts/cond_asfr_uk_ons.py`.
```
