# How I used AI

> Drafted with Claude from my running prompt log (`AI_WORKFLOW_LOG.md`, committed alongside this file),
> then reviewed and edited by me. Every prompt below happened during the session.

## 1. Tools and why

- **Claude (chat), connected to my live Power BI Desktop model through the Power BI MCP server.** That let the
  assistant read the model (relationships, measures, column storage stats), run DAX queries against the real
  data, and make model changes I specified (creating relationships, hiding columns) — instead of me copy-pasting
  screenshots and guessing.
- **The same assistant running independent SQL against `data/warehouse.db`.** I used this as the *second path* for
  every number: a measure is accepted only when the DAX result in the model and a separately written SQL query
  agree. That is the main control in this workflow — it is how both errors in section 3 were caught.
- **Power BI Desktop (PBIP/TMDL)** as the build tool, so the model is reviewable as text.

Division of work: I made the modelling decisions and wrote or approved every measure; the AI reviewed my DAX,
proposed fixes, validated numbers two ways, and drafted the documents, which I reviewed.

## 2. Concrete prompts and what came back

1. **"Which option for the studio filter: bidirectional on the bridge, CROSSFILTER in the measures, or TREATAS?"**
   → Recommended bidirectional on `bridge_title_studio → dim_title`: one model where every measure respects a
   studio filter, simple DAX; the cost is that studio RLS needs the security filter in both directions. I chose it
   and listed it as one of my two least-sure decisions.
2. **"Review my measure: `Net Revenue = SUM(fact_order[gross_usd]`"** → Pointed out the missing parenthesis, that
   `gross_usd` is before the store's cut (the brief says `net_usd`), and that refunds were missing; suggested
   base measures `Order Net` / `Refund Net` and a derived `Net Revenue`. I rewrote them; validated FY2026 =
   1,441,253.46 in DAX and SQL.
3. **"Review my `% of Studio Net Revenue` = DIVIDE([Net Revenue], CALCULATE([Net Revenue], REMOVEFILTERS(dim_studio)))"**
   → It ran the measure in my model: 100% for both Twin Hearth titles (sum 200%). I had removed the studio filter
   and kept the title filter, so the denominator equalled the numerator. Fix: `REMOVEFILTERS(dim_title)`; tested
   before I applied it: 74.21% + 25.79% = 100%, denominator 915,896.67 = Twin Hearth's Q4 row.
4. **"Propose a definition of paying player and show me its impact."** → Net revenue > 0 in the period, so fully
   refunded players are excluded: 12,498 paying players vs 12,807 with any order in FY2026 Q2 (309 fully refunded).
   DAX and SQL agree; the definition is stated in the scorecard.
5. **"Fill in SCORECARD.md from my measures."** → Evaluated all seven questions in one DAX query that uses only my
   eleven measures, cross-checked against SQL, and wrote the cells plus the required notes.

## 3. When the AI was confidently wrong, and how I caught it

**AI error 1 — a plausible number that was wrong.** After validating the studio rows, the assistant told me the
four studios "add up to 1,865,659.99". When the scorecard was produced from the measures, the sum of the four
studio rows came back as **1,865,660.01**. The 0.02 gap is small, but it was a number stated confidently from
mental arithmetic rather than produced by the model — exactly the kind of number the brief says not to trust.
The scorecard uses only the measure-produced value.

**AI error 2 — a confident, wrong explanation.** Drafting the Q4 note, the assistant named *Lantern & Lock (Emberwatch
+ Saltpine)* as the second co-developed title. It read plausibly and the numbers around it were right. Querying
`bridge_title_studio` joined to names showed the actual shared titles: *Hollow Crown: Ashen Tide* (Twin Hearth +
Emberwatch) and *Emberwatch Tactics* (Emberwatch + Nine Lanterns). The corrected note now proves the gap: studio sum
− company = 424,406.55 on rounded rows = those two titles' FY2026 revenue (236,166.69 + 188,239.85), counted twice.

**AI error 3 — "done" that wasn't.** I asked for the hard-coded CSV path to become a parameter. The assistant
created a `DataFolder` parameter, rewrote all eight table queries through the MCP connection (also replacing
queries that picked each CSV by its *position* in the folder — adding one file to `data/` would have loaded the
wrong table silently), ran a full refresh and reported identical row counts. True in the live session — but when
I saved, Power BI Desktop wrote its own copy of the Power Query definitions back and the change was gone. Caught by
reading the saved TMDL files instead of trusting the live model. Fixed by closing Desktop and editing the TMDL
partitions directly (the supported route for PBIP), then reopen, refresh, save, and re-check both the files
(8/8 tables use the parameter) and the scorecard values (unchanged).

**For completeness — my own plausible-but-wrong measure.** `Refunds by Refund Date` first returned 5,686.75 for
December 2025. SQL by refund date said 5,009.66. Reading the measure back from the model showed I had pasted
`USERELATIONSHIP(fact_order[settlement_date], …)` — a relationship that doesn't touch `fact_refund`, so it
silently kept the active order-date relationship (SQL by order date = 5,686.75 exactly). No error, believable
number, wrong logic; the two-path check caught it.

## 4. Parallel agents / subagents / worktrees

Not used. The work was sequential by nature — every derived measure depends on the base measures and on the
relationship decisions — and the bottleneck was validation, not typing speed. One assistant with live access to
the model plus an independent SQL path was the better fit than splitting the work.
