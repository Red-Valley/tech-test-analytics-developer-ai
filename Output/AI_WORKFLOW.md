# AI_WORKFLOW.md

## Tools

**Claude (Opus 5), in a project workspace.** One long conversation rather than isolated prompts, so the model carried the brief, the schema and every earlier decision forward. That mattered more than any single answer: most of the useful output came from the model catching that a new decision contradicted an earlier one.

**Power BI Desktop** for the model and measures. **`bin/query.py`** against the SQLite warehouse as the independent check on every number.

I did not use parallel agents, subagents or worktrees. The work was a single dependency chain — the schema decides the relationships, the relationships decide the measures, the measures decide the scorecard — so there was nothing to split. Parallelising it would have meant one agent designing measures against a model another agent was still changing.

---

## How I drove it

Two rules, set at the start and kept:

**Push back is allowed.** I told the model explicitly that I wanted disagreement, and that I intended to review its logic rather than accept output. This changed the character of the responses — I got flagged trade-offs and reversals rather than confident single answers.

**Nothing goes in the scorecard that did not come out of a measure.** Before Power BI Desktop was confirmed as available, the plan was to write the DAX first and then build a Python harness that mirrored each measure's *composition* — base functions calling base functions — so that a divergence would show up as a composition bug rather than as differently-shaped SQL. Once Desktop was working, the harness became the independent check instead of the source.

---

## Prompts, and what came back

**1. "Read these instructions and help me create the steps I need to follow. Push back is allowed when discussing the steps and solution."**

Came back with a plan, and three pushbacks I had not asked for: that "scalable for future clients" and a three-hour limit pull against each other, that no measure could be designed before reading all seven questions, and that the biggest execution risk was the scorecard-must-come-from-measures rule. The third one reshaped my whole approach. It also refused to design anything until I supplied `METRIC_BRIEF.md` and the schema, which was correct.

**2. "I don't know about cross-filter direction. I need a good explanation of what it is, why it's important, and how it affects the current test."**

Explained filter propagation, then reviewed screenshots of my relationship list and found four defects: a many-to-many between `fact_order` and the bridge, three dimension relationships set to Both by autodetect, `dim_studio` and `fact_refund` entirely unconnected, and the bridge set to Single when it needed Both. It traced a specific leak path — date filter → `fact_order` → uphill into `dim_player` → down into `fact_refund` — and predicted a wrong refund number.

**3. "Why would it change when the `dim_player` direction is with `fact_order` and the refund value is in `fact_refund`?"**

The most productive prompt I wrote. The model had asserted the leak would produce a silent wrong number. Challenged, it separated the mechanism from the outcome and conceded it had overstated: the silent failure only occurs in a specific build order, and once `fact_refund[order_date]` → `dim_date` exists, Power BI would more likely throw an ambiguity error than silently mislead. Both failures come from the same defect, but they present completely differently. I would not have understood the filter graph without asking.

**4. "I didn't create the fiscal quarter sort. You can use the fiscal quarter columns."**

The model had proposed a calculated column to fix fiscal quarter sort order. I checked the actual values before building it. See below.

**5. "Imagine you are the manager of all the studio leads on one side, and the one building the dashboard on the other."**

Produced `DASHBOARD.md`. Framing it as two audiences surfaced something a single-perspective prompt did not: under RLS, "company net revenue" means the titles a studio lead can see, so the reference line on the studio comparison collapses onto their own bar. That visual is genuinely useful to two of the six users. Designing only as the builder, I would have shipped it without noticing.

---

## Where the AI was confidently wrong

### The plausible number: refunds in December 2025

While wiring relationships, I built `fact_refund[player_id]` → `dim_player` before building `fact_refund[order_date]` → `dim_date`, with `fact_order` ↔ `dim_player` still set to Both from autodetect. A card showing `SUM(fact_refund[net_refund_usd])` with a December 2025 slicer returned **about $5,000**.

That number is entirely plausible. Total refunds across both fiscal years are $98,306.10, so five thousand in a month sits right where a month should sit. Nothing about it invites a second look. In a monthly review it would have been read out and accepted.

It was wrong. The date filter never reached `fact_refund`. It went into `fact_order`, climbed uphill into `dim_player` through the bidirectional relationship, and came down into `fact_refund` as a *player* filter. The figure meant "refunds belonging to players who happened to order in December 2025" — a population with no business meaning.

**How I caught it:** not by inspecting the number, which looked fine, but by changing one relationship setting and watching a number move that had no business moving. Setting `fact_order` ↔ `dim_player` back to Single made the card jump to $98,306.10 — recognisably the all-time total, which announced itself as wrong in a way the $5,000 never did. Adding the missing `order_date` relationship produced a third value, which matched:

```
python3 bin/query.py "SELECT ROUND(SUM(net_refund_usd),2) FROM fact_refund
                      WHERE order_date BETWEEN '2025-12-01' AND '2025-12-31'"
```

The lesson I took from it: a wrong number that looks wrong costs nothing. The dangerous one is the one that looks right. The only defence is a second source that was computed a different way.

### The invented problem: fiscal quarter sorting

The model told me, with a worked formula and confident reasoning, that `fiscal_quarter` would sort alphabetically and put FY2026 Q2 in the wrong place on an axis, and that sorting by `fiscal_quarter_no` would not help because FY2025 Q1 and FY2026 Q1 both map to 1. It proposed a calculated column:

```
Fiscal Quarter Sort = VALUE ( RIGHT ( dim_date[fiscal_year], 4 ) ) * 10 + dim_date[fiscal_quarter_no]
```

All of that reasoning is correct for the *usual* fiscal calendar, where the quarter column holds bare labels like `Q1`. It is wrong for this warehouse. `dim_date[fiscal_quarter]` holds `FY2025 Q1` — a fixed-width year prefix followed by the quarter number — so the default alphabetical sort is already chronological.

I caught it by looking at the column values before building the fix. The model had pattern-matched to the common case and never checked the data it had already been shown.

### The reversal: bridge cross-filter direction

Early on, before I had supplied `METRIC_BRIEF.md`, the model recommended keeping every relationship single-direction and handling the many-to-many with `CROSSFILTER` or `TREATAS` inside the specific measures needing studio context. Standard advice, and it argued for it on both correctness and performance grounds.

Once it had the brief, it reversed itself: studio context is needed by question 4, question 7 *and* row-level security — most of the page, not one measure — and the bridge is 7 rows, so the performance argument does not apply. It set out why it had changed position rather than quietly switching.

This is less a failure than a lesson about sequencing. Architectural advice given before the model has the requirements is advice about the general case. I now treat any structural recommendation made before the brief was in context as provisional.

---

## What I would do differently

Give the model the full brief and schema before asking for any structural decision. Two of the three problems above trace to advice given with partial context.

And test the mechanism, not the number. Every wrong value I found was found by changing one thing and watching something move that should not have — never by looking at a figure and judging whether it seemed right.