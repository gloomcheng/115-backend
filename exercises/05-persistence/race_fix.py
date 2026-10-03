"""Lesson 05 — the same race, three ways to lose it.

    python race_fix.py naive A &  python race_fix.py naive B &  wait
    python race_fix.py naive A &  python race_fix.py naive B &  wait   # again

    python race_fix.py counting A & python race_fix.py counting B & wait
    python race_fix.py locked A   & python race_fix.py locked B   & wait

naive   read the whole file, add one key, write it back  -> data disappears
counting read, increment a number held in the file       -> data disappears
locked  read, add one key, write back, while holding an OS lock -> no data lost
"""

import fcntl
import json
import os
import sys
import time

PATH = "race.json"
mode, label = sys.argv[1], sys.argv[2]


def read() -> dict:
    if not os.path.exists(PATH):
        return {}
    with open(PATH) as handle:
        return json.load(handle)


def write(data: dict) -> None:
    with open(PATH, "w") as handle:
        json.dump(data, handle)


def acquire_lock() -> int:
    # O_CREAT without O_TRUNC: open the lock file without destroying it.
    # The returned fd must stay open for the whole critical section. flock is
    # tied to the open file description, so closing it early releases the lock.
    lock = os.open("race.lock", os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(lock, fcntl.LOCK_EX)
    return lock


if mode == "naive":
    data = read()
    print(f"{label}: read {data}, writing back in 1s")
    time.sleep(1)
    data[f"{label}"] = {"at": time.time()}
    write(data)
    print(f"{label}: wrote the file")

elif mode == "counting":
    data = read()
    current = data.get("count", 0)
    print(f"{label}: read count={current}, writing back in 1s")
    time.sleep(1)
    data["count"] = current + 1
    data[f"{label}"] = {"at": time.time()}
    write(data)
    print(f"{label}: wrote count={current + 1}")

elif mode == "locked":
    lock = acquire_lock()
    data = read()
    print(f"{label}: hold lock, read {data}, writing back in 1s")
    time.sleep(1)
    data[f"{label}"] = {"at": time.time()}
    write(data)
    fcntl.flock(lock, fcntl.LOCK_UN)
    os.close(lock)
    print(f"{label}: wrote the file, released lock")
