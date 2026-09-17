# AI Workflow

Full session-by-session detail — every prompt, every query, every fix — is in `AI_WORKFLOW_LOG.md`.
This is the summary the brief asks for.

## 1. Tools, and why

- **Claude Code**, used interactively in VS Code against a local SQLite copy of the warehouse via
  `bin/query.py` and ad-hoc Python. Chosen because the task is genuinely tool-driven, not just
  conversational: the hard rule this exercise is graded on — "DAX first, prove it with SQL that mirrors
  the measure's exact filter context" — requires an agent that can actually run queries and read their
  output back into the same reasoning loop, not one that reasons about a warehouse it can't touch.
  Every number in `SCORECARD.md` was produced by running something, not by asking a model to compute it
  from a description.
- **An adversarial subagent** (see §4): a second, isolated agent given only the brief, the blank
  scorecard, and the raw schemas, asked to solve the same seven questions cold.
- **Claude (chat)**: planning, question-to-model review, and a final line-by-line review of the
  deliverables. That last pass is where the most serious defects in this submission were found — see
  §5.

## 2. Prompts, and what came back

**1. Read-only discovery, before any deliverable existed.** Told the agent the fixed business rules
(fiscal year, net revenue definition, co-credit rule) and asked it to profile the warehouse — grain and
keys of every table, orphans, refund sign, date ranges, which titles are co-credited — and report back
without touching the scorecard. It came back with a full structural profile (all keys unique, zero
orphans across 13 FK paths, `dim_title.lead_studio_id` identified as a trap that agrees with the bridge
on all 5 titles but would under-count credits if used directly) and one real catch: an initial query
comparing refund amounts to order amounts reported 1,883 false "over-refunds" because SQLite compares
untyped `TEXT` columns as strings — every SQL proof from then on casts explicitly.

**2. Model, measures, and a verification harness, in that order.** Gave seven specific adjustments
(add a named measure for every scorecard cell including the "sum of four" studio total, redefine
`Paying Players` to iterate the player dimension not the order fact, use `DATEADD` for YoY unless it
provably fails here, put SQL proofs in a checked `checks.json`) and told it to stop after `SCORECARD.md`
for review before building the dashboard. It came back with `MODEL.md`, `MEASURES.dax`, a
`verify_scorecard.py` harness (no such skill existed to reuse — built from scratch), and one caught
mistake along the way: see §3.

**3. Correction and hardening pass.** Asked it to make `Paying Players` robust to floating-point
residue, to either back a "two-thirds of growth is new titles" claim with a real measure or delete it,
and to move the verification artifacts into their own folder. It came back having discovered its own
earlier claim was wrong: the real like-for-like YoY figure is 53.56%, not "two-thirds" of anything — the
number was corrected in `SCORECARD.md` with the mistake stated, not quietly replaced.

**4. An independent-agent stress test.** Spawned a second, isolated agent given only the business brief,
the *blank* scorecard template, and raw table schemas — no access to the model or measures already
built — and asked it to write its own DAX for all seven questions from scratch. Its output was
translated to SQL and run against the same checks. See §3 below for what that found.

## 3. Where the AI was confidently wrong

The independent stress-test agent (prompt 4 above) wrote this measure for "paying players," having
never seen our definition or the ambiguity we'd already flagged:

```dax
Paying Players :=
CALCULATE ( DISTINCTCOUNT ( fact_order[player_id] ), fact_order[net_usd] > 0 )
```

It returned **12,807** for FY2026 Q2, and a resulting revenue-per-player of **$24.66** — a completely
plausible number, in the right range, with the right shape. It is wrong. `fact_order[net_usd]` is a
per-order value and is positive on all 106,293 rows by construction (a purchase can't have a
non-positive gross value), so the filter `> 0` excludes nothing — the measure silently collapses to
"everyone who placed an order," identical to a plain transacted-player count, and never looks at
`fact_refund` at all. A player whose entire quarter was refunded still counts as "paying." The correct
figure, from our own measure — which iterates the player dimension and nets `fact_order` against
`fact_refund` per player — is **12,498**, giving **$25.27** per player.

Caught by exactly the mechanism the brief asks for: the independent measure was translated to SQL and
run against `verification/checks.json`, which already carried the verified-correct value from our own
model. It failed two checks (`q5_paying_players`, `q5_revenue_per_player`) immediately, by a large
enough margin (12,807 vs. 12,498; $24.66 vs. $25.27) to be unmistakable, not a rounding-scale
discrepancy. No change was made to our shipped measures as a result — the test's purpose was to find a
bug in ours, and instead it demonstrated that the ambiguity we'd already identified and resolved
explicitly (§5 of `SCORECARD.md`) is a real trap that an engineer working from the brief alone,
with no other signal, plausibly falls into. Full detail, including a second (non-numeric) defect the
same agent produced — an invalid `CROSSFILTER` direction constant that would fail to compile — is in
`AI_WORKFLOW_LOG.md`.

## 4. Splitting the work

Single-threaded for the model, measures, and verification harness — the 3-hour budget and the number of
sequential judgment calls (each one changing what the next step should check) made parallelizing that
core path counterproductive; a subagent working on `MEASURES.dax` in parallel with the model design
would have needed to re-derive decisions being made turns later anyway. One subagent was used
deliberately, and only once: after the model was built and verified, an isolated agent — given the
brief and the blank scorecard, nothing else — was asked to solve the same seven questions cold, as an
adversarial check rather than a division of labour. That's the only place in this exercise where a
second agent ran: not to go faster, but to get a genuinely independent second opinion on the one thing
that's hardest to self-check — whether an obvious-looking measure is actually right.

## 5. What SQL verification could not catch

The verification harness in `verification/` proves that each measure's *filter context* produces the
right number. It cannot prove the DAX is valid DAX, and it cannot test anything that isn't a number.
Two defects lived through a full green run and were only caught in the final line-by-line human review:

**(a) The like-for-like measures returned correct numbers but were invalid DAX.** As originally written,
`Titles Active Both Periods` used `INTERSECT` to return a *table* from a measure, and
`Net Revenue (Like-for-like)` then passed that measure reference into `CALCULATE` as a filter argument.
A measure must return a scalar, and a measure reference cannot be a `CALCULATE` filter — this would
have failed to save in Power BI. The SQL proofs passed anyway, because they were written to mirror what
the measure *meant* (restrict both periods to titles active in both), which was correct, rather than
what the DAX would actually do, which was nothing — it wouldn't have run at all. Fixed by returning
`COUNTROWS(...)` from the helper and building the table inside each measure as a `VAR`, which is a
legal `CALCULATE` filter.

**(b) The RLS section stated something false about how security filters propagate.** It claimed that
making `dim_title ↔ bridge_title_studio` bidirectional was sufficient for a studio lead's restriction
on `dim_studio` to reach `dim_title` and the facts. It isn't: cross-filter direction governs ordinary
query filtering, while RLS propagation across a relationship is a separate setting ("Apply security
filter in both directions"). With that flag off, every studio lead would have seen every title's
revenue — a silent confidentiality leak with no error to catch it. No SQL check could have found this,
because it isn't a number: it's a claim about engine behaviour in a document. Fixed in `DASHBOARD.md`
and added as an explicit column in the `MODEL.md` relationship table.

Both defects share a shape worth naming: the verification harness was built to catch wrong *numbers*,
and it did that job — it caught a real wrong number from the independent agent (§3), and it caught two
of my own rounding errors. But a green check on every cell says nothing about whether the DAX compiles,
whether a documented setting exists, or whether a sentence about how the engine works is true. Those
need a different kind of review, and on this submission they needed a human to ask for it.

**What was built in response: `verification/lint_dax.py`.** Nothing here can compile DAX, so the next
best thing is a structural audit. The linter parses `MEASURES.dax` and checks, per measure: balanced
parentheses/brackets/quotes; that every `[Measure]` reference resolves to a measure defined in the file;
that every `table[column]` reference exists in `data/warehouse.db` (with an explicit allow-list for
`sec_user_studio`, which lives in the model rather than the warehouse); that every function called is a
real DAX function; that the outermost function does not return a table; that no measure reference is
passed as a `CALCULATE` filter argument; that no `VAR` is declared unused or without a `RETURN`; and
that enum arguments such as `DATEADD`'s interval are valid members.

A linter that reports "all clear" is worth nothing unless it can be shown to fail on real defects, so it
ships with a fixture of deliberately broken DAX, `verification/lint_fixture_bad.dax`, containing ten
planted defects — including **both defects this exercise actually shipped** (a measure returning a table
via `INTERSECT`, and a measure reference used as a `CALCULATE` filter) and the independent agent's
invalid `CROSSFILTER ( ..., BothDirections )` enum from §3. Run it against the fixture and it reports
eleven errors; run it against the real file and it reports zero errors and one informational note.

```
python verification/lint_dax.py                                # the real file
python verification/lint_dax.py verification/lint_fixture_bad.dax   # the known-bad fixture
```

Writing it also surfaced two bugs in the linter itself, both found by running it against the fixture
rather than by reading it: measure names containing parentheses (`[Net Revenue (Like-for-like)]`) were
parsed as function calls, and `RETURN [Net Revenue]` was read as a table named `RETURN`. That is the same
lesson one level up — a checking tool needs its own failing test before its passing result means
anything.
