"""Tests for the 05b lock-contention demonstration."""

import os
import tempfile
import unittest
from pathlib import Path


class LockContentionTests(unittest.TestCase):
    def test_loser_retries_after_lock_release_without_duplicate_rows(self):
        self.assertTrue(Path(__file__).with_name("retry_the_lock.py").exists())

        from retry_the_lock import run_contention

        with tempfile.TemporaryDirectory() as directory:
            result = run_contention(
                os.path.join(directory, "locks.db"),
                hold_seconds=0.4,
                busy_timeout_seconds=0.1,
            )

        events = result["events"]
        self.assertTrue(any("database is locked" in event for event in events))
        holder_release = next(
            index for index, event in enumerate(events) if "COMMIT -> lock released" in event
        )
        loser_commit = next(
            index
            for index, event in enumerate(events)
            if "loser: attempt" in event and "committed" in event
        )
        self.assertLess(holder_release, loser_commit)
        self.assertEqual(result["winner_rows"], 1)
        self.assertEqual(result["loser_rows"], 1)

    def test_barrier_race_produces_exactly_one_winner_per_trial(self):
        self.assertTrue(Path(__file__).with_name("barrier_race.py").exists())

        from barrier_race import run_barrier_race

        with tempfile.TemporaryDirectory() as directory:
            result = run_barrier_race(os.path.join(directory, "barrier.db"), trials=6)

        self.assertEqual(len(result["trials"]), 6)
        self.assertTrue(all(trial["winners"] == 1 for trial in result["trials"]))
        self.assertTrue(all(trial["loser"] == "database is locked" for trial in result["trials"]))
        self.assertTrue(all(trial["rows"] == 1 for trial in result["trials"]))


if __name__ == "__main__":
    unittest.main()
