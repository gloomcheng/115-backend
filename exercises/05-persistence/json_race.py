"""Lesson 05 — the same race against a plain text file.

Run two of these at once and one write disappears without any error:

    python json_race.py A & python json_race.py B & wait

Both processes print "wrote the file". Only one key survives in the file.
"""

import json
import sys
import time

label = sys.argv[1]

data = json.load(open("users.json"))
data[f"writer-{label}"] = {"name": label}
print(f"writer {label}: read the file, writing back in 1 second")
time.sleep(1)
with open("users.json", "w") as handle:
    json.dump(data, handle)
print(f"writer {label}: wrote the file")