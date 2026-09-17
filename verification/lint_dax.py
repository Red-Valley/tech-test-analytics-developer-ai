#!/usr/bin/env python3
"""Structural linter for MEASURES.dax.

This does NOT compile DAX — nothing in this repo can. It is a static audit that catches the
class of defect that slipped through verify_scorecard.py: a measure whose mirrored SQL returns
the right number while the DAX itself could never run (a measure returning a table, a measure
reference used as a CALCULATE filter, a reference to a column that does not exist).

Checks, per measure:
  1. Balanced parentheses, brackets and double quotes.
  2. Every [Measure] reference resolves to a measure defined in this file.
  3. Every table[column] reference exists in data/warehouse.db (plus a declared allow-list of
     model-only tables that exist in the semantic model but not in the warehouse).
  4. Every function called appears in the valid-DAX-function list below.
  5. The outermost function does not return a table (that would be a compile error in a measure).
  6. No measure reference is passed as a CALCULATE filter argument (also a compile error).
  7. VAR declared but never used; VAR used without a RETURN.
  8. Bonus: enum arguments (DATEADD interval, CROSSFILTER direction) are valid members.

    python verification/lint_dax.py
"""
import os
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
# Optional path argument so the linter can be pointed at a fixture to prove it catches known-bad
# DAX (see the self-test note at the bottom of AI_WORKFLOW_LOG.md); defaults to the real file.
DAX_FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "MEASURES.dax")
DB = os.path.join(REPO_ROOT, "data", "warehouse.db")

# Tables that exist in the semantic model but not in the warehouse. sec_user_studio is the
# disconnected RLS mapping table introduced in DASHBOARD.md; it is created in the model, so a
# reference to it is correct DAX even though data/warehouse.db knows nothing about it.
MODEL_ONLY_TABLES = {
    "sec_user_studio": {"user_principal_name", "studio_id"},
}

# Functions that return a TABLE. A measure must return a scalar, so any of these appearing as the
# outermost function of a measure expression is a compile error.
TABLE_FUNCTIONS = {
    "FILTER", "VALUES", "ALL", "ALLEXCEPT", "ALLSELECTED", "ALLNOBLANKROW", "SUMMARIZE",
    "SUMMARIZECOLUMNS", "INTERSECT", "EXCEPT", "UNION", "ADDCOLUMNS", "SELECTCOLUMNS",
    "DISTINCT", "TOPN", "CALCULATETABLE", "CROSSJOIN", "GENERATE", "GENERATEALL", "ROW",
    "DATATABLE", "NATURALINNERJOIN", "NATURALLEFTOUTERJOIN", "TREATAS", "GROUPBY",
    "DATESBETWEEN", "DATESINPERIOD", "DATEADD", "SAMEPERIODLASTYEAR", "PARALLELPERIOD",
    "PREVIOUSMONTH", "PREVIOUSQUARTER", "PREVIOUSYEAR", "NEXTMONTH", "NEXTQUARTER",
    "NEXTYEAR", "DATESMTD", "DATESQTD", "DATESYTD", "RELATEDTABLE", "CURRENTGROUP",
}

# Functions whose first argument is a table (used to validate bare table-name references).
TABLE_FIRST_ARG_FUNCTIONS = {
    "FILTER", "ALL", "ALLEXCEPT", "ALLSELECTED", "ALLNOBLANKROW", "ISEMPTY", "COUNTROWS",
    "SUMX", "AVERAGEX", "MINX", "MAXX", "COUNTX", "CONCATENATEX", "RANKX", "ADDCOLUMNS",
    "SELECTCOLUMNS", "SUMMARIZE", "TOPN", "DISTINCT", "GROUPBY",
}

VALID_DAX_FUNCTIONS = {
    # aggregation
    "SUM", "SUMX", "AVERAGE", "AVERAGEX", "MIN", "MINX", "MAX", "MAXX", "COUNT", "COUNTX",
    "COUNTA", "COUNTAX", "COUNTROWS", "COUNTBLANK", "DISTINCTCOUNT", "DISTINCTCOUNTNOBLANK",
    "PRODUCT", "PRODUCTX", "MEDIAN", "MEDIANX", "PERCENTILE.INC", "PERCENTILE.EXC",
    # filter / context
    "CALCULATE", "CALCULATETABLE", "FILTER", "ALL", "ALLEXCEPT", "ALLSELECTED", "ALLNOBLANKROW",
    "REMOVEFILTERS", "KEEPFILTERS", "VALUES", "DISTINCT", "EARLIER", "EARLIEST", "RELATED",
    "RELATEDTABLE", "USERELATIONSHIP", "CROSSFILTER", "TREATAS", "SELECTEDVALUE", "HASONEVALUE",
    "ISFILTERED", "ISCROSSFILTERED", "ISINSCOPE", "SELECTEDMEASURE",
    # table
    "SUMMARIZE", "SUMMARIZECOLUMNS", "ADDCOLUMNS", "SELECTCOLUMNS", "TOPN", "UNION", "INTERSECT",
    "EXCEPT", "CROSSJOIN", "GENERATE", "GENERATEALL", "ROW", "DATATABLE", "GROUPBY", "NATURALINNERJOIN",
    "NATURALLEFTOUTERJOIN", "CURRENTGROUP", "ISEMPTY",
    # logical
    "IF", "IFERROR", "SWITCH", "AND", "OR", "NOT", "TRUE", "FALSE", "COALESCE", "ISBLANK",
    "ISERROR", "ISNUMBER", "ISTEXT", "ISNONTEXT", "ISLOGICAL", "ISEVEN", "ISODD", "IN",
    # math
    "DIVIDE", "ROUND", "ROUNDUP", "ROUNDDOWN", "INT", "TRUNC", "ABS", "CEILING", "FLOOR",
    "MROUND", "POWER", "SQRT", "EXP", "LN", "LOG", "LOG10", "SIGN", "MOD", "QUOTIENT", "RAND",
    "FIXED", "CONVERT", "CURRENCY", "BLANK",
    # time intelligence
    "DATEADD", "DATESBETWEEN", "DATESINPERIOD", "DATESMTD", "DATESQTD", "DATESYTD",
    "SAMEPERIODLASTYEAR", "PARALLELPERIOD", "PREVIOUSDAY", "PREVIOUSMONTH", "PREVIOUSQUARTER",
    "PREVIOUSYEAR", "NEXTDAY", "NEXTMONTH", "NEXTQUARTER", "NEXTYEAR", "FIRSTDATE", "LASTDATE",
    "FIRSTNONBLANK", "LASTNONBLANK", "STARTOFMONTH", "STARTOFQUARTER", "STARTOFYEAR",
    "ENDOFMONTH", "ENDOFQUARTER", "ENDOFYEAR", "TOTALMTD", "TOTALQTD", "TOTALYTD",
    "CLOSINGBALANCEMONTH", "OPENINGBALANCEMONTH",
    # date/time
    "DATE", "DATEVALUE", "DAY", "MONTH", "YEAR", "HOUR", "MINUTE", "SECOND", "NOW", "TODAY",
    "EOMONTH", "EDATE", "WEEKDAY", "WEEKNUM", "CALENDAR", "CALENDARAUTO", "DATEDIFF",
    # text
    "CONCATENATE", "CONCATENATEX", "FORMAT", "LEFT", "RIGHT", "MID", "LEN", "LOWER", "UPPER",
    "TRIM", "SUBSTITUTE", "REPLACE", "SEARCH", "FIND", "REPT", "UNICHAR", "VALUE", "EXACT",
    # info / security
    "USERNAME", "USERPRINCIPALNAME", "USEROBJECTID", "CUSTOMDATA", "LOOKUPVALUE", "CONTAINS",
    "CONTAINSSTRING", "CONTAINSROW", "PATH", "PATHITEM", "PATHCONTAINS",
    # ranking / stats
    "RANK.EQ", "RANKX", "STDEV.P", "STDEV.S", "VAR.P", "VAR.S", "GEOMEAN", "GEOMEANX",
}

ENUM_ARGS = {
    # function -> (1-based arg position, allowed values)
    "DATEADD": (3, {"DAY", "MONTH", "QUARTER", "YEAR"}),
    "CROSSFILTER": (3, {"NONE", "ONEWAY", "BOTH", "ONEWAY_RIGHTFILTERSLEFT"}),
    "DATESINPERIOD": (4, {"DAY", "MONTH", "QUARTER", "YEAR"}),
}

DAX_KEYWORDS = {"VAR", "RETURN", "IN", "NOT", "AND", "OR", "TRUE", "FALSE", "BLANK",
                "DAY", "MONTH", "QUARTER", "YEAR", "NONE", "ONEWAY", "BOTH"}


def load_schema():
    con = sqlite3.connect(DB)
    schema = {}
    for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        schema[t] = {c[1] for c in con.execute(f"PRAGMA table_info({t})")}
    con.close()
    return schema


def strip_strings(expr):
    """Replace double-quoted string literals with same-length filler so their contents
    don't confuse bracket/paren counting or identifier extraction."""
    out, in_str, i = [], False, 0
    while i < len(expr):
        ch = expr[i]
        if ch == '"':
            if in_str and i + 1 < len(expr) and expr[i + 1] == '"':  # escaped "" inside string
                out.append("__")
                i += 2
                continue
            in_str = not in_str
            out.append('"')
        else:
            out.append("_" if in_str else ch)
        i += 1
    return "".join(out), in_str


def parse_measures(text):
    """Return [(name, expression, comment)] . A measure header is a line at column 0 that ends
    with '=' and is not a comment, VAR or RETURN line."""
    measures, lines = [], text.splitlines()
    header_re = re.compile(r"^(?P<name>[^\s/][^=]*?)\s*=\s*$")
    cur_name, cur_body, cur_comment = None, [], []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        is_header = False
        if line and not line[0].isspace() and not stripped.startswith(("--", "VAR ", "RETURN")):
            m = header_re.match(line)
            if m:
                is_header = True
        if is_header:
            if cur_name is not None:
                measures.append((cur_name, "\n".join(cur_body).strip(), " ".join(cur_comment).strip()))
            cur_name = header_re.match(line).group("name").strip()
            cur_body, cur_comment = [], []
        elif cur_name is not None:
            if stripped.startswith("--"):
                cur_comment.append(stripped.lstrip("- ").strip())
            elif stripped:
                cur_body.append(line)
    if cur_name is not None:
        measures.append((cur_name, "\n".join(cur_body).strip(), " ".join(cur_comment).strip()))
    return measures


def split_top_level_args(arg_text):
    """Split a function's argument list on top-level commas."""
    args, depth, cur = [], 0, []
    for ch in arg_text:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0:
            args.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        args.append("".join(cur).strip())
    return args


def find_call_args(expr, func_name):
    """Yield the raw argument-list text of every call to func_name in expr."""
    for m in re.finditer(r"\b" + func_name + r"\s*\(", expr, re.IGNORECASE):
        start = m.end()
        depth, i = 1, start
        while i < len(expr) and depth > 0:
            if expr[i] in "([":
                depth += 1
            elif expr[i] in ")]":
                depth -= 1
            i += 1
        yield expr[start:i - 1]


def outermost_function(expr):
    """Name of the function that produces the measure's returned value."""
    body = expr
    if re.search(r"\bRETURN\b", body, re.IGNORECASE):
        body = re.split(r"\bRETURN\b", body, flags=re.IGNORECASE)[-1]
    body = body.strip()
    m = re.match(r"([A-Za-z][A-Za-z0-9_.]*)\s*\(", body)
    return m.group(1).upper() if m else None


def lint():
    text = open(DAX_FILE, encoding="utf-8").read()
    schema = load_schema()
    measures = parse_measures(text)
    defined = {name for name, _, _ in measures}
    known_tables = dict(schema)
    for t, cols in MODEL_ONLY_TABLES.items():
        known_tables[t] = cols

    findings = []  # (measure, severity, message)
    all_functions = set()

    for name, expr, comment in measures:
        clean, unterminated = strip_strings(expr)

        # 1. balance
        if unterminated:
            findings.append((name, "ERROR", 'unterminated double-quoted string'))
        for open_ch, close_ch, label in [("(", ")", "parentheses"), ("[", "]", "brackets")]:
            if clean.count(open_ch) != clean.count(close_ch):
                findings.append((name, "ERROR",
                                 f"unbalanced {label}: {clean.count(open_ch)} '{open_ch}' vs "
                                 f"{clean.count(close_ch)} '{close_ch}'"))
            depth = 0
            for ch in clean:
                if ch == open_ch:
                    depth += 1
                elif ch == close_ch:
                    depth -= 1
                    if depth < 0:
                        findings.append((name, "ERROR", f"{label} close before open"))
                        break

        # 2. measure references
        for ref in re.findall(r"(?<![A-Za-z0-9_\)\]])\[([^\]]+)\]", clean):
            if ref not in defined:
                findings.append((name, "ERROR", f"[{ref}] does not resolve to a measure in this file"))

        # 3. column references. A DAX keyword immediately before a bracket is not a table name —
        # "RETURN [Net Revenue]" is a keyword followed by a measure reference, not RETURN[...].
        for tbl, col in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\[([^\]]+)\]", clean):
            if tbl.upper() in DAX_KEYWORDS:
                continue
            if tbl not in known_tables:
                findings.append((name, "ERROR", f"unknown table '{tbl}' in {tbl}[{col}]"))
            elif col not in known_tables[tbl]:
                findings.append((name, "ERROR", f"unknown column {tbl}[{col}]"))
            elif tbl in MODEL_ONLY_TABLES:
                findings.append((name, "INFO",
                                 f"{tbl}[{col}] is a model-only table (not in warehouse.db) — "
                                 f"must be created in the model"))

        # bare table names as first argument of table-taking functions
        for fn in TABLE_FIRST_ARG_FUNCTIONS:
            for args_text in find_call_args(clean, fn):
                args = split_top_level_args(args_text)
                if args and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args[0]):
                    ident = args[0]
                    if ident.upper() in DAX_KEYWORDS:
                        continue
                    # could be a VAR name
                    var_names = {v.upper() for v in re.findall(r"\bVAR\s+([A-Za-z_][A-Za-z0-9_]*)",
                                                               clean, re.IGNORECASE)}
                    if ident.upper() in var_names:
                        continue
                    if ident not in known_tables:
                        findings.append((name, "ERROR",
                                         f"{fn}() first argument '{ident}' is not a known table"))

        # 4. functions. Blank out the contents of [...] first: measure and column names may
        # legitimately contain parentheses (e.g. [Net Revenue (Like-for-like)]), and without this
        # the extractor reads "Revenue (" inside the name as a call to a function named Revenue.
        no_refs = re.sub(r"\[[^\]]*\]", lambda m: "[" + "_" * (len(m.group(0)) - 2) + "]", clean)
        for fn in re.findall(r"\b([A-Za-z][A-Za-z0-9_.]*)\s*\(", no_refs):
            fn_up = fn.upper()
            if fn_up in DAX_KEYWORDS and fn_up not in VALID_DAX_FUNCTIONS:
                continue
            all_functions.add(fn_up)
            if fn_up not in {f.upper() for f in VALID_DAX_FUNCTIONS}:
                findings.append((name, "ERROR", f"unknown function {fn}()"))

        # 5. outermost returns a table
        outer = outermost_function(clean)
        if outer and outer in TABLE_FUNCTIONS:
            findings.append((name, "ERROR",
                             f"outermost function {outer}() returns a table — a measure must "
                             f"return a scalar"))

        # 6. measure reference as a CALCULATE filter argument
        for args_text in find_call_args(clean, "CALCULATE"):
            args = split_top_level_args(args_text)
            for arg in args[1:]:
                if re.fullmatch(r"\[[^\]]+\]", arg.strip()):
                    findings.append((name, "ERROR",
                                     f"measure reference {arg.strip()} used as a CALCULATE filter "
                                     f"argument — not allowed"))

        # 7. VAR / RETURN
        var_names = re.findall(r"\bVAR\s+([A-Za-z_][A-Za-z0-9_]*)", clean, re.IGNORECASE)
        has_return = bool(re.search(r"\bRETURN\b", clean, re.IGNORECASE))
        if var_names and not has_return:
            findings.append((name, "ERROR", "VAR declared but no RETURN"))
        for v in var_names:
            uses = len(re.findall(r"\b" + re.escape(v) + r"\b", clean))
            if uses <= 1:
                findings.append((name, "ERROR", f"VAR {v} declared but never used"))

        # 8. enum arguments
        for fn, (pos, allowed) in ENUM_ARGS.items():
            for args_text in find_call_args(clean, fn):
                args = split_top_level_args(args_text)
                if len(args) >= pos:
                    val = args[pos - 1].strip().upper()
                    if re.fullmatch(r"[A-Z_]+", val) and val not in allowed:
                        findings.append((name, "ERROR",
                                         f"{fn}() argument {pos} '{args[pos-1].strip()}' is not a "
                                         f"valid member: {sorted(allowed)}"))

    # report
    print("=" * 78)
    print(f"DAX STRUCTURAL LINT — {os.path.basename(DAX_FILE)}")
    print("=" * 78)
    print(f"Measures parsed: {len(measures)}")
    print(f"Warehouse tables: {', '.join(sorted(schema))}")
    print(f"Model-only tables declared: {', '.join(sorted(MODEL_ONLY_TABLES))}")
    print()

    by_measure = {}
    for m, sev, msg in findings:
        by_measure.setdefault(m, []).append((sev, msg))

    for name, expr, comment in measures:
        issues = by_measure.get(name, [])
        errors = [i for i in issues if i[0] == "ERROR"]
        infos = [i for i in issues if i[0] == "INFO"]
        status = "ERROR" if errors else ("INFO " if infos else "OK   ")
        outer = outermost_function(strip_strings(expr)[0]) or "(none)"
        print(f"[{status}] {name}")
        print(f"         outermost: {outer}()")
        for sev, msg in issues:
            print(f"         {sev}: {msg}")

    print()
    print("=" * 78)
    print("FUNCTIONS USED (all validated against the list in this script)")
    print("=" * 78)
    print(", ".join(sorted(all_functions)))

    print()
    print("=" * 78)
    errors = [f for f in findings if f[1] == "ERROR"]
    infos = [f for f in findings if f[1] == "INFO"]
    if errors:
        print(f"RESULT: {len(errors)} error(s), {len(infos)} info across {len(measures)} measures.")
        return 1
    print(f"RESULT: PASS — 0 errors, {len(infos)} info across {len(measures)} measures.")
    print("NOTE: this is a structural audit, not a compiler. It cannot prove the DAX is")
    print("semantically correct, only that it is structurally well-formed.")
    return 0


if __name__ == "__main__":
    sys.exit(lint())
