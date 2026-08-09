# Explore

Following from first-vs-second-birth, it would be ideal to find data on first births to integorgate the causes for the drop in fertility. The UK does not publish first birth data at town level. It does publish Age Specific Fertility Rates (ASFR) in 5 year buckets for towns, which is presented here. 

The reduction in fertility can be seen clearly in the 20-24 and 25-29 age groups as expected based on the reduction in global first birth rates. The fertility decline in 30-34 year olds is much less severe.




There are much fewer births in 20-24 year olds so there's more room for randomness

Compare any two fertility metrics across local authority districts (2024). Bubble size is live births; pick the X, Y, and color metrics from the dropdowns above the chart. Source: [ONS](https://www.ons.gov.uk/).

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
<script>
  function showCohort(x, y, color, size) {
    document.getElementById('sync-checkbox').checked = true;
    var win = document.getElementById('scatter-frame').contentWindow;
    win.setSyncAxes(true);
    win.setPreset(x, y, color, size);
  }
</script>
<p>
  <button class="preset-btn" onclick="showCohort('asfr_under20_2013', 'asfr_under20', 'mean_age_mother', 'pop_15_19')">&lt;20</button>
  <button class="preset-btn" onclick="showCohort('asfr_20_24_2013', 'asfr_20_24', 'mean_age_mother', 'pop_20_24')">20–24</button>
  <button class="preset-btn" onclick="showCohort('asfr_25_29_2013', 'asfr_25_29', 'mean_age_mother', 'pop_25_29')">25–29</button>
  <button class="preset-btn" onclick="showCohort('asfr_30_34_2013', 'asfr_30_34', 'mean_age_mother', 'pop_30_34')">30–34</button>
  <button class="preset-btn" onclick="showCohort('asfr_35_39_2013', 'asfr_35_39', 'mean_age_mother', 'pop_35_39')">35–39</button>
  <button class="preset-btn" onclick="showCohort('asfr_40_44_2013', 'asfr_40_44', 'mean_age_mother', 'pop_40_44')">40–44</button>
  <button class="preset-btn" onclick="showCohort('asfr_45plus_2013', 'asfr_45plus', 'mean_age_mother', 'pop_45_49')">45+</button>
</p>
<p>
  <label style="font: inherit; cursor: pointer;">
    <input type="checkbox" id="sync-checkbox" onchange="document.getElementById('scatter-frame').contentWindow.setSyncAxes(this.checked)">
    Sync X/Y axis limits (adds 0%/-20%/-40%/-60% reference lines)
  </label>
</p>
<p>
  <label style="font: inherit;">
    Year: <b id="scatter-year-label">2024</b>
    <br>
    <input
      type="range" min="2013" max="2024" step="1" value="2024" style="width: 100%; max-width: 400px;"
      oninput="document.getElementById('scatter-year-label').textContent = this.value; document.getElementById('scatter-frame').contentWindow.setYear(this.value);"
    >
  </label>
</p>
<iframe id="scatter-frame" src="../_static/ons/scatter_plotly.html" style="width: 100%; aspect-ratio: 4 / 3; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```
