"""Lesson 05 — what an index actually does, and what it costs.

    python indexes.py plan      # why one query reads the whole table
    python indexes.py index     # the same query after CREATE INDEX
    python indexes.py composite # the order of the columns matters
    python indexes.py cost      # indexes make writes slower
    python indexes.py unused    # an index nobody queries is pure overhead
    python indexes.py build     # what CREATE INDEX costs, and why it is not linear
    python indexes.py all

Every number printed here was measured on the machine that ran this file.
Timings are printed as well as row counts, because the row count is the
part you can reason about and the timing is the part that varies.
"""

import os
import sqlite3
import sys
import time

DB = "indexes.db"
ROWS = 50_000
AUTHORS_COUNT = 5_000
REPEAT = 50

SCHEMA = """
CREATE TABLE notes (
    id      INTEGER PRIMARY KEY,
    title   TEXT NOT NULL,
    body    TEXT NOT NULL,
    author  TEXT NOT NULL,
    tag     TEXT NOT NULL
)
"""

# Enough authors that one author is a handful of rows, not a quarter of the
# table. When a filter matches a large share of the rows, SQLite reads the
# table once instead, and that is the correct choice, not a failure.
AUTHORS = [f"user{number:04d}" for number in range(AUTHORS_COUNT)]
TAGS = ["python", "http", "sql", "git", "docker", "log", "auth", "test"]


def seed() -> sqlite3.Connection:
    """Build a table big enough that scanning it is visibly slow."""
    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.executescript(SCHEMA)
    rows = (
        (
            number,
            f"note {number}",
            f"body of note {number}, padded so rows are not suspiciously small",
            AUTHORS[number % len(AUTHORS)],
            TAGS[number % len(TAGS)],
        )
        for number in range(ROWS)
    )
    connection.executemany("INSERT INTO notes VALUES (?, ?, ?, ?, ?)", rows)
    connection.commit()
    connection.execute("ANALYZE")
    connection.commit()
    connection.close()
    return sqlite3.connect(DB)


def plan_of(connection: sqlite3.Connection, sql: str, params: tuple = ()) -> str:
    rows = connection.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " | ".join(row[3] for row in rows)


def timed(connection: sqlite3.Connection, sql: str, params: tuple = ()) -> float:
    """Run the query REPEAT times and report the total.

    A single indexed lookup finishes inside the timer's resolution, which
    prints as 0.0 ms and tells the reader nothing. Repeating makes both
    numbers large enough to compare.
    """
    start = time.perf_counter()
    for _ in range(REPEAT):
        connection.execute(sql, params).fetchall()
    return (time.perf_counter() - start) * 1000


def report(connection: sqlite3.Connection, label: str, sql: str, params: tuple) -> None:
    plan = plan_of(connection, sql, params)
    rows = len(connection.execute(sql, params).fetchall())
    elapsed = timed(connection, sql, params)
    print(f"  {label}")
    print(f"    plan : {plan}")
    print(f"    rows : {rows}")
    print(f"    time : {elapsed:.0f} ms for {REPEAT} runs")


def run_plan() -> None:
    print(f"1. One author out of {ROWS} rows, no index")
    connection = seed()
    sql = "SELECT title FROM notes WHERE author = ?"
    report(connection, "author = 'user0042'", sql, ("user0042",))
    report(
        connection,
        "author = 'user0042' AND tag = 'sql'",
        sql + " AND tag = ?",
        ("user0042", "sql"),
    )
    print(f"   for contrast, a filter that matches {len(TAGS)} values out of {ROWS} rows:")
    report(connection, "tag = 'sql'", "SELECT title FROM notes WHERE tag = ?", ("sql",))
    connection.close()


def run_index() -> None:
    print("2. The same query, after CREATE INDEX")
    connection = seed()
    connection.execute("CREATE INDEX idx_notes_author ON notes (author)")
    connection.execute("ANALYZE")
    sql = "SELECT title FROM notes WHERE author = ?"
    report(connection, "author = 'user0042'", sql, ("user0042",))
    print("   the primary key was already an index — that is why id was never slow:")
    report(
        connection,
        "id = 42000",
        "SELECT title FROM notes WHERE id = ?",
        (42000,),
    )
    connection.close()


def run_composite() -> None:
    print("3. Reading the plan line: it says exactly what happened")
    connection = seed()
    connection.execute("CREATE INDEX idx_tag_author ON notes (tag, author)")
    connection.execute("ANALYZE")
    both = "SELECT title FROM notes WHERE author = ? AND tag = ?"

    print("   both columns named, both usable:")
    report(connection, "WHERE author = ? AND tag = ?", both, ("user0042", "sql"))

    print("   same query, conditions written in the other order — no difference:")
    report(
        connection,
        "WHERE tag = ? AND author = ?",
        "SELECT title FROM notes WHERE tag = ? AND author = ?",
        ("sql", "user0042"),
    )

    print("   only the right-hand column named — SQLite still uses the index:")
    report(
        connection,
        "WHERE author = ?",
        "SELECT title FROM notes WHERE author = ?",
        ("user0042",),
    )

    print("   add the selected column to the index and the plan says COVERING:")
    connection.execute("CREATE INDEX idx_cover ON notes (author, tag, title)")
    connection.execute("ANALYZE")
    report(
        connection,
        "SELECT title WHERE author = ? AND tag = ?",
        both,
        ("user0042", "sql"),
    )

    print("   a pattern match on the front of a string is not the same as = :")
    report(
        connection,
        "WHERE author LIKE 'user0042%'",
        "SELECT title FROM notes WHERE author LIKE ?",
        ("user0042%",),
    )
    connection.close()


def run_cost() -> None:
    print("4. What an index costs the writer")
    connection = seed()
    sql = "INSERT INTO notes VALUES (?, ?, ?, ?, ?)"
    payload = (999_999, "later note", "padded body", "user0042", "python")

    def insert_batch(start_id: int) -> float:
        start = time.perf_counter()
        for offset in range(2000):
            connection.execute(sql, (start_id + offset,) + payload[1:])
        connection.commit()
        return (time.perf_counter() - start) * 1000

    # Three rounds, median reported: a single timing on this machine varies by
    # more than the effect being measured.
    without = sorted(insert_batch(200_000 + n * 10_000) for n in range(3))[1]
    connection.execute("CREATE INDEX idx_notes_author ON notes (author)")
    connection.execute("CREATE INDEX idx_notes_tag ON notes (tag)")
    with_index = sorted(insert_batch(400_000 + n * 10_000) for n in range(3))[1]

    print(f"    2000 inserts, no index   : {without:.0f} ms")
    print(f"    2000 inserts, 2 indexes : {with_index:.0f} ms")
    print(f"    the writer got {with_index / without:.1f}x slower")
    print("    (median of 3 runs, one transaction, your numbers will differ)")
    connection.close()


def run_unused() -> None:
    print("5. An index nobody queries")
    connection = seed()
    before = os.path.getsize(DB)
    connection.execute("CREATE INDEX idx_notes_body ON notes (body)")
    connection.execute("ANALYZE")
    connection.commit()
    after = os.path.getsize(DB)

    print(f"    file, before the index : {before / 1024 / 1024:.1f} MB")
    print(f"    file, after it         : {after / 1024 / 1024:.1f} MB")
    print("    indexes on notes now:")
    for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'notes'"
    ):
        print(f"      {row[0]}")
    print("    the one indexed column is body, and nothing here filters on it:")
    report(
        connection,
        "WHERE author = ?",
        "SELECT title FROM notes WHERE author = ?",
        ("user0042",),
    )
    print("    dropping it and compacting the file gives the space back:")
    connection.execute("DROP INDEX idx_notes_body")
    connection.execute("VACUUM")
    print(f"    file, after DROP INDEX + VACUUM : {os.path.getsize(DB) / 1024 / 1024:.1f} MB")
    connection.close()


def run_build() -> None:
    """What CREATE INDEX costs, measured against ADD COLUMN at three sizes.

    Section 09.4 of the lesson claims that building an index rewrites the
    table while adding a column does not. This mode is where that claim's
    numbers come from.
    """
    print("6. What it costs to BUILD the index, at three table sizes")
    print(f"    {'rows':>9}  {'CREATE INDEX':>14}  {'ADD COLUMN':>11}  {'per row':>9}  {'db size':>9}")
    for rows in (50_000, 200_000, 800_000):
        path = f"build_{rows}.db"
        if os.path.exists(path):
            os.remove(path)
        connection = sqlite3.connect(path)
        connection.executescript(SCHEMA)
        connection.executemany(
            "INSERT INTO notes VALUES (?, ?, ?, ?, ?)",
            (
                (
                    number,
                    f"note {number}",
                    f"body of note {number}, padded so rows are not suspiciously small",
                    AUTHORS[number % len(AUTHORS)],
                    TAGS[number % len(TAGS)],
                )
                for number in range(rows)
            ),
        )
        connection.commit()
        connection.execute("ANALYZE")
        connection.commit()

        # Median of 3: DROP INDEX is cheap, so the rows are only paid for once.
        # One untimed build first, so the first timed run is not paying for a
        # cold cache on a file that was written seconds ago.
        connection.execute("CREATE INDEX idx_build_author ON notes (author)")
        connection.commit()
        connection.execute("DROP INDEX idx_build_author")
        connection.commit()

        builds = []
        for _ in range(3):
            start = time.perf_counter()
            connection.execute("CREATE INDEX idx_build_author ON notes (author)")
            connection.commit()
            builds.append((time.perf_counter() - start) * 1000)
            connection.execute("DROP INDEX idx_build_author")
            connection.commit()
        build = sorted(builds)[1]

        start = time.perf_counter()
        connection.execute("ALTER TABLE notes ADD COLUMN build_probe TEXT")
        connection.commit()
        add = (time.perf_counter() - start) * 1000

        size_mb = connection.execute("PRAGMA page_count").fetchone()[0] * 4096 / 1048576
        print(
            f"    {rows:>9,}  {build:>11.0f} ms  {add:>8.1f} ms"
            f"  {build / rows * 1000:>6.2f} us  {size_mb:>6.1f} MB"
        )
        connection.close()
        os.remove(path)

    print()
    print("    Read the ratio, not the absolute numbers. ADD COLUMN stays")
    print("    under a millisecond at every size because it only rewrites the")
    print("    schema. CREATE INDEX grows with the rows, because it has to")
    print("    read all of them and sort them.")
    print("    The per row column is here so you can see it is not constant,")
    print("    but the run-to-run spread is as wide as the trend, so do not")
    print("    read a law into it.")
    print("    (median of 3 after one warm-up build, one machine)")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "plan": run_plan,
        "index": run_index,
        "composite": run_composite,
        "cost": run_cost,
        "unused": run_unused,
        "build": run_build,
    }
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