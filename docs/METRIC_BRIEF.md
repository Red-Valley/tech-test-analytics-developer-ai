# What leadership asks for

*From the Head of Publishing Operations. This is the brief; the questions below are the ones I get
asked in the monthly review, in roughly the order I get asked them.*

---

## How we count things

Rules you would have been told in your first week. None of them are up for debate.

- **The fiscal year starts on 1 October.** FY2026 is 2025-10-01 → 2026-09-30. Fiscal Q1 is Oct–Dec,
  Q2 is Jan–Mar, Q3 is Apr–Jun, Q4 is Jul–Sep. Every "quarter" in this document is a fiscal quarter.
- **Net revenue** is what we keep: the order value, less refunds, less the store's cut. The
  warehouse has already applied the store's cut — `net_usd` on `fact_order` and `net_refund_usd` on
  `fact_refund` are both net of it.
- **Revenue is recognised on the order date. Cash arrives on the settlement date**, 30 to 60 days
  later depending on the store. Both dates are on `fact_order`.
- **Refunds hit revenue on the date of the original order, and cash on the date of the refund.**
  Both dates are on `fact_refund`. Finance reports the first; Treasury reports the second.
- **Co-developed titles are credited in full to every studio that worked on them.** If two studios
  share a credit, both studios' scorecards show the whole title. That is intentional — it is how we
  pay out and how the studio leads are reviewed.
- Internal and QA accounts have already been stripped out of this warehouse. Everything you see is
  a real player.

## What I need to be able to answer

1. **How did each title do last quarter?** Net revenue by title for FY2026 Q2, and the company
   total for the quarter.
2. **How much money actually landed in the bank in December 2025?** Not what we sold in December —
   what settled in December.
3. **How much did we give back in December 2025?** Refunds as Treasury counts them, on the date the
   refund happened.
4. **How is each studio doing?** Net revenue by studio for FY2026 — and, separately, the company's
   FY2026 net revenue. Those two things get put on the same slide constantly and I need it to stop
   being confusing.
5. **What is a paying player worth?** Revenue per paying player for FY2026 Q2, and how many paying
   players that was.
6. **Are we growing?** FY2026 Q2 against the same quarter of the prior fiscal year, as a percentage.
7. **Inside Twin Hearth Studios, what is carrying the year?** Each of its titles as a share of that
   studio's FY2026 revenue.

## What I actually want on the screen

One page. I open it on a laptop, in a meeting, and I have about forty seconds before someone asks
me a follow-up. Six people use it: me, the CFO, and the four studio leads — the studio leads only
ever care about their own studio.

I do not want a wall of cards. I have been given those before.
