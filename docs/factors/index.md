# Factors

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Factors proposed as drivers of lower fertility. Linked factor names go to their own page; the rest are candidates without a page yet.

The ticks mark where each factor's proposed mechanism mainly acts. They are a starting classification, not measured effects. For how much of the UK's post-2010 drop the measured effects explain, see [Explaining the 2010s Drop](explaining-the-2010s-drop.md).

- **Coupling**: the factor acts on forming a partnership.
- **PPR 0→1, PPR 1→2+**: [parity progression ratios](../theory/mdf.md), measured at the end of childbearing. PPR 0→1 is the proportion of women who ever become mothers (1 − childlessness; the period equivalent is TMR). PPR 1→2+ is the proportion of mothers who go on to have a second or further child, which drives [CPM](../theory/mdf.md). A tick means the factor lowers the final proportion, not just delays births.
- **First-birth / Second+ cond. ASFR**: which [conditional ASFR](../uk/cond-asfr.md) the factor mainly lowers — the yearly probability that a childless woman has a first birth, or that a mother has her next birth. Factors acting through partnership formation count towards first births. Age at first birth is the outcome of the first-birth rate, so it is marked only for second+.
- **Young first births**: the factor lowers first births at young ages (teens and twenties) disproportionately, so it mostly postpones first births rather than lowering the first-birth rate evenly across ages. Whether postponed births are later recovered is the open question for these factors.
- **?**: the evidence for this cell is mixed, rests on a single paper, or is untested, so neither a tick nor a blank is justified. See `research/factor-evidence/opus-verdicts.md`.

```{raw} html
<style>
  .factor-table table { width: 100%; }
  .factor-table th:nth-child(n+3) {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    white-space: nowrap;
    vertical-align: middle;
    text-align: left;
    padding: 0.5em 0.25em;
  }
  /* Sticky header: ancestors must not clip overflow */
  .content:has(.factor-table), .factor-table .table-wrapper { overflow: visible !important; }
  .factor-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: var(--color-table-header-background, var(--color-background-secondary));
  }
  @media (max-width: 63em) {
    .factor-table thead th { top: var(--header-height, 3rem); }
  }
  .factor-filter-selects { display: flex; flex-wrap: wrap; gap: 0.4em 1em; font-size: 0.9em; }
  .factor-filter select { margin-left: 0.2em; }
  .factor-filter button { font: inherit; font-size: 0.9em; padding: 0.15em 0.6em; margin-right: 0.4em; cursor: pointer; }
  .factor-filter-count { font-size: 0.9em; color: var(--color-foreground-secondary); }
  .factor-table td:nth-child(n+3) {
    width: 1.8em;
    padding-left: 0.2em;
    padding-right: 0.2em;
    text-align: center;
  }
</style>
```

```{raw} html
<div class="factor-filter">
  <div class="factor-filter-selects"></div>
  <p>
    <button type="button" data-preset="young-not-second">Young first births, not second+ cond. ASFR</button>
    <button type="button" data-preset="clear">Clear filters</button>
    <span class="factor-filter-count"></span>
  </p>
</div>
```

:::{container} factor-table

| Factor | Proposed mechanism | Coupling | PPR 0→1 | First-birth cond. ASFR | Young first births | PPR 1→2+ | Second+ cond. ASFR |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| **Life-course timing** | | | | | | | |
| [Leaving home](leaving-home.md) | Later departure from the parental home delays partnership and first birth | ✓ | ✓ | ✓ | ✓ |  |  |
| Partnership formation | Fewer and later partnerships delay or prevent first births | ✓ | ✓ | ✓ | ✓ |  |  |
| Partnership stability | Separation and divorce end relationships before later births happen (PPR 1→2+: small net effect once repartnering is counted) |  |  |  |  | ✓ | ✓ |
| Age at first birth | Later first births leave less time for higher-order births |  | |  | | ? | ✓ |
| Female age-related infertility | Fecundity falls with age; postponed births are more often not realised |  | ✓ | ✓ |  | ✓ | ✓ |
| Falling sperm counts | Reported declines in semen quality may lower conception rates at all ages |  | ✓ | ✓ |  | ✓ | ✓ |
| **Education and work** | | | | | | | |
| [Education](education.md) | Longer schooling delays family formation; graduates have higher childlessness (coupling: delays marriage rather than preventing it) | ✓ | ✓ | ✓ | ✓ |  |  |
| Student debt | Repayments reduce disposable income during prime childbearing years | ✓ | ✓ | ✓ | ✓ |  |  |
| Female employment | More women in paid work raises the cost of time out of work for children |  | ✓ | ? | ✓ | ✓ | ✓ |
| Motherhood earnings penalty | Mothers' lasting loss of earnings after a birth raises the price of each child |  | ✓ | ✓ |  | ✓ | ✓ |
| Long working hours | Little time left for children, especially a second |  |  |  |  | ✓ | ✓ |
| Job insecurity | Temporary contracts and unstable early careers delay partnership and first births (young first births: not for low-educated groups) | ✓ | ✓ | ✓ | ✓ |  |  |
| Left-behind young men | Young men falling behind in education, work and earnings (including NEETs) leave fewer partners seen as able to support a family (young first births: not for low-educated men) | ✓ | ✓ | ✓ | ✓ |  |  |
| **Costs and housing** | | | | | | | |
| [House prices and home ownership](housing.md) | Delayed home ownership postpones partnership and family formation | ✓ | ✓ | ✓ | ✓ | ✓ | ? |
| [Rents](housing.md) | High rents cut disposable income and keep young adults living with parents or sharing | ✓ | ✓ | ? | ✓ |  |  |
| [Home size](housing.md) | Too few bedrooms for another child |  |  |  |  | ✓ | ✓ |
| Childcare costs | Expensive formal childcare raises the cost of combining work and children |  | ✓ | ✓ | | ✓ | ✓ |
| Cost of raising children | Rising spending per child (education, activities, "intensive parenting") |  |  |  | | ✓ | ✓ |
| Income level | Higher income makes children more affordable but also raises the cost of time spent on them |  | ✓ | ✓ |  | ? | ? |
| Economic uncertainty | Recessions and insecure prospects lead couples to postpone births |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Policy and the state** | | | | | | | |
| Parental leave | Length and pay of leave around a birth |  | ✓ | ✓ |  | ✓ | ✓ |
| Child benefits and tax credits | Cash support per child lowers the net cost of each child |  | ✓ | ✓ |  | ✓ | ✓ |
| Childcare provision | Availability of childcare places, separate from their price |  | ✓ | ✓ |  | ? | ? |
| Tax system | Individual vs household taxation, marginal rates on second earners |  |  |  | | ✓ | ✓ |
| Pensions and welfare state | State old-age support removes children's role as old-age security |  |  |  | | ✓ | ✓ |
| Car-seat rules | Mandatory child seats mean a third child often needs a bigger car |  |  |  |  | ✓ | ✓ |
| Childcare staff ratios | Strict staff-to-child ratios raise the cost of formal childcare |  | ✓ | ✓ |  | ✓ | ✓ |
| Planning rules | Restricting housing supply raises house prices and rents | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Social and cultural** | | | | | | | |
| Contraception | Reliable contraception (the pill, then long-acting methods) prevents unintended births and lets couples delay |  | ✓ | ✓ | ✓ | ✓ | ✓ |
| Abortion | Legal access ends unintended pregnancies, most of them among young women |  | ✓ | ✓ | ✓ |  |  |
| Sex education and teen pregnancy campaigns | Teaching contraception and campaigns against teenage pregnancy cut unintended births among teenagers, mostly delaying rather than preventing motherhood |  |  | ? | ? |  |  |
| Low fertility awareness | People overestimate how late they can conceive and how well IVF works, so they postpone past the point where births are realised |  | ✓ | ✓ |  | ✓ | ✓ |
| Secularisation | Decline in religious practice, which is associated with marriage and larger families | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Gender equality at home | Women carrying most housework and childcare after a first birth deters a second |  |  | ? | | ✓ | ✓ |
| Ideal family size | Smaller desired family size; children as one life option among many |  | ? | ? |  | ? | ? |
| Intensive parenting norms | Higher expected time and money per child raise the cost of each extra child |  |  | ? |  | ✓ | ✓ |
| Smartphones | Screen time displaces in-person socialising, so young adults meet fewer potential partners | ✓ | ✓ | ✓ | ✓ |  |  |
| Dating apps | Abundant choice and swipe markets delay commitment and concentrate attention on a minority of profiles | ✓ | ✓ | ✓ | ✓ |  |  |
| Social media | Online comparison and curated lives shift expectations of partners and of parenthood | ✓ | ✓ | ✓ | ✓ |  |  |
| Political divide between young men and women | Young women and men diverging in politics and values makes partners harder to match | ✓ | ✓ | ✓ | ✓ |  |  |
| [Low-fertility trap](../owid/the-low-fertility-trap.md) | Small families become the norm, lowering ideals in the next generation |  |  |  | | ✓ | ✓ |
| **Population structure** | | | | | | | |
| Urbanisation | Cities have higher housing costs and lower fertility than rural areas |  | ✓ | ✓ | | ✓ | ✓ |
| Child mortality decline | Fewer births are needed to reach a desired number of surviving children |  | ? | ? | ? | ✓ | ✓ |
| [Population ageing and politics](../democracy/index.md) | Older electorates favour spending on pensions over families |  | ✓ | ✓ | | ✓ | ✓ |
:::


```{raw} html
<script>
(function () {
  var table = document.querySelector(".factor-table table");
  var box = document.querySelector(".factor-filter");
  if (!table || !box) return;
  var heads = Array.prototype.slice.call(table.querySelectorAll("thead th"));
  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
  var cols = [2, 3, 4, 5, 6, 7];
  var selects = {};
  cols.forEach(function (c) {
    var label = document.createElement("label");
    label.textContent = heads[c].textContent.trim() + " ";
    var sel = document.createElement("select");
    [["any", "Any"], ["yes", "✓"], ["no", "Blank"]].forEach(function (o) {
      var opt = document.createElement("option");
      opt.value = o[0]; opt.textContent = o[1]; sel.appendChild(opt);
    });
    sel.addEventListener("change", apply);
    label.appendChild(sel);
    box.querySelector(".factor-filter-selects").appendChild(label);
    selects[c] = sel;
  });
  function isHeading(r) { return r.cells[1].textContent.trim() === ""; }
  function apply() {
    var shown = 0, total = 0, heading = null, groupShown = 0;
    function closeGroup() { if (heading) heading.style.display = groupShown ? "" : "none"; }
    rows.forEach(function (r) {
      if (isHeading(r)) { closeGroup(); heading = r; groupShown = 0; return; }
      total++;
      var ok = cols.every(function (c) {
        var v = selects[c].value;
        var ticked = r.cells[c].textContent.indexOf("✓") !== -1;
        return v === "any" || (v === "yes") === ticked;
      });
      r.style.display = ok ? "" : "none";
      if (ok) { shown++; groupShown++; }
    });
    closeGroup();
    box.querySelector(".factor-filter-count").textContent =
      shown === total ? "" : "Showing " + shown + " of " + total + " factors";
  }
  box.querySelectorAll("button").forEach(function (b) {
    b.addEventListener("click", function () {
      cols.forEach(function (c) { selects[c].value = "any"; });
      if (b.dataset.preset === "young-not-second") {
        selects[5].value = "yes";
        selects[7].value = "no";
      }
      apply();
    });
  });
})();
</script>
```

## How factors influence each other

Arrows show proposed influences: education, for example, delays partnership and so raises age at first birth. Factors act through the life-stage outcomes (blue), which feed the two conditional rates (yellow) and then TFR (red). Low TFR then feeds back: population ageing shifts politics towards pensions and away from family policy, and the low-fertility trap lowers ideal family size in the next generation. Those feedback arrows are left off to keep the layout readable. Like the table, this is a map of hypotheses, not estimated effects.

```{raw} html
<p><a href="../_static/factor-graph.html">Open the factor influence graph</a></p>
```

For which of these links have studies separated cause from correlation, see the [causal analysis](causal-analysis.md).

```{toctree}
:maxdepth: 1
:hidden:

leaving-home
education
housing
causal-analysis
explaining-the-2010s-drop
```
