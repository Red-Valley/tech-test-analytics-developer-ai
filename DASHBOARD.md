# Dashboard — the one page

**Audience:** the Head of Publishing Operations and the CFO see every studio. Each of the four studio
leads sees only their own studio. Six people, one report, no separate builds — the difference is row-
level security, not a second page.

**Viewing conditions:** a laptop, in a meeting, ~40 seconds before the first follow-up question. One
page. No wall of cards.

## Order, and why

The page reads top to bottom in exactly the order the brief's questions get asked, because that is the
order the room already thinks in — reordering it to what looks best on a grid would mean the Head has
to re-find their place every month instead of reading down once.

1. **Headline — FY2026 Q2 net revenue with YoY**, one visual, not two cards side by side. The number
   and its growth are one fact ("are we growing" is unanswerable without "growing from what"), so they
   never get separated onto different tiles where someone could screenshot just the big number.
2. **Net revenue by title, this quarter vs. prior year.** Answers "how did each title do" (Q1) with
   the growth context (Q6) built into the same chart, so nobody has to hold two visuals in their head
   to ask "is Emberwatch Tactics' number good?" — a title that didn't exist last year shows as
   no-prior-year, not zero, so it doesn't read as decline.
3. **Studio — FY2026, credited revenue.** No total row on the bar chart. The company figure sits in
   its own tile beside it, explicitly labelled "each title counted once," with a one-line subtitle:
   *co-developed titles are credited in full to every studio that worked on them, so studio bars will
   not add up to the company total.* This is the single most important design decision on the page —
   see below.
4. **Monthly trend — Finance vs. Treasury.** Three series, one chart, explicitly labelled: Net Revenue
   (Finance, order date), Cash Settled (Treasury, settlement date), Refunds (Treasury) (Treasury,
   refund date). This is Q2 and Q3 answered as one picture instead of two separate numbers that leadership
   would otherwise have to remember are on different clocks.
5. **Title share within studio.** One 100%-stacked bar per visible studio (one bar total under RLS,
   four for Head/CFO). Answers Q7 for whichever studio is on screen — generalised past just Twin
   Hearth, because every studio lead asks this same question about their own portfolio, not only Twin
   Hearth's.
6. **Paying players and revenue per paying player — small, secondary.** A single footer-height strip,
   not a KPI card the same size as the headline. It's a real number leadership tracks, but it has never
   been the number the room opens the meeting arguing about, and giving it equal visual weight to the
   headline would be exactly the "wall of cards" the brief says not to build.

## Wireframe

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ TWIN HEARTH STUDIOS — Monthly Review   Fiscal Year: [FY2026 ▾]  Quarter: [Q2 ▾] │ <- two slicers
│ Viewing as: Unrestricted (Head/CFO)  ·  or, for a lead: "Nine Lanterns only"    │
├────────────────────────────────────────────────────────────────────────────────┤
│ ① NET REVENUE — FY2026 Q2                                     [FY + Quarter]    │
│  ┌───────────────────────────────────────┐                                     │
│  │   $315,862.09        ▲ 120.55% YoY     │  vs FY2025 Q2: $143,217.79          │
│  │   like-for-like (same titles): ▲ 53.56%│                                     │
│  └───────────────────────────────────────┘                                     │
├────────────────────────────────────────────────────────────────────────────────┤
│ ② NET REVENUE BY TITLE — this quarter (■) vs FY2025 Q2 (░)    [FY + Quarter]    │
│  Hollow Crown             ■■■■■■■■■■■■■■■■■■  ░░░░░░░░░░░░   145.5K vs 100.9K   │
│  Emberwatch Tactics       ■■■■■■■■■■■■         (no FY25 Q2 — launched Feb 2026) │
│  Saltmarsh Rally          ■■■■■■■■■■■■         ░░░░░░░░        47.1K vs 31.4K   │
│  Hollow Crown: Ashen Tide ■■■■■■■■■■■          (no FY25 Q2 — launched Sep 2025) │
│  Lantern & Lock           ■■■■■■■             ░░░              27.3K vs 10.9K   │
│                            (sorted by this quarter's net revenue, descending)   │
├────────────────────────────────────────────────────────────────────────────────┤
│ ③ STUDIO — FY2026 (each title counted once per credited studio)  [FY only]     │
│  Twin Hearth Studios     ■■■■■■■■■■■■■■■■■■■■■■  $915.9K   ┌──────────────────┐│
│  Emberwatch Interactive  ■■■■■■■■■■■              $424.4K   │ COMPANY, FY2026  ││
│  Nine Lanterns           ■■■■■■■■                 $310.0K   │  $1,441,253.46   ││
│  Saltpine Games          ■■■■■■                   $215.4K   │ each title       ││
│                                                              │ counted once     ││
│  * Co-developed titles are credited in full to every studio │ (blank for a     ││
│    that worked on them — bars will not sum to the total →  │  studio lead —   ││
│    (see note)                                                │  see note below) ││
│                                                              └──────────────────┘│
├────────────────────────────────────────────────────────────────────────────────┤
│ ④ MONTHLY — FINANCE vs TREASURY (FY2026, Oct 2025 → Sep 2026)    [FY only]     │
│    ── Net Revenue (Finance · order date)                                       │
│    ── Cash Settled (Treasury · settlement date)                                │
│    ·· Refunds (Treasury) (Treasury · refund date)                              │
│    [line/column chart, one month per x-axis tick, Oct → Sep]                   │
├────────────────────────────────────────────────────────────────────────────────┤
│ ⑤ TITLE SHARE WITHIN STUDIO — FY2026  [FY only] │ ⑥ Paying players: 12,498      │
│  Twin Hearth  [■■■■74%■■■■][■■26%■■]             │  Rev per paying player: $25.27│
│  (one 100%-stacked bar per visible studio;       │  (12,807 transacted — 309     │
│   RLS narrows this to one bar for a lead)        │   fully refunded, excluded)   │
│                                                  │  [FY + Quarter]               │
├────────────────────────────────────────────────────────────────────────────────┤
│ A closed quarter can still move: refunds post against the ORIGINAL order date, │
│ so a refund processed today can revise a quarter already reported last month.  │
└────────────────────────────────────────────────────────────────────────────────┘
```

## The period control

Two slicers in the header: **Fiscal Year** and **Fiscal Quarter**. Both act on `dim_date`, and the
split of responsibility is enforced with **visual interactions**, not with separate measures:

| Visual | Fiscal Year | Fiscal Quarter |
|---|---|---|
| ① headline net revenue + YoY | applies | applies |
| ② net revenue by title vs prior year | applies | applies |
| ③ studio credited revenue | applies | **interaction off** |
| ④ monthly Finance vs Treasury | applies | **interaction off** |
| ⑤ title share within studio | applies | **interaction off** |
| ⑥ paying players, revenue per player | applies | applies |

Fiscal Quarter's interaction is switched off for ③, ④ and ⑤ so those three always show the **full
selected fiscal year**. That is what the brief actually asks for — Q4 is "net revenue by studio for
FY2026," Q7 is "each of its titles as a share of that studio's FY2026 revenue," and a monthly trend
needs the whole year to be a trend at all. Doing it with interaction settings rather than by writing
year-scoped variants of the measures means ③④⑤ use the *same* `Net Revenue` measure as everything
else; there is no second definition of net revenue anywhere in the model that could drift from the
first.

Selecting a different Fiscal Year moves the whole page together, including ③④⑤. Selecting a different
Fiscal Quarter moves only the quarter-grain visuals, leaving the annual context beneath them steady —
which is the reading order the page is built for: here is the quarter, and here is the year it sits in.

There is no studio slicer anywhere on the page. Studio scope is never a control a person can touch —
see below.

## How a studio lead sees only their studio: RLS

**Security table.** A new table, `sec_user_studio` (`user_principal_name`, `studio_id`), one row per
studio lead. It is **disconnected** — no relationships to anything. It exists only to be read by the
role's filter expression and by `Company Net Revenue (Page-Safe)`.

**Two roles:**
- **Studio Lead** (dynamic): a row filter on `dim_studio`:

  ```dax
  dim_studio[studio_id]
      IN CALCULATETABLE (
          VALUES ( sec_user_studio[studio_id] ),
          sec_user_studio[user_principal_name] = USERPRINCIPALNAME ()
      )
  ```

  Because `sec_user_studio` is disconnected, the mapping is looked up explicitly inside the filter
  expression rather than relying on a relationship to carry it — which also means the security table
  can never accidentally filter a fact table through some other path.
- **Unrestricted** (no filter): assigned to the Head of Publishing Operations and the CFO. They see all
  four studios and the true company figure, and have no row in `sec_user_studio`.

**The relationship setting that actually makes this work.** Restricting `dim_studio` is not enough on
its own. The restriction has to reach `dim_title` (and through it, the facts) across the bridge — and
**a bidirectional cross-filter does not propagate row-level security by itself.** Cross-filter direction
governs ordinary query filtering; RLS propagation across a relationship is a separate setting. So
`dim_title ↔ bridge_title_studio` needs **both**:

- cross-filter direction: **Both** (so studio selections filter titles in ordinary queries), and
- **"Apply security filter in both directions": enabled** (so the RLS restriction on `dim_studio`
  travels the same path).

Without that second setting, a studio lead's role would restrict `dim_studio` — the studio bar chart
would correctly show one bar — while `dim_title` stayed unfiltered, so **every title's revenue would
remain visible to every lead** in visuals ②, ④ and ⑤. That is a silent, confidentiality-breaking leak:
nothing errors, the page just quietly shows a lead the whole company's titles. It is the single most
safety-critical setting in this model, which is why it is recorded in the `MODEL.md` relationship table
as part of the relationship definition rather than left as deployment trivia.

One related note, since it motivated the model's shape: `CROSSFILTER` inside a measure is *also* no
substitute here, and for the same underlying reason — it modifies filter propagation for that one
measure's evaluation, not the security filter. A studio-to-title path that existed only as per-measure
`CROSSFILTER` would leak in exactly the same way.

### The company-figure trap under RLS

`REMOVEFILTERS`/`ALL` clear ordinary report and visual filters — **they do not clear row-level
security.** `Company Net Revenue` strips every studio/bridge/title filter with `ALL()`, which is
correct for the Head/CFO's unrestricted view. But evaluate that same measure under the Studio Lead
role, and `ALL(dim_studio)` still only sees the one studio row RLS allows through — so the "company"
tile would silently render that lead's own studio total, under a label that says "company." That is
the exact kind of "two numbers on the same slide" confusion the brief exists to end, made worse by RLS
hiding the cause.

**Decision: blank it, don't relabel it.** A dynamically relabelled tile ("Your studio" instead of
"Company total") is easy to skim past in a 40-second read — the number is still there, still looks like
a KPI, and someone glancing at the slide reads the big number without registering the small caption
that changed its meaning. Blanking the tile forces a "why is this empty?" moment instead, which is the
safer failure: nobody mistakes a blank tile for a real number.

```dax
Company Net Revenue (Page-Safe) =
VAR IsStudioLead =
    NOT ISEMPTY ( FILTER ( sec_user_studio, sec_user_studio[user_principal_name] = USERPRINCIPALNAME () ) )
RETURN
    IF ( IsStudioLead, BLANK (), [Company Net Revenue] )
```

It asks the mapping table directly — does the current user have a row in `sec_user_studio`? — rather
than inferring restriction by counting how many studios are still visible. That avoids hardcoding the
current studio count (a literal `4` would silently start lying the day a fifth studio is onboarded) and
states the actual condition: this viewer is a studio lead, so the company figure is not theirs to read.
This is the measure bound to the company tile in ③; every other tile uses the ordinary measures from
`MEASURES.dax`; and it is the only measure on the page that exists because of RLS rather than because
of the brief's seven questions.

## The closed-quarter note

Refunds recognise on the **original order date** (Finance basis) — so a refund processed in, say,
August against a March order restates FY2026 Q2's net revenue after that quarter has already been
reported and the room has moved on. This is stated as a standing footer line on the page, not tucked
into a tooltip, because it's the single fact most likely to cause a "wait, didn't we already report
this number?" moment, and that moment is cheaper to prevent with one sentence than to explain live in
the meeting.

## What's on the page, and what isn't

Cut, and what would bring each one back:

| Cut | Would bring it back |
|---|---|
| **Storefront (platform) breakdown** | Leadership starts asking store-specific questions (a fee renegotiation, a platform outage) — right now no question in the brief is "how's Steam doing." |
| **Player/cohort views** (signup cohort, LTV curves) | The meeting's purpose shifts from a revenue review to a growth-marketing review — a genuinely different audience and question set, not a deeper cut of this one. |
| **Daily trend** | Someone needs to explain one specific anomalous day (a launch spike, an outage) — that's drill-through/investigation detail, not monthly-review detail, and daily noise would crowd out the monthly signal in ④. |
| **Settlement lag by store** | Treasury cash-flow forecasting becomes a standing agenda item for this same meeting — right now that's a Treasury planning question, a different cadence and audience than this page serves. |
| **Orders count** | Leadership wants to separate "more revenue from more purchases" from "more revenue from bigger/fewer purchases" — until asked, an orders count sitting next to net revenue with no per-player context is exactly the kind of number this whole exercise exists to stop people from misreading. |

Nothing above is missing by oversight — each one is a real, legitimate question this model could
answer today if asked; none of them are the question this specific page, for this specific 40-second
read, is built to answer.
