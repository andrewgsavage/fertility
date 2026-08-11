# Later Births

The [Conditional ASFR](cond-asfr) page reconstructs conditional (parity-progression) ASFR for the UK, since HFD has no such tables for it. HFD does, however, publish plain ASFR (all birth orders combined, not split by parity) directly for England & Wales — no reconstruction needed here.

Each chart below is colored by birth cohort — one line per cohort, tracing that cohort's fertility across its own lifetime — rather than one calendar year's cross-section across all ages. The chart below shows plain ASFR; further down, the same conditional and cumulative first/second-birth charts from the Conditional ASFR page, colored by cohort instead of period. Drag either handle to narrow the cohorts shown across all three charts at once.

```{raw} html
<style>
  .range-slider-wrap { position: relative; height: 32px; max-width: 500px; }
  .range-slider-wrap input[type="range"] { position: absolute; width: 100%; pointer-events: none; }
  .range-slider-wrap input[type="range"]::-webkit-slider-thumb { pointer-events: auto; }
  .range-slider-wrap input[type="range"]::-moz-range-thumb { pointer-events: auto; }
</style>
<p>
  <label style="font: inherit;">
    Cohort: <b id="later-births-range-label">1883–2010</b>
    <div class="range-slider-wrap">
      <input id="later-births-min" type="range" min="1883" max="2010" value="1883">
      <input id="later-births-max" type="range" min="1883" max="2010" value="2010">
    </div>
  </label>
</p>
<iframe id="asfr-uk-frame" src="../_static/hfd/asfr_uk.html" style="width: 100%; aspect-ratio: 16 / 7; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
<iframe id="cond-asfr-cohort-frame" src="../_static/ons/cond_asfr_uk_ons_cohort.html" style="width: 100%; aspect-ratio: 11 / 6; height: auto; display: block; border: 1px solid var(--color-background-border); margin-top: 8px;" loading="lazy"></iframe>
<iframe id="cumulative-cohort-frame" src="../_static/ons/cond_asfr_uk_ons_cumulative.html" style="width: 100%; aspect-ratio: 11 / 6; height: auto; display: block; border: 1px solid var(--color-background-border); margin-top: 8px;" loading="lazy"></iframe>
<script>
  (function () {
    var frameIds = ["asfr-uk-frame", "cond-asfr-cohort-frame", "cumulative-cohort-frame"];
    var minInput = document.getElementById("later-births-min");
    var maxInput = document.getElementById("later-births-max");
    var label = document.getElementById("later-births-range-label");

    function applyRange() {
      var lo = Math.min(parseInt(minInput.value), parseInt(maxInput.value));
      var hi = Math.max(parseInt(minInput.value), parseInt(maxInput.value));
      label.textContent = lo + "–" + hi;
      frameIds.forEach(function (id) {
        var win = document.getElementById(id).contentWindow;
        if (win && win.setRange) win.setRange(lo, hi);
      });
    }

    minInput.addEventListener("input", applyRange);
    maxInput.addEventListener("input", applyRange);
  })();
</script>
```

```{note}
HFD. Human Fertility Database. Max Planck Institute for Demographic Research (Germany)
and Vienna Institute of Demography (Austria). Available at [www.humanfertility.org](https://www.humanfertility.org/).
Data downloaded on 2026-07-13. See `HFD/scripts/asfr_uk.py`.
```

```{note}
Office for National Statistics, "Childbearing for women born in different years,
England and Wales", Table 3 (percentage of women by number of live-born children, by
age and year of birth). Available at
[ons.gov.uk](https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/conceptionandfertilityrates/datasets/childbearingforwomenbornindifferentyearsreferencetable).
See `ONS/scripts/cond_asfr_uk_ons.py`.
```
