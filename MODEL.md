# Semantic Model

Star schema, one fact grain each, all filtering routed through conformed dimensions. No fact-to-fact
relationship exists anywhere in this model — **rule: only shared dimensions may filter both facts.**
`fact_refund` carries its own `title_id`, `player_id`, `platform_code` and `order_date` (verified to
agree with the parent order on all 7,722 rows), so it hangs directly off the same four dimensions as
`fact_order` instead of joining through it.

## Tables

### `fact_order` — grain: one row per order
PK `order_id`. 106,293 rows.

| Column | Type | Exposed? | Role |
|---|---|---|---|
| `order_id` | Text | Hidden | surrogate key |
| `order_date` | **Date** | Hidden | FK → `dim_date[date]`, **active** — revenue recognition date |
| `settlement_date` | **Date** | Hidden | FK → `dim_date[date]`, inactive — cash date |
| `player_id` | Text | Hidden | FK → `dim_player` |
| `title_id` | Text | Hidden | FK → `dim_title` |
| `platform_code` | Text | Hidden | FK → `dim_platform` |
| `order_status` | Text | **Hidden** | `completed` \| `refunded` — **never filter on this** (see trap below) |
| `gross_usd` | Fixed Decimal (4dp) | Hidden | source for measures only |
| `platform_fee_usd` | Fixed Decimal (4dp) | Hidden | source for measures only |
| `net_usd` | Fixed Decimal (4dp) | Hidden | source for measures only |

Every column in this table is hidden from the field list. Nothing is dragged into a visual directly;
everything is consumed through a measure. `order_status` is called out separately because it is the
one column a report author would be tempted to filter on — doing so double-counts or under-counts
refunds (see Non-obvious decision #1).

### `fact_refund` — grain: one row per refund, 1:1 with the order it refunds
PK `refund_id`. 7,722 rows. No order gets more than one refund row (verified).

| Column | Type | Exposed? | Role |
|---|---|---|---|
| `refund_id` | Text | Hidden | surrogate key |
| `order_id` | Text | **Hidden, unrelated** | kept for traceability only — **not** used in any relationship |
| `order_date` | **Date** | Hidden | FK → `dim_date[date]`, **active** — Finance basis |
| `refund_date` | **Date** | Hidden | FK → `dim_date[date]`, inactive — Treasury basis |
| `title_id` | Text | Hidden | FK → `dim_title` |
| `player_id` | Text | Hidden | FK → `dim_player` |
| `platform_code` | Text | Hidden | FK → `dim_platform` |
| `refund_reason` | Text | Hidden | not used by any scorecard measure |
| `refund_usd` | Fixed Decimal (4dp) | Hidden | source for measures only |
| `platform_fee_credit_usd` | Fixed Decimal (4dp) | Hidden | source for measures only |
| `net_refund_usd` | Fixed Decimal (4dp) | Hidden | source for measures only, always **positive** — subtract, don't add |

### `dim_date` — **marked as the Date Table** on `date`
822 contiguous rows, 2024-10-01 → 2026-12-31, 0 gaps.

| Column | Type | Exposed? |
|---|---|---|
| `date` | Date | Yes (hidden helper for hierarchy only) |
| `calendar_year`, `calendar_month`, `calendar_quarter` | Whole Number | Yes |
| `month_short` | Text | Yes (**Sort By Column: `fiscal_month_no`**, so months read Oct → Sep, not Jan → Dec) |
| `fiscal_year`, `fiscal_quarter` | Text | Yes |
| `fiscal_quarter_no`, `fiscal_month_no` | Whole Number | Yes (sort columns) |
| `year_month` | Text | Yes |
| `is_weekend` | Boolean | Hidden — unused |

Confirmed: FY starts 1 Oct every fiscal year (`FY2025 Q1` = 2024-10-01→2024-12-31, `FY2026 Q1` =
2025-10-01→2025-12-31). Q2 of every fiscal year = Jan-Mar. `fiscal_quarter_no`/`fiscal_month_no` are
stored as text like every other column in the source and must be cast to Whole Number at import — they
exist purely as **Sort By Column** for `fiscal_quarter`/`month_short`, not for filtering.

### `dim_title` — 5 rows, PK `title_id`
`lead_studio_id` is **hidden**: it agrees with the bridge's `Lead` row on all 5 titles, so it looks
like a safe shortcut for "which studio owns this title" — but joining on it gives 5 credits instead of
7 and silently makes studio totals reconcile to the company total, which question 4 explicitly says
must *not* happen. The bridge is the only path from a title to a studio.

### `dim_studio` — 4 rows, PK `studio_id`. `dim_player` — 44,990 rows, PK `player_id`, **no relationship to `dim_date`** (its `signup_date` starts 2024-06-03, four months before the date table begins, and no scorecard question needs a signup-date model role — adding one would just create an unused blank-row risk). `dim_platform` — 5 rows, PK `platform_code`.

### `bridge_title_studio` — grain: one row per title–studio credit
7 rows: 5 titles, 2 of them (`T-02`, `T-05`) credited to two studios each (`Lead` + `Co-development`).
`credit_role` is exposed but not used by any measure — kept for a future "co-dev only" slice if asked.

## Relationships

| From | To | Cardinality | Cross-filter | Apply security filter both directions | Active |
|---|---|---|---|---|---|
| `dim_date[date]` | `fact_order[order_date]` | 1 : * | Single | — | **Yes** |
| `dim_date[date]` | `fact_order[settlement_date]` | 1 : * | Single | — | No |
| `dim_date[date]` | `fact_refund[order_date]` | 1 : * | Single | — | **Yes** |
| `dim_date[date]` | `fact_refund[refund_date]` | 1 : * | Single | — | No |
| `dim_title[title_id]` | `fact_order[title_id]` | 1 : * | Single | — | Yes |
| `dim_title[title_id]` | `fact_refund[title_id]` | 1 : * | Single | — | Yes |
| `dim_player[player_id]` | `fact_order[player_id]` | 1 : * | Single | — | Yes |
| `dim_player[player_id]` | `fact_refund[player_id]` | 1 : * | Single | — | Yes |
| `dim_platform[platform_code]` | `fact_order[platform_code]` | 1 : * | Single | — | Yes |
| `dim_platform[platform_code]` | `fact_refund[platform_code]` | 1 : * | Single | — | Yes |
| `dim_studio[studio_id]` | `bridge_title_studio[studio_id]` | 1 : * | Single | — | Yes |
| `dim_title[title_id]` | `bridge_title_studio[title_id]` | 1 : * | **Both** | **Enabled** | Yes |

`sec_user_studio` (`user_principal_name`, `studio_id`) is **disconnected** — it has no relationships at
all. It is read directly by the Studio Lead role's filter expression and by `Company Net Revenue
(Page-Safe)`. See `DASHBOARD.md` for both.

**"Apply security filter in both directions" on `dim_title ↔ bridge_title_studio` is load-bearing, not
optional.** Cross-filter direction governs ordinary query filtering; row-level security propagation
across a relationship is a *separate* setting, and a bidirectional cross-filter does **not** carry an
RLS restriction by itself. With the flag off, a studio lead's role would restrict `dim_studio` while
`dim_title` stayed unfiltered — every title's revenue would remain visible to every lead, silently, with
no error. This is the single most safety-critical setting in the model, which is why it lives in this
table rather than in deployment notes.

Two inactive relationships exist on purpose (`settlement_date`, `refund_date`) and are invoked with
`USERELATIONSHIP` only inside the two measures that need them (`Cash Settled`, `Refunds (Treasury)`).
Leaving the order-date relationships active by default means the ordinary `Net Revenue` measure — the
one used in 5 of the 7 questions — needs no relationship gymnastics at all; the two Treasury/cash
exceptions carry the complexity, not the common case.

### The bridge direction decision

`dim_title ↔ bridge_title_studio` is **bidirectional**. The alternative — single-direction plus
`CROSSFILTER(bridge_title_studio, dim_title, BOTH)` inside every studio-facing measure — was
considered and rejected: it makes the studio scoping opt-in per measure, so a visual using a measure
that forgot the `CROSSFILTER` would silently show a studio lead the *company* total instead of their
own studio's — exactly the RLS failure this dashboard exists to prevent. A bidirectional relationship
on a 7-row bridge against a 5-row dimension carries no realistic ambiguity risk (no fan-out: each
title's credits are few and known), so the blast radius of getting it wrong the other way is far
larger than the cost of making it structural.

## Data types (declared at import, not inferred)

Every source column is `TEXT` in the warehouse — this is a SQLite artifact of an untyped CSV load,
not a business rule. Types are cast explicitly on import:

| Source pattern | Model type | Notes |
|---|---|---|
| `*_date`, `date`, `signup_date`, `launch_date` | **Date** | never Text |
| `*_usd`, `base_price_usd` | **Fixed Decimal Number (4 dp)** | matches the data's native precision (up to 4 dp observed) exactly |
| `*_id`, `*_code`, `title_name`, `studio_name`, `region`, `genre`, `country_code`, `currency_code`, `acquisition_channel`, `credit_role`, `refund_reason`, `platform_name` | Text | |
| `calendar_year`, `calendar_month`, `calendar_quarter`, `fiscal_quarter_no`, `fiscal_month_no`, `founded_year`, `settlement_lag_days` | **Whole Number** | cast from text |
| `is_weekend` | Boolean | cast from `"0"`/`"1"` |

**Ratio measures return ratios, not percentages.** `% of Studio Net Revenue`, `Net Revenue YoY %`,
`Net Revenue YoY % (Like-for-like)` and `Net Revenue YoY % (New Titles)` all use `DIVIDE` and therefore
return a decimal (`1.2055`, `0.7421`). Each carries a **Percentage format string (`"0.00%"`)** in the
model, which is what renders them as the `120.55` / `74.21%` figures printed in `SCORECARD.md`; the SQL
proofs in `verification/checks.json` multiply by 100 to match that rendered form. Nothing multiplies by
100 inside the DAX.

**Rounding happens only at display** (visual/format-string level, or once when transcribing into
`SCORECARD.md`). **No measure rounds a value it returns** — doing so inside a base measure would
corrupt any ratio or YoY % built on top of it (a rounded numerator over a rounded denominator drifts
from the true ratio). The only `ROUND` anywhere in `MEASURES.dax` is a boolean guard inside `Paying
Players` (`ROUND([Net Revenue], 4) > 0`), which protects the comparison against floating-point
representation noise and does not change any returned value. `Fixed Decimal Number` already matches the
source precision, so no intermediate truncation happens on import either.

## Non-obvious modeling decisions

1. **Never filter on `order_status`.** Every `refunded` order has a `fact_refund` row for exactly
   100% of its `net_usd` — but 4,800 further `completed` orders carry a *partial* refund. The refund
   is always expressed in `fact_refund`, never by zeroing out `fact_order`. Filtering to
   `order_status = "completed"` before subtracting refunds double-counts the deduction on those 4,800
   rows. `Net Revenue` always sums the full `fact_order[net_usd]`, unfiltered by status, and always
   subtracts `fact_refund[net_refund_usd]` in the same date-role context.
2. **Studio totals exceed the company total by design.** `SUMX` over `dim_studio` re-evaluates `Net
   Revenue` once per studio row; `T-02` and `T-05` each get counted twice (once per credited studio).
   `Company Net Revenue` strips the studio/bridge/title filters with `ALL()` so it always returns the
   5-title, no-double-count figure regardless of which visual it sits next to.
3. **`% of studio` uses a many-to-many-safe parent total.** `Studio Total Net Revenue` clears the
   title and bridge filters, then re-applies the currently selected studio with
   `VALUES(dim_studio[studio_id])`. Stating the studio scope explicitly this way means the denominator
   never depends on filter-propagation details across the bridge — it is pinned to the current
   studio's own titles by construction, while the numerator iterates them.
4. **Paying Players counts people, not orders.** It iterates `dim_player` and keeps a player only if
   their `Net Revenue` in the filtered period is strictly positive — so a player whose orders were
   entirely refunded (309 of the 12,807 who transacted in FY2026 Q2) is **not** paying. This is the
   more defensible reading of "paying" for a revenue-per-player ratio, but it is one of the two
   decisions I am least sure about: it makes the transacted count (12,807) and the paying count
   (12,498) genuinely different numbers that will both appear in conversation, and someone has to
   remember which one the ratio's denominator uses.
5. **Year-over-year uses `DATEADD(-1, YEAR)`, not a custom fiscal-quarter index.** This works cleanly
   here specifically because this fiscal calendar's quarters are calendar-month ranges relabeled by a
   shifted year (Q2 is always Jan–Mar, whichever fiscal year), so shifting every boundary date back by
   exactly one calendar year always lands on the equivalent fiscal quarter of the prior fiscal year —
   verified: calendar year 2025 is fully present in `dim_date` (365/365 days), so the FY2026 Q2 →
   FY2025 Q2 shift has no missing dates to fall back on. A fiscal-index approach would only be needed
   if multiple non-contiguous quarters could be selected at once and still need a defined comparison
   period; the scorecard and dashboard never do that, so it was not built.
6. **`dim_player` has no relationship to `dim_date`.** `signup_date` predates the date table by four
   months (2024-06-03 vs. 2024-10-01) and no question in the brief needs a cohort-by-signup-date view.
   Adding the relationship now would just be an unused edge with a guaranteed blank-row case.

---

## Performance at ~50× volume

Today: 106,293 order rows, 7,722 refund rows, 44,990 players. At 50×: ~5.3M orders, ~386K refunds,
plausibly ~2M+ players (acquisition doesn't scale 1:1 with orders, but grows). `dim_title`/`dim_studio`
stay small regardless of order volume (they grow with the catalog, not with transaction count) —
`dim_date` never grows meaningfully either. The pain in this model is entirely on the fact side, on two
specific measures, and on the fact that the source is untyped text. Concretely, in *this* model:

1. **The bidirectional `dim_title ↔ bridge_title_studio` relationship, now also carrying RLS.** Today
   this relationship is free — 5 titles, 7 bridge rows, no fan-out. But this is also the exact path
   the Studio Lead RLS role depends on (`DASHBOARD.md`): every query a studio lead's session issues now
   evaluates a security filter across a bidirectional many-to-many path, on *every single visual on the
   page*, not just the ones that look studio-scoped. At 50× order volume the bridge itself likely
   doesn't grow much (still driven by catalog size, not transactions) — but if the catalog grows into
   dozens of co-developed titles across more studios, a bidirectional relationship carrying RLS is
   exactly where Power BI's ambiguous-filter-path and query-plan-complexity costs concentrate first,
   because RLS forces the engine to evaluate that path on queries that wouldn't otherwise touch it.
   Action: watch bridge row count, not order volume, as the trigger for revisiting this — if it grows
   past roughly a hundred credits, re-benchmark the Studio Lead role specifically (not the Head/CFO
   role, which never touches RLS at all) before assuming it still scales.
2. **`Paying Players`.** `COUNTROWS(FILTER(dim_player, ROUND([Net Revenue], 4) > 0))` row-context-
   iterates every player and re-evaluates a `CALCULATE`-wrapped measure per row against a fact table
   that will hold ~5.3M order rows. At 44,990 players today this is instant; at ~2M+ players, iterating
   the full player table once per visual refresh (and Power BI re-evaluates it per row of any matrix
   it's sliced by) against a 50×-larger fact is the single most expensive measure in this workbook —
   the cost is a product of two dimensions growing at once, not one. Action: pre-aggregate a hidden
   `player-period net revenue` table at refresh time (player_id × fiscal_year × fiscal_quarter, one row
   per player-quarter with net revenue already summed from the full-grain facts), and redefine `Paying
   Players` as a `COUNTROWS(FILTER(...))` over *that* narrow table instead of the raw
   44,990/2M-row-by-5.3M-order-row join. This turns an O(players × orders) evaluation into an
   O(players × quarters) one.
3. **The inactive-relationship measures (`Cash Settled`, `Refunds (Treasury)`).** These are the only
   two measures that never use the default `order_date` relationship — they force `USERELATIONSHIP`
   onto `settlement_date`/`refund_date` instead. If a 50×-scale refresh policy partitions `fact_order`/
   `fact_refund` by `order_date` (see #5), these two measures are the ones that get the least benefit
   from that partitioning: a settlement-date or refund-date filter doesn't line up with partition
   boundaries drawn on order-date, so the engine can't prune partitions for them the way it can for
   every other measure in this workbook. They stay correct, just structurally the most expensive
   queries on the page precisely because they're the exception path — which is an acceptable trade
   given they only back Q2 and Q3, not the 5 questions the ordinary `Net Revenue` measure answers.
   Action: no change to the measures themselves; if either becomes a live bottleneck, they are the
   first candidates for their own dedicated aggregation table (#6), independent of the order-date one.
4. **TEXT source columns and type conversion at refresh.** Every column in the source is `TEXT` (a
   SQLite/CSV-load artifact, not a business rule — see `AI_WORKFLOW_LOG.md`), so every refresh casts
   dates to Date, amounts to Fixed Decimal, and calendar/fiscal numbers to Whole Number on ingest. At
   106K rows this is invisible; at 5.3M+ rows, re-running that cast over the *entire* history on every
   refresh is real, avoidable CPU cost. This is precisely why #5 (incremental refresh) matters here
   specifically, not just for refresh duration in the abstract: incremental refresh only reprocesses —
   and therefore only re-casts — the rows inside the changed partitions, so the type-conversion cost
   stays bounded to the incremental window regardless of how large the frozen history gets.
5. **Incremental refresh window sized from the measured maximum lag, not from the platform table.**
   At 5.3M rows a full reload on every refresh stops being viable. Partition `fact_order` and
   `fact_refund` by `order_date` month, keep historical partitions frozen, and refresh a rolling
   trailing window. The window has to be sized from what the data actually does, so both lags were
   queried directly:

   | Lag | Measured maximum |
   |---|---|
   | `order_date` → `settlement_date` | **60 days** (matches `dim_platform`'s longest declared lag, Nintendo eShop) |
   | `order_date` → `refund_date` | **71 days** |

   The binding constraint is the **refund** lag at 71 days, not the settlement lag — a refund can be
   processed against an order up to 71 days old, so a row in an already-frozen `order_date` partition
   can still change. Sizing the window off `dim_platform`'s 60-day settlement figure alone would leave
   an 11-day hole through which late refunds would be silently missed. A **rolling 4-month window**
   (current month plus three prior) covers 71 days in the worst case — an order placed on the 1st of
   month M with a refund 71 days later lands in month M+2, and a 3-month window is only guaranteed to
   reach back that far for orders late in the month. Four months covers every case with margin.
   Re-measure both lags before narrowing the window; if the platform mix or the refund policy changes,
   this number changes with it.
6. **Aggregation tables.** Nothing in `SCORECARD.md` needs order-level grain — every measure resolves
   to title, studio, player-count, or a fiscal quarter/year, never a single order row. At 50× that gap
   between the fact table's grain (order) and the measures' actual grain (period × title/studio) is
   exactly what Power BI aggregation tables exist to close. Build one import-mode aggregation table at
   `title_id × calendar_year_month`, pre-summing `net_usd` and (separately, from `fact_refund`)
   `net_refund_usd`, and let Power BI's aggregation-awareness auto-redirect any query at that grain or
   coarser — which is nearly every query this dashboard issues — away from the 5.3M-row detail table
   entirely. `Paying Players` (#2) and the two inactive-relationship measures (#3) don't benefit from
   this particular aggregation (different grain, different date role) and would need their own if they
   ever need the same treatment.
