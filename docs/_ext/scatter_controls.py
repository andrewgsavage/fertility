import json
import pathlib
import sys

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_ONS_SCRIPTS = _REPO_ROOT / "ONS" / "scripts"
if str(_ONS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_ONS_SCRIPTS))

from metrics import ASFR_BASE_KEYS, METRIC_LABELS, POPULATION_ORDER  # noqa: E402

_FERTILITY_JSON = _REPO_ROOT / "ONS" / "outputs" / "fertility_by_lad.json"


def _cohort_label(asfr_key):
    label = METRIC_LABELS[asfr_key].removeprefix("ASFR — ")
    return label.replace("under 20", "<20")


# One preset per 5-year ASFR band (skipping "under 18", which has no
# button) paired with its matching female-population age band —
# ASFR_BASE_KEYS/POPULATION_ORDER are the same lists
# ONS/scripts/build_plotly_scatter.py builds its dropdowns from, so a band
# added/removed there is picked up here too without editing this file.
_COHORT_PRESETS = [
    (_cohort_label(asfr_key), asfr_key, pop_key) for asfr_key, pop_key in zip(ASFR_BASE_KEYS[1:], POPULATION_ORDER[1:])
]

with open(_FERTILITY_JSON, "r", encoding="utf-8") as f:
    _YEARS = json.load(f)["years"]
_YEAR_MIN, _YEAR_MAX = _YEARS[0], _YEARS[-1]


class ScatterControlsDirective(SphinxDirective):
    """The Explore page's cohort-preset buttons, sync-axes checkbox, and
    year/play controls above the scatter iframe. Built live at Sphinx
    build time from ONS/scripts/metrics.py's ASFR/population key lists and
    outputs/fertility_by_lad.json's year range, so the buttons and the
    slider's min/max always match what scatter_plotly.html actually
    contains rather than being hand-copied into this page."""

    has_content = False
    required_arguments = 0

    def run(self):
        buttons = "\n".join(
            f"  <button class=\"preset-btn\" onclick=\"showCohort('{asfr_key}_2013', '{asfr_key}', 'mean_age_mother', '{pop_key}')\">{label}</button>"
            for label, asfr_key, pop_key in _COHORT_PRESETS
        )
        housing_buttons = "\n".join(
            f"  <button class=\"preset-btn\" onclick=\"showHousingCohort('{asfr_key}', '{pop_key}')\">{label}</button>"
            for label, asfr_key, pop_key in _COHORT_PRESETS
        )
        html = f"""```{{raw}} html
<style>
  .preset-btn {{
    font: inherit;
    padding: 6px 12px;
    border: 1px solid var(--color-background-border);
    border-radius: 4px;
    background: var(--color-background-secondary);
    color: var(--color-foreground-primary);
    cursor: pointer;
    margin: 0 6px 6px 0;
  }}
</style>
<script>
  function showCohort(x, y, color, size) {{
    document.getElementById('sync-checkbox').checked = true;
    var win = document.getElementById('scatter-frame').contentWindow;
    win.setSyncAxes(true);
    win.setPreset(x, y, color, size);
  }}

  function showHousingCohort(y, size) {{
    document.getElementById('sync-checkbox').checked = false;
    var win = document.getElementById('scatter-frame').contentWindow;
    win.setSyncAxes(false);
    win.setPreset('house_price', y, 'mean_age_mother', size);
  }}

  var yearPlayTimer = null;

  function toggleYearPlay() {{
    var btn = document.getElementById('year-play-btn');
    if (yearPlayTimer) {{
      clearInterval(yearPlayTimer);
      yearPlayTimer = null;
      btn.textContent = '▶ Play';
      return;
    }}
    btn.textContent = '⏸ Pause';
    var slider = document.getElementById('year-slider');
    var min = parseInt(slider.min, 10), max = parseInt(slider.max, 10);
    if (parseInt(slider.value, 10) >= max) {{
      slider.value = min;
      slider.dispatchEvent(new Event('input', {{bubbles: true}}));
    }}
    yearPlayTimer = setInterval(function () {{
      var next = parseInt(slider.value, 10) + 1;
      if (next > max) {{
        clearInterval(yearPlayTimer);
        yearPlayTimer = null;
        btn.textContent = '▶ Play';
        return;
      }}
      slider.value = next;
      slider.dispatchEvent(new Event('input', {{bubbles: true}}));
    }}, 700);
  }}
</script>
<p>
  <label style="font: inherit; cursor: pointer; margin-right: 12px;">
    <input type="checkbox" id="sync-checkbox" onchange="document.getElementById('scatter-frame').contentWindow.setSyncAxes(this.checked)">
    Sync Axes
  </label>
  <span style="margin-right: 6px;">ASFR:</span>
{buttons}
</p>
<p>
  <span style="margin-right: 6px;">Housing:</span>
{housing_buttons}
</p>
<p>
  <label style="font: inherit;">
    Year: <b id="scatter-year-label">{_YEAR_MAX}</b>
    <br>
    <span style="display: inline-flex; align-items: center; gap: 8px; width: 100%; max-width: 400px;">
      <button id="year-play-btn" class="preset-btn" style="margin: 0;" onclick="toggleYearPlay()">▶ Play</button>
      <input
        id="year-slider"
        type="range" min="{_YEAR_MIN}" max="{_YEAR_MAX}" step="1" value="{_YEAR_MAX}" style="flex: 1;"
        oninput="document.getElementById('scatter-year-label').textContent = this.value; document.getElementById('scatter-frame').contentWindow.setYear(this.value);"
      >
    </span>
  </label>
</p>
<iframe id="scatter-frame" src="../_static/ons/scatter_plotly.html" style="width: 100%; aspect-ratio: 4 / 3; height: auto; display: block; border: 1px solid var(--color-background-border);" loading="lazy"></iframe>
```"""
        return self.parse_text_to_nodes(html)


def setup(app: Sphinx):
    app.add_directive("scatter-controls", ScatterControlsDirective)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
