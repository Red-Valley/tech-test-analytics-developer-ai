# Verification run

`SCORECARD.md` is filled in only from a run of `verify_scorecard.py` that ends in `RESULT: PASS`.
This file is that run, captured verbatim. To reproduce:

```
python verification/verify_scorecard.py
```

There is no `.claude/skills/bi-semantic-model-builder` in this repo or the user profile that produced
this submission — `checks.json` and `verify_scorecard.py` were written from scratch for this exercise
(see `AI_WORKFLOW_LOG.md`, Session 2).

## Run output

```
==============================================================================
VALUE CHECKS -- one per scorecard cell
==============================================================================
[PASS] q1_T-01                          1. Hollow Crown                            expected=145510.77      actual=145510.77
[PASS] q1_T-02                          1. Hollow Crown: Ashen Tide                expected=44894.38       actual=44894.38
[PASS] q1_T-05                          1. Emberwatch Tactics                      expected=51037.14       actual=51037.14
[PASS] q1_T-04                          1. Saltmarsh Rally                         expected=47119.73       actual=47119.73
[PASS] q1_T-03                          1. Lantern & Lock                          expected=27300.05       actual=27300.05
[PASS] q1_company                       1. Company total, FY2026 Q2                expected=315862.09      actual=315862.09
[PASS] q2_cash_settled_dec25            2. Net revenue settled in Dec 2025         expected=103907.4       actual=103907.4
[PASS] q3_refunds_treasury_dec25        3. Refunds recognised in Dec 2025          expected=5009.66        actual=5009.66
[PASS] q4_STU-01                        4. Twin Hearth Studios                     expected=915896.67      actual=915896.67
[PASS] q4_STU-02                        4. Emberwatch Interactive                  expected=424406.54      actual=424406.54
[PASS] q4_STU-04                        4. Nine Lanterns                           expected=309959.94      actual=309959.94
[PASS] q4_STU-03                        4. Saltpine Games                          expected=215396.86      actual=215396.86
[PASS] q4_sum_four                      4. Sum of the four rows above              expected=1865660.01     actual=1865660.01
[PASS] q4_company                       4. Company net revenue, FY2026             expected=1441253.46     actual=1441253.46
[PASS] q5_paying_players                5. Paying players                          expected=12498          actual=12498
[PASS] q5_paying_players_transacted_footnote 5. footnote — Paying Players (Transacted)  expected=12807          actual=12807
[PASS] q5_revenue_per_player            5. Revenue per paying player               expected=25.27          actual=25.27
[PASS] q6_fy25q2                        6. (intermediate) FY2025 Q2 net revenue    expected=143217.79      actual=143217.79
[PASS] q6_growth_pct                    6. FY2026 Q2 vs FY2025 Q2, %               expected=120.55         actual=120.55
[PASS] q7_T-01                          7. Hollow Crown — Net revenue              expected=679729.98      actual=679729.98
[PASS] q7_T-02                          7. Hollow Crown: Ashen Tide — Net revenue  expected=236166.69      actual=236166.69
[PASS] q7_T-01_pct                      7. Hollow Crown — % of studio              expected=74.21          actual=74.21
[PASS] q7_T-02_pct                      7. Hollow Crown: Ashen Tide — % of studio  expected=25.79          actual=25.79
[PASS] q6_likeforlike_current           6. footnote — Net Revenue (Like-for-like), FY2026 Q2 expected=219930.56      actual=219930.56
[PASS] q6_likeforlike_py                6. footnote — Net Revenue (Like-for-like) PY, FY2025 Q2 expected=143217.79      actual=143217.79
[PASS] q6_likeforlike_growth_pct        6. footnote — Net Revenue YoY % (Like-for-like) expected=53.56          actual=53.56
[PASS] py_by_title_T-01                 DASHBOARD wireframe 2 — Hollow Crown, FY2025 Q2 (prior-year bar) expected=100859.89      actual=100859.89
[PASS] py_by_title_T-04                 DASHBOARD wireframe 2 — Saltmarsh Rally, FY2025 Q2 (prior-year bar) expected=31433.03       actual=31433.03
[PASS] py_by_title_T-03                 DASHBOARD wireframe 2 — Lantern & Lock, FY2025 Q2 (prior-year bar) expected=10924.87       actual=10924.87
[PASS] py_by_title_T-02                 DASHBOARD wireframe 2 — Hollow Crown: Ashen Tide, FY2025 Q2 (no prior-year bar) expected=0              actual=0
[PASS] py_by_title_T-05                 DASHBOARD wireframe 2 — Emberwatch Tactics, FY2025 Q2 (no prior-year bar) expected=0              actual=0
[PASS] launch_dates_shown_in_wireframe  DASHBOARD wireframe 2 — launch months annotated on the two titles with no prior-year bar expected=2              actual=2
[PASS] q6_new_titles_pp                 6. footnote — Net Revenue YoY % (New Titles) expected=66.98          actual=66.98

==============================================================================
ASSERTION CHECKS -- internal consistency / regression
==============================================================================
[PASS] assert_q1_titles_sum_to_company            left=315862.091 right=315862.091
       Q1: sum of the 5 title rows equals the company total exactly (titles are mutually exclusive per order/refund row, no bridge involved at this grain). Computed at full precision from source -- summing the already-rounded-to-2dp display values instead would show a false 2-cent gap (145510.77+44894.38+27300.05+47119.73+51037.14=315862.07 vs company 315862.09), which is a rounding-accumulation artifact, not a data issue: rounding happens only at display, per MODEL.md.
[PASS] assert_q4_double_count_equals_shared_titles left=424406.5409999995 right=424406.541
       Q4: (sum of 4 studio rows) - (company total) must equal netrev(T-02,FY26) + netrev(T-05,FY26) exactly -- proves the excess is caused only by the two co-credited titles, nothing else. Both sides computed at full precision from source, not from rounded display literals.
[PASS] assert_q6_pp_decomposition_sums_to_total   left=120.54668851227694 right=120.54668851227694
       Q6: Net Revenue YoY % (Like-for-like) + Net Revenue YoY % (New Titles) must equal Net Revenue YoY % exactly -- both terms share the same denominator (the full prior-year total), so the decomposition is additive by construction. Both sides computed live from source, not from rounded/hardcoded literals; the identity (LLF_cur-LLF_py)+(Total_cur-LLF_cur) = Total_cur-Total_py holds exactly once both fractions share the Total_py denominator.
[PASS] assert_py_titles_sum_to_py_total           left=143217.789 right=143217.789
       The five per-title Net Revenue PY values (FY2025 Q2) sum to the FY2025 Q2 total of 143,217.79 used in the headline and the YoY denominator -- ties the DASHBOARD wireframe's prior-year bars to the scorecard's Q6 figure. Full precision on both sides.
[PASS] assert_q7_pct_sums_to_100                  left=100.0 right=100.0
       Q7: Twin Hearth's two %-of-studio rows sum to 100.00% (only two titles are credited to STU-01, confirmed via bridge)
[PASS] assert_q5_paying_le_transacted             left=12498 right=12807
       Q5: net-revenue-positive paying players (12,498) must be <= transacted players (12,807) -- the 309 players fully refunded in the period must be excluded
[PASS] regression_no_string_comparison_over_refunds left=0 right=0
       Regression test for the Session 1 bug: comparing TEXT-typed amount columns without CAST made SQLite do lexical string comparison and reported 1,883 false 'over-refunds'. With CAST, must be 0.
[PASS] regression_refund_sign_positive            left=0 right=0
       All net_refund_usd values are positive (measures subtract this column; if the warehouse ever shipped a negative refund, Net Revenue would silently add it back)
[PASS] regression_no_fact_to_fact_relationship_needed left=0 right=0
       fact_refund's own title_id/player_id/platform_code/order_date must still agree with the parent fact_order on every row -- the basis for routing fact_refund through the shared dimensions instead of through fact_order

==============================================================================
RESULT: PASS -- all 33 value checks and 9 assertion checks passed.
```

## What each check proves

- **24 of the 33 value checks** correspond one-to-one to a printed cell in `SCORECARD.md`.
- **4 value checks** (`q6_likeforlike_*`, `q6_new_titles_pp`) back the Q6 growth decomposition in the
  §6 footnote — not printed scorecard cells, but a claim made in prose that needed the same discipline.
  It was corrected twice over the course of this exercise (see `AI_WORKFLOW_LOG.md`).
- **6 value checks** (`py_by_title_*`, `launch_dates_shown_in_wireframe`) verify the numbers and launch
  months printed in the `DASHBOARD.md` wireframe, so the wireframe is not carrying unverified figures.
- **9 assertion checks** are internal-consistency and regression tests: five tie independently computed
  numbers together (title sum = company total, studio double-count = shared-title revenue, the Q6
  percentage-point decomposition sums to the total, prior-year title rows sum to the prior-year total,
  two %-of-studio rows sum to 100%), one is a definitional sanity check (paying <= transacted), and three
  are regression tests for mistakes already made once in this exercise (the TEXT-column
  string-comparison bug from Session 1, refund sign, and the fact_refund/fact_order attribute agreement
  that justifies not building a fact-to-fact relationship).

## What this harness does NOT prove

Worth stating plainly, because a green run here was taken as more assurance than it deserved earlier in
this exercise. These checks verify that each measure's **filter context produces the right number**.
They do **not** verify:

- **That the DAX is valid DAX.** The SQL mirrors what each measure is intended to compute, written by
  hand. A measure can be syntactically invalid — returning a table where a scalar is required, or using
  a measure reference as a `CALCULATE` filter — and its mirrored SQL will still return the correct
  number. This happened: the like-for-like measures passed every run while being uncompilable. Only a
  human reading the DAX caught it.
- **Anything that isn't a number.** Relationship settings, RLS propagation behaviour, format strings,
  sort-by columns, and every claim made in prose in `MODEL.md` / `DASHBOARD.md` are outside what this
  script can see. A false statement about how Power BI propagates security filters passed through
  several green runs untouched.

Both classes of defect are recorded in `AI_WORKFLOW_LOG.md` (Session 4) and summarised in
`AI_WORKFLOW.md` section 5.

## Independent-agent stress test

A fresh subagent, given only `docs/METRIC_BRIEF.md`, the blank `SCORECARD.md` template, and the raw
table schemas (no `MODEL.md`, no `MEASURES.dax`), was asked to write its own measures for all seven
questions. Its measures were translated to SQL exactly as written and run against these same checks.
See `AI_WORKFLOW_LOG.md`, Session 2, for what it produced and what the checks caught.
