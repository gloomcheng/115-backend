"""Lesson 05 — a cache is a second copy of the data, and copies go stale.

    python cache.py stale       # the problem, made visible
    python cache.py ttl         # expiry bounds how wrong it can be
    python cache.py invalidate  # fixing it on write
    python cache.py workers     # why one cache per worker is not a cache
    python cache.py all

The source of truth is SQLite. Everything else is a dict in this file,
which is exactly what a real in-process cache is.

Two counters are printed for every read:

    queries  how many times SQLite was actually asked
    value    what the caller got back

When they disagree, you are looking at a bug.
"""

import os
import sqlite3
import sys

DB = "cache.db"


def reset() -> sqlite3.Connection:
    if os.path.exists(DB):
        os.remove(DB)
    connection = sqlite3.connect(DB)
    connection.execute("CREATE TABLE products (name TEXT PRIMARY KEY, price INTEGER NOT NULL)")
    connection.execute("INSERT INTO products VALUES ('keyboard', 100)")
    connection.commit()
    return connection


class Cache:
    """One process's memory. That is the whole abstraction."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.entries: dict[str, int] = {}
        self.queries = 0

    def get(self, name: str) -> int:
        if name in self.entries:
            return self.entries[name]
        self.queries += 1
        row = self.connection.execute(
            "SELECT price FROM products WHERE name = ?", (name,)
        ).fetchone()
        price = row[0]
        self.entries[name] = price
        return price


def set_price(connection: sqlite3.Connection, name: str, price: int) -> None:
    connection.execute("UPDATE products SET price = ? WHERE name = ?", (price, name))
    connection.commit()


def truth(connection: sqlite3.Connection, name: str = "keyboard") -> int:
    return connection.execute("SELECT price FROM products WHERE name = ?", (name,)).fetchone()[0]


def show(label: str, cache: Cache, name: str, connection: sqlite3.Connection) -> None:
    value = cache.get(name)
    print(
        f"  {label:<46} value={value:<4} "
        f"queries={cache.queries}  (database says {truth(connection, name)})"
    )


def run_stale() -> None:
    print("1. A cache that never expires")
    connection = reset()
    cache = Cache(connection)

    show("first read (cache miss)", cache, "keyboard", connection)
    show("second read (cache hit)", cache, "keyboard", connection)
    print("   queries stopped at 1. That is the entire benefit of a cache.")

    # Somebody else changes the price. The cache is not told.
    set_price(connection, "keyboard", 200)
    show("after the database changed to 200", cache, "keyboard", connection)

    print()
    print("   The caller got 100 from a database that says 200.")
    print("   queries is still 1, so nothing in the log shows the write happened.")
    print()
    print("   Unit 06 already showed a silent wrong answer: json_race.py returns a")
    print("   200 with data missing. A cache is the second source, and the two are")
    print("   worth telling apart:")
    print("     a race loses writes that were meant to happen")
    print("     a cache returns a value that was correct, and then stopped being so")
    connection.close()


def run_ttl() -> None:
    print("2. A cache with an expiry")
    connection = reset()
    cache = Cache(connection)
    expires_at: dict[str, float] = {}

    def get_with_ttl(name: str, now: float) -> int:
        if name in cache.entries and expires_at[name] > now:
            return cache.entries[name]
        cache.queries += 1
        price = truth(connection, name)
        cache.entries[name] = price
        expires_at[name] = now + 30
        return price

    print("   TTL is 30 seconds. t is in seconds since the server started.")
    for now, label in [(0.0, "t=0  first read"), (10.0, "t=10 read again")]:
        value = get_with_ttl("keyboard", now)
        print(f"  {label:<46} value={value:<4} queries={cache.queries}")

    set_price(connection, "keyboard", 200)
    print("   the database changed to 200, and nobody told the cache")
    for now, label in [(20.0, "t=20 still inside the TTL"), (40.0, "t=40 TTL has passed")]:
        value = get_with_ttl("keyboard", now)
        note = "stale" if value != truth(connection, "keyboard") else "correct"
        print(
            f"  {label:<46} value={value:<4} queries={cache.queries}"
            f"  (database says {truth(connection, 'keyboard')}, {note})"
        )
    print()
    print("   A TTL does not make the cache correct. It bounds how wrong it can be.")
    connection.close()


def run_invalidate() -> None:
    print("3. Invalidate on write")
    connection = reset()
    cache = Cache(connection)

    cache.get("keyboard")
    cache.get("keyboard")
    print(f"  after two reads: queries={cache.queries}")

    # Every write must remember to clear the cache. This is the whole cost.
    set_price(connection, "keyboard", 200)
    cache.entries.clear()
    value = cache.get("keyboard")
    print(f"  after a write that cleared the cache: value={value} queries={cache.queries}")

    print()
    print("   The rule is simple and it is easy to forget:")
    print("     every write path must clear, or the next reader gets the old value.")
    print("   One UPDATE statement that forgets is enough to ship a wrong number.")
    connection.close()


def run_workers() -> None:
    print("4. Two workers, two caches")
    connection = reset()
    worker_a = Cache(connection)
    worker_b = Cache(connection)

    worker_a.get("keyboard")
    print(f"  worker A read: queries={worker_a.queries}, value={worker_a.entries['keyboard']}")

    # worker B handles the write and correctly clears its own cache.
    set_price(connection, "keyboard", 200)
    worker_b.get("keyboard")
    print(f"  worker B read after the write: value={worker_b.entries['keyboard']}")

    value = worker_a.get("keyboard")
    print(f"  worker A read again:            value={value}")
    print()
    print(f"   database says {truth(connection, 'keyboard')}")
    print("   worker B is correct. worker A is not, and it will stay wrong")
    print("   until its own entry expires or that worker handles a write.")
    print()
    print("   A cache inside the process is not one cache. It is one cache per worker,")
    print("   and invalidation only ever reaches the worker that performed the write.")
    connection.close()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    runners = {
        "stale": run_stale,
        "ttl": run_ttl,
        "invalidate": run_invalidate,
        "workers": run_workers,
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