# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

> All values below were read from table visuals in `TwinHearth.pbix`, using the measures in
> `MEASURES.dax`. The measure behind each cell is named in the notes.

## 1. Net revenue by title — FY2026 Q2

| Title | Net revenue |
|---|---|
| Hollow Crown | 145,510.77 |
| Hollow Crown: Ashen Tide | 44,894.38 |
| Emberwatch Tactics | 51,037.14 |
| Saltmarsh Rally | 47,119.73 |
| Lantern & Lock | 27,300.05 |
| **Company total, FY2026 Q2** | **315,862.09** |

Measure: `[Net Revenue]`, `dim_date[fiscal_quarter] = "FY2026 Q2"`, rows = `dim_title[title_name]`.

## 2. Cash settled in December 2025

| | Value |
|---|---|
| Net revenue settled in Dec 2025 | 103,907.40 |

Measure: `[Cash Settled]`, `dim_date[year_month] = Dec 2025`.
Assumption: this is order net value (after the store's cut) by `settlement_date`, and it **includes
orders that were later refunded** — the store paid that money in December; refunds leave the bank on
their own date and are reported in section 3, so they are not netted here.

## 3. Refunds in December 2025, as Treasury counts them

| | Value |
|---|---|
| Refunds recognised in Dec 2025 | 5,009.66 |

Measure: `[Refunds (Treasury)]`, `dim_date[year_month] = Dec 2025`, dated by `refund_date`.
Assumption: uses `net_refund_usd` (net of the store fee credit), consistent with net revenue being
net of the store's cut. The gross amount returned to players (`refund_usd`) would be 6,977.47.

## 4. Studios — FY2026

| Studio | Net revenue |
|---|---|
| Twin Hearth Studios | 915,896.67 |
| Emberwatch Interactive | 424,406.54 |
| Nine Lanterns | 309,959.94 |
| Saltpine Games | 215,396.86 |
| **Sum of the four rows above** | **1,865,660.01** |
| **Company net revenue, FY2026** | **1,441,253.46** |

Measures: `[Net Revenue]` per studio, `[Studio Credited Net Revenue]`, `[Company Net Revenue]`; FY2026.

The sum is 424,406.54 higher because the two co-developed titles (Ashen Tide and Emberwatch Tactics) are credited in full to both of their studios, so they are counted twice in the studio sum but once in the company total. On the dashboard, company net revenue is the headline number and the studio chart is labelled "credited revenue — co-developed titles count in each studio", with no studio total shown.

## 5. Paying players — FY2026 Q2

| | Value |
|---|---|
| Paying players | 12,498 |
| Net revenue per paying player | 25.27 |

Formula:
- `Paying Players` = number of distinct players whose net revenue in the period (net orders − net
  refunds, both by order date) is greater than zero.
- `Net Revenue per Paying Player` = `[Net Revenue]` ÷ `[Paying Players]` = 315,862.09 ÷ 12,498.

Why: 12,807 distinct players placed an order in FY2026 Q2, but 309 of them were refunded in full and
left zero net revenue. Counting them would understate what a paying player is worth (24.66 instead
of 25.27).

## 6. Growth

| | Value |
|---|---|
| FY2026 Q2 vs FY2025 Q2, % | 120.55% |

Measure: `[Net Revenue YoY %]` = (FY2026 Q2 − FY2025 Q2) ÷ FY2025 Q2 = (315,862.09 − 143,217.79) ÷
143,217.79. FY2025 Q2 = Jan–Mar 2025, via `SAMEPERIODLASTYEAR`. Part of the growth comes from titles
that did not exist a year earlier (Ashen Tide launched Sep 2025, Emberwatch Tactics Feb 2026).

## 7. Twin Hearth Studios — FY2026 by title

| Title | Net revenue | % of studio |
|---|---|---|
| Hollow Crown | 679,729.98 | 74.21% |
| Hollow Crown: Ashen Tide | 236,166.69 | 25.79% |

Measure: `[Net Revenue]` and `[% of Studio Net Revenue]`, filtered to `dim_studio[studio_name] = "Twin
Hearth Studios"` and FY2026. Ashen Tide is co-developed with Emberwatch but is credited in full to
Twin Hearth, per the brief, so the two titles add up to 100% of the studio's 915,896.67.
