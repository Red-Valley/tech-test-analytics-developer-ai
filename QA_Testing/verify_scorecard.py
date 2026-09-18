#!/usr/bin/env python3
"""
verify_scorecard.py — composition-mirroring harness for the Twin Hearth model.

Each function below mirrors ONE measure in MEASURES.dax, and mirrors the way the
DAX composes: derived measures call the base functions, they never re-aggregate a
fact table. So if a number here disagrees with the DAX, the disagreement is a
composition bug rather than an artefact of hand-written SQL that happened to be
shaped differently.

Usage:  python3 verify_scorecard.py [path/to/warehouse.db]
"""

import sqlite3
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else "data/warehouse.db"
con = sqlite3.connect(DB)

FY2026    = ("2025-10-01", "2026-09-30")
FY2026_Q2 = ("2026-01-01", "2026-03-31")
FY2025_Q2 = ("2025-01-01", "2025-03-31")
DEC_2025  = ("2025-12-01", "2025-12-31")


def _scalar(sql, params):
    v = con.execute(sql, params).fetchone()[0]
    return 0.0 if v is None else v


def _dim_filters(alias, title, studio):
    """Mirrors filter propagation: title directly, studio through the bridge."""
    sql, params = "", []
    if title:
        sql += f" AND {alias}.title_id = ?"
        params.append(title)
    if studio:
        sql += (f" AND {alias}.title_id IN "
                "(SELECT title_id FROM bridge_title_studio WHERE studio_id = ?)")
        params.append(studio)
    return sql, params


# ----------------------------------------------------------------- base -----

def gross_revenue(period, date_col="order_date", title=None, studio=None):
    """[Gross Revenue]. order_status deliberately unfiltered."""
    f, fp = _dim_filters("o", title, studio)
    return _scalar(
        f"SELECT SUM(o.net_usd) FROM fact_order o "
        f"WHERE o.{date_col} BETWEEN ? AND ?{f}",
        [*period, *fp])


def refunds(period, date_col="order_date", title=None, studio=None):
    """[Refunds]."""
    f, fp = _dim_filters("r", title, studio)
    return _scalar(
        f"SELECT SUM(r.net_refund_usd) FROM fact_refund r "
        f"WHERE r.{date_col} BETWEEN ? AND ?{f}",
        [*period, *fp])


def net_revenue(period, title=None, studio=None):
    """[Net Revenue] = [Gross Revenue] - [Refunds], both on the order date."""
    return (gross_revenue(period, "order_date", title, studio)
            - refunds(period, "order_date", title, studio))


# ------------------------------------------------------- cash date roles -----

def revenue_settled(period):
    """[Revenue Settled] — same base, settlement_date role."""
    return gross_revenue(period, date_col="settlement_date")


def refunds_paid(period):
    """[Refunds Paid] — same base, refund_date role."""
    return refunds(period, date_col="refund_date")


def net_cash_settled(period):
    """[Net Cash Settled]."""
    return revenue_settled(period) - refunds_paid(period)


# --------------------------------------------------------------- studio -----

def studios():
    return [r[0] for r in con.execute(
        "SELECT studio_id FROM dim_studio ORDER BY studio_id")]


def studio_credited_net_revenue(period):
    """[Studio Credited Net Revenue] — SUMX over studios, co-dev counted twice."""
    return sum(net_revenue(period, studio=s) for s in studios())


def codev_overlap(period):
    """[Co-dev Overlap]."""
    return studio_credited_net_revenue(period) - net_revenue(period)


# -------------------------------------------------------------- players -----

def paying_players(period, title=None, studio=None):
    """[Paying Players] — distinct players with an order in the period."""
    f, fp = _dim_filters("o", title, studio)
    return _scalar(
        "SELECT COUNT(DISTINCT o.player_id) FROM fact_order o "
        f"WHERE o.order_date BETWEEN ? AND ?{f}",
        [*period, *fp])


def revenue_per_paying_player(period):
    """[Revenue per Paying Player]."""
    n = paying_players(period)
    return net_revenue(period) / n if n else 0.0


# ------------------------------------------------------- growth & share -----

def net_revenue_growth_pct(current, prior):
    """[Net Revenue Growth %]."""
    py = net_revenue(prior)
    return (net_revenue(current) - py) / py if py else 0.0


def pct_of_studio(period, title, studio):
    """[% of Studio Net Revenue]."""
    denom = net_revenue(period, studio=studio)
    return net_revenue(period, title=title) / denom if denom else 0.0


# ----------------------------------------------------------- assertions -----

def sanity_checks():
    print("SANITY CHECKS")
    full = _scalar("SELECT SUM(o.net_usd) FROM fact_order o "
                   "WHERE o.order_status = 'refunded'", [])
    rev = _scalar("SELECT SUM(r.net_refund_usd) FROM fact_refund r "
                  "JOIN fact_order o USING(order_id) "
                  "WHERE o.order_status = 'refunded'", [])
    print(f"  'refunded' orders net_usd .......... {full:>14,.2f}")
    print(f"  refunds booked against them ....... {rev:>14,.2f}")
    print(f"  full reversal holds ............... {abs(full - rev) < 0.01}")

    titles = [r[0] for r in con.execute("SELECT title_id FROM dim_title")]
    by_title = sum(net_revenue(FY2026_Q2, title=t) for t in titles)
    print(f"  Q1 title rows sum ................. {by_title:>14,.2f}")
    print(f"  Q1 company total .................. "
          f"{net_revenue(FY2026_Q2):>14,.2f}")
    print(f"  titles reconcile to company ....... "
          f"{abs(by_title - net_revenue(FY2026_Q2)) < 0.01}")
    print()


# ------------------------------------------------------------ scorecard -----

def main():
    sanity_checks()

    print("1. NET REVENUE BY TITLE — FY2026 Q2")
    for tid, name in con.execute(
            "SELECT title_id, title_name FROM dim_title ORDER BY title_id"):
        print(f"  {name:<28} {net_revenue(FY2026_Q2, title=tid):>14,.2f}")
    print(f"  {'Company total':<28} {net_revenue(FY2026_Q2):>14,.2f}\n")

    print("2. CASH SETTLED IN DECEMBER 2025")
    print(f"  {'Revenue Settled (inflows)':<28} "
          f"{revenue_settled(DEC_2025):>14,.2f}")
    print(f"  {'Net Cash Settled (alt)':<28} "
          f"{net_cash_settled(DEC_2025):>14,.2f}\n")

    print("3. REFUNDS IN DECEMBER 2025 — TREASURY BASIS")
    print(f"  {'Refunds Paid':<28} {refunds_paid(DEC_2025):>14,.2f}\n")

    print("4. STUDIOS — FY2026")
    for sid, name in con.execute(
            "SELECT studio_id, studio_name FROM dim_studio ORDER BY studio_id"):
        print(f"  {name:<28} {net_revenue(FY2026, studio=sid):>14,.2f}")
    print(f"  {'Sum of the four rows':<28} "
          f"{studio_credited_net_revenue(FY2026):>14,.2f}")
    print(f"  {'Company net revenue':<28} {net_revenue(FY2026):>14,.2f}")
    print(f"  {'Co-dev Overlap':<28} {codev_overlap(FY2026):>14,.2f}\n")

    print("5. PAYING PLAYERS — FY2026 Q2")
    print(f"  {'Paying Players':<28} {paying_players(FY2026_Q2):>14,}")
    print(f"  {'Revenue per Paying Player':<28} "
          f"{revenue_per_paying_player(FY2026_Q2):>14,.2f}\n")

    print("6. GROWTH — FY2026 Q2 vs FY2025 Q2")
    print(f"  {'FY2025 Q2 net revenue':<28} {net_revenue(FY2025_Q2):>14,.2f}")
    print(f"  {'FY2026 Q2 net revenue':<28} {net_revenue(FY2026_Q2):>14,.2f}")
    print(f"  {'Growth %':<28} "
          f"{net_revenue_growth_pct(FY2026_Q2, FY2025_Q2) * 100:>13,.2f}%\n")

    print("7. TWIN HEARTH STUDIOS — FY2026 BY TITLE")
    for tid, name in con.execute(
            "SELECT t.title_id, t.title_name FROM dim_title t "
            "JOIN bridge_title_studio b USING(title_id) "
            "WHERE b.studio_id = 'STU-01' ORDER BY t.title_id"):
        print(f"  {name:<28} {net_revenue(FY2026, title=tid):>14,.2f}"
              f"  {pct_of_studio(FY2026, tid, 'STU-01') * 100:>7,.2f}%")
    print(f"  {'Studio total':<28} "
          f"{net_revenue(FY2026, studio='STU-01'):>14,.2f}")


if __name__ == "__main__":
    main()
