## Dashboard

+---------------------------------------------------------------+
|  Twin Hearth Studios                                          |
|  Executive Dashboard                                          |
+------------+------------+------------+------------+-----------+
| Net Revenue| Growth %   | Settled    | Revenue /  | Refunds   |
| FY26 Q2    | YoY        | Revenue    | Paying Plr | Treasury  |
| 316.70 mil | +120.70%   | 103.91 mil | 24.73      | 5.01 mil  |
+------------+------------+------------+------------+-----------+
| Net Revenue by Studio — FY26   | Net Revenue by Title — FY26Q2|
| Twin Hearth       913,971.25   | Hollow Crown      145,066.30 |
| Emberwatch        424,376.81   | Emberwatch Tactics 52,396.11 |
| Nine Lanterns     309,732.17   | Saltmarsh Rally    47,254.92 |
| Saltpine          214,765.44   | Ashen Tide         44,722.14 |
| Sum of studios  1,862,845.65   | Lantern & Lock     27,261.38 |
|                                 | Total             316,700.84 |
| Note: co-developed titles are  |                               |
| credited in full to each       |                               |
| studio; sum does not equal     |                               |
| the company Net Revenue above. |                               |
+---------------------------------+-------------------------------+

## Layout and order, and why

1. Header — company name and dashboard title, so anyone opening the
   page cold knows what they're looking at without asking.
2. Top row (5 KPI cards) — Net Revenue FY26 Q2, YoY Growth %, Settled
   Revenue (Dec 2025), Revenue per Paying Player, and Refunds Treasury
   (Dec 2025), all in one row. These are exactly the numbers the brief
   says get asked in nearly every review, so they're all visible within
   the 40-second window, with no scrolling or drilling needed.
3. Second row — studio breakdown on the left, title breakdown on the
   right. Studio is placed first (left-to-right reading order) because
   "how is each studio doing" is the recurring question the brief
   singles out as a source of confusion — its explanatory note sits
   directly underneath it, resolving the mismatch with the top KPI
   before anyone has to ask about it. Title breakdown sits alongside it
   as the natural next-level detail.

## Studio lead view
A row-level security role filters dim_studio[studio_name] by the signed-in
user (via USERNAME() mapped to a studio, or a user-to-studio mapping
table). Because dim_studio connects to titles and orders through
bridge_title_studio, the filter propagates automatically to that
studio's titles and revenue. The CFO and analyst roles see every studio
unfiltered; each of the four studio leads sees only their own row and
their own titles. (RLS implementation itself is out of scope per the
assignment — this describes the intent only.)

## What was left off, and what would bring it back
- Storefront/platform breakdown — not among the 7 questions in the
  brief; would add it if the CFO starts asking about store-specific
  fees or settlement lag by platform.
- Per-player detail — the brief asks for an average (Q5), not a
  player-level list; that belongs in a separate operational report,
  not this executive page.
- Month-over-month trend line — the brief only asks for quarter-over-
  quarter comparisons; would add a trend if leadership wants to see
  movement within a quarter rather than just the closing number.
- Refunds by title/studio — the brief's refund question (Q3) is
  company-wide only; would break it down further if a specific studio
  lead starts asking about refund rates on their own titles.