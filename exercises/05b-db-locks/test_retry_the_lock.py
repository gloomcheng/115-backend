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


if __name__ == "__main__":
    unittest.main()
