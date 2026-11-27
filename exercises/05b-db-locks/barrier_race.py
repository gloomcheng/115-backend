"""Lesson 05b — two threads start together and race for the write lock.

Run from this directory:

    python barrier_race.py

Both threads pass a Barrier at the same instant. busy_timeout is zero, so a
thread either gets the lock immediately or gets database is locked. Each
trial uses a fresh database file.
"""

import os
import sqlite3
import threading

NAMES = ("A", "B")


def run_trial(db_path):
    setup = sqlite3.connect(db_path, isolation_level=None)
    setup.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, who TEXT)")
    setup.close()

    start = threading.Barrier(2)
    attempted = threading.Barrier(2)
    outcomes = []

    def attempt(who):
        connection = sqlite3.connect(db_path, isolation_level=None)
        connection.execute("PRAGMA busy_timeout = 0")
        acquired = False
        start.wait()
        try:
            connection.execute("BEGIN EXCLUSIVE")
            acquired = True
            outcomes.append((who, "acquired"))
        except sqlite3.OperationalError as error:
            outcomes.append((who, str(error)))
        finally:
            attempted.wait()
        if acquired:
            connection.execute("INSERT INTO t (who) VALUES (?)", (who,))
            connection.commit()
        connection.close()

    threads = [threading.Thread(target=attempt, args=(name,)) for name in NAMES]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    audit = sqlite3.connect(db_path)
    rows = audit.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    audit.close()

    winners = [who for who, outcome in outcomes if outcome == "acquired"]
    losers = [outcome for _, outcome in outcomes if outcome != "acquired"]
    return {
        "winner": winners[0] if winners else "none",
        "loser": losers[0] if losers else "none",
        "winners": len(winners),
        "rows": rows,
    }


def run_barrier_race(db_path, trials=20):
    stem, extension = os.path.splitext(db_path)
    records = []
    for index in range(1, trials + 1):
        trial_db = f"{stem}-{index:02d}{extension or '.db'}"
        record = run_trial(trial_db)
        record["index"] = index
        records.append(record)
    return {"trials": records}


if __name__ == "__main__":
    result = run_barrier_race("barrier.db")
    for trial in result["trials"]:
        loser_name = "B" if trial["winner"] == "A" else "A"
        print(
            f"trial {trial['index']:02d}: {trial['winner']} acquired, "
            f"{loser_name} failed -> {trial['loser']}, rows={trial['rows']}"
        )
    counts = sorted({trial["winners"] for trial in result["trials"]})
    print(
        f"trials={len(result['trials'])}, winners-per-trial={counts}, "
        f"all-exactly-one={all(count == 1 for count in counts)}"
    )
