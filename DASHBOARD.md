# Dashboard — monthly review (one page)

Audience: Head of Publishing Operations, the CFO, and four studio leads. Opened on a laptop, in a meeting,
with about 40 seconds before the first follow-up.

## Wireframe

Values shown are FY2026 Q2 (the default selection), taken from the measures.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Twin Hearth — Monthly review     Fiscal quarter [FY2026 Q2 ▾]  Studio [All ▾] │
├──────────────────────────────────────────────────────────────────────────────┤
│ 1  NET REVENUE  $315,862   ▲ 120.6% vs FY2025 Q2  │ 12,498 paying players     │
│                                                    │ $25.27 per paying player │
├──────────────────────────────────────┬───────────────────────────────────────┤
│ 2  NET REVENUE BY TITLE              │ 3  STUDIOS — CREDITED NET REVENUE      │
│    this quarter  ▮  same Q last FY | │    fiscal year to date                 │
│                                      │                                        │
│ Hollow Crown       ▮▮▮▮▮▮▮▮▮▮ 145.5K │ Twin Hearth   ▮▮▮▮▮▮▮▮▮▮▮▮ 915.9K      │
│ Emberwatch Tactics ▮▮▮▮      51.0K   │ Emberwatch    ▮▮▮▮▮▮      424.4K       │
│ Saltmarsh Rally    ▮▮▮       47.1K   │ Nine Lanterns ▮▮▮▮        310.0K       │
│ Ashen Tide         ▮▮▮       44.9K   │ Saltpine      ▮▮▮         215.4K       │
│ Lantern & Lock     ▮▮        27.3K   │                                        │
│                                      │ Co-developed titles count in full in   │
│ (click a studio → this chart shows   │ each studio. Studios add up to $1.87M; │
│  only its titles, with % of studio)  │ company FY2026 net revenue is $1.44M.  │
├──────────────────────────────────────┴───────────────────────────────────────┤
│ 4  CASH — by month                                                           │
│    line: net revenue (sold)   bars: cash settled (in)   bars: refunds (out)  │
│    Oct ── Nov ── Dec ── Jan ── Feb ── Mar ── …                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

## What is on it, in what order, and why

1. **Headline line (Q1 total, Q6, Q5).** The first thing asked is "how did we do and are we growing", so
   the quarter's net revenue and its growth vs the same quarter last fiscal year sit top-left, in one line.
   Paying players and value per player sit next to it. Four numbers in one strip, each with its context,
   instead of a row of separate cards.
2. **Net revenue by title (Q1, Q6).** Sorted from largest to smallest, with last year's same quarter as a
   thin marker, so "which title moved" is visible without a second chart.
3. **Studios (Q4, Q7).** Credited net revenue per studio for the fiscal year. Clicking a studio filters the
   title chart, which then shows each title's share of that studio (Q7) — no extra visual needed.
4. **Cash (Q2, Q3).** Sold vs settled vs refunded by month. It is mainly the CFO's view and the least frequent
   question, so it goes last.

The order follows the order of the brief's questions, which is the order they get asked in the meeting.

## How the studio vs company confusion is avoided (Q4)

- The company figure is the headline; the studio chart is titled "credited net revenue".
- The studio chart has no total row or total bar, so nobody adds the studios up.
- A fixed note under the chart states both numbers and why they differ.

## How a studio lead sees only their studio

Row-level security, described and not built (out of scope):

- One role, "Studio Lead", with a filter on `dim_studio` that matches the signed-in user to their studio
  (a small user→studio mapping table and `USERPRINCIPALNAME()`).
- The filter flows `dim_studio` → bridge → `dim_title` → both facts, so the lead sees all their titles,
  including co-developed ones in full, as the brief requires. The bridge→title relationship needs
  "Apply security filter in both directions" turned on for this.
- The Head of Operations and the CFO have no role filter and see everything.
- For a lead, the headline shows their credited revenue, not the company total: `REMOVEFILTERS` cannot
  bypass security, which is intended — they only care about their studio.

## What I left off, and what would bring it back

| Left off | Why | Would add it if I were told… |
|---|---|---|
| Platform / storefront breakdown | None of the seven questions asks for it | …decisions are made about which store to invest in |
| Country, currency, acquisition channel | Not asked; would add filters nobody uses in 40 seconds | …marketing joins the review |
| Gross revenue and store fees | The business is defined in net | …someone negotiates store fees |
| Refund reasons | Q3 asks how much, not why | …refund rate becomes a problem to fix |
| Finance-view refunds by month | Net revenue already includes them | …Finance wants to reconcile refunds separately |

## Design decisions

- **One number per question, with context.** Each headline number carries its comparison (vs last year)
  so it answers "is that good?" without a follow-up.
- **Bars, sorted, labelled with values.** Five titles and four studios are compared most quickly as sorted
  horizontal bars; labels avoid having to read an axis.
- **Interaction instead of more visuals.** Q7 is answered by clicking a studio, which keeps the page to four
  blocks.
- **Two filters only:** fiscal quarter and studio. More slicers cost time in a 40-second window.
- **Muted colours, one highlight colour** for the selected period, so the eye goes to the current quarter.
