# Economic Decline

A population's age structure is set by two things: how many children are born (fertility) and how long people live (life expectancy). Below-replacement fertility combined with rising life expectancy shrinks the working-age share of the population and raises the ratio of retirees to workers.

```{raw} html
<style>
  .econ-calc label { font: inherit; display: block; margin-bottom: 4px; }
  .econ-calc .slider-row { margin-bottom: 16px; max-width: 480px; }
  .econ-calc .slider-row input[type="range"] { width: 100%; }
  .econ-calc .stats { display: flex; gap: 20px; margin: 20px 0; max-width: 900px; }
  .econ-calc .stat-card {
    border: 1px solid var(--color-background-border);
    border-radius: 6px;
    padding: 12px 20px;
    background: var(--color-background-secondary);
    flex: 1;
    min-width: 0;
  }
  .econ-calc .stat-card .value { font-size: 1.8em; font-weight: 600; }
  .econ-calc .stat-card .label { font-size: 0.85em; color: var(--color-foreground-secondary); }
  .econ-calc .legend { display: flex; gap: 16px; font-size: 0.85em; margin-top: 8px; }
  .econ-calc .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .econ-calc .legend i { width: 12px; height: 12px; display: inline-block; border-radius: 2px; }
</style>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<div class="econ-calc">
  <div class="slider-row">
    <label>Long-term TFR: <b id="tfr-value">1.41</b></label>
    <input type="range" id="tfr-slider" min="0.5" max="2.5" step="0.01" value="1.41">
  </div>
  <div class="slider-row">
    <label>Retirement age: <b id="retire-value">66</b></label>
    <input type="range" id="retire-slider" min="50" max="75" step="1" value="66">
  </div>
  <div class="slider-row">
    <label>Mean life expectancy: <b id="life-value">81</b></label>
    <input type="range" id="life-slider" min="60" max="95" step="1" value="81">
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="value" id="working-pct-value">—</div>
      <div class="label">Working-age population (18 to retirement)</div>
    </div>
    <div class="stat-card">
      <div class="value" id="dependency-value">—</div>
      <div class="label">Old-age dependency ratio (retirees per 100 working-age)</div>
    </div>
    <div class="stat-card">
      <div class="value" id="flow-value">—</div>
      <div class="label">Working-age population change per year</div>
    </div>
    <div class="stat-card">
      <div class="value" id="voter-age-value">—</div>
      <div class="label">Median voter age (18+)</div>
    </div>
  </div>

  <div id="pyramid-chart" style="width: 100%; max-width: 700px; height: 500px;"></div>
  <div class="legend">
    <span><i style="background:#a3c4dc;"></i>Under 18</span>
    <span><i style="background:#2a78d6;"></i>Working age</span>
    <span><i style="background:#eb6834;"></i>Retired</span>
  </div>
</div>
<script>
(function () {
  var REPLACEMENT_TFR = 2.1;
  var GENERATION_YEARS = 30;
  var WORK_START = 18;
  var VOTE_START = 18;

  var tfrSlider = document.getElementById('tfr-slider');
  var retireSlider = document.getElementById('retire-slider');
  var lifeSlider = document.getElementById('life-slider');

  function recompute() {
    var tfr = parseFloat(tfrSlider.value);
    var retireAge = parseInt(retireSlider.value, 10);
    var lifeExp = parseInt(lifeSlider.value, 10);

    document.getElementById('tfr-value').textContent = tfr.toFixed(2);
    document.getElementById('retire-value').textContent = retireAge;
    document.getElementById('life-value').textContent = lifeExp;

    var effRetireAge = Math.min(retireAge, lifeExp);
    var r = Math.log(tfr / REPLACEMENT_TFR) / GENERATION_YEARS;

    var raw = [];
    var total = 0;
    for (var a = 0; a < lifeExp; a++) {
      raw.push(Math.exp(-r * a));
      total += raw[a];
    }

    var ages = [], shares = [], colors = [];
    var workingSum = 0, retiredSum = 0, youngSum = 0;
    var voterSum = 0;
    for (a = 0; a < lifeExp; a++) {
      var share = (raw[a] / total) * 100;
      ages.push(a);
      shares.push(share);
      if (a < WORK_START) {
        colors.push('#a3c4dc');
        youngSum += share;
      } else if (a < effRetireAge) {
        colors.push('#2a78d6');
        workingSum += share;
      } else {
        colors.push('#eb6834');
        retiredSum += share;
      }
      if (a >= VOTE_START) {
        voterSum += share;
      }
    }

    // Median voter age: age at which the cumulative voting-age (18+)
    // population reaches half, interpolated within the single-year bin.
    var medianVoterAge = null;
    var cumulative = 0;
    for (a = VOTE_START; a < lifeExp; a++) {
      var binShare = (raw[a] / total) * 100;
      if (cumulative + binShare >= voterSum / 2) {
        medianVoterAge = a + (voterSum / 2 - cumulative) / binShare;
        break;
      }
      cumulative += binShare;
    }

    document.getElementById('working-pct-value').textContent = workingSum.toFixed(1) + '%';
    document.getElementById('dependency-value').textContent =
      workingSum > 0 ? (retiredSum / workingSum * 100).toFixed(1) : '—';

    // Net flow across the working-age band: headcount turning 18 (entering)
    // minus headcount turning retirement age (leaving), as a share of the
    // working-age population itself.
    var inflowShare = (raw[WORK_START] / total) * 100;
    var outflowAge = effRetireAge < lifeExp ? effRetireAge : lifeExp - 1;
    var outflowShare = (raw[outflowAge] / total) * 100;
    var flowPct = workingSum > 0 ? (inflowShare - outflowShare) / workingSum * 100 : 0;
    document.getElementById('flow-value').textContent =
      workingSum > 0 ? (flowPct >= 0 ? '+' : '') + flowPct.toFixed(1) + '%/yr' : '—';

    document.getElementById('voter-age-value').textContent =
      medianVoterAge !== null ? medianVoterAge.toFixed(1) : '—';

    Plotly.react('pyramid-chart', [{
      x: shares, y: ages, type: 'bar', orientation: 'h',
      marker: { color: colors },
      hovertemplate: 'Age %{y}<br>%{x:.2f}% of population<extra></extra>',
    }], {
      template: 'plotly_white',
      xaxis: { title: 'Share of population (%)' },
      yaxis: { title: 'Age' },
      margin: { t: 20, r: 20, b: 50, l: 50 },
      showlegend: false,
    }, { responsive: true, displayModeBar: false });
  }

  tfrSlider.addEventListener('input', recompute);
  retireSlider.addEventListener('input', recompute);
  lifeSlider.addEventListener('input', recompute);
  recompute();
})();
</script>
```

```{note}
Age structure modeled as p(a) ∝ e^(−ra) for ages 0 to life expectancy (rectangular survivorship: everyone survives to life expectancy, then dies), where r = ln(TFR / 2.1) / 30 is the annual growth rate — the same generation-based model as [Demographic half-life](../theory/demographic-half-life.md). Working age is 18 to retirement age. Old-age dependency ratio = retired population ÷ working-age population × 100. Working-age population change per year = (headcount at age 18 − headcount at retirement age) ÷ working-age population. Median voter age = age at which half of the voting-age (18+) population is younger.

Defaults are current UK figures: TFR 1.41 (ONS, England & Wales, 2024), life expectancy 81 (ONS national life tables, average of male 79.1 and female 83.0, 2022–2024), retirement age 66 (UK State Pension age, 2026).
```
