Tables

### dim_date
Columns:
date	
calendar_year	
calendar_month	
month_short	calendar_quarter	
fiscal_year	
fiscal_quarter	
fiscal_quarter_no	
fiscal_month_no	
year_month	
is_weekend

## bridge_title_studio
Columns:
title_id
studio_id	
credit_role

## dim_platform
Colums
platform_code	
platform_name	
settlement_lag_days

## dim_studio
Columns
studio_id	
studio_name	
region	
founded_year

## dim_title
Columns
title_id	
title_name	
genre	
launch_date	
lead_studio_id	
base_price_usd

## dim_player
Columns
player_id	
country_code	
currency_code	
signup_date	
acquisition_channel

## fact_order
columns
order_id	
order_date	
settlement_date	
player_id	
title_id	
platform_code	
order_status	
gross_usd	
platform_fee_usd	
net_usd

## fact_refund
Columns
refund_id	
order_id	
refund_date	
order_date	
title_id	
platform_code	
player_id	
refund_reason	
refund_usd	
platform_fee_credit_usd	net_refund_usd

## Relationships
bridge_title_studio(studio_id) -> dim_studio(studio_id), *:1, single
bridge_title_studio(title_id) -> dim_title(title_id), *:1, single
fact_order(platform_code) -> dim_platform(platform_code), *:1, single
fact_order(player_id) -> dim_player(player_id), *:1, single
fact_order(title_id) -> dim_title(title_id), *:1, single
fact_order(order_date) -> dim_date(date), *:1, single, ACTIVE
fact_order(settlement_date) -> dim_date(date), *:1, single, INACTIVE
fact_refund(order_id) -> fact_order(order_id), 1:1, single, INACTIVE (auto-detected, unused)
fact_refund(platform_code) -> dim_platform(platform_code), *:1, single
fact_refund(player_id) -> dim_player(player_id), *:1, single
fact_refund(title_id) -> dim_title(title_id), *:1, single
fact_refund(order_date) -> dim_date(date), *:1, single, INACTIVE
fact_refund(refund_date) -> dim_date(date), *:1, single, ACTIVE

## Date table
dim_date is the designated date table conceptually (all date relationships
point to it). Could not confirm the "Mark as date table" UI toggle in this
Power BI Desktop build within the time available — relationships and grain
are correct regardless; this setting mainly affects built-in time-intelligence
functions, which this model does not rely on (measures use USERELATIONSHIP
and explicit date filters instead).

## Non-obvious decision: role-playing date
fact_order and fact_refund each carry two date columns pointing at dim_date,
but only one relationship per table can stay active. The inactive ones are
switched on inside specific measures using USERELATIONSHIP, so each question
uses the date the brief requires (order date for revenue recognition,
settlement date for cash landing, refund date for Treasury's refund count).

## Columns exposed vs hidden

Hidden (technical keys, not useful in visuals):
- All *_id / *_code columns used only for relationships: title_id,
  studio_id, player_id, platform_code, order_id, refund_id
- fact_order[order_status] — hidden if not used in any measure/filter
  in the final dashboard

Exposed (used directly in visuals or filters):
- title_name, studio_name, platform_name, region, genre
- All dim_date columns (date, calendar_year, calendar_month,
  fiscal_year, fiscal_quarter, etc.)
- net_usd, net_refund_usd, gross_usd (kept visible for ad-hoc
  analysis even though the dashboard itself uses the measures, not
  the raw columns)

## Performance considerations 

1. Net Revenue by Studio (CROSSFILTER over bridge_title_studio <->
   dim_title) is the most expensive measure in this model. Bidirectional
   filtering forces re-evaluation across the many-to-many path on every
   call. At 50x fact_order volume, any visual slicing this measure by
   several dimensions at once (studio x month, for example) would be
   the first to slow down. I would pre-aggregate studio-level revenue
   into a summary table refreshed on a schedule, rather than computing
   it live with CROSSFILTER on every interaction.

2. Settled Revenue and Refunds Treasury both use USERELATIONSHIP, which
   costs more than querying the active relationship. At 50x scale I
   would evaluate whether these are queried often enough on the
   dashboard to justify materializing them as a settlement-date-based
   summary table at load time, instead of recomputing the relationship
   swap on every filter change.

3. The automatic Total row on any visual using Net Revenue by Studio is
   not reliable — Power BI recalculates it in its own filter context
   rather than summing the visible rows (confirmed directly: the
   table's Total silently matched the company-wide Net Revenue instead
   of the true studio sum). At 50x scale, with more studios and more
   co-development combinations, this becomes a bigger trap for anyone
   building on this model later. Sum of Studio Totals is the only
   supported way to total that column, and this is documented here for
   that reason.

4. fact_refund's unused auto-detected relationship to fact_order
   (order_id, 1:1, inactive) adds a relationship Power BI must account
   for in the model graph without any measure using it. I would remove
   it — it only exists because Power BI auto-detected it on load.



