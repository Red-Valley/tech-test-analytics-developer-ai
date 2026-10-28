# Dashboard — monthly leadership review (one page)

**Audience:** Head of Publishing Operations, CFO, four studio leads. **Device:** a laptop, in a meeting.
**Budget:** ~40 seconds before the first follow-up question. **Design rule:** every number on the page answers one
of the seven questions, in the order they get asked; nothing is there "because we have the data".

## 1. Wireframe

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ TWIN HEARTH — MONTHLY REVIEW     Viewing: [Company ▾]       Period: [FY2026 Q2 ▾]            │  ← dynamic title + 1 slicer
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ A  NET REVENUE  FY2026 Q2                                                                    │
│    $315,862   ▲ +120.6% vs FY2025 Q2 ($143,218)      $25.27 per paying player · 12,498 players │  ← Q1 total, Q6, Q5 in one line
├───────────────────────────────────────────────┬──────────────────────────────────────────────┤
│ B  NET REVENUE BY TITLE — FY2026 Q2           │ C  STUDIOS — FY2026 (credit view)            │
│                                               │                                              │
│ Hollow Crown         ███████████████ 145,511 ▮│ Twin Hearth   915,897                        │
│ Emberwatch Tactics   █████           51,037  ▮│   Hollow Crown            74%  ████████      │
│ Saltmarsh Rally      █████           47,120  ▮│   Ashen Tide ⇄            26%  ███           │
│ Ashen Tide           ████            44,894  ▮│ Emberwatch    424,407                        │
│ Lantern & Lock       ███             27,300  ▮│ Nine Lanterns 309,960                        │
│        ▮ = same quarter last year             │ Saltpine      215,397                        │
│                                               │ ⇄ co-developed: credited in full to each     │
│                                               │   studio — rows don't add up to company      │
│                                               │   Company FY2026: 1,441,253 (shown separately)│
├───────────────────────────────────────────────┴──────────────────────────────────────────────┤
│ D  CASH vs REVENUE — last 12 months (monthly)                                                │
│   ── net revenue (order date)   ── cash settled (settlement date)   ▂ refunds paid (refund date)│
│   Dec 2025 callout: settled $103,907 · refunds $5,010                                        │  ← Q2, Q3
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 2. What is on it, in what order, and why

1. **A — one headline line, not a row of cards.** Quarter net revenue with its growth and its per-player value
   read as one sentence ("we made $316k, up 121%, $25 per paying player"). That covers Q1-total, Q6 and Q5 in
   the first 5 seconds — the three numbers that get quoted out loud. Growth sits next to the number it
   qualifies instead of in its own card.
2. **B — titles (Q1), sorted by revenue, with a last-year marker on each bar.** Bars are compared by length,
   which is faster than reading five numbers; the marker answers "which title drove the growth" without a
   second chart.
3. **C — studios (Q4) with the studio's own titles nested underneath (Q7).** One matrix: studio rows expand into
   their credited titles with `% of Studio Net Revenue`. The grand total row is **switched off**, co-developed
   titles carry a ⇄ marker, and the company figure comes from `[Company Net Revenue]` in a separate,
   labelled line — so the slide that always causes the argument no longer has a total to add up.
4. **D — cash vs revenue by month (Q2, Q3).** Treasury questions are about *when money moved*, so they get a
   time axis: three series on three different dates (order, settlement, refund). The gap between the revenue
   and cash lines *is* the 30–60-day settlement lag, which makes "why is cash lower than sales this month?"
   self-explaining. December is called out because it's the month in the review.

**One slicer only — fiscal period.** Defaults to the last complete fiscal quarter. Panel C is fixed to the fiscal
year of the selected quarter (the brief's studio view is annual); panel D always shows the trailing 12 months.

## 3. How a studio lead sees only their studio

- **RLS role "Studio Lead"** on `dim_studio`: a user→studio mapping table filters `dim_studio[studio_id]` for
  `USERPRINCIPALNAME()`. (Intent only — implementation is out of scope.)
- The filter reaches both fact tables through `bridge_title_studio → dim_title`, which is set to filter **and
  apply the security filter in both directions**. A lead therefore sees every title their studio is credited
  on, including co-developed ones in full — the same rule they are paid and reviewed on.
- **Consequence I designed for:** under RLS, *every* number is restricted, including `[Company Net Revenue]`
  (REMOVEFILTERS cannot lift a security filter). So for a studio lead the page relabels itself: the header
  shows "Viewing: Twin Hearth Studios", panel A becomes their studio's headline, and the separate company line
  in panel C is hidden — otherwise a lead would see their own total labelled as "Company".
- Head of Publishing and the CFO have no role filter and see the company view.

## 4. How nobody misreads studio totals vs the company total

- No grand total on the studio matrix; studio values are never summed anywhere on the page.
- ⇄ marker + one-line footnote on co-developed titles.
- Company FY2026 net revenue sits on its own labelled line driven by `[Company Net Revenue]`, not by a total row.

## 5. What I left off, and what I'd need to be told to put it back

| Left off | Why | Put it back if… |
|---|---|---|
| Storefront (platform) split | Not one of the seven questions; fees are already netted out | …store cuts or settlement lags start changing, or a storefront deal is being renegotiated |
| Refunds by reason | Treasury asks *how much*, not *why* | …the refund rate moves beyond a threshold someone agrees on |
| Player acquisition channel / country | Marketing questions, not publishing-review ones | …the review starts owning user-acquisition spend |
| Gross revenue and store fees | "Net revenue is what we keep" — showing gross invites the wrong number being quoted | …finance needs to reconcile to store statements |
| Daily or weekly trend | Monthly review; daily noise costs attention | …a launch or a sale event is being reviewed |
| Separate KPI cards per question | "I do not want a wall of cards" | never — combined into the headline line |
