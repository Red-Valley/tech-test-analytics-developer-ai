# AI Workflow

## Tool used
Claude (Anthropic). I used it as a technical reference while building the
model and measures myself in Power BI Desktop — mainly to clarify DAX
concepts I hadn't used before (USERELATIONSHIP, CROSSFILTER, bidirectional
filtering) and to sanity-check my modeling decisions before implementing
them.

## Prompts and what came back

1. Asked how to handle fact_order and fact_refund each having two date
   columns that both need to point at the same calendar (order date vs.
   settlement date, order date vs. refund date). Claude explained the
   role-playing dimension pattern — only one relationship per table pair
   can be active in Power BI, so I built both relationships and left the
   second one inactive, then activated it per-measure with
   USERELATIONSHIP where the brief required that specific date.

2. Asked how the co-development credit rule (a title counted in full for
   every studio that made it) should be modeled given the bridge table.
   Claude explained that the studio-side relationship would need a
   bidirectional filter to reach through the bridge into dim_title, and
   that I should scope that behavior to a single measure (CROSSFILTER)
   rather than making the physical relationship bidirectional, to avoid
   affecting other questions that don't involve studios.

3. Asked how to interpret "FY2026 Q2" against the fiscal year rule (fiscal
   year starts Oct 1). Confirmed FY2026 Q2 = Jan–Mar 2026, not the
   calendar Q2 — I verified this against the pre-built fiscal_quarter
   column in dim_date rather than trusting it blindly.

4.	While building the studio-level measure (Net Revenue by Studio, using
	CROSSFILTER to reach through the bridge table), Claude's first suggestion
	was to compare it directly against the company-wide Net Revenue in a
	simple card. Both came back showing the exact same number
	(1,438,468.85), which looked plausible on its own but was wrong given
	that I had already confirmed two titles are co-developed and should be
	double-counted at the studio level.
	I caught it by building a detail table (studio x title x measure) instead
	of trusting the summary cards. The detail table showed the double-count
	was actually happening correctly at the row level (co-developed titles
	appeared under both studios with the same value) — the bug was that the
	table's automatic Total row was not simply adding the visible rows; it
	was recalculating the measure in its own filter context, silently
	matching the company total instead. The fix was to stop relying on any
	visual's automatic Total for this measure and add an explicit SUMX
	measure that sums the studios one by one.
	
5.	Parallel agents / subagents / worktrees
	Not used — this was a single, sequential build (model, then measures,
	then scorecard, then dashboard), done in one Power BI Desktop session
	with Claude as a step-by-step technical reference throughout.																								