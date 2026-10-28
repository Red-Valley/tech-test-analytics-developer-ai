# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

> Every value below was produced by the measures in `MEASURES.dax`, evaluated in the Power BI model
> (`powerbi/TwinHearth_Analytics.pbip`), and cross-checked against an independent SQL query on `data/warehouse.db`.

## 1. Net revenue by title — FY2026 Q2

Measure: `[Net Revenue]`, filtered to FY2026 Q2 (2026-01-01 → 2026-03-31) by order date.

| Title | Net revenue |
|---|---|
| Hollow Crown | 145,510.77 |
| Hollow Crown: Ashen Tide | 44,894.38 |
| Emberwatch Tactics | 51,037.14 |
| Saltmarsh Rally | 47,119.73 |
| Lantern & Lock | 27,300.05 |
| **Company total, FY2026 Q2** | **315,862.09** |

## 2. Cash settled in December 2025

Measure: `[Net Revenue Settled]` for December 2025 (by `settlement_date`).

| | Value |
|---|---|
| Net revenue settled in Dec 2025 | 103,907.40 |

Ambiguity: this is net order value whose settlement date falls in December 2025. Refunds are **not**
subtracted here — refunds hit cash on their own refund date and are reported separately in section 3,
so subtracting them by original order date would mix two date logics in one number.

## 3. Refunds in December 2025, as Treasury counts them

Measure: `[Refunds by Refund Date]` for December 2025 (by `refund_date`), net of the store's fee credit.

| | Value |
|---|---|
| Refunds recognised in Dec 2025 | 5,009.66 |

## 4. Studios — FY2026

Measure: `[Net Revenue]` by studio; `[Company Net Revenue]` for the company row.

| Studio | Net revenue |
|---|---|
| Twin Hearth Studios | 915,896.67 |
| Emberwatch Interactive | 424,406.54 |
| Nine Lanterns | 309,959.94 |
| Saltpine Games | 215,396.86 |
| **Sum of the four rows above** | **1,865,660.01** |
| **Company net revenue, FY2026** | **1,441,253.46** |

The rows add up to more than the company because co-developed titles are credited in full to every
studio that worked on them (Hollow Crown: Ashen Tide to Twin Hearth and Emberwatch Interactive; Emberwatch
Tactics to Emberwatch Interactive and Nine Lanterns), so that revenue is counted once per credited studio — the
difference (424,406.55 on the rounded rows) is those two titles' FY2026 net revenue (236,166.69 + 188,239.85 =
424,406.54), counted a second time; the 0.01 gap is rounding. On the dashboard, studio
values are never summed: the company figure comes from `[Company Net Revenue]` and is shown separately,
labelled "Company total — studio figures include shared credit and do not add up to it".

## 5. Paying players — FY2026 Q2

Measures: `[Paying Players]`, `[Net Revenue per Paying Player]`, filtered to FY2026 Q2.

| | Value |
|---|---|
| Paying players | 12,498 (count) |
| Net revenue per paying player | 25.27 |

Formula: Net Revenue per Paying Player = Net Revenue ÷ Paying Players, where a paying player has
Net Revenue > 0 in the period (orders minus refunds, by original order date). Players whose orders were
fully refunded are excluded (309 in FY2026 Q2; 12,807 players placed at least one order).

## 6. Growth

Measure: `[Net Revenue YoY %]` (built on `[Net Revenue PY]`), filtered to FY2026 Q2.

| | Value |
|---|---|
| FY2026 Q2 vs FY2025 Q2, % | +120.55% |

FY2026 Q2 = 315,862.09; FY2025 Q2 = 143,217.79.

## 7. Twin Hearth Studios — FY2026 by title

Measures: `[Net Revenue]`, `[% of Studio Net Revenue]`, filtered to Twin Hearth Studios and FY2026.

| Title | Net revenue | % of studio |
|---|---|---|
| Hollow Crown | 679,729.98 | 74.21% |
| Hollow Crown: Ashen Tide | 236,166.69 | 25.79% |

Hollow Crown: Ashen Tide is co-developed with Emberwatch Interactive and counts in full here, so the two
rows add up to Twin Hearth's studio total (915,896.67), not to a split share.
