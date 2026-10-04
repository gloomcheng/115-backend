"""Lesson 06 — N+1, counted rather than described.

    python n_plus_one.py small     # the shape, with every statement shown
    python n_plus_one.py scale     # the same code at 5 rows and at 500 rows
    python n_plus_one.py indexed    # why adding an index does not fix it
    python n_plus_one.py latency    # why the local timings look harmless
    python n_plus_one.py all

set_trace_callback gives us every statement sqlite3 executes, so the query
count in the output is measured, not claimed.

The rule being demonstrated: one query for the list, then one more per row,
is a different program from one query for the list. It returns the same
rows either way.
"""

import os
import sqlite3
import sys
import time

DB = "n_plus_one.db"

SCHEMA = """
CREATE TABLE authors (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE notes (
    id       INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    title    TEXT NOT NULL
);
"""

ROWS = 500


def reset(author_count: int) -> sqlite3.Connection:
    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.executescript(SCHEMA)
    connection.executemany(
        "INSERT INTO authors VALUES (?, ?)", ((n, f"author {n}") for n in range(author_count))
    )
    connection.executemany(
        "INSERT INTO notes VALUES (?, ?, ?)",
        ((n, n % author_count, f"note {n}") for n in range(ROWS)),
    )
    connection.commit()
    return connection


def counting(connection: sqlite3.Connection) -> tuple[list[str], float]:
    """Run a function while recording every statement sqlite3 executes."""
    statements: list[str] = []
    connection.set_trace_callback(statements.append)
    start = time.perf_counter()
    connection.execute("SELECT 1").fetchone()  # warm the page cache
    result = _collector[0]()
    elapsed = (time.perf_counter() - start) * 1000
    connection.set_trace_callback(None)
    return statements, elapsed, result


def fetch_n_plus_one(connection: sqlite3.Connection, author_count: int) -> list[tuple]:
    """One query for the authors, then one query per author for their notes."""
    result = []
    authors = connection.execute("SELECT id, name FROM authors ORDER BY id").fetchall()
    for author_id, name in authors:
        notes = connection.execute(
            "SELECT title FROM notes WHERE author_id = ? ORDER BY id", (author_id,)
        ).fetchall()
        result.append((name, [row[0] for row in notes]))
    return result


def fetch_join(connection: sqlite3.Connection, author_count: int) -> list[tuple]:
    """One query. The same rows, grouped in Python afterwards."""
    rows = connection.execute(
        "SELECT a.name, n.title FROM authors a "
        "LEFT JOIN notes n ON n.author_id = a.id "
        "ORDER BY a.id, n.id"
    ).fetchall()
    result: list[tuple] = []
    for name, title in rows:
        if not result or result[-1][0] != name:
            result.append((name, []))
        result[-1][1].append(title)
    return result


def run(label: str, fetcher, author_count: int) -> None:
    connection = reset(author_count)
    global _collector
    _collector = [lambda: fetcher(connection, author_count)]
    statements, elapsed, result = counting(connection)
    # The warm-up SELECT 1 is not part of the work.
    real = [s for s in statements if "SELECT 1" not in s]
    print(f"  {label}")
    print(f"    statements: {len(real)}")
    print(f"    authors returned: {len(result)}")
    print(f"    total titles: {sum(len(titles) for _, titles in result)}")
    print(f"    time: {elapsed:.0f} ms")
    connection.close()
    _REPORTS.append((label, len(real), elapsed, result))


def run_small() -> None:
    print("1. Twenty authors, and every statement")
    connection = reset(20)
    shown: list[str] = []
    connection.set_trace_callback(lambda s: shown.append(s))
    fetch_n_plus_one(connection, 20)
    connection.set_trace_callback(None)
    for statement in shown[:6]:
        print(f"    {statement}")
    print(f"    ... and {len(shown) - 6} more")
    print(f"    total: {len(shown)} statements for 20 authors")
    connection.close()

    _REPORTS.clear()
    run("n_plus_one, 20 authors", fetch_n_plus_one, 20)
    run("join,       20 authors", fetch_join, 20)
    same = _REPORTS[0][3] == _REPORTS[1][3]
    print(f"    identical result: {same}")


def run_scale() -> None:
    print("2. The same code, at 20 authors and at 500 authors")
    _REPORTS.clear()
    for count in (20, 500):
        run(f"n_plus_one, {count} authors", fetch_n_plus_one, count)
    for count in (20, 500):
        run(f"join,       {count} authors", fetch_join, count)
    small = next(r for r in _REPORTS if r[0] == "n_plus_one, 20 authors")
    large = next(r for r in _REPORTS if r[0] == "n_plus_one, 500 authors")
    small_join = next(r for r in _REPORTS if r[0] == "join,       20 authors")
    large_join = next(r for r in _REPORTS if r[0] == "join,       500 authors")
    print()
    print(f"    20 authors:  n_plus_one {small[1]:>3} statements, join {small_join[1]}")
    print(f"    500 authors: n_plus_one {large[1]:>3} statements, join {large_join[1]}")
    print(f"    the gap grew from {small[1] - small_join[1]}x to {large[1] - large_join[1]}x")
    print()
    print("   At 20 authors the difference is small enough to miss in review.")


def run_indexed() -> None:
    print("3. Adding an index makes each query faster, and does not help")
    connection = reset(500)
    connection.execute("CREATE INDEX idx_notes_author ON notes (author_id)")
    connection.execute("ANALYZE")
    connection.commit()
    shown: list[str] = []
    connection.set_trace_callback(lambda s: shown.append(s))
    fetch_n_plus_one(connection, 500)
    connection.set_trace_callback(None)
    real = [s for s in shown if "SELECT 1" not in s]
    print(f"    with an index on notes(author_id): {len(real)} statements")
    print("    the plan for the per-author query:")
    for row in connection.execute(
        "EXPLAIN QUERY PLAN SELECT title FROM notes WHERE author_id = ?", (0,)
    ):
        print(f"      {row[3]}")
    print()
    print("   Every one of those statements is fast now. There are just 501 of them.")
    print("   An index makes a query cheap. It does not make 501 queries into one.")
    connection.close()


def run_latency() -> None:
    print("4. Why the local numbers look harmless, and where they stop being so")
    print()
    print("   Above: 501 statements cost about 10 ms, because SQLite is a file on")
    print("   this same disk. That number proves nothing about a real deployment.")
    print()
    print("   Here is the same work with a fixed cost per statement, which is what a")
    print("   network round trip to PostgreSQL or MySQL actually adds. The cost is")
    print("   simulated and labelled as such; the statement counts are real.")
    print()
    latency_ms = 1.0
    _REPORTS.clear()
    for count in (20, 500):
        run(f"n_plus_one, {count} authors", fetch_n_plus_one, count)
    for count in (20, 500):
        run(f"join,       {count} authors", fetch_join, count)
    print()
    for label, statements, elapsed, _ in _REPORTS:
        added = statements * latency_ms
        print(
            f"    {label}: {statements:>3} statements, "
            f"{elapsed:>6.0f} ms local, {added:>6.0f} ms if each cost {latency_ms:g} ms"
        )
    print()
    print("   500 statements at 1 ms each is half a second of waiting, on every")
    print("   single request, for a page that shows the same rows either way.")


_REPORTS: list = []
_collector: list = [lambda: None]


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {"small": run_small, "scale": run_scale, "indexed": run_indexed, "latency": run_latency}
    if mode == "all":
        for runner in runners.values():
            runner()
    elif mode in runners:
        runners[mode]()
    else:
        print(f"unknown mode: {mode}")
        print(f"try one of: {', '.join(runners)}")
        sys.exit(1)


if __name__ == "__main__":
    main()