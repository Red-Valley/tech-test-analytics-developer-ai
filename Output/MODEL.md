# Analytics Developer (AI) — Technical Assessment

## Twin Hearth Studios — semantic model

This document describes the semantic model behind `MEASURES.dax` and `SCORECARD.md`. It is written so the model can be rebuilt from this document alone.

---

## Tables and columns

"Hidden" below means *Hide in report view*: the column does not appear in the Data pane and cannot be dragged onto a visual. Hidden columns remain visible in Model view and Table view for maintenance.

### dim_date

* 822 records
* Marked as the date table on `[date]`. Contains the fiscal calendar structure.
* Columns: `date`, `calendar_year`, `calendar_month`, `month_short`, `calendar_quarter`, `fiscal_year`, `fiscal_quarter`, `fiscal_quarter_no`, `fiscal_month_no`, `year_month`, `is_weekend`
* Hidden: `calendar_quarter`, `calendar_year`. The brief defines every quarter as a fiscal quarter, so exposing calendar equivalents would let two people build the same visual and get different numbers — the disagreement this model exists to end. `year_month` and `month_short` remain exposed for calendar-month questions such as December 2025.
* `fiscal_quarter` holds values of the form `FY2025 Q1`, so the default alphabetical sort is already chronological. No sort-by column is required.
* Carries direct relationships to both `fact_order` and `fact_refund`, detailed in Relationships below.

### fact_order

* One of the two fact tables. One row per order: the order and settlement dates, the player, title and storefront, and the gross value, platform fee and net value.
* 106,293 records
* 10 columns
* Hidden: `order_id`, `title_id`, `player_id`, `platform_code`, `order_date`, `settlement_date`, `gross_usd`, `platform_fee_usd`, `order_status`
  * Foreign keys are hidden because slicing must come from the dimensions.
  * The raw date columns are hidden because all date context comes from `dim_date`.
  * `gross_usd` and `platform_fee_usd` are hidden because dragging `gross_usd` onto a visual yields revenue before the store's cut, which is not what the business means by revenue.
  * `order_status` is hidden because filtering it is always wrong here — see Decisions.
  * `order_id` supports no relationship and is unused; see Performance.
* Exposed: `net_usd` only, and only as the input to `[Gross Revenue]`.

### fact_refund

* The second fact table. One row per refund event: the refund and original order dates, the player, title and storefront, the refund reason, and the refund value, platform fee credit and net refund.
* 7,722 records
* 11 columns
* Hidden: `refund_id`, `order_id`, `title_id`, `player_id`, `platform_code`, `order_date`, `refund_date`, `refund_usd`, `platform_fee_credit_usd`
* Exposed: `net_refund_usd` and `refund_reason`. The reason code is genuinely useful for breaking down why money was given back.

### dim_title

* Dimension table. The five published titles, with genre, launch date and base price.
* 5 records
* Columns: `title_id`, `title_name`, `genre`, `launch_date`, `lead_studio_id`, `base_price_usd`
* Hidden: `title_id`, `lead_studio_id`
* `lead_studio_id` carries no relationship and is deliberately unused. It agrees with every `Lead` row in the bridge, so relating it would give one studio per title — tidier, and contrary to the brief. See Decisions.

### dim_player

* Dimension table. Acquisition channel, country, currency and signup date for every player.
* 44,990 records
* 5 columns
* Hidden: `player_id`
* `signup_date` carries no relationship to `dim_date`. This is intentional: no question in the brief slices by cohort, and a second active relationship into the date table would create an ambiguous filter path.

### dim_studio

* Dimension table. The four studios, their region and founding year.
* 4 records
* 4 columns
* Hidden: `studio_id`

### dim_platform

* Dimension table. The five storefronts and the lag in days between an order and the cash settling for it — 30 to 60 days depending on the store.
* 5 records
* 3 columns
* Hidden: `platform_code`
* `settlement_lag_days` is descriptive. The model does not compute settlement dates from it; `fact_order[settlement_date]` is already in the warehouse.

### bridge_title_studio

* Bridge table resolving the many-to-many between titles and studios. Two of the five titles are co-developed, so the table holds 7 rows. `credit_role` distinguishes `Lead` from `Co-development`.
* 7 records
* 3 columns: `title_id`, `studio_id`, `credit_role`
* **The entire table is hidden.** It has no meaning on its own, and its `title_id` looks identical to `dim_title[title_id]` while filtering differently.
* The bridge is not involved in gross revenue, refunds or net revenue — those come from the facts and `dim_date` alone. It exists solely for studio attribution: scorecard questions 4 and 7, and row-level security.

### _Measures

* Empty table holding every measure, so a reviewer finds them all in one place rather than scattered across the fact tables.

---

## Grain

| Table | Grain |
|---|---|
| `fact_order` | One row per order. 106,293 rows. |
| `fact_refund` | One row per refund event. 7,722 rows. Currently no order carries more than one refund, but the grain does not assume that — partial and subsequent refunds would land as additional rows. |

Both facts are additive over `net_usd` / `net_refund_usd`. Neither is a snapshot.

---

## Relationships

Twelve relationships. One is bidirectional, two are inactive.

| From | To | Cardinality | Cross-filter | Active |
|---|---|---|---|---|
| `fact_order[order_date]` | `dim_date[date]` | Many-to-one | Single | Yes |
| `fact_order[settlement_date]` | `dim_date[date]` | Many-to-one | Single | No |
| `fact_order[title_id]` | `dim_title[title_id]` | Many-to-one | Single | Yes |
| `fact_order[player_id]` | `dim_player[player_id]` | Many-to-one | Single | Yes |
| `fact_order[platform_code]` | `dim_platform[platform_code]` | Many-to-one | Single | Yes |
| `fact_refund[order_date]` | `dim_date[date]` | Many-to-one | Single | Yes |
| `fact_refund[refund_date]` | `dim_date[date]` | Many-to-one | Single | No |
| `fact_refund[title_id]` | `dim_title[title_id]` | Many-to-one | Single | Yes |
| `fact_refund[player_id]` | `dim_player[player_id]` | Many-to-one | Single | Yes |
| `fact_refund[platform_code]` | `dim_platform[platform_code]` | Many-to-one | Single | Yes |
| `bridge_title_studio[title_id]` | `dim_title[title_id]` | Many-to-one | **Both** | Yes |
| `bridge_title_studio[studio_id]` | `dim_studio[studio_id]` | Many-to-one | Single | Yes |

Every dimension-to-fact relationship is single-direction: dimensions filter facts, facts never filter dimensions. The one exception is the bridge, covered under Decisions.

`fact_refund` is modelled as its own star against the shared dimensions rather than joined to `fact_order` through `order_id`. `order_id` is therefore unused and hidden on both facts.

---

## Date table and date roles

`dim_date` is marked as the date table on `[date]`. It is contiguous from 2024-10-01 to 2026-12-31 (822 rows), covering the full FY2025 and FY2026 order range plus the settlement tail — the latest settlement in the warehouse is 2026-11-29.

The fiscal year starts 1 October: FY2026 runs 2025-10-01 to 2026-09-30, and fiscal Q1 is Oct–Dec.

Four date roles exist across the two facts. One date table serves all four:

| Role | Column | Relationship | Used by |
|---|---|---|---|
| Revenue recognition | `fact_order[order_date]` | Active | `[Gross Revenue]` and everything built on it |
| Cash in | `fact_order[settlement_date]` | Inactive | `[Revenue Settled]` |
| Refund recognition | `fact_refund[order_date]` | Active | `[Refunds]`, so `[Net Revenue]` is Finance's basis |
| Cash out | `fact_refund[refund_date]` | Inactive | `[Refunds Paid]` |

The inactive relationships are switched on with `USERELATIONSHIP` inside the two cash-basis measures only.

---

## Decisions the model makes that are not obvious

**`order_status` is never filtered.**
Orders marked `refunded` carry their full original value in `net_usd`; the reversal lives in `fact_refund`. The two tie exactly — $61,849.13 on both sides. Separately, 4,800 orders marked `completed` carry partial refunds. So filtering to `completed` would remove the full-refund orders from gross *and* subtract them again through `[Refunds]`, double-counting the reversal. All orders are included; reversals come from `fact_refund` alone. The column is hidden to prevent anyone filtering it.

**Refunds are a separate star, not a child of `fact_order`.**
`fact_refund` carries its own `title_id`, `player_id` and `platform_code`, so it joins the shared dimensions directly. Routing it through `fact_order` would make refunds depend on the order fact's filter state and would break the moment an order carries two refunds.

**One date table, four roles, two inactive relationships.**
The brief asks for revenue on the order date (Finance) and cash on the settlement and refund dates (Treasury). A second date table would put two date slicers on one page, which reintroduces the disagreement this model exists to end. Instead the active relationships serve the Finance basis, which answers five of the seven questions, and two measures shift context explicitly.

**Studio reaches title only through the bridge; `lead_studio_id` is unused.**
`dim_title[lead_studio_id]` agrees with every `Lead` row in the bridge, so relating it would give one studio per title and make the four studio rows sum cleanly to the company total. That contradicts the brief: co-developed titles are credited in full to every studio that worked on them. The bridge preserves the intended double-count.

**The bridge is the model's only bidirectional relationship.**
Filters travel `dim_studio` → bridge → `dim_title` → facts, and that last hop runs from the many side to the one side, which requires cross-filtering set to Both. It is safe here because there is exactly one path between studio and title, so no ambiguity, and because the bridge is 7 rows and does not grow with order volume.

**RLS intent (not implemented, per scope).**
A `Studio Lead` role would filter `dim_studio[studio_id]` against a mapping of user principal to studio. Because the bridge relationship is bidirectional, *Apply security filter in both directions* must be enabled on it, or the security filter stops at `dim_studio` and never reaches the facts. A lead assigned to Emberwatch Interactive would see Ashen Tide, since co-development credits the title to them in full.

---

## Performance

The fact tables are 106k and 7.7k rows today. At roughly fifty times order volume that is about 5.3M and 390k. Naming what would and would not hurt:

### What would hurt first

**`order_id` on both facts.** A unique string key, so VertiPaq cannot compress it — the dictionary grows linearly with row count and this becomes the single largest column in the model. It supports no relationship and appears in no measure. Remove it in Power Query. Same for `refund_id`. This is the cheapest large win available.

**`DISTINCTCOUNT(fact_order[player_id])` behind `[Paying Players]`.** Distinct counts do not pre-aggregate; the engine builds a distinct set per filter context, and cost scales with both row count and cardinality — `dim_player` is already 44,990 and would grow alongside orders. It is re-evaluated for every cell of every visual it appears in. Mitigations in order: keep it off high-cardinality breakdowns, which the current page design already does by using it as a single headline figure rather than a per-title-per-month matrix; if that stops being enough, add a pre-aggregated player-period table in the gold layer and point the measure at it.

**Refresh duration rather than query duration.** A full import of 5.3M rows will break the refresh window before it breaks any visual. Incremental refresh partitioned on `fact_order[order_date]`, keeping a rolling window. One model-specific caveat: `fact_refund` must be partitioned on `refund_date`, not `order_date`. A refund arriving today against a two-year-old order would fall into a cold partition and never be picked up.

### What would not hurt, and why

**The bidirectional bridge.** 7 rows against 5 titles, independent of order volume, trivial at any fact size. Stated explicitly because bidirectional relationships are a standard performance flag and this one is not the problem.

**`platform_code` as a string relationship key.** Integer surrogate keys are the usual advice, but this column has 5 distinct values, so dictionary encoding reduces it to a few bits per row regardless of table size. Replacing it would be effort spent for no measurable gain.

**`[Studio Credited Net Revenue]` iterating studios.** `SUMX` over `VALUES(dim_studio[studio_id])` costs four evaluations of `[Net Revenue]`. The iterator is over 4 rows and does not grow with order volume. It would only matter if the studio count reached the hundreds.

**Storage mode.** Import remains correct at 5.3M rows. The point to revisit is when the compressed model approaches the workspace limit or refresh stops fitting its window — not a row count on its own.