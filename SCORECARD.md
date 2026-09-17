# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

## 1. Net revenue by title — FY2026 Q2

| Title | Net revenue |
|---|---|
| Hollow Crown | 1,309,044,873|
| Hollow Crown: Ashen Tide | 411,608,585 |
| Emberwatch Tactics | 465,854,929|
| Saltmarsh Rally | 434,635,094|
| Lantern & Lock | 249,289,599|
| **Company total, FY2026 Q2** | 2,870,433,080|

## 2. Cash settled in December 2025

| | Value |
|---|---|
| Net revenue settled in Dec 2025 | 932,163,360|

## 3. Refunds in December 2025, as Treasury counts them

| | Value |
|---|---|
| Refunds recognised in Dec 2025 | 46,438,698|

## 4. Studios — FY2026

| Studio | Net revenue |
|---|---|
| Twin Hearth Studios | 8,279,400,449|
| Emberwatch Interactive | 3,887,638,662|
| Nine Lanterns | 2,844,622,852|
| Saltpine Games | 1,965,239,781|
| **Sum of the four rows above** | 16,976,901,744|
| **Company net revenue, FY2026** | 13,089,263,082|

Underneath, in two sentences: why those last two rows differ, and what you put on the dashboard so
nobody misreads it. 
  Because there are Titles that can have multiple Studios and the Revenue for One Title with multiple Studios is counted for every Studios.
  I added a note for the total Company.

## 5. Paying players — FY2026 Q2

| | Value |
|---|---|
| Paying players | 12,807|
| Net revenue per paying player | 224,130|

State the formula you used.
Net Revenue per Paying Players = DIVIDE([Net Revenue],[Distinct Paying Players Count],0)
  Where Net Revenue is the Revenue less the refund less the store's cut.
  And Distinct Playing Players Count, is the count of distinct players with at least one transaction with positive revenue in the fact_order table.

## 6. Growth

| | Value |
|---|---|
| FY2026 Q2 vs FY2025 Q2, % | 117.42%|

## 7. Twin Hearth Studios — FY2026 by title

| Title | Net revenue | % of studio |
|---|---|---|
| Hollow Crown | 6,118,034,383| 73.89%|
| Hollow Crown: Ashen Tide | 2,161,366,066| 26.11%|
