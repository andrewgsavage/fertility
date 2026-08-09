# Explore

Compare any two fertility metrics across local authority districts (2024). Bubble size is live births; pick the X, Y, and color metrics from the dropdowns above the chart. Source: [ONS](https://www.ons.gov.uk/).

Each button below sets X = ASFR (2013) for that age band, Y = its current (2024) level, Color = mean age of mother, and Size = the female population in that age band.

```{raw} html
<style>
  .preset-btn {
    font: inherit;
    padding: 6px 12px;
    border: 1px solid var(--color-background-border);
    border-radius: 4px;
    background: var(--color-background-secondary);
    color: var(--color-foreground-primary);
    cursor: pointer;
    margin: 0 6px 6px 0;
  }
</style>
<p>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_under20_2013', 'asfr_under20', 'mean_age_mother', 'pop_15_19')">Show &lt;20 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_20_24_2013', 'asfr_20_24', 'mean_age_mother', 'pop_20_24')">Show 20–24 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_25_29_2013', 'asfr_25_29', 'mean_age_mother', 'pop_25_29')">Show 25–29 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_30_34_2013', 'asfr_30_34', 'mean_age_mother', 'pop_30_34')">Show 30–34 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_35_39_2013', 'asfr_35_39', 'mean_age_mother', 'pop_35_39')">Show 35–39 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_40_44_2013', 'asfr_40_44', 'mean_age_mother', 'pop_40_44')">Show 40–44 cohort</button>
  <button class="preset-btn" onclick="document.getElementById('scatter-frame').contentWindow.setPreset('asfr_45plus_2013', 'asfr_45plus', 'mean_age_mother', 'pop_45_49')">Show 45+ cohort</button>
</p>
<p>
  <label style="font: inherit; cursor: pointer;">
    <input type="checkbox" onchange="document.getElementById('scatter-frame').contentWindow.setSyncAxes(this.checked)">
    Sync X/Y axis limits (adds 0%/-20%/-40%/-60% reference lines)
  </label>
</p>
<p>
  <label style="font: inherit;">
    Year: <b id="scatter-year-label">2024</b>
    (Levels and Female population metrics animate — the 2013-baseline and "change vs 2013" groups stay fixed)
    <br>
    <input
      type="range" min="2013" max="2024" step="1" value="2024" style="width: 100%; max-width: 400px;"
      oninput="document.getElementById('scatter-year-label').textContent = this.value; document.getElementById('scatter-frame').contentWindow.setYear(this.value);"
    >
  </label>
</p>
<iframe id="scatter-frame" src="../_static/ons/scatter_plotly.html" style="width: 100%; aspect-ratio: 4 / 3; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
