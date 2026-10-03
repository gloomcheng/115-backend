"""Lesson 08 — SQL injection, in three shapes.

    python injection.py value        # the classic: ' OR '1'='1
    python injection.py delete       # the same mistake, but it destroys data
    python injection.py identifier   # why a column name is harder to protect
    python injection.py all

The application under test is one function long:

    find(name) -> list[tuple]
    remove(name) -> int

`value` reads rows it was not asked for. `delete` destroys rows.
`identifier` is the one that still bites real code, because SQL has no
placeholder for a column name.
"""

import sqlite3
import sys

DB = "injection.db"

SCHEMA = """
CREATE TABLE users (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL
)
"""

SEED = [("iris", "student"), ("root", "admin")]


def reset() -> sqlite3.Connection:
    import os

    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.executescript(SCHEMA)
    connection.executemany("INSERT INTO users (name, role) VALUES (?, ?)", SEED)
    connection.commit()
    return connection


def vulnerable(name: str) -> list[tuple]:
    """The bug: the caller's text becomes part of the statement."""
    connection = reset()
    query = f"SELECT name, role FROM users WHERE name = '{name}'"
    print(f"    SQL: {query}")
    rows = connection.execute(query).fetchall()
    connection.close()
    return rows


def safe(name: str) -> list[tuple]:
    """The fix: the caller's text stays data, because it is bound, not pasted."""
    connection = reset()
    query = "SELECT name, role FROM users WHERE name = ?"
    print(f"    SQL: {query}")
    rows = connection.execute(query, (name,)).fetchall()
    connection.close()
    return rows


def remove_vulnerable(name: str) -> int:
    """The same mistake in a DELETE. One statement, so nothing else stops it."""
    connection = reset()
    query = f"DELETE FROM users WHERE name = '{name}'"
    print(f"    SQL: {query}")
    cursor = connection.execute(query)
    connection.commit()
    remaining = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    connection.close()
    return cursor.rowcount, remaining


def remove_safe(name: str) -> int:
    connection = reset()
    query = "DELETE FROM users WHERE name = ?"
    print(f"    SQL: {query}")
    cursor = connection.execute(query, (name,))
    connection.commit()
    remaining = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    connection.close()
    return cursor.rowcount, remaining


def identifier(column: str) -> list[tuple]:
    """A column name cannot be a placeholder, so it has to be checked instead."""
    connection = reset()
    allowed = {"name", "role"}
    if column not in allowed:
        connection.close()
        return []

    query = f"SELECT name, role FROM users ORDER BY {column}"
    print(f"    SQL: {query}")
    rows = connection.execute(query).fetchall()
    connection.close()
    return rows


def identifier_without_whitelist(column: str) -> list[tuple]:
    """Same function, minus the allow-list. The caller decides the statement."""
    connection = reset()
    query = f"SELECT name, role FROM users ORDER BY {column}"
    print(f"    SQL: {query}")
    try:
        rows = connection.execute(query).fetchall()
    except sqlite3.Error as error:
        connection.close()
        return [("ERROR", str(error))]
    connection.close()
    return rows


def show(rows: list[tuple]) -> None:
    if not rows:
        print("    -> 0 rows")
    for row in rows:
        print(f"    -> {row}")


def run_value() -> None:
    print("1. The value is pasted into the statement")
    print("   searching for the user named iris:")
    show(vulnerable("iris"))
    print("   searching for ' OR '1'='1:")
    show(vulnerable("' OR '1'='1"))
    print("   the same search with a bound parameter:")
    show(safe("' OR '1'='1"))


def run_delete() -> None:
    print("2. The same mistake in a DELETE")
    print("   deleting the user named iris:")
    deleted, remaining = remove_vulnerable("iris")
    print(f"    -> deleted {deleted}, {remaining} left")
    print("   deleting 'x' OR '1'='1 :")
    deleted, remaining = remove_vulnerable("x' OR '1'='1")
    print(f"    -> deleted {deleted}, {remaining} left")
    print("   the same request with a bound parameter:")
    deleted, remaining = remove_safe("x' OR '1'='1")
    print(f"    -> deleted {deleted}, {remaining} left")


def run_identifier() -> None:
    print("3. The column name cannot be a placeholder")
    print("   ORDER BY name, checked against an allow-list:")
    show(identifier("name"))
    print("   ORDER BY role, checked against an allow-list:")
    show(identifier("role"))
    print("   ORDER BY name; DROP TABLE users -- , with the allow-list:")
    show(identifier("name; DROP TABLE users --"))
    print("   the same input, with the allow-list removed:")
    show(identifier_without_whitelist("name; DROP TABLE users --"))
    print("   and a column the author never imagined, still unchecked:")
    show(identifier_without_whitelist("1"))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("value", "all"):
        run_value()
    if mode in ("delete", "all"):
        run_delete()
    if mode in ("identifier", "all"):
        run_identifier()


if __name__ == "__main__":
    main()