# AI Workflow Log

Running log of how this analytics layer was built with AI assistance. Raw material for `AI_WORKFLOW.md`.

**Tool:** Claude Code in VS Code, driving a local SQLite copy of the warehouse
via `bin/query.py` and ad-hoc Python profiling scripts written to a scratchpad (never into the repo).

---

## Session 1 — Discovery (read-only)

**Date:** 2026-09-15
**Goal:** Understand the warehouse before writing a single measure. No deliverables produced.

### Prompt given

> Context: this repo is a 3-hour Analytics Developer (AI) technical test. We must build the analytics
> layer on a clean warehouse: MODEL.md (semantic model + performance at 50x volume), MEASURES.dax
> (layered, one-line comment per measure), SCORECARD.md (every cell, 2 decimals), DASHBOARD.md (one
> page, studio leads see only their studio) and AI_WORKFLOW.md. Everything in English.
>
> Fixed business rules (from docs/METRIC_BRIEF.md):
> - Fiscal year starts 1 Oct (FY2026 = 2025-10-01 to 2026-09-30; Q2 = Jan–Mar).
> - Net revenue = net_usd (fact_order) minus net_refund_usd (fact_refund); store cut already applied.
> - Revenue on order date; cash on settlement date. Refunds: Finance uses original order date,
>   Treasury uses refund date.
> - Co-developed titles are credited in full to every studio, so studio totals exceed company revenue
>   by design.
>
> Hard rules: numbers must come from DAX measures, proven by SQL that mirrors each measure's filter
> context (DAX first, never SQL first). One model must answer all 7 questions. Do not modify data/,
> docs/ or bin/.
>
> Your task now (read-only, no deliverables yet):
> 1. Read the README, docs/METRIC_BRIEF.md and SCORECARD.md. Explore the data with
>    `python3 bin/query.py --tables` and sample rows. If .claude/skills/bi-semantic-model-builder
>    exists, use its profile_warehouse.py and pitfalls.md.
> 2. Confirm with queries: grain and keys of every table, orphans, what the bridge links and which
>    titles are co-credited, whether fact_refund has a title_key, the sign of refunds, min/max of
>    every date column, whether Jan–Mar 2025 has data, and all titles credited to Twin Hearth Studios.
> 3. Give me a short summary: A. Tables (role, grain, keys, rows) B. For each of the 7 questions
>    (fact, date role, dimension path, main trap) C. Proposed relationships (cardinality, direction,
>    active) and the bridge direction decision D. Anything in the data that contradicts the rules
>    above E. Ambiguous scorecard cells and the default you'd use F. Plan for the remaining time
> 4. Create AI_WORKFLOW_LOG.md with this prompt and what you found.
>
> Stop after the summary and wait for my go-ahead.

### What was done

- Read `README.md`, `docs/METRIC_BRIEF.md`, `SCORECARD.md`, `bin/query.py`.
- Checked for `.claude/skills/bi-semantic-model-builder` — **it does not exist** in this repo or in
  the user profile. Profiling was written from scratch instead (two Python scripts in the scratchpad,
  ~40 queries total).
- Deliberately did **not** compute any scorecard figure, to honour the "DAX first, never SQL first"
  rule. SQL in this session was structural only (grain, keys, orphans, ranges, counts).

### Findings

**Grain and keys — all verified unique, zero nulls across every column of every table**

| Table | Rows | Key | Unique |
|---|---|---|---|
| `fact_order` | 106,293 | `order_id` | yes |
| `fact_refund` | 7,722 | `refund_id` | yes |
| `dim_player` | 44,990 | `player_id` | yes |
| `dim_date` | 822 | `date` | yes |
| `dim_title` | 5 | `title_id` | yes |
| `dim_platform` | 5 | `platform_code` | yes |
| `dim_studio` | 4 | `studio_id` | yes |
| `bridge_title_studio` | 7 | `title_id` + `studio_id` | yes |

**Referential integrity — zero orphans on all 13 FK paths tested.** Every fact key resolves; every
`order_date`, `settlement_date` and `refund_date` lands inside `dim_date`; every title and studio
appears in the bridge.

**The bridge.** 7 rows, `credit_role` ∈ {Lead, Co-development}. Two titles are co-credited:
`T-02 Hollow Crown: Ashen Tide` (STU-01 Lead + STU-02 Co-dev) and `T-05 Emberwatch Tactics`
(STU-02 Lead + STU-04 Co-dev). `dim_title.lead_studio_id` agrees with the bridge's Lead row for all
5 titles — it is a redundant denormalisation and a trap: joining on it gives 5 credits instead of 7
and silently makes studio totals reconcile to company total, which the brief says must *not* happen.

**Twin Hearth Studios (STU-01) is credited with exactly two titles: T-01 and T-02.** This matches
the two rows pre-printed in scorecard §7 — no hidden third row.

**`fact_refund` carries its own `title_id`, `player_id`, `platform_code` and `order_date`** — and all
four agree with the parent order on all 7,722 rows (0 mismatches). So refunds can hang directly off
the dimensions; no fact-to-fact relationship is needed.

**Refund sign is positive.** `net_refund_usd` ranges 0.7736 → 99.4129, all 7,722 rows > 0. Net
revenue must therefore *subtract*. `net_refund_usd = refund_usd − platform_fee_credit_usd` on every
row (0 mismatches), mirroring `net_usd = gross_usd − platform_fee_usd`.

**Date ranges**

| Column | Min | Max |
|---|---|---|
| `dim_date.date` | 2024-10-01 | 2026-12-31 (822 days, contiguous, 0 gaps) |
| `fact_order.order_date` | 2024-10-02 | 2026-09-30 |
| `fact_order.settlement_date` | 2024-11-01 | 2026-11-29 |
| `fact_refund.refund_date` | 2024-10-05 | 2026-09-30 |
| `fact_refund.order_date` | 2024-10-02 | 2026-09-27 |
| `dim_player.signup_date` | 2024-06-03 | 2026-09-25 |
| `dim_title.launch_date` | 2024-10-02 | 2026-02-12 |

`dim_date` deliberately runs three months past the last order date to absorb settlement lag; 8,815
orders settle in FY2027 Q1. `signup_date` starts 4 months *before* `dim_date` (6,545 players) — it
cannot be given a relationship to the date table without a blank-row bucket.

**Jan–Mar 2025 (FY2025 Q2) has data:** 6,858 orders. Question 6 is computable. But only three titles
existed then (T-01, T-03, T-04); T-02 launched 2025-09-30 and T-05 on 2026-02-12, so FY2026 Q2 has
five. The growth number is real but is partly new-title launch, not like-for-like growth.

**`order_status`** is `completed` (103,371) or `refunded` (2,922). Verified: every one of the 2,922
`refunded` orders has a matching `fact_refund` row for exactly 100% of its `net_usd`, and a further
4,800 `completed` orders carry *partial* refunds (~36% of order value on average). So the refund is
always expressed in `fact_refund` — filtering `fact_order` to `completed` *and* subtracting refunds
would double-count the deduction. **Do not filter on `order_status`.**

**Fiscal calendar is pre-built and correct.** `dim_date` already carries `fiscal_year`,
`fiscal_quarter` ("FY2026 Q2"), `fiscal_quarter_no`, `fiscal_month_no`. FY2026 Q2 = 2026-01-01 →
2026-03-31, 90 days. No custom fiscal logic needs to be invented — only a sort-order column and a
contiguous quarter index for the year-over-year shift.

### The one thing that looked like a data defect and was not

A query comparing `net_refund_usd` to the parent order's `net_usd` reported **1,883 over-refunds** —
refunds larger than the order they refund, which would contradict the brief. An earlier query that
summed per order had reported zero.

Cause: **every column in `warehouse.db` is declared and stored as `TEXT`** (the CSVs were loaded
without typing). The first query wrapped the columns in `SUM()`, which coerces to numeric; the second
compared them directly, so SQLite compared them as *strings* — `"9.99" > "10.00"` lexically. Re-run
with explicit `CAST(... AS REAL)`, the count is **0**. The data is clean; the query was wrong.

Consequence for every SQL proof from here on: **cast before comparing or aggregating.** This is
exactly the class of error the brief warns about — a plausible number that is not the right number.

### Precision

Amounts carry up to 4 decimal places (95,474 of 106,293 order rows have 4). Rounding must happen at
presentation only; SQL proofs must aggregate at full precision and round once at the end, or the
scorecard will disagree with the measures in the cents column.

---

## Open questions carried into Session 2

1. Scorecard §2 "Net revenue settled in Dec 2025" — inflow only, or inflow net of Dec refund outflow?
2. Scorecard §5 — do players whose FY2026 Q2 orders were entirely refunded (309 of 12,807) count as
   paying players?
3. Whether the bridge gets a bidirectional relationship globally, or `CROSSFILTER` inside the studio
   measures only.

Session paused here for direction before any deliverable was written.

---

## Session 2 — MODEL.md, MEASURES.dax, checks.json, SCORECARD.md

**Date:** 2026-09-15

### Direction given

> Good summary. Go ahead with these adjustments:
> 1. Add a measure for "Sum of the four rows" (e.g. Studio Credit Total = SUMX over dim_studio of
>    [Net Revenue]). Every scorecard cell must come from a named measure.
> 2. Hide order_status and every non-key fact column. In MODEL.md, state the rule: only shared
>    dimensions may filter both facts.
> 3. Paying players = players with Net Revenue > 0 in the period (iterate dim_player[player_id], not
>    fact_order[player_id], so refunds are included in the test). Report the 12,807 "transacted"
>    count in the note under §5. Flag this as one of the two least-sure decisions.
> 4. For Q6, use DATEADD(-1, YEAR) unless you find a concrete reason it fails here; if you keep a
>    fiscal quarter index, define the behaviour when several quarters are selected.
> 5. Confirm whether dim_date has fiscal columns and that they start in October. Confirm the full list
>    of titles credited to Twin Hearth Studios; add rows to §7 if needed.
> 6. In MODEL.md, declare data types: dates as Date, amounts as Fixed Decimal (4 dp), round only at
>    display.
> 7. All SQL proofs CAST text columns. Put them in checks.json and run the skill's
>    verify_scorecard.py; fill SCORECARD.md only from a PASS run.
>
> Order of work: MODEL.md, then MEASURES.dax, then checks.json and SCORECARD.md. Stop after
> SCORECARD.md and show me the verification output before starting DASHBOARD.md.

### What was done

- Re-confirmed the three facts adjustment #5 asked to check, before writing anything: `dim_date`
  carries `fiscal_year`/`fiscal_quarter`/`fiscal_quarter_no`/`fiscal_month_no`, and every fiscal Q1
  starts 1 Oct across all three fiscal years present (FY2025, FY2026, FY2027). Twin Hearth Studios is
  credited with exactly `T-01` and `T-02` via the bridge — no third row exists, so §7 needed no
  addition.
- Verified DATEADD safety concretely rather than assuming it: calendar year 2025 is 100% present in
  `dim_date` (365/365 days), so shifting FY2026 Q2 back one calendar year to FY2025 Q2 has no missing
  target dates. Used `DATEADD(-1, YEAR)`, not a fiscal-quarter index — documented in `MODEL.md` why it
  works for this specific fiscal calendar (fixed calendar-month quarters, relabeled by year).
- Verified the redefined `Paying Players`: iterating `dim_player` and requiring `Net Revenue > 0`
  gives **12,498** for FY2026 Q2, versus **12,807** transacted (`DISTINCTCOUNT(fact_order[player_id])`)
  — a 309-player gap, exactly the players whose entire quarter was refunded.
- **No `.claude/skills/bi-semantic-model-builder` exists** in this repo or the user profile (checked
  again this session) — there is no pre-built `verify_scorecard.py` to run. Built an equivalent from
  scratch: `checks.json` (23 value checks, one per scorecard cell, each SQL query mirroring the exact
  filter context of the DAX measure it proves — same fact, same date-role column, explicit
  `CAST(... AS REAL)` on every amount column per the Session-1 lesson) plus 7 assertion/regression
  checks (sum-to-company, sum-to-100%, paying ≤ transacted, and three regression tests including a
  repeat of the Session-1 string-comparison bug so it can never silently return).
- Wrote `MODEL.md`, `MEASURES.dax`, `checks.json`, `verify_scorecard.py`, then ran the script and fixed
  what it caught before filling `SCORECARD.md` — see below.
- Filled `SCORECARD.md` only after `verify_scorecard.py` printed `RESULT: PASS` for all 23 value
  checks and 7 assertion checks.

### The moment the AI was confidently wrong (this session)

The first run of `verify_scorecard.py` reported one failure: `assert_q1_titles_sum_to_company` —
summing the five per-title Net Revenue rows gave **315,862.07**, while the company-total measure gave
**315,862.09**. A 2-cent gap, in a check specifically designed to catch exactly this class of
discrepancy — worth taking seriously, not waving away.

The assertion's SQL was the bug, not the data or the measures: I had written the "sum of five titles"
side of the check using the *rounded-to-2dp display values already sitting in `SCORECARD.md`*
(145,510.77 + 44,894.38 + 27,300.05 + 47,119.73 + 51,037.14), which is a plausible thing to write —
those are, after all, "the numbers" — but it directly violates the model's own rule that rounding
happens only at display. Recomputed both sides from source at full precision: the unrounded sum of the
five titles is 315,862.091, and the unrounded company total is also 315,862.091 — identical to nine
significant figures, both rounding to 315,862.09. The discrepancy existed only because I'd rounded
twice: once implicitly by using pre-rounded literals, and once explicitly in the assertion's `ROUND()`.
Fixed both `checks.json` assertions that had this pattern (`assert_q1_titles_sum_to_company` and
`assert_q4_double_count_equals_shared_titles`) to query live, unrounded values on both sides instead of
embedding rounded literals. Re-ran: full PASS.

The catch here is procedural, not just numerical: a verification script is not automatically correct
just because it produces a PASS/FAIL. This one was checked by re-deriving both sides independently
(a plain Python script computing full-precision sums, run separately from `checks.json`) before
trusting the "fixed" version's PASS result.

### Verification output (full PASS, 23 value checks + 7 assertion checks)

```
RESULT: PASS -- all 23 value checks and 7 assertion checks passed.
```

Full per-check output is reproducible by running `python verify_scorecard.py` from the repo root; not
duplicated here to keep this log readable — see the terminal transcript in this session for the
complete table.

### Carried forward

- §5 "paying players" definition remains one of the two decisions flagged as least-sure (per
  adjustment #3), now stated explicitly in `SCORECARD.md` with both numbers on record.
- Stopped after `SCORECARD.md` per instruction, pending go-ahead before `DASHBOARD.md`.

---

## Session 2 (continued) — corrections, verification/ move, independent-agent stress test

**Date:** 2026-09-16

### Direction given

Five follow-ups before `DASHBOARD.md`: (1) show the full `SCORECARD.md` and a captured verification
run, confirm the bridge credits for Twin Hearth and Emberwatch Interactive; (2) confirm Fixed Decimal
in `MODEL.md`, make `Paying Players` robust to floating-point residue and re-verify; (3) make the "two
thirds of Q6 growth is new titles" claim measure-backed or remove it; (4) move the verification
scripts into `verification/`; (5) spawn a fresh subagent with no access to `MODEL.md`/`MEASURES.dax`,
have it write its own measures for all 7 questions from the brief + blank scorecard + table schemas
alone, translate its DAX to mirrored SQL exactly as written, and log any plausible-but-wrong result
without changing our own measures unless it reveals a genuine error.

### What was done

- **Bridge re-confirmed:** Twin Hearth Studios (`STU-01`) = `T-01` (Lead) + `T-02` (Lead). Emberwatch
  Interactive (`STU-02`) = `T-02` (Co-development) + `T-05` (Lead). No change to §7.
- **`Paying Players` hardened:** `COUNTROWS(FILTER(dim_player, [Net Revenue] > 0))` became
  `COUNTROWS(FILTER(dim_player, ROUND([Net Revenue], 4) > 0))`. The `ROUND` guards the boolean test
  against floating-point representation noise; it is not a display rounding (the measure's returned
  value is unchanged) — documented as such in `MEASURES.dax` and `MODEL.md` so it doesn't read as a
  contradiction of the "round only at display" rule. Re-verified: still 12,498, unchanged.
- **Like-for-like YoY added:** `Titles Active Both Periods` (helper table measure, `INTERSECT` of
  titles with positive Net Revenue in the current period and the same period a year earlier via
  `DATEADD`), `Net Revenue (Like-for-like)`, `Net Revenue (Like-for-like) PY`, and `Net Revenue YoY %
  (Like-for-like)`. Three new checks added to `checks.json` (`q6_likeforlike_current`,
  `q6_likeforlike_py`, `q6_likeforlike_growth_pct`).
- **Caught my own imprecise claim while backing it with a measure.** The Session 1 summary had said
  "two-thirds of this growth is title-count growth" from memory, not from a calculation. The
  like-for-like measure returns **53.56%** for the three titles present in both quarters (`T-01`,
  `T-03`, `T-04`), against **120.55%** for the full portfolio — meaning the continuing titles grew a
  genuine 53.56% on their own, and new-title revenue is 30.37% of the FY2026 Q2 total (95,931.53 of
  315,862.09), not "two-thirds of the growth." The original claim was corrected in `SCORECARD.md`
  rather than quietly dropped, because the instruction was specifically to make it measure-backed or
  remove it — silently deleting an imprecise claim without saying it had been wrong would have hidden
  the mistake instead of correcting it.
- **Rounding-accumulation false alarm, round two.** Re-running `verify_scorecard.py` after these
  additions initially failed nothing new, but re-confirmed the fix from the prior run (both
  `assert_q1_*` and `assert_q4_*` assertions now compute both sides from source at full precision — see
  the prior entry in this log). Full run: **26 value checks + 7 assertion checks, all PASS.**
- **Moved `checks.json` and `verify_scorecard.py` into `verification/`**, fixed the script's path
  resolution (`DB` now resolves one directory above the script, `CHECKS` alongside it), re-ran from the
  new location to confirm nothing broke, and wrote `verification/VERIFICATION.md` as a durable, checked
  record of the PASS run (rather than only a terminal transcript that disappears at the end of the
  session). `SCORECARD.md`'s references to `checks.json`/`verify_scorecard.py` were updated to the new
  paths.

### Independent-agent stress test

A fresh `general-purpose` subagent was given, verbatim in its prompt, only: the full text of
`docs/METRIC_BRIEF.md`, the **original blank** `SCORECARD.md` template (not our filled version — giving
it our filled answers would have defeated the point), and the raw table/column list from `python
bin/query.py --tables` (no relationships, no row samples, no orphan/trap findings). It was told to
assume a standard star schema and write DAX for all 7 questions. It was explicitly instructed not to
read any file in the repository — there is no git worktree isolation available here (the outer
`RedValleyTest` folder is not a git repo, only this inner one is, and no sandboxing tool applies), so
this relies on instruction-following rather than filesystem isolation; the model was not given
Read/Glob/Grep access to project files it could have used to defeat that instruction, only asked not to
explore, since the harness's default subagent tool grant is broad.

Its measures were translated to SQL mirroring its logic exactly as written and run against the same
`checks.json` values already verified as correct. Full comparison:

| Question | Result | Verdict |
|---|---|---|
| Q1 (title + company) | Matches ours exactly on all 6 values | Correct |
| Q2 (cash settled Dec 2025) | Matches ours exactly | Correct |
| Q3 (refunds Treasury Dec 2025) | Matches ours exactly | Correct |
| Q4 (studios, company) | Matches ours exactly **if its `CROSSFILTER` syntax were fixed** (see below) | Bug, not a wrong number |
| Q5 (paying players, revenue/player) | **Wrong — see below** | Confirmed bug |
| Q6 (YoY growth) | Matches ours exactly | Correct |
| Q7 (% of studio) | Matches ours exactly, same caveat as Q4 | Bug, not a wrong number |

**Bug 1 — plausible but wrong number: `Paying Players`.**

```dax
Paying Players :=
CALCULATE (
    DISTINCTCOUNT ( fact_order[player_id] ),
    fact_order[net_usd] > 0
)
```

- **Its number:** 12,807 (for FY2026 Q2) → `Revenue per Paying Player` = 315,862.09 ÷ 12,807 =
  **24.66**.
- **Correct number:** 12,498 → 315,862.09 ÷ 12,498 = **25.27**.
- **Why it's wrong:** `fact_order[net_usd]` is a per-order value, always positive by construction (a
  purchase can't have a non-positive gross value) — verified: 0 of 106,293 orders have `net_usd <= 0`.
  So `fact_order[net_usd] > 0` filters out nothing, and the measure silently degrades to "everyone who
  placed an order," identical to the `Transacted` footnote figure. It never looks at `fact_refund` at
  all, so a player whose entire quarter was refunded still counts as "paying." The number it returns
  (24.66) is entirely plausible on its face — it's in the right range, it has the right shape — which
  is exactly the failure mode the brief warns about.
- **Which check caught it:** `q5_paying_players` (expected 12,498, this measure's mirrored SQL gives
  12,807) and `q5_revenue_per_player` (expected 25.27, gives 24.66) in `verification/checks.json`.
- **Why ours doesn't have this bug:** `Paying Players` iterates `dim_player` and tests
  `ROUND([Net Revenue], 4) > 0`, where `[Net Revenue]` already nets `fact_order` against
  `fact_refund` per player. This is precisely the distinction the user's earlier instruction drew
  ("iterate dim_player[player_id], not fact_order[player_id], so refunds are included in the test") —
  the independent agent, working from the brief alone with no steer on this point, took the more
  obvious-looking but incomplete approach, which is good evidence that instruction was worth giving
  explicitly rather than assuming any reasonable engineer would land on it unprompted.

**Bug 2 — invalid DAX, not a silent wrong number: `CROSSFILTER` direction constant.**

```dax
Studio Net Revenue :=
CALCULATE (
    [Net Revenue],
    CROSSFILTER ( bridge_title_studio[title_id], dim_title[title_id], BothDirections )
)
```

`CROSSFILTER`'s third argument only accepts `None`, `OneWay`, `Both`, or
`OneWay_RightFiltersLeft` — `BothDirections` is not a valid member and this measure would fail to
save in Power BI Desktop. This is a different failure class from Bug 1: it doesn't silently return a
wrong number, it doesn't run at all, so a developer would catch it immediately on first use rather
than carrying it into a scorecard. Worth recording because it's a plausible-*looking* API call (`Both`
is real; the agent appears to have merged it with a descriptive word), and because the underlying
approach — forcing bidirectional crossfilter on `bridge_title_studio ↔ dim_title` inside the measure
rather than declaring the relationship bidirectional in the model — is the alternative we considered
and rejected in `MODEL.md` ("the bridge direction decision"), for the reason stated there: it makes
studio scoping opt-in per measure, and this is a concrete instance of exactly that failure (an
easy-to-get-wrong per-measure incantation) surfacing on the very next measure that needed it. Confirmed
by hand-computing the intended logic (as if `Both` had been written correctly): the resulting numbers
match ours exactly on all four studios and both Twin Hearth title rows, so the *model design choice* it
was trying to express was correct — only its DAX syntax and its choice to implement it per-measure
rather than in the relationship were the problems.

**No change made to `MEASURES.dax` or `MODEL.md`** as a result of this exercise — per instruction, the
stress test's purpose was to find errors in *our* measures, and it didn't: it confirmed the `Paying
Players` definition we'd already chosen (and flagged as one of the two least-sure decisions) is the one
that avoids a real, demonstrable bug, and it independently arrived at the same bridge-direction
conclusion we'd already documented, by hitting the failure mode we'd predicted.

---

## Session 3 — rounding notes, a second correction to the Q6 footnote, verification, branch

**Date:** 2026-09-17

### Direction given

Before committing: (1) add a rounding-accumulation note to §1 (and §4 if it applies), showing both the
naive-sum and the correct figures; (2) fix the Q6 footnote — 30.37% is new titles' *share of revenue*,
not their *contribution to growth* — by adding `Net Revenue YoY % (New Titles)` as an additive
decomposition with its own check and an assertion that the two growth terms sum to the total; (3)
confirm §4's company row uses `Company Net Revenue`, not the RLS-safe dashboard variant; (4) re-verify
and update `VERIFICATION.md`; (5) print `MEASURES.dax` in full; (6) `git remote -v`; (7) branch and
commit, no push; (8) draft the PR description.

### A second correction to the same footnote

This is the second time the Q6 growth footnote has needed correcting, and worth being direct about
that rather than treating it as routine. The first correction (Session 2) fixed an unmeasured claim
("two-thirds of growth is new titles") by building `Net Revenue YoY % (Like-for-like)` and reporting
53.56% against 30.37%. That 30.37% figure was itself real and measure-backed — it just answered a
different question than the one it was placed next to. 30.37% is new-title revenue **as a share of the
current quarter's total** (95,931.53 of 315,862.09); the footnote's sentence structure implied it was
comparable to, or additive with, the 53.56% like-for-like growth rate, and it isn't — one is a
share-of-total (divides by the current period), the other is a growth rate (divides by the prior
period), and adding a share-of-total to a growth-rate produces a number with no defined meaning even
though 53.56 + 30.37 doesn't look obviously wrong at a glance (83.93 vs. the true 120.55 — the mismatch
is large enough that it should have been caught by eye, and wasn't, until asked to verify the arithmetic
identity explicitly).

Fixed by adding `Net Revenue YoY % (New Titles) = DIVIDE([Net Revenue] - [Net Revenue (Like-for-like)],
[Net Revenue PY])` — critically, dividing by the **same** prior-year-total denominator that `Net Revenue
YoY %` and `Net Revenue YoY % (Like-for-like)` both use (not the like-for-like PY figure), which is what
makes the two terms genuinely additive: `(LLF_current - LLF_PY) + (Total_current - LLF_current)`, both
over `PY_total`, telescopes exactly to `Total_current - PY_total`. New check `q6_new_titles_pp` (66.98)
and a new assertion, `assert_q6_pp_decomposition_sums_to_total`, computed live from source on both
sides — confirms `53.56 + 66.98 = 120.55` (unrounded: 120.5467 both ways) to the 0.01 tolerance.
Corrected footnote: **"120.55% = 53.56 pp like-for-like + 66.98 pp from titles launched since (T-02,
T-05)."** The 30.37% figure wasn't deleted — it's true and worth keeping — but it now lives clearly
labelled as a share-of-revenue statistic, not folded into the growth decomposition it doesn't belong to.

### Rounding-accumulation notes added to §1 and §4

§1: naive sum of the five *displayed* (2dp-rounded) title rows is 315,862.07; the correct company total
(unrounded rows summed, then rounded once) is 315,862.09. Both figures now stated explicitly in
`SCORECARD.md`, with the two-cent gap attributed to rounding accumulation rather than left implicit.

§4: same principle checked, but here it doesn't produce a visible gap — the four unrounded studio rows
(915,896.6705 + 424,406.5410 + 309,959.9377 + 215,396.8566 = 1,865,660.0058) and the four displayed
figures both round to 1,865,660.01. Stated as such rather than fabricating a discrepancy that isn't
there, with an explicit reminder that this "sum of four" was never supposed to reconcile with the
company total anyway — that's a different, deliberate discrepancy (the co-credit double-count), not to
be confused with rounding accumulation.

### Confirmed

§4's company row uses `Company Net Revenue` (the unrestricted measure), not `Company Net Revenue
(Page-Safe)` — correct, since the flat `SCORECARD.md` document has no RLS context to be page-safe
against; the Page-Safe variant exists only for the live dashboard.

### Re-verified

`python verification/verify_scorecard.py`: **27 value checks, 8 assertion checks, all PASS** (up from
26/7 — the new `q6_new_titles_pp` check and `assert_q6_pp_decomposition_sums_to_total` assertion).
`verification/VERIFICATION.md` updated with this run.

---

## Session 4 — final human review: two defects a green verification run could not see

**Date:** 2026-09-17

A line-by-line human review of the deliverables found real defects that every previous check had
missed. Recording them here in full, because the *category* of miss matters more than the individual
fixes: the verification harness only ever proved that filter contexts produce the right numbers. It
cannot prove that DAX is valid DAX, and it cannot test a sentence.

### Defect 1 — `MEASURES.dax` did not compile

The like-for-like block, as shipped through three green verification runs, was invalid DAX:

```dax
Titles Active Both Periods =
VAR CurrentTitles = FILTER ( VALUES ( dim_title[title_id] ), [Net Revenue] > 0 )
VAR PriorTitles = FILTER ( VALUES ( dim_title[title_id] ), CALCULATE ( [Net Revenue], DATEADD ( dim_date[date], -1, YEAR ) ) > 0 )
RETURN INTERSECT ( CurrentTitles, PriorTitles )        -- a measure cannot return a table

Net Revenue (Like-for-like) =
CALCULATE ( [Net Revenue], [Titles Active Both Periods] )   -- a measure cannot be a CALCULATE filter
```

Two separate violations: a measure must return a scalar (this returned a table via `INTERSECT`), and a
measure reference cannot be used as a `CALCULATE` filter argument. Power BI would have refused to save
either one. **The SQL proofs passed regardless**, because they were written to mirror what the measures
*meant* — restrict both periods to the titles active in both, which is the correct intent and produced
the correct 219,930.56 / 143,217.79 / 53.56% figures — rather than what the DAX would actually do,
which was fail to execute at all. Every number in the footnote was right; the code that was supposed to
produce those numbers could not run.

Fixed to the reviewer-supplied form: the helper returns `COUNTROWS(...)` (a scalar), and each
like-for-like measure builds its own `ComparableTitles` table in a `VAR`, which *is* a legal `CALCULATE`
filter argument. Also took the same opportunity to build `Cash Settled` and `Refunds (Treasury)` on the
Layer 0 base measures (`[Order Net Revenue]`, `[Refund Net Amount]`) instead of repeating raw `SUM()`
calls, which is what the layering was supposed to mean in the first place.

### Defect 2 — the RLS design was based on a false claim about Power BI

`DASHBOARD.md` asserted that making `dim_title ↔ bridge_title_studio` bidirectional was sufficient for
a studio lead's restriction on `dim_studio` to reach `dim_title` and the fact tables, and went further —
it argued this was *why* the bidirectional relationship had been chosen over a per-measure
`CROSSFILTER`, presenting the reasoning as the safety-critical insight of the whole model.

The premise is false. Cross-filter direction governs ordinary query filtering; RLS propagation across a
relationship is a **separate** setting ("Apply security filter in both directions"), and a bidirectional
cross-filter does not carry a security filter on its own. With that flag off, the role restricts
`dim_studio`, the studio bar chart correctly shows one bar, and `dim_title` stays unfiltered — so every
studio lead sees **every title's revenue** in visuals ②, ④ and ⑤. Silent, no error, and it is precisely
the confidentiality failure the page's whole RLS section exists to prevent.

Worth being clear about what happened: the conclusion (make the relationship bidirectional) was
defensible, and the rejected alternative (`CROSSFILTER` per measure) genuinely is unsafe for RLS — but
the stated *reason* was wrong, and a wrong reason stated confidently is worse than no reason, because it
would have shipped a model that leaks while documenting why it doesn't. Rewritten per the reviewer's
specification: `sec_user_studio` is now a **disconnected** table read directly by the role's filter
expression, the security-filter flag is documented as an explicit column in the `MODEL.md` relationship
table (not deployment trivia), and the consequence of leaving it off is stated in both files.

Also replaced the hardcoded `4` in `Company Net Revenue (Page-Safe)` — it inferred "is this viewer
restricted?" by counting visible studios against a literal studio count, which would have started
silently lying the day a fifth studio was onboarded. It now asks `sec_user_studio` directly whether the
current user is a studio lead.

### Everything else corrected in the same pass

- **Period control**: replaced the single quarter picker with two header slicers (Fiscal Year, Fiscal
  Quarter), with Fiscal Quarter's visual interaction switched **off** for visuals ③, ④ and ⑤ so they
  always show the full selected fiscal year. Doing this with interaction settings rather than
  year-scoped measure variants means there is still exactly one definition of net revenue in the model.
- **Wireframe numbers verified, not asserted**: added per-title `Net Revenue PY` checks for FY2025 Q2
  (T-01 100,859.89 · T-04 31,433.03 · T-03 10,924.87 · T-02 and T-05 both 0), an assertion that they sum
  to the 143,217.79 total, and a check that the two launch months annotated in the wireframe match
  `dim_title.launch_date` (T-02 → 2025-09, T-05 → 2026-02). The prior-year figures in the wireframe were
  already correct; the **bar sort order was not** — `Hollow Crown: Ashen Tide` (44,894.38) was printed
  below `Lantern & Lock` (27,300.05). Now sorted by current-quarter net revenue descending.
- **Performance #5 was sized from the wrong number.** It claimed the 60-day settlement lag (Nintendo
  eShop) was the longest lag in the model and sized a 3-month refresh window from it. Querying the data
  directly: `order_date → settlement_date` maxes at 60 days, but `order_date → refund_date` maxes at
  **71 days**. The refund lag is the binding constraint, and a window sized off the settlement figure
  would leave an 11-day hole through which late refunds are silently missed. Now a 4-month rolling
  window, justified from the measured maximum, with an instruction to re-measure before narrowing it.
- **MODEL.md wording**: the ROUND claim now says no measure rounds a *returned value* (the one `ROUND`
  is a boolean guard inside `Paying Players`); decision #3 no longer makes claims about how
  `ALL(dim_title)` interacts with bridge filter propagation, and instead states plainly that the
  denominator clears title and bridge filters then re-applies the current studio with
  `VALUES(dim_studio[studio_id])`, so studio scope never depends on propagation details; `month_short`
  is documented as sorting by `fiscal_month_no` (Oct first), not `calendar_month`.
- **SCORECARD §6**: added that the two displayed parts sum to 120.54, not 120.55, because each is
  rounded independently — unrounded they sum exactly.
- **Naming**: `Refunds Paid` replaced with the actual measure name `Refunds (Treasury)` everywhere.
- **Format strings**: while auditing every measure for scalar-return, noticed the four ratio measures
  return decimal ratios (1.2055), not percentages (120.55) — they render as the scorecard's figures only
  because they carry a Percentage format string, and the SQL proofs multiply by 100 to match. That
  assumption was implicit and is now stated at the top of `MEASURES.dax`.
