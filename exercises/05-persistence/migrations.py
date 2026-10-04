"""Lesson 05 — schema changes, and the order you do them in.

    python migrations.py runner     # what a migration runner actually does
    python migrations.py limits     # what SQLite will not let you do
    python migrations.py expand     # the order that does not lose data
    python migrations.py all

Every step prints the table contents after it runs, so the data either
survives or visibly does not. Nothing here is asserted without a row count
next to it.
"""

import os
import sqlite3
import sys

DB = "migrations.db"

STEPS = [
    ("0001", "CREATE TABLE users (name TEXT PRIMARY KEY, role TEXT)"),
    ("0002", "INSERT INTO users VALUES ('iris', 'student')"),
    ("0003", "INSERT INTO users VALUES ('root', 'admin')"),
    ("0004", "ALTER TABLE users ADD COLUMN email TEXT"),
    ("0005", "UPDATE users SET email = name || '@example.test'"),
    ("0006", "CREATE TABLE users_new (name TEXT PRIMARY KEY, role TEXT, email TEXT NOT NULL)"),
    ("0007", "INSERT INTO users_new SELECT name, role, email FROM users"),
    ("0008", "DROP TABLE users"),
    ("0009", "ALTER TABLE users_new RENAME TO users"),
]


def connect() -> sqlite3.Connection:
    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS schema_version (version TEXT PRIMARY KEY, applied_at TEXT)"
    )
    connection.commit()
    return connection


def rows(connection: sqlite3.Connection, table: str = "users") -> list[tuple]:
    return connection.execute(f"SELECT * FROM {table}").fetchall()


def columns(connection: sqlite3.Connection, table: str = "users") -> list[str]:
    return [r[1] for r in connection.execute(f"PRAGMA table_info({table})")]


def show(connection: sqlite3.Connection, note: str = "", table: str = "users") -> None:
    if note:
        print(f"    {note}")
    existing = {
        r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if table not in existing:
        print(f"    {table}: does not exist")
        print()
        return
    print(f"    {table} columns: {columns(connection, table)}")
    for row in rows(connection, table):
        print(f"    row: {row}")
    print()


def run_step(connection: sqlite3.Connection, version: str, sql: str) -> None:
    connection.execute(sql)
    connection.execute("INSERT INTO schema_version VALUES (?, datetime('now'))", (version,))
    connection.commit()


def run_runner() -> None:
    print("1. A migration runner is just a numbered list and a ledger")
    connection = connect()
    for version, sql in STEPS:
        already = connection.execute(
            "SELECT 1 FROM schema_version WHERE version = ?", (version,)
        ).fetchone()
        if already:
            print(f"  {version} already applied, skipping")
            continue
        run_step(connection, version, sql)
        print(f"  applied {version}")
        show(connection)

    applied = connection.execute("SELECT version FROM schema_version ORDER BY version").fetchall()
    print(f"  ledger: {[v[0] for v in applied]}")
    print()
    print("  Run it again and nothing happens:")
    for version, sql in STEPS:
        already = connection.execute(
            "SELECT 1 FROM schema_version WHERE version = ?", (version,)
        ).fetchone()
        if not already:
            print("  this should not print")
    print("  every version was already in the ledger, so every step was skipped")
    print()
    print("  The ledger is the whole point. Without it you cannot tell which")
    print("  migrations ran, and re-running INSERT would duplicate rows.")
    connection.close()


def run_limits() -> None:
    print("2. Three things SQLite will not do")
    connection = connect()
    run_step(connection, "0001", "CREATE TABLE users (name TEXT PRIMARY KEY, role TEXT)")
    run_step(connection, "0002", "INSERT INTO users VALUES ('iris', 'student')")

    for label, sql in [
        ("change a column's type", "ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50)"),
        ("add a NOT NULL column with no default", "ALTER TABLE users ADD COLUMN age INTEGER NOT NULL"),
    ]:
        try:
            connection.execute(sql)
            print(f"  {label}: accepted (unexpected)")
        except sqlite3.Error as error:
            print(f"  {label}: refused")
            print(f"    {type(error).__name__}: {error}")
    connection.commit()

    print()
    print("  The same column WITH a default is accepted:")
    connection.execute("ALTER TABLE users ADD COLUMN age INTEGER NOT NULL DEFAULT 0")
    connection.commit()
    show(connection, "age exists, every row has 0")
    print("  A new NOT NULL column cannot ask old rows what their value should be,")
    print("  so SQLite refuses unless you supply the default yourself.")
    connection.close()


def run_expand() -> None:
    print("3. Changing a column, without losing data")
    connection = connect()
    run_step(connection, "0001", "CREATE TABLE users (name TEXT PRIMARY KEY, role TEXT)")
    for name, role in [("iris", "student"), ("root", "admin"), ("ada", "student")]:
        connection.execute("INSERT INTO users VALUES (?, ?)", (name, role))
    connection.commit()
    show(connection, "before")

    # SQLite cannot retype a column. So build the new shape alongside.
    run_step(connection, "0002", "CREATE TABLE users_new (name TEXT PRIMARY KEY, role_id INTEGER NOT NULL)")
    show(connection, "expand: the new table exists, the old one is untouched")
    show(connection, "and the new one starts empty", "users_new")

    run_step(
        connection,
        "0003",
        "INSERT INTO users_new SELECT name, CASE role WHEN 'admin' THEN 1 ELSE 0 END FROM users",
    )
    show(connection, "backfill: rows copied and converted, nothing dropped yet")
    show(connection, "users still has the original text values", "users")
    show(connection, "users_new has the converted integers", "users_new")

    # Only now is it safe to stop reading the old column.
    print("    reads can switch to users_new here, while users is still intact")
    print("    if this release breaks, roll back by pointing reads at users again")
    print()

    run_step(connection, "0004", "DROP TABLE users")
    show(connection, "contract: the old table is gone", "users")
    show(connection, "and the new one is still complete", "users_new")

    run_step(connection, "0005", "ALTER TABLE users_new RENAME TO users")
    show(connection, "final shape")
    print("  Three rows in, three rows out. The old column went away with a DROP,")
    print("  and by then nothing was reading it.")
    connection.close()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "runner": run_runner,
        "limits": run_limits,
        "expand": run_expand,
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