# Semantic model — Twin Hearth Studios

Built in Power BI Desktop (`TwinHearth.pbix`), Import mode, from the eight CSVs in `data/`.
Star schema: two fact tables sharing conformed dimensions, plus a title–studio bridge for co-development.
Measures live in a display table `Measures_table` (see `MEASURES.dax`).

Load settings: locale for import = English (United States) (the CSVs use `.` as decimal separator),
Auto date/time = off, autodetect relationships = off.

## Tables and grain

| Table | Rows | Role | Grain (one row = …) |
|---|---|---|---|
| `fact_order` | 106,293 | Fact | one order |
| `fact_refund` | 7,722 | Fact | one refund (at most one per order) |
| `dim_date` | 822 | Dimension, **marked as date table** | one calendar day, 2024-10-01 → 2026-12-31 |
| `dim_title` | 5 | Dimension | one title |
| `dim_studio` | 4 | Dimension | one studio |
| `dim_platform` | 5 | Dimension | one storefront |
| `dim_player` | 44,990 | Dimension | one player |
| `bridge_title_studio` | 7 | Bridge | one studio credit on one title |
| `Measures_table` | — | Display table | holds the 13 measures only |

## Exposed and hidden columns

| Table | Visible | Hidden |
|---|---|---|
| `fact_order` | — (whole table hidden) | all columns |
| `fact_refund` | — (whole table hidden) | all columns |
| `dim_date` | all columns | — |
| `dim_title` | `title_name`, `genre`, `launch_date`, `base_price_usd` | `title_id`, `lead_studio_id` |
| `dim_studio` | `studio_name`, `region`, `founded_year` | `studio_id` |
| `dim_platform` | `platform_name`, `settlement_lag_days` | `platform_code` |
| `dim_player` | `country_code`, `currency_code`, `signup_date`, `acquisition_channel` | `player_id` |
| `bridge_title_studio` | `credit_role` | `title_id`, `studio_id` |
| `Measures_table` | the 13 measures | `Column1` |

Why: the only path to a business number should be a measure that already applies the rules. Hiding
the fact tables stops anyone summing `net_usd` without refunds or filtering `order_status`; hiding
`lead_studio_id` stops anyone attributing titles to a single studio.

## Relationships

All are one-to-many, from the dimension (1) to the fact or bridge (*).

| # | From (1) | To (*) | Filter direction | Active |
|---|---|---|---|---|
| 1 | `dim_date[date]` | `fact_order[order_date]` | Single | Yes |
| 2 | `dim_date[date]` | `fact_order[settlement_date]` | Single | **No** |
| 3 | `dim_date[date]` | `fact_refund[order_date]` | Single | Yes |
| 4 | `dim_date[date]` | `fact_refund[refund_date]` | Single | **No** |
| 5 | `dim_title[title_id]` | `fact_order[title_id]` | Single | Yes |
| 6 | `dim_title[title_id]` | `fact_refund[title_id]` | Single | Yes |
| 7 | `dim_platform[platform_code]` | `fact_order[platform_code]` | Single | Yes |
| 8 | `dim_platform[platform_code]` | `fact_refund[platform_code]` | Single | Yes |
| 9 | `dim_player[player_id]` | `fact_order[player_id]` | Single | Yes |
| 10 | `dim_player[player_id]` | `fact_refund[player_id]` | Single | Yes |
| 11 | `dim_studio[studio_id]` | `bridge_title_studio[studio_id]` | Single | Yes |
| 12 | `dim_title[title_id]` | `bridge_title_studio[title_id]` | **Both** | Yes |

There is deliberately no relationship between `fact_order` and `fact_refund`.

## Date table

`dim_date` is marked as the date table on `dim_date[date]`. It is contiguous and covers every order,
refund and settlement date (the latest settlement is 2026-11-29). Fiscal attributes (`fiscal_year`,
`fiscal_quarter`, `fiscal_quarter_no`, `fiscal_month_no`) come from the warehouse, so FY starts on
1 October without any DAX. `year_month` is imported as a date (first day of the month).

## Where the model does something non-obvious

- **Q2, cash vs revenue:** revenue is dated by order, cash by settlement → `settlement_date` is an inactive relationship, switched on only inside `[Cash Settled]` with `USERELATIONSHIP`.
- **Q3, Finance vs Treasury refunds:** Finance dates refunds by the original order, Treasury by the refund → `fact_refund[order_date]` is active, `refund_date` is inactive and used only in `[Refunds (Treasury)]`.
- **Refunds, not order status:** `order_status` misses partial refunds → net revenue always subtracts `fact_refund[net_refund_usd]`; `order_status` is hidden and used nowhere.
- **Q4 and Q7, co-development:** a title can belong to two studios and is credited in full to each → many-to-many via `bridge_title_studio`, with the bridge→`dim_title` relationship set to Both so a studio filter reaches the facts; it is the only bidirectional relationship.
- **Q4, studios vs company:** the studio sum double-counts shared titles → `[Company Net Revenue]` removes the studio filter, `[Studio Credited Net Revenue]` sums studios explicitly, and `[Co-Development Overlap]` shows the gap. The same model answers Q1 (no studio filter, titles counted once) and Q4.
- **Q5, paying players:** a player filter must reach both facts → `[Paying Players]` iterates `dim_player`, not `fact_order[player_id]` (a fact column does not filter the other fact).
- **Q6, fiscal growth:** `SAMEPERIODLASTYEAR` on the marked date table shifts FY2026 Q2 (Jan–Mar 2026) to FY2025 Q2 (Jan–Mar 2025); a 12-month shift lands on the same fiscal quarter.

## Performance — what would hurt first at 50x

1. **`[Paying Players]` is the slowest measure.** It goes player by player (45K today) and calculates net revenue for each one. More orders means more players, so this gets slow first.
   *What I'd change:* each order has at most one refund, so the warehouse could add the refund amount to each order row. Then net revenue lives in one table and counting paying players is a simple group-by instead of a per-player loop.

2. **Columns I load but never use.** `order_id`, `gross_usd`, `platform_fee_usd` and `order_status` are in the model but no measure uses them, and `order_id` is unique on every row, so it takes the most memory.
   *What I'd change:* stop importing those columns and round amounts to 2 decimals.

3. **Full refresh.** Every refresh reloads all orders since 2024.
   *What I'd change:* incremental refresh by order date, keeping a few months open for refunds because a late refund changes an old month.

The bidirectional bridge and the studio measures are not a problem at this size: they work on 4 studios and 5 titles, not on orders.
