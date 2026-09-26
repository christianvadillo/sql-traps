"""Run every trap in traps.json against DuckDB and check that the broken query
and the fixed one give different results, in the way the page says.

    pip install duckdb
    python verify.py            # all traps
    python verify.py fanout     # one trap
"""

import json
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent


def first_statement(sql):
    # The SQL shown on each page may carry human comments after the final ";".
    return sql.split(";", 1)[0] + ";"


def norm(rows):
    def v(x):
        if x is None:
            return None
        try:
            return round(float(x), 6)
        except (TypeError, ValueError):
            return str(x)
    out = [[v(x) for x in row] for row in rows]
    out.sort(key=lambda r: json.dumps(r, default=str))
    return out


def check(trap, lang):
    c = trap["comprobar"]
    t = trap[lang]
    con = duckdb.connect(":memory:")
    con.execute(t["datos"])
    problems = []

    if c.get("mal_error"):
        try:
            con.execute(first_statement(t["mal_sql"])).fetchall()
            problems.append("broken query was expected to fail and didn't")
        except duckdb.Error:
            pass
        bad = None
    else:
        bad = con.execute(first_statement(t["mal_sql"])).fetchall()
        if "mal_filas" in c and len(bad) != c["mal_filas"]:
            problems.append(f"broken query: {len(bad)} rows, expected {c['mal_filas']}")
        if "mal" in c and norm(bad) != norm(c["mal"]):
            problems.append("broken query: unexpected result")

    runs = [("bien", t["bien_sql"])]
    if t.get("bien_sql_alt"):
        runs.append(("bien_alt", t["bien_sql_alt"]))
    for key, sql in runs:
        good = con.execute(first_statement(sql)).fetchall()
        if f"{key}_filas" in c and len(good) != c[f"{key}_filas"]:
            problems.append(f"{key}: {len(good)} rows, expected {c[key + '_filas']}")
        if key in c and norm(good) != norm(c[key]):
            problems.append(f"{key}: unexpected result")
        if bad is not None and norm(bad) == norm(good):
            problems.append(f"{key}: same result as the broken query")
    return problems


def main():
    traps = json.loads((HERE / "traps.json").read_text(encoding="utf-8"))
    wanted = set(sys.argv[1:])
    failed = 0
    for trap in traps:
        if wanted and trap["slug"] not in wanted:
            continue
        for lang in ("en", "es"):
            problems = check(trap, lang)
            status = "ok  " if not problems else "FAIL"
            print(f"{status} {trap['slug']} ({lang})" + ("" if not problems else ": " + "; ".join(problems)))
            failed += bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
