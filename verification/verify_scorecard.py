#!/usr/bin/env python3
"""Runs checks.json against data/warehouse.db and reports PASS/FAIL for every scorecard cell.

There is no `.claude/skills/bi-semantic-model-builder` in this repo or user profile (checked at the
start of the exercise), so there is no pre-built `verify_scorecard.py` to reuse -- this one was written
from scratch to serve the same purpose: SCORECARD.md is filled in ONLY from a run of this script that
prints PASS across the board.

Each `value_check` runs a SQL query that mirrors the exact filter context of the DAX measure named
alongside it (same fact table, same date column for that date role, same dimension filter) and compares
the rounded-to-2dp result against the value recorded when the query was first run. Each
`assertion_check` is an internal-consistency regression test (e.g. "the two %-of-studio rows sum to
100.00", "no over-refunds once TEXT columns are cast") that would catch the class of bug found in
Session 1 (a string-vs-numeric comparison bug on SQLite's untyped columns) if it recurred.

    python verification/verify_scorecard.py
"""
import json
import os
import sqlite3
import sys

# Check descriptions contain non-ASCII (em dashes, accented studio names). On Windows the console
# defaults to cp1252 and printing them raises UnicodeEncodeError, so force UTF-8 output.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
DB = os.path.join(REPO_ROOT, "data", "warehouse.db")
CHECKS = os.path.join(HERE, "checks.json")


def run_scalar(con, sql):
    row = con.execute(sql).fetchone()
    return row[0] if row else None


def main():
    con = sqlite3.connect(DB)
    with open(CHECKS, encoding="utf-8") as f:
        checks = json.load(f)

    failures = []

    print("=" * 78)
    print("VALUE CHECKS -- one per scorecard cell")
    print("=" * 78)
    for c in checks["value_checks"]:
        raw = run_scalar(con, c["sql"])
        actual = round(raw, 2) if raw is not None else None
        expected = round(c["expected"], 2)
        ok = actual is not None and abs(actual - expected) <= 0.01
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures.append(c["id"])
        print(f"[{status}] {c['id']:32s} {c['scorecard_cell']:42s} "
              f"expected={expected:<14} actual={actual}")

    print()
    print("=" * 78)
    print("ASSERTION CHECKS -- internal consistency / regression")
    print("=" * 78)
    ops = {
        "eq_tolerance": lambda l, r, tol: abs(l - r) <= tol,
        "le": lambda l, r, tol=None: l <= r,
    }
    for a in checks["assertion_checks"]:
        left = run_scalar(con, a["sql_left"])
        right = run_scalar(con, a["sql_right"])
        tol = a.get("tolerance", 0.01)
        ok = ops[a["op"]](left, right, tol)
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures.append(a["id"])
        print(f"[{status}] {a['id']:42s} left={left} right={right}")
        print(f"       {a['description']}")

    print()
    print("=" * 78)
    if failures:
        print(f"RESULT: FAIL -- {len(failures)} check(s) failed: {', '.join(failures)}")
        con.close()
        sys.exit(1)
    else:
        print(f"RESULT: PASS -- all {len(checks['value_checks'])} value checks and "
              f"{len(checks['assertion_checks'])} assertion checks passed.")
    con.close()


if __name__ == "__main__":
    main()
