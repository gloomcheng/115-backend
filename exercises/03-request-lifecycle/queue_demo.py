"""Lesson 03 — work that has no request, and therefore nobody to tell.

    python queue_demo.py inline     # doing the work during the request
    python queue_demo.py queued     # the same work, after the response
    python queue_demo.py crash      # the worker dies mid-job
    python queue_demo.py retry      # and the retry charges twice
    python queue_demo.py idempotent # the fix
    python queue_demo.py all

The queue is a table. That is not a simplification: it is what a real
broker such as Redis or RabbitMQ gives you, plus delivery guarantees you
have to think about.

Every section prints the same two numbers:

    jobs       what the queue thinks happened
    effects    what actually happened in the world

When they disagree, you have a bug that no exception ever reported.
"""

import os
import sqlite3
import sys

DB = "queue.db"

SCHEMA = """
CREATE TABLE jobs (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    status  TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE effects (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id  INTEGER NOT NULL,
    note    TEXT NOT NULL
);
"""

EFFECT = "charged the customer"


def reset() -> sqlite3.Connection:
    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.executescript(SCHEMA)
    return connection


def counts(connection: sqlite3.Connection) -> tuple[int, int]:
    jobs = connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    effects = connection.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
    return jobs, effects


def report(connection: sqlite3.Connection, note: str) -> None:
    jobs, effects = counts(connection)
    status = connection.execute(
        "SELECT status, COUNT(*) FROM jobs GROUP BY status ORDER BY status"
    ).fetchall()
    detail = ", ".join(f"{name}={count}" for name, count in status)
    print(f"  {note}")
    print(f"    jobs: {jobs} ({detail})   effects: {effects}")
    if jobs != effects:
        print("    ^ these disagree. nothing raised. nothing was logged.")


def charge(connection: sqlite3.Connection, job_id: int) -> None:
    # A blind charge. Nothing here checks whether this job already ran, which
    # is exactly what makes a retry unsafe.
    connection.execute("INSERT INTO effects (job_id, note) VALUES (?, ?)", (job_id, EFFECT))
    connection.commit()


def run_inline() -> None:
    print("1. Doing the work during the request")
    connection = reset()
    connection.execute("INSERT INTO jobs VALUES (1, 'charge', 'done', 1)")
    charge(connection, 1)
    report(connection, "request handled, client got its response")
    print("   The client knows the answer, because the client was still waiting.")
    print("   If charge() had raised, the client would have gotten a 500.")
    connection.close()


def run_queued() -> None:
    print("2. The same work, after the response")
    connection = reset()
    connection.execute("INSERT INTO jobs VALUES (1, 'charge', 'pending', 0)")
    report(connection, "request handled, client got 202 Accepted")
    print("   The client no longer knows the answer, and that is the trade.")

    # The worker, later.
    connection.execute("UPDATE jobs SET status = 'running', attempts = 1 WHERE id = 1")
    charge(connection, 1)
    connection.execute("UPDATE jobs SET status = 'done' WHERE id = 1")
    report(connection, "worker finished")
    print("   Now the client knows nothing, the worker knows, and only the log ties them.")
    connection.close()


def run_crash() -> None:
    print("3. The worker dies between the charge and the bookkeeping")
    connection = reset()
    connection.execute("INSERT INTO jobs VALUES (1, 'charge', 'pending', 0)")
    connection.execute("UPDATE jobs SET status = 'running', attempts = 1 WHERE id = 1")
    charge(connection, 1)
    # ... and here the process is killed. The job is still 'running'.
    report(connection, "worker killed after charging, before marking done")
    print("   status is stuck at 'running'. No exception, no 500, no Client to tell.")
    print("   The queue still holds a job that will never finish on its own.")
    connection.close()


def run_retry() -> None:
    print("4. The operator retries the stuck job")
    connection = reset()
    connection.execute("INSERT INTO jobs VALUES (1, 'charge', 'running', 1)")
    charge(connection, 1)
    # Someone notices the job is stuck and runs it again.
    connection.execute("UPDATE jobs SET attempts = 2 WHERE id = 1")
    charge(connection, 1)
    connection.execute("UPDATE jobs SET status = 'done' WHERE id = 2")
    connection.execute("UPDATE jobs SET status = 'done' WHERE id = 1")
    report(connection, "after one retry")
    print()
    print("   1 job, 2 charges. The customer was billed twice.")
    print()
    print("   A queue cannot promise exactly-once. It promises at-least-once, which")
    print("   means 'at least', and the second time is your problem to make safe.")
    connection.close()


def charge_once(connection: sqlite3.Connection, job_id: int) -> str:
    """Let the database decide, instead of asking first.

    There is no SELECT here. The UNIQUE constraint is the check, and the
    INSERT is the answer, in one statement the database can serialise. Two
    processes racing on the same job produce one charge and one refusal.
    """
    try:
        connection.execute("INSERT INTO effects (job_id, note) VALUES (?, ?)", (job_id, EFFECT))
        connection.commit()
        return "charged"
    except sqlite3.IntegrityError:
        connection.rollback()
        return "already charged, skipping"


def run_idempotent() -> None:
    print("5. The same retry, protected by a UNIQUE constraint")
    connection = reset()
    # This constraint is the whole mechanism. It is absent from the schema
    # above on purpose, because without it you cannot watch the duplicate.
    connection.execute("CREATE UNIQUE INDEX idx_effect ON effects (job_id)")

    connection.execute("INSERT INTO jobs VALUES (1, 'charge', 'running', 1)")
    charge(connection, 1)
    connection.execute("UPDATE jobs SET attempts = 2 WHERE id = 1")

    outcome = charge_once(connection, 1)
    print(f"   second attempt: {outcome}")
    connection.execute("UPDATE jobs SET status = 'done' WHERE id = 1")
    report(connection, "after the same retry")

    print()
    print("   1 job, 1 charge. The retry was safe.")
    print()
    print("   Compare this with checking first and inserting second:")
    print("     SELECT whether it happened  ->  INSERT")
    print("   That is two statements, so there is a gap between them. Die in the")
    print("   gap and the next attempt cannot tell 'never started' from 'finished'.")
    print()
    print("   With a UNIQUE constraint there is no gap: the insert either lands")
    print("   once, or the database refuses it. Asking the question and recording")
    print("   the answer are the same statement, so nothing can slip between them.")
    connection.close()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "inline": run_inline,
        "queued": run_queued,
        "crash": run_crash,
        "retry": run_retry,
        "idempotent": run_idempotent,
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