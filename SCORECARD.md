# Scorecard — fill in every cell

These are the numbers your model has to produce. Fill them in from **your measures**, not from a
one-off query. Every value is USD unless the row says otherwise, rounded to 2 decimals.

Leave nothing blank. If you believe a cell is ambiguous, put your number in and say why underneath.

## 1. Net revenue by title — FY2026 Q2

| Hollow Crown = 145,066.30 
| Hollow Crown: Ashen Tide = 44,722.14 
| Emberwatch Tactics = 52,396.11 
| Saltmarsh Rally = 47,254.92 
| Lantern & Lock = 27,261.38 
| Company total, FY2026 Q2 = 316,700.84

## 2. Cash settled in December 2025

| Net revenue settled in Dec 2025 | 103,910.00 |

## 3. Refunds in December 2025, as Treasury counts them

| Refunds recognised in Dec 2025 | 5,010.00 |

## 4. Studios — FY2026

| Twin Hearth Studios = 913,971.25 
| Emberwatch Interactive = 424,376.81 
| Nine Lanterns = 309,732.17 
| Saltpine Games = 214,765.44 
| Sum of the four rows above  = 1,862,845.65
| Company net revenue, FY2026 = 1,438,468.85


## 5. Paying players — FY2026 Q2

| Paying players = 12,807 
| Revenue per paying player = 24.73 

Formula used: Paying Players = DISTINCTCOUNT of player_id in fact_order
(a "paying player" is any player with at least one order, regardless of
whether that order was later refunded). Revenue per Paying Player =
Net Revenue / Paying Players (Net Revenue already nets out refunds, but
the player is still counted as "paying" even if refunded — this is the
ambiguity flagged in the brief's instructions)

## 6. Growth

| FY2026 Q2 vs FY2025 Q2, % = 120.70% 

## 7. Twin Hearth Studios — FY2026 by title

| Hollow Crown = 677,834.29 - 74.16% 
| Hollow Crown = Ashen Tide - 236,136.96 - 25.84% 
