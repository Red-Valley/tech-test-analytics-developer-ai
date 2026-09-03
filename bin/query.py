#!/usr/bin/env python3
"""Tiny convenience wrapper so you can poke at the warehouse without installing anything.

    python3 bin/query.py "SELECT COUNT(*) FROM fact_order"
    python3 bin/query.py --tables
"""
import os, sqlite3, sys

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "warehouse.db")

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    con = sqlite3.connect(DB)
    if sys.argv[1] == "--tables":
        for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            cols = [c[1] for c in con.execute(f"PRAGMA table_info({t})")]
            n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"{t}  ({n:,} rows)\n    {', '.join(cols)}")
        return
    cur = con.execute(sys.argv[1])
    if cur.description:
        print(" | ".join(c[0] for c in cur.description))
        for row in cur.fetchall():
            print(" | ".join(str(v) for v in row))

if __name__ == "__main__":
    main()
