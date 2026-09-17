# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

Every number below is verified by `verification/verify_scorecard.py` against `verification/checks.json`
— see `verification/VERIFICATION.md` for the full PASS run. Each SQL check mirrors the exact filter
context of the DAX measure named in `MEASURES.dax`; nothing here was queried first and
reverse-engineered into DAX afterward.

## 1. Net revenue by title — FY2026 Q2

Measure: `Net Revenue`, filtered to `dim_title` and `order_date` in FY2026 Q2 (2026-01-01 → 2026-03-31).

| Title | Net revenue |
|---|---|
| Hollow Crown | 145,510.77 |
| Hollow Crown: Ashen Tide | 44,894.38 |
| Emberwatch Tactics | 51,037.14 |
| Saltmarsh Rally | 47,119.73 |
| Lantern & Lock | 27,300.05 |
| **Company total, FY2026 Q2** | **315,862.09** |

Company total = `Company Net Revenue` (title/studio/bridge filters stripped), not a manual sum of the
rows above — though at title grain (each order/refund has exactly one `title_id`, no bridge involved)
the two agree to the cent: verified by `assert_q1_titles_sum_to_company` in `verification/checks.json`.

**Each row above is rounded independently to 2dp for display; the underlying, unrounded rows sum
exactly to the unrounded company total.** Unrounded: 145,510.7727 + 44,894.3843 + 51,037.1449 +
47,119.7342 + 27,300.0549 = 315,862.0910, which rounds to **315,862.09** — the figure printed above.
If you instead add the five **displayed** (already-2dp-rounded) figures — 145,510.77 + 44,894.38 +
51,037.14 + 47,119.73 + 27,300.05 — you get **315,862.07**, two cents short. That gap is rounding
accumulation from summing five independently-rounded numbers, not a data or measure discrepancy;
`Company Net Revenue` is never computed by summing the displayed rows, precisely to avoid it.

## 2. Cash settled in December 2025

Measure: `Cash Settled` — `SUM(fact_order[net_usd])` on `settlement_date`, via `USERELATIONSHIP`. Not
netted against refunds (§3 reports the refund outflow separately; see the note under §4 for why the
two are kept apart rather than combined into one cash figure).

| | Value |
|---|---|
| Net revenue settled in Dec 2025 | 103,907.40 |

## 3. Refunds in December 2025, as Treasury counts them

Measure: `Refunds (Treasury)` — `SUM(fact_refund[net_refund_usd])` on `refund_date`, via
`USERELATIONSHIP`. This is the refund-date basis, not the order-date basis §1/§4 use.

| | Value |
|---|---|
| Refunds recognised in Dec 2025 | 5,009.66 |

## 4. Studios — FY2026

Measure: `Studio Credit Total`'s per-studio term is `Net Revenue` evaluated once per `dim_studio` row,
crossing the bidirectional `dim_title ↔ bridge_title_studio` relationship — each studio's titles come
from the bridge, not from `dim_title[lead_studio_id]`.

| Studio | Net revenue |
|---|---|
| Twin Hearth Studios | 915,896.67 |
| Emberwatch Interactive | 424,406.54 |
| Nine Lanterns | 309,959.94 |
| Saltpine Games | 215,396.86 |
| **Sum of the four rows above** | **1,865,660.01** |
| **Company net revenue, FY2026** | **1,441,253.46** |

**Why those two rows differ:** the "sum of four" is `Studio Credit Total` — it re-evaluates `Net
Revenue` once per studio, so `Hollow Crown: Ashen Tide` (Twin Hearth + Emberwatch) and `Emberwatch
Tactics` (Emberwatch + Nine Lanterns) are each counted twice, once per studio that shares the credit.
"Company net revenue" is `Company Net Revenue` — the same `Net Revenue` measure with every
studio/bridge/title filter stripped, so it counts each of the 5 titles exactly once. The gap
(424,406.54) is exactly the FY2026 net revenue of the two co-credited titles — verified by
`assert_q4_double_count_equals_shared_titles`. **On the dashboard:** the two figures never sit in the
same visual without a label distinguishing "per-studio credit" from "company total," and the studio
breakdown carries a standing footnote that co-developed titles are double-counted by design (see
`DASHBOARD.md`).

**On rounding:** the same per-row-independent-rounding effect from §1 applies here in principle — each
studio row is rounded to 2dp on its own before display. In this case it happens not to move the last
cent: the unrounded studio rows (915,896.6705 + 424,406.5410 + 309,959.9377 + 215,396.8566 =
1,865,660.0058) round to **1,865,660.01**, identical to summing the four displayed 2dp figures
(915,896.67 + 424,406.54 + 309,959.94 + 215,396.86 = 1,865,660.01). Unlike §1, there is no visible gap
here — but the "sum of four" row was never intended to reconcile with "company net revenue" anyway
(that's the whole point of this section), so the two kinds of discrepancy (rounding accumulation vs.
the deliberate double-count) should not be confused with each other.

## 5. Paying players — FY2026 Q2

| | Value |
|---|---|
| Paying players | 12,498 |
| Revenue per paying player | 25.27 |

**Formula:** `Revenue per Paying Player` = `Net Revenue` ÷ `Paying Players`, both for FY2026 Q2 =
315,862.09 ÷ 12,498 = 25.27.

**`Paying Players`** iterates `dim_player` and keeps a player only if their `Net Revenue` for the
period is strictly positive (`COUNTROWS(FILTER(dim_player, ROUND([Net Revenue], 4) > 0))` — the
`ROUND` guards the test against floating-point representation noise, it is not a display rounding) —
a player whose entire FY2026 Q2 order was refunded does not count as paying. A separate footnote measure, `Paying
Players (Transacted)` (`DISTINCTCOUNT(fact_order[player_id])`), shows **12,807** — everyone who placed
an order in the period regardless of refund outcome. The 309-player gap between the two is exactly the
players whose net revenue for the quarter is zero or negative.

**This is one of the two decisions I am least sure about.** "Paying player" could reasonably mean
either number, and the two are close enough (12,498 vs 12,807, a 2.4% difference) that the choice
matters less for the ratio than for the conversation about it — someone in the room will ask why this
isn't the same number as "orders this quarter," and the model needs the transacted figure on hand as
the answer, not just the net-revenue figure.

## 6. Growth

Measure: `Net Revenue YoY %` = `(Net Revenue − Net Revenue PY) ÷ Net Revenue PY`, where `Net Revenue
PY` uses `DATEADD(dim_date[date], -1, YEAR)`.

| | Value |
|---|---|
| FY2026 Q2 vs FY2025 Q2, % | 120.55 |

FY2026 Q2 net revenue: 315,862.09. FY2025 Q2 net revenue: 143,217.79. `DATEADD(-1, YEAR)` shifts every
date in the FY2026 Q2 filter back exactly one calendar year, landing on 2025-01-01→2025-03-31 — the
same fiscal quarter of the prior fiscal year, because this fiscal calendar's quarters are fixed
calendar-month ranges (see `MODEL.md`, decision #5).

**Decomposed, measure-backed:** `Net Revenue YoY % (Like-for-like)` restricts both periods to the
titles that had positive net revenue in *both* quarters (`T-01`, `T-03`, `T-04` — `T-02` launched
2025-09-30 and `T-05` launched 2026-02-12, so both are zero in FY2025 Q2 and excluded by the measure's
own filter, not by a manual list). `Net Revenue YoY % (New Titles)` takes the remainder — current-period
revenue from titles *not* in that set — over the **same** prior-year-total denominator, so the two
measures are additive:

> **120.55% = 53.56 pp like-for-like + 66.98 pp from titles launched since (T-02, T-05)**

Note that the two displayed parts add to **120.54**, one hundredth short of the displayed total, because
each is rounded to 2dp independently. Unrounded they sum exactly: 53.56371812… + 66.98297039… =
120.54668851…, which rounds to **120.55**. Same rounding-accumulation effect as §1 — the decomposition
is exact, the display isn't; `assert_q6_pp_decomposition_sums_to_total` checks the identity at full
precision rather than on the rounded figures.

An earlier draft of this note said "new-title revenue is 30.37% of the FY2026 Q2 total" and conflated
that with "growth" — that 30.37% (95,931.53 of 315,862.09) is a real, correct number, but it's new
titles' **share of current revenue**, not their **contribution to the YoY growth percentage**, and the
two aren't the same statistic: share-of-revenue divides by the current period's own total, while a
growth-percentage-point contribution has to divide by the *prior*-period total to be additive with the
other growth term. The corrected framing above is what actually decomposes to 120.55% when added; the
30.37% figure is kept in `verification/checks.json`'s `q6_likeforlike_current` commentary as a distinct,
still-true, but differently-scoped fact. Checked by `q6_likeforlike_growth_pct`, `q6_new_titles_pp`, and
`assert_q6_pp_decomposition_sums_to_total` in `verification/checks.json`.

## 7. Twin Hearth Studios — FY2026 by title

Measure: `Net Revenue` for the title row; `% of Studio Net Revenue` = `Net Revenue ÷ Studio Total Net
Revenue`, where the denominator is pinned to Twin Hearth's own FY2026 total regardless of which title
row is being evaluated (see `MEASURES.dax`, `Studio Total Net Revenue`).

| Title | Net revenue | % of studio |
|---|---|---|
| Hollow Crown | 679,729.98 | 74.21% |
| Hollow Crown: Ashen Tide | 236,166.69 | 25.79% |

These are the only two titles credited to Twin Hearth Studios (verified against
`bridge_title_studio`); the two percentages sum to 100.00% (`assert_q7_pct_sums_to_100`).
