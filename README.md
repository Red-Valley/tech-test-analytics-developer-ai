# Analytics Developer (AI) — Technical Assessment

**Time limit:** 3 hours max.

---

## Context

**Twin Hearth Studios** publishes five titles across five storefronts. The data team finished the
warehouse; the analytics layer on top of it does not exist yet. Leadership currently runs the
monthly review off a spreadsheet that one person maintains by hand, and every meeting spends its
first ten minutes arguing about whose number is right.

You own the layer that ends that argument: the semantic model, the measures, and the one page
leadership actually looks at.

## What you're given

```
data/*.csv               the gold layer: 5 dimensions, a bridge, 2 fact tables
data/warehouse.db        the same tables as SQLite, if you'd rather explore in SQL
docs/METRIC_BRIEF.md     the business rules, and the seven questions leadership asks
SCORECARD.md             the numbers your model has to produce. Fill in every cell.
bin/query.py             a one-liner SQL runner, so you don't have to install anything to look around
```

Start by looking at the data:

```bash
python3 bin/query.py --tables
python3 bin/query.py "SELECT * FROM fact_order LIMIT 5"
```

The warehouse is clean. Nobody has planted broken rows in it. Everything that is hard here is hard
because of how the business counts, not because the data is dirty.

One column needs a definition, because its name promises more than it delivers:

- **`fact_order.order_status`** — `refunded` marks orders that were refunded **in full**. An order
  with a **partial** refund stays `completed`. So the column never tells you the whole refund story:
  refund amounts always come from `fact_refund`, and you should not filter on `order_status` to
  account for refunds.

## What to deliver

### 1. The semantic model — `MODEL.md`

Define it precisely enough that someone could rebuild it from your document alone: tables, which
columns are exposed and which are hidden, every relationship with its **cardinality and filter
direction**, which table is marked as the date table, and the grain of each fact.

Where the model has to do something non-obvious to answer the brief, say so in one line: what the
business question is, and what the model does about it.

If you ship a `.pbip` / TMDL export instead of prose, that counts — as long as a reviewer can read
the relationships without opening Power BI.

### 2. The measures — `MEASURES.dax`

Every measure behind the scorecard, named as you would ship them, with a one-line comment on each
saying what it answers. Base measures and the derived ones built on them; we are looking at how you
compose them, not just whether each works.

### 3. `SCORECARD.md`, filled in

Every cell. These are the numbers the review runs on, and they either match the warehouse or they
don't. **A right number produced by a measure that doesn't say what you claim it says scores as a
wrong number** — we read the DAX.

### 4. The dashboard — `DASHBOARD.md`

The one page from the brief. A wireframe (ASCII, image, Figma link, or a `.pbix` screenshot),
plus:

- What is on it, and in what order, and why that order.
- How a studio lead sees only their studio.
- **What you left off**, and what you would have to be told to put it back on.

Design decisions with reasons. Not a list of visual types.

### 5. Performance — a section in `MODEL.md`

This model is small today. It will not stay small: order volume is growing and the fact table is
expected to be roughly fifty times larger within two years. Name the specific things in *your*
model that would be the first to hurt, and what you would change. Be concrete about your own
choices — generic best-practice lists score nothing.

### 6. `AI_WORKFLOW.md`

How you used AI while doing this:

1. Which tool(s) and why.
2. 3–5 concrete prompts and what came back.
3. One moment where the AI was confidently wrong — a measure that returned a plausible number that
   was not the right number — and how you caught it.
4. If you used parallel agents, subagents or worktrees, how you split the work.

## Tooling

**Power BI Desktop is not required, and you are not penalised for not having it.** Everything that
gets graded is text: `MODEL.md`, `MEASURES.dax`, `SCORECARD.md`, `DASHBOARD.md`.

If you do build it in Power BI, commit the `.pbix` or a `.pbip`/TMDL export as well — it is welcome,
and it is not worth extra marks on its own. Any other BI tool is acceptable if you also express the
model and the measures in DAX, because DAX is what the team writes.

Use AI tools. This role is graded partly on how well you drive them.

## Out of scope

Building the gold layer (it's given), row-level security implementation, deployment, gateways,
workspace administration, data refresh. Describe the intent where the brief asks; don't build it.

## Evaluation

| Area | Weight |
|---|---|
| Scorecard accuracy — the numbers, produced by the measures you shipped | 30% |
| Measure quality: correctness of the DAX, composition, naming, readability | 25% |
| Semantic model: grain, relationships, cardinality and direction, date table | 20% |
| Dashboard design and the decisions behind it, including what you cut | 15% |
| Use of AI tools (`AI_WORKFLOW.md`) | 10% |

Two things that sink an otherwise strong submission:

- **Numbers that don't come from the measures.** Querying the SQLite file to fill in the scorecard
  and writing DAX afterwards that doesn't actually produce those values. We check.
- **A model that answers question 1 and quietly breaks question 4.** The brief's seven questions
  are meant to be answered by *one* model, not seven.

## How to submit

1. **Fork** this repo.
2. Create branch `submission/<your-name>`.
3. Implement.
4. Open a **Pull Request** to `main` of this repo.
5. In the PR: time spent, which tool you built in, and the two decisions you are least sure about.

Expect to defend the numbers live.
