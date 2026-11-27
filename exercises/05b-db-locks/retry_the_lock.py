"""Lesson 05b — one write lock, one winner, one safe retry.

Run from this directory:

    python retry_the_lock.py

The holder takes BEGIN EXCLUSIVE. The loser waits, gets database is locked,
backs off, and commits only after the holder releases the lock.
"""

import sqlite3
import threading
import time


def run_contention(db_path, hold_seconds=1.0, busy_timeout_seconds=0.3):
    events = []
    holder_locked = threading.Event()

    def holder():
        connection = sqlite3.connect(db_path, isolation_level=None)
        connection.execute("BEGIN EXCLUSIVE")
        events.append("holder: BEGIN EXCLUSIVE -> write lock acquired")
        holder_locked.set()
        time.sleep(hold_seconds)
        connection.execute("INSERT INTO requests (id, label) VALUES ('holder', 'winner')")
        connection.commit()
        events.append("holder: COMMIT -> lock released")
        connection.close()

    def loser():
        holder_locked.wait(5)
        connection = sqlite3.connect(db_path, isolation_level=None)
        connection.execute(f"PRAGMA busy_timeout = {int(busy_timeout_seconds * 1000)}")
        for attempt in range(1, 11):
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute(
                    "INSERT INTO requests (id, label) VALUES ('loser', 'retried') "
                    "ON CONFLICT(id) DO NOTHING"
                )
                connection.commit()
                events.append(f"loser: attempt {attempt} -> committed")
                break
            except sqlite3.OperationalError as error:
                if "locked" not in str(error):
                    raise
                events.append(f"loser: attempt {attempt} -> {error}")
                time.sleep(min(0.2, 0.05 * 2 ** (attempt - 1)))
        else:
            raise RuntimeError("loser never acquired the write lock")
        connection.close()

    setup = sqlite3.connect(db_path, isolation_level=None)
    setup.execute("CREATE TABLE requests (id TEXT PRIMARY KEY, label TEXT NOT NULL)")
    setup.close()

    holder_thread = threading.Thread(target=holder)
    loser_thread = threading.Thread(target=loser)
    holder_thread.start()
    loser_thread.start()
    holder_thread.join()
    loser_thread.join()

    replay = sqlite3.connect(db_path, isolation_level=None)
    replay.execute(
        "INSERT INTO requests (id, label) VALUES ('loser', 'retried') "
        "ON CONFLICT(id) DO NOTHING"
    )
    replay.close()

    audit = sqlite3.connect(db_path)
    winner_rows = audit.execute("SELECT COUNT(*) FROM requests WHERE id = 'holder'").fetchone()[0]
    loser_rows = audit.execute("SELECT COUNT(*) FROM requests WHERE id = 'loser'").fetchone()[0]
    audit.close()
    events.append(f"replay: same loser id inserted again -> rows for loser = {loser_rows}")

    return {"events": events, "winner_rows": winner_rows, "loser_rows": loser_rows}


if __name__ == "__main__":
    result = run_contention("locks.db")
    for event in result["events"]:
        print(event)
    print(f"winner rows: {result['winner_rows']}, loser rows: {result['loser_rows']}")
