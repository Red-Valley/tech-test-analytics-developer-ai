# DASHBOARD.md — Twin Hearth Studios, Publishing Review

One page, opened on a laptop in a meeting, with about forty seconds before the first follow-up. Six readers: the Head of Publishing Operations, the CFO, and four studio leads who care only about their own studio.

The brief asked for no wall of cards. This page carries two bare numbers; everything else is a comparison.

---

## The page

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ Twin Hearth Studios — Publishing Review        Quarter: [ FY2026 Q2      ▾ ]   │
├────────────────────────────────────────────────────────────────────────────────┤
│   NET REVENUE — FY2026 Q2                                                      │
│   $ 4 5 6 , 7 8 9 . 0 1            ▲ +62.4%  vs FY2025 Q2  ($281,402.55)       │
├─────────────────────────────────────────┬──────────────────────────────────────┤
│ NET REVENUE BY TITLE — FY2026 Q2        │ NET REVENUE BY STUDIO — FY2026       │
│                                         │                                      │
│ Hollow Crown        ██████████ $XXX,XXX │ Twin Hearth     ██████████ $XXX,XXX  │
│ Saltmarsh Rally     ███████    $XXX,XXX │ Emberwatch      ████████   $XXX,XXX  │
│ Ashen Tide          █████      $XXX,XXX │ Saltpine        █████      $XXX,XXX  │
│ Lantern & Lock      ███        $XXX,XXX │ Nine Lanterns   ████       $XXX,XXX  │
│ Emberwatch Tactics  ██         $XXX,XXX │ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌  │
│   ◦ launched 12 Feb — partial quarter   │ company net revenue  $X,XXX,XXX      │
│                                         │ Bars total $XXX,XXX above the line:  │
│                                         │ co-developed titles credit both      │
│                                         │ studios in full — by design.         │
├─────────────────────────────────────────┼──────────────────────────────────────┤
│ PAYING PLAYERS          REVENUE / PLAYER│ CASH — TREASURY BASIS, FY2026 Q2     │
│ XX,XXX                  $XX.XX          │ Settled in    $XXX,XXX               │
│                                         │ Refunds paid  $ XX,XXX               │
└─────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## Order, and why

The order follows the sequence the questions actually get asked, and the eye starts top-left.

1. **The quarter's number, growth attached to it.** "How did we do" and "are we growing" are one thought. Putting the percentage beside the figure kills the most common first follow-up before it is asked.

2. **Net revenue by title** *(Q1)*. Horizontal bars, sorted descending — the meeting wants to know what is carrying the quarter, and alphabetical order makes the reader do the ranking. An annotation marks any title that launched mid-period, without which Emberwatch Tactics reads as a failure rather than as seven weeks on sale.

3. **Net revenue by studio, with the company total as a reference line** *(Q4)*. The brief named this one: the two numbers get put on the same slide and cause confusion. They are shown in one visual rather than two, precisely because two separate figures is what creates the confusion. The line sits visibly below the stacked bars, with one sentence saying why. Reader sees it, sees it is labelled, moves on.

4. **Paying players and revenue per player** *(Q5)*. The only two bare numbers, because they have no honest breakdown at this grain — one player who buys two titles is one paying player.

5. **Cash, Treasury basis** *(Q2, Q3)*. Last position, because it is the CFO's number rather than the room's. Shown separately and never netted, since the brief asks them as two questions. Labelled "Treasury basis" so nobody compares them to the revenue figures above, which sit on different dates entirely.

**Q7** is not a separate visual. It is what the title chart becomes under a studio filter, with share-of-studio on the data label. A second near-identical chart is what turns one page into two.

---

## How a studio lead sees only their studio

Intent only; implementation is out of scope.

A `Studio Lead` role filters `dim_studio` via `USERPRINCIPALNAME()` against a user-to-studio mapping table. Leads are assigned to the role; Ops and the CFO are not.

The filter travels `dim_studio` → bridge → `dim_title` → both facts. **"Apply security filter in both directions" must be enabled on the bridge-to-title relationship** — security filters do not follow a bidirectional path otherwise, and without it every lead sees company-wide numbers.

Two consequences that look like bugs and are not:

- **Co-developed titles appear for both leads.** The Emberwatch lead sees Ashen Tide. Same rule that makes the studio bars exceed the company total, applied to visibility. If that revenue ever becomes confidential between partner studios, the credit model and the security model change together.
- **The studio visual degenerates for a lead.** Under RLS, "company net revenue" means the titles they can see, so the reference line collapses onto their own bar. That panel is genuinely for two of the six users. I would accept that and revisit if a lead complains — the cost of being wrong is an empty panel, not a wrong number.

---

## What I cut

| Cut | Why | Put it back when |
|---|---|---|
| Storefront breakdown | No question asks it; invites a platform-mix conversation in a meeting scheduled for something else | Store terms are being renegotiated |
| Monthly trend line | Q6 asks for one percentage; a trend answers within-quarter momentum instead | The review starts asking whether a quarter was front-loaded — **first thing I would add** |
| Refund reason breakdown | An operations question, not a leadership one | Refunds move materially as a share of gross |
| Acquisition channel, country | Marketing attribution is a different report with a different audience | Someone owning acquisition spend joins this review |
| Gross revenue and platform fees | Gross beside net is how a meeting ends up arguing which number is right — the failure this layer exists to prevent | Someone is negotiating platform fees |
| A row of KPI cards | Explicitly rejected in the brief | — |

---

## Design decisions

**One date slicer, quarter grain.** Two date controls guarantees two people look at different periods believing they look at the same one. Every panel states its own period in its title.

**The studio block deliberately ignores the slicer.** The brief frames studios annually and titles quarterly. Rather than a second slicer, that block uses `[Net Revenue (Fiscal Year)]`, which expands the selection to the containing fiscal year. Named after what it does, so the mismatch reads as a decision rather than a bug.

**Two bases, never mixed, always labelled.** Revenue is the Finance basis, on order date. Cash is the Treasury basis, on settlement and refund dates. They will not reconcile and are not meant to.

**Exact figures on every bar.** Nobody hovers in a meeting — they ask, and the forty seconds are gone.

**Sorted by value.** The question is always "what is carrying this."

**No conditional colour on revenue.** Red-and-green implies a target the brief does not define. Colour is reserved for the growth indicator, where direction is real.