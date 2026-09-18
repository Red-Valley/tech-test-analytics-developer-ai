# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

## 1. Net revenue by title — FY2026 Q2

| Title | Net revenue |
|---|---|
| Hollow Crown | 145,510.77 |
| Hollow Crown: Ashen Tide | 44,894.38|
| Emberwatch Tactics | 27,300.05|
| Saltmarsh Rally | 47,119.73|
| Lantern & Lock | 51,037.14|
| **Company total, FY2026 Q2** | 315,862.0|

## 2. Cash settled in December 2025

| | Value |
|---|---|
| Net revenue settled in Dec 2025 | 103,907.40|

This cell is ambiguous. "Net revenue settled" could mean cash arriving on settlement dates in December, or that figure less refunds paid out in December. I report inflows only — [Revenue Settled], which moves [Gross Revenue] onto fact_order[settlement_date] via USERELATIONSHIP — because the brief asks cash-in and cash-out as two separate questions, and question 3 collects the outflow. The netted alternative, [Net Cash Settled] = 103,907.40 − 5,009.66 = 98,897.74, is available as a measure if Treasury prefers that reading.


## 3. Refunds in December 2025, as Treasury counts them

| | Value |
|---|---|
| Refunds recognised in Dec 2025 | 5,009.66|

## 4. Studios — FY2026

| Studio | Net revenue |
|---|---|
| Twin Hearth Studios | 915,896.67|
| Emberwatch Interactive | 424,406.54|
| Nine Lanterns | 215,396.86|
| Saltpine Games | 309,959.94|
| **Sum of the four rows above** | 1,865,660.01|
| **Company net revenue, FY2026** | 1,441,253.46|

Underneath, in two sentences: why those last two rows differ, and what you put on the dashboard so nobody misreads it.

Company net revenue counts each order once, while the four studio rows are independent credit figures in which co-developed titles are credited in full to every studio that worked on them — so the rows sum to 424,406.55 more than the company total. On the dashboard the studio bars are drawn against a dashed reference line showing company net revenue, captioned to say the bars exceed it by design, so the gap is labelled rather than discovered mid-meeting.

## 5. Paying players — FY2026 Q2

| | Value |
|---|---|
| Paying players | 12,807|
| Revenue per paying player | 24.66|

State the formula you used.

[Revenue per Paying Player] = DIVIDE ( [Net Revenue], [Paying Players] ), where [Paying Players] = DISTINCTCOUNT ( fact_order[player_id] ) over orders whose order date falls in FY2026 Q2. A player whose only order was fully refunded still counts as a paying player: they transacted. The ratio is therefore asymmetric on purpose — the numerator is net of refunds, the denominator is a headcount that is not.

## 6. Growth

| | Value |
|---|---|
| FY2026 Q2 vs FY2025 Q2, % | 120.55%|

## 7. Twin Hearth Studios — FY2026 by title

| Title | Net revenue | % of studio |
|---|---|---|
| Hollow Crown | 679,729.98| 74.21%|
| Hollow Crown: Ashen Tide | 236,166.69| 25.79%|
