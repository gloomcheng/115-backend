"""Lesson 05 — three ways to "save" something, and what each one costs.

Every mode takes one argument: add writes, list reads from a fresh
process. Run them in this order to see the whole comparison:

    python store.py dict-add
    python store.py dict-list

    python store.py json-add
    python store.py json-list

    python store.py sqlite-add
    python store.py sqlite-list

Only json-* and sqlite-* leave anything behind on disk.
"""

import json
import sqlite3
import sys

USERS = {"alice": {"name": "Alice"}}
NOTE = "carol"

mode = sys.argv[1]

if mode == "dict-add":
    users = dict(USERS)
    users[NOTE] = {"name": "Carol"}
    print(f"added {NOTE} to a dict, held by this process only")

elif mode == "dict-list":
    # A new process starts with a fresh dict. Nothing carried over.
    print(f"dict sees: {sorted(USERS)}")

elif mode == "json-add":
    try:
        users = json.load(open("users.json"))
    except FileNotFoundError:
        users = dict(USERS)
    users[NOTE] = {"name": "Carol"}
    with open("users.json", "w") as handle:
        json.dump(users, handle)
    print(f"added {NOTE} to users.json")

elif mode == "json-list":
    print(f"users.json sees: {sorted(json.load(open('users.json')))}")

elif mode == "sqlite-add":
    connection = sqlite3.connect("notes.db")
    connection.execute(
        "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)"
    )
    connection.execute("INSERT INTO notes (text) VALUES (?)", (NOTE,))
    connection.commit()
    connection.close()
    print(f"added {NOTE} to notes.db")

elif mode == "sqlite-list":
    connection = sqlite3.connect("notes.db")
    rows = connection.execute("SELECT id, text FROM notes").fetchall()
    connection.close()
    print(f"notes.db sees: {[row[1] for row in rows]}")

elif mode == "sqlite-schema":
    connection = sqlite3.connect("notes.db")
    for row in connection.execute("SELECT sql FROM sqlite_master"):
        print(row[0])
    connection.close()

else:
    raise SystemExit(f"unknown mode: {mode}")