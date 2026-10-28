# Semantic model — Twin Hearth Studios

Built in Power BI Desktop, saved as a Power BI Project: `powerbi/TwinHearth_Analytics.pbip`
(the TMDL in `powerbi/TwinHearth_Analytics.SemanticModel/definition/` is the source of truth; this document describes it).

**Data source:** each table is an Import query that reads its own CSV by file name from one Power Query parameter,
`DataFolder` (the repo's `data/` folder, with a trailing backslash). To refresh from another clone, change only that
parameter (Transform data → Edit parameters).

## 1. Tables and grain

| Table | Type | Grain (one row = …) | Key |
|---|---|---|---|
| fact_order | Fact | one order (one title bought by one player on one storefront), 106,293 rows; carries both the order date and the settlement date | order_id |
| fact_refund | Fact | one refund, 7,722 rows; at most one refund per order (7,722 distinct order_id); partial or full; carries the original order date and the refund date | refund_id |
| dim_date | Dimension (marked as date table) | one calendar day, 2024-10-01 → 2026-12-31, with fiscal columns (FY starts 1 Oct) | date |
| dim_title | Dimension | one title (5) | title_id |
| dim_studio | Dimension | one studio (4) | studio_id |
| bridge_title_studio | Bridge | one studio credit on one title (7): Lead or Co-development | (title_id, studio_id) |
| dim_platform | Dimension | one storefront (5), with its settlement lag (30–60 days) | platform_code |
| dim_player | Dimension | one player (44,990; internal/QA accounts already removed) | player_id |

## 2. Exposed vs hidden columns

The rule: **users build visuals from dimension attributes and measures, never from fact columns.**

- **Fact tables — every column hidden.** `fact_order` and `fact_refund` show only the measures. Keys and dates are
  hidden (dates are browsed through `dim_date`); amount columns are hidden so nobody drags `gross_usd` or
  `net_usd` and gets a number without refunds; `order_status` is hidden because it must never be used to count
  refunds (partial refunds keep `completed`).
- **`bridge_title_studio` — table hidden.** It exists only to carry the studio filter to titles.
- **Dimensions — keys hidden, descriptive attributes exposed:**
  - `dim_title`: `title_name`, `genre`, `launch_date`, `base_price_usd` exposed; `title_id` and `lead_studio_id`
    hidden (`lead_studio_id` is not used for credit — see §3).
  - `dim_studio`: `studio_name`, `region`, `founded_year` exposed; `studio_id` hidden.
  - `dim_platform`: `platform_name`, `settlement_lag_days` exposed; `platform_code` hidden.
  - `dim_player`: `country_code`, `currency_code`, `signup_date`, `acquisition_channel` exposed; `player_id` hidden.
  - `dim_date`: all calendar and fiscal columns exposed (`fiscal_year`, `fiscal_quarter`, `year_month`, …).

## 3. Relationships

All relationships are many-to-one (*:1), fact/bridge on the many side.

| # | From (many) | To (one) | Active | Cross-filter | Why |
|---|---|---|---|---|---|
| 1 | fact_order[order_date] | dim_date[date] | Yes | Single | Revenue is recognised on the order date |
| 2 | fact_order[settlement_date] | dim_date[date] | **No** | Single | Cash view (Q2), activated with USERELATIONSHIP |
| 3 | fact_refund[order_date] | dim_date[date] | Yes | Single | Finance view: refunds hit revenue on the original order date |
| 4 | fact_refund[refund_date] | dim_date[date] | **No** | Single | Treasury view (Q3), activated with USERELATIONSHIP |
| 5 | fact_order[title_id] | dim_title[title_id] | Yes | Single | |
| 6 | fact_refund[title_id] | dim_title[title_id] | Yes | Single | |
| 7 | fact_order[platform_code] | dim_platform[platform_code] | Yes | Single | |
| 8 | fact_refund[platform_code] | dim_platform[platform_code] | Yes | Single | |
| 9 | fact_order[player_id] | dim_player[player_id] | Yes | Single | |
| 10 | fact_refund[player_id] | dim_player[player_id] | Yes | Single | |
| 11 | bridge_title_studio[studio_id] | dim_studio[studio_id] | Yes | Single | |
| 12 | bridge_title_studio[title_id] | dim_title[title_id] | Yes | **Both** (security filter: both) | Studio filter must reach the facts through every title the studio is credited on |

**Deliberately not modelled:** no fact_refund ↔ fact_order relationship (both facts share the dimensions instead); no relationship on dim_title[lead_studio_id] (it would credit co-developed titles to one studio only and create a second studio→title path).

## 4. Non-obvious decisions (business question → what the model does)

- **Revenue vs cash vs Treasury refunds (Q2, Q3).** Each fact has two date roles; the order date is the active
  relationship and the settlement / refund dates are inactive, switched on only inside `[Net Revenue Settled]`
  and `[Refunds by Refund Date]` with `USERELATIONSHIP`. One date table, no duplicated facts.
- **Co-developed titles credited in full to every studio (Q4, Q7).** `bridge_title_studio → dim_title` filters in
  both directions, so a studio reaches the facts through every title it is credited on; studio rows therefore add
  up to more than the company, and `[Company Net Revenue]` (REMOVEFILTERS on `dim_studio`) supplies the real total.
  `dim_title[lead_studio_id]` is deliberately not related.
- **Refunds never inferred from `order_status` (all questions).** `[Net Revenue]` always subtracts
  `fact_refund[net_refund_usd]`; 4,800 of the 7,722 refunds are partial and sit on orders still marked `completed`.
- **Fiscal calendar (Q1, Q5, Q6).** FY starts 1 October; `dim_date` carries `fiscal_year` / `fiscal_quarter`, is
  marked as the date table, and `SAMEPERIODLASTYEAR` works because fiscal quarters are fixed calendar months.
- **Paying player (Q5)** = net revenue > 0 in the period, so fully refunded players are not counted.

## 5. Performance at 50× fact volume (~5.3M orders, ~390k refunds)

Ordered by what would hurt first in *this* model:

1. **`[Paying Players]` iterates players.** `FILTER(VALUES(dim_player[player_id]), [Net Revenue] > 0)` runs a context
   transition and two fact scans per player in the filter context — today ~12.8k players a quarter, at 50× hundreds
   of thousands, and it is evaluated again inside `[Net Revenue per Paying Player]` and for every studio/title cell.
   **Change:** add a pre-aggregated table in the gold layer at grain *player × month* (net order value, net refunds by
   order month), related to `dim_player` and `dim_date`; count players with net > 0 over that table (one small scan
   instead of per-player evaluation). Second option if the gold layer can't change: a calculation that groups once
   (`SUMMARIZE` over `fact_order[player_id]`) rather than iterating the dimension.
2. **`fact_order[order_id]` is already the largest object in the model** (~1.1 MB of 106k unique text values plus its
   attribute-hierarchy structures — measured with `INFO.STORAGETABLECOLUMNSEGMENTS`), and no measure uses it; the same
   goes for `fact_refund[order_id]` / `refund_id`. At 50× it dominates memory and refresh time. **Change:** drop them
   from the semantic model (keep them in gold for drill-to-detail), or at minimum set *Available in MDX = false* to drop
   the hierarchy.
3. **Unused amount columns stored as Double.** `gross_usd`, `platform_fee_usd`, `refund_usd`,
   `platform_fee_credit_usd` are each as large as `net_usd` and unused by any measure. **Change:** remove them; store
   `net_usd` / `net_refund_usd` as Fixed Decimal (currency) for exact 2-dp sums and better compression.
4. **Text surrogate keys.** `player_id` (45k → millions of distinct values) and the other `*_id` text keys cost
   dictionary memory on both the fact and the dimension side. **Change:** integer surrogate keys from the gold layer.
5. **Refresh window vs. three date roles.** With incremental refresh partitioned on `order_date`, recent partitions
   keep changing for ~60 days (settlement lag) and refunds arrive after the order. **Change:** partition `fact_order`
   by `order_date` with a refresh window ≥ 3 months (covers the 30–60-day settlement lag), and `fact_refund` by
   `refund_date` (rows land when the refund happens, so only the latest partitions change).
6. **What will *not* be the bottleneck:** the bidirectional bridge. It has 7 rows and stays that size as orders grow,
   and there is exactly one path from studio to facts, so it adds negligible cost even with RLS applied through it.
   I'd revisit only if the number of studios or co-development deals grew by orders of magnitude.
7. **If we move to Fabric:** points 2–4 are the same work for Direct Lake; the gold tables would need V-Order and the
   aggregated player table from point 1, and the inactive-relationship measures work unchanged.
