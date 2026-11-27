# Factors

```{warning}
This page was written by AI and has not been fully reviewed. Check figures and claims against the linked sources.
```

Factors are proposed drivers of lower birth rates. Factors that have been investigated have their own page.

## Factor table

Outcomes are changes that have occurred in most countries with large drops in fertility since the 2010s (see the [country comparison](country-comparison.md)):

- Coupling has fallen (marriage and cohabitation rates).
- Fewer couples have had a first child (women with a child by an age, divided by women in a couple at that age).
- First births have fallen ([PPR 0→1](../theory/mdf.md)).
- First-birth [conditional ASFRs](../uk/cond-asfr.md) have fallen at young ages (under 25).
- First-birth conditional ASFRs are fairly similar at older ages (over 35).
- Second births have fallen (PPR 1→2).
- Second-birth conditional ASFRs are broadly constant at all ages.

Period measures like TFR aren't very useful because they aggregate all ages. Cohort measures aren't very useful because a cohort has to reach the end of childbearing before they are complete, which is too late. So this section concentrates on measures that can be taken by age: coupling rates and conditional ASFRs.

In the table:

- **✓**: the factor is expected to affect the outcome.
- **?**: mixed evidence.
- **✗**: the factor is not expected to affect the outcome.
- **Blank**: no data.
- **Two marks** (first-birth cond. ASFR): the factor's effect under 25, then at 35 and over.
- **↓ ↑ →** (Observed rows): the median change across countries fell, rose, or showed no consistent change, one arrow per age from youngest to oldest.

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

| Factor | Proposed mechanism | Single → couple | Couple → first birth | Childless → first birth (PPR 0→1) | First-birth cond. ASFR (under 25, 35+) | PPR 1→2 | Second+ cond. ASFR |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| **Observed, median across countries** | | | | | | | |
| 2005–2010 | Change by age: 20–24, 25–29, 30–34, 35–39 (PPRs: by 25, 30, 35, 40) | ↓↓↓↓ | →↑↑↑ | ↓→↑↑ | ↓→↑↑ | →→→↑ | →→↑↑ |
| 2010–2019 | Change by age: 20–24, 25–29, 30–34, 35–39 (PPRs: by 25, 30, 35, 40) | ↓↓↓→ | ↓↓↓↓ | ↓↓↓↓ | ↓↓↓↑ | →↓↓↓ | ↑→→↑ |
| **Life-course timing** | | | | | | | |
| [Leaving home](leaving-home.md) | Later departure from the parental home delays partnership and first birth | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Partnership formation](partnership-formation.md) | Fewer and later partnerships delay or prevent first births | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Partnership stability](union-stability.md) | Separation and divorce end relationships before later births happen (PPR 1→2+: small net effect once repartnering is counted) | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Age at first birth | Later first births leave less time for higher-order births | ✗ | ✗ | ✗ | ✗ ✗ | ? | ✓ |
| Female age-related infertility | Fecundity falls with age; postponed births are more often not realised | ✗ | ✓ | ✓ | ✗ ✓ | ✓ | ✓ |
| Falling sperm counts | Reported declines in semen quality may lower conception rates at all ages | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| **Education and work** | | | | | | | |
| [Education](education.md) | Longer schooling delays family formation; graduates have higher childlessness (coupling: delays marriage rather than preventing it) | ✓ | ✓ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Student debt](student-debt.md) | Repayments reduce disposable income during prime childbearing years | ✓ | ✓ | ✓ | ✓ ✗ | ✗ | ✗ |
| Female employment | More women in paid work raises the cost of time out of work for children | ✗ | ✓ | ✓ | ✓ ✗ | ✓ | ? |
| Motherhood earnings penalty | Mothers' lasting loss of earnings after a birth raises the price of each child | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| Long working hours | Little time left for children, especially a second | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| [Job insecurity](job-insecurity.md) | Temporary contracts and unstable early careers delay partnership and first births (young first births: not for low-educated groups) | ✓ | ✓ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Left-behind young men](left-behind-young-men.md) | Young men falling behind in education, work and earnings (including NEETs) leave fewer partners seen as able to support a family (young first births: not for low-educated men) | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| **Costs and housing** | | | | | | | |
| [House prices and home ownership](housing.md) | Delayed home ownership postpones partnership and family formation | ✓ | ✓ | ✓ | ✓ ✗ | ✓ | ? |
| [Rents](housing.md) | High rents cut disposable income and keep young adults living with parents or sharing | ✓ | ✓ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Home size](housing.md) | Too few bedrooms for another child | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Childcare costs | Expensive formal childcare raises the cost of combining work and children | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| Cost of raising children | Rising spending per child (education, activities, "intensive parenting") | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Income level | Higher income makes children more affordable but also raises the cost of time spent on them | ✗ | ✓ | ✓ | ✓ ✓ | ? | ? |
| Economic uncertainty | Recessions and insecure prospects lead couples to postpone births | ✗ | ✓ | ✓ | ✓ ✗ | ✓ | ✓ |
| **Policy and the state** | | | | | | | |
| [Parental leave](parental-leave.md) | Length and pay of leave around a birth | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| [Child benefits and tax credits](child-benefits.md) | Cash support per child lowers the net cost of each child | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| [Childcare provision](childcare-provision.md) | Availability of childcare places, separate from their price | ✗ | ✓ | ✓ | ✓ ✓ | ? | ? |
| Tax system | Individual vs household taxation, marginal rates on second earners | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Pensions and welfare state | State old-age support removes children's role as old-age security | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Car-seat rules | Mandatory child seats mean a third child often needs a bigger car | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| Childcare staff ratios | Strict staff-to-child ratios raise the cost of formal childcare | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| Planning rules | Restricting housing supply raises house prices and rents | ✓ | ✓ | ✓ | ✓ ✗ | ✓ | ✓ |
| **Social and cultural** | | | | | | | |
| Contraception | Reliable contraception (the pill, then long-acting methods) prevents unintended births and lets couples delay | ✗ | ✓ | ✓ | ✓ ✗ | ✓ | ✓ |
| [Abortion](abortion.md) | Legal access ends unintended pregnancies, most of them among young women | ✗ | ✓ | ✓ | ✓ ? | ✗ | ✗ |
| Sex education and teen pregnancy campaigns | Teaching contraception and campaigns against teenage pregnancy cut unintended births among teenagers, mostly delaying rather than preventing motherhood | ✗ | ✗ | ✗ | ? ? | ✗ | ✗ |
| Low fertility awareness | People overestimate how late they can conceive and how well IVF works, so they postpone past the point where births are realised | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| Secularisation | Decline in religious practice, which is associated with marriage and larger families | ✓ | ✓ | ✓ | ✓ ✗ | ✓ | ✓ |
| Gender equality at home | Women carrying most housework and childcare after a first birth deters a second | ✗ | ✗ | ✗ | ? ? | ✓ | ✓ |
| [Ideal family size](ideal-family-size.md) | Smaller desired family size; children as one life option among many | ✗ | ? | ? | ? ? | ? | ? |
| Intensive parenting norms | Higher expected time and money per child raise the cost of each extra child | ✗ | ✗ | ✗ | ? ? | ✓ | ✓ |
| [Smartphones](smartphones.md) | Screen time displaces in-person socialising, so young adults meet fewer potential partners | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Dating apps](dating-apps.md) | Abundant choice and swipe markets delay commitment and concentrate attention on a minority of profiles | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Social media](social-media.md) | Online comparison and curated lives shift expectations of partners and of parenthood | ✓ | ? | ✓ | ✓ ✗ | ✗ | ✗ |
| [Political divide between young men and women](political-divide-between-young-men-and-women.md) | Young women and men diverging in politics and values makes partners harder to match | ✓ | ✗ | ✓ | ✓ ✗ | ✗ | ✗ |
| [Low-fertility trap](../owid/the-low-fertility-trap.md) | Small families become the norm, lowering ideals in the next generation | ✗ | ✗ | ✗ | ✗ ✗ | ✓ | ✓ |
| **Population structure** | | | | | | | |
| Urbanisation | Cities have higher housing costs and lower fertility than rural areas | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
| Child mortality decline | Fewer births are needed to reach a desired number of surviving children | ✗ | ? | ? | ? ? | ✓ | ✓ |
| [Population ageing and politics](../democracy/index.md) | Older electorates favour spending on pensions over families | ✗ | ✓ | ✓ | ✓ ✓ | ✓ | ✓ |
:::

```{note}
Observed rows: medians of the [country comparison](country-comparison.md) cells for 2005–2010 and 2010–2019, up to 36 countries; sources and coverage are listed there. Couple → first birth is the share of women with a child by the end of each age band divided by the share in a couple in it. Census-based coupling cells compare 2001–2011 and 2011–2021, and coupling at 25–39 covers 9 to 13 countries. PPR 1→2 by age is the share of mothers by 25, 30, 35 and 40 with a second child by that age, run through each year's [HFD](https://www.humanfertility.org) period fertility table by birth order (pft), for HFD countries without the UK; it is not on the country comparison. An arrow is ↓ or ↑ when the median moved by at least 1 point, 0.02 in the ratio or 5% in a rate, and at least 60% of countries moved the same way; otherwise →.
```

```{raw} html
<script>
(function () {
  var table = document.querySelector(".factor-table table");
  var box = document.querySelector(".factor-filter");
  if (!table || !box) return;
  var heads = Array.prototype.slice.call(table.querySelectorAll("thead th"));
  var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
  var cols = [2, 3, 4, 5, 6, 7];
  var selects = {}, preset = null;
  function isHeading(r) { return r.cells[1].textContent.trim() === ""; }
  cols.forEach(function (c) {
    var label = document.createElement("label");
    label.textContent = heads[c].textContent.trim() + " ";
    var sel = document.createElement("select");
    var vals = {};
    rows.forEach(function (r) { if (!isHeading(r)) vals[r.cells[c].textContent.trim()] = 1; });
    var order = "✓?✗";
    var opts = Object.keys(vals).filter(function (v) { return v !== "" && !/[↓↑→]/.test(v); }).sort(function (a, b) {
      for (var i = 0; i < Math.max(a.length, b.length); i++) {
        var d = order.indexOf(a[i]) - order.indexOf(b[i]); if (d) return d;
      }
      return 0;
    }).map(function (v) { return [v, v]; });
    [["any", "Any"]].concat(opts, [["", "Blank"]]).forEach(function (o) {
      var opt = document.createElement("option");
      opt.value = o[0]; opt.textContent = o[1]; sel.appendChild(opt);
    });
    sel.addEventListener("change", function () { preset = null; apply(); });
    label.appendChild(sel);
    box.querySelector(".factor-filter-selects").appendChild(label);
    selects[c] = sel;
  });
  function apply() {
    var shown = 0, total = 0, heading = null, groupShown = 0, observed = false;
    function closeGroup() { if (heading && !observed) heading.style.display = groupShown ? "" : "none"; }
    rows.forEach(function (r) {
      if (isHeading(r)) {
        closeGroup(); heading = r; groupShown = 0;
        observed = r.cells[0].textContent.trim().indexOf("Observed") === 0;
        return;
      }
      if (observed) return;
      total++;
      var ok = cols.every(function (c) {
        var v = selects[c].value;
        return v === "any" || r.cells[c].textContent.trim() === v;
      }) && (!preset || preset(r));
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
      preset = b.dataset.preset === "young-not-second" ? function (r) {
        return r.cells[5].textContent.trim().charAt(0) === "✓" && r.cells[7].textContent.trim() === "✗";
      } : null;
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

background
life-course
education-and-work
costs-and-housing
policy-and-the-state
social-and-cultural
```
