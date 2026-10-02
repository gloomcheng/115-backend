"""Lesson 05 — two writers, one file, two different outcomes.

Run the holder in one terminal, then the writer in another:

    python hold_the_lock.py
    python write_impatiently.py

The SQLite version refuses loudly. Compare it with json_race.py, where
both writers report success and one row silently disappears.
"""

import sqlite3
import sys
import time

if sys.argv[1] == "hold":
    connection = sqlite3.connect("notes.db", timeout=0.5)
    connection.execute("BEGIN EXCLUSIVE")
    connection.execute("INSERT INTO notes (text) VALUES ('writer A')")
    print("writer A: holding the write lock for 3 seconds")
    time.sleep(3)
    connection.commit()
    connection.close()
    print("writer A: committed")

else:
    try:
        connection = sqlite3.connect("notes.db", timeout=0.5)
        connection.execute("INSERT INTO notes (text) VALUES ('writer B')")
        connection.commit()
        connection.close()
        print("writer B: committed")
    except sqlite3.OperationalError as error:
        print(f"writer B: refused -> {error}")