"""The append-only event log.

This is the part of the harness that remembers. A conversation can be
compacted and thrown away; a line that was already appended cannot. So every
state change is written down before anything reads it back, and an existing
line is never rewritten.

One JSON object per line. The format is boring on purpose: the log has to be
readable by `cat`, `grep` and a text editor when something goes wrong.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now() -> str:
    """UTC timestamp in the same shape everywhere: 2026-10-24T02:11:33Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass(frozen=True)
class Event:
    """One recorded fact about what happened."""

    event_id: str
    observed_at: str
    op: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "observed_at": self.observed_at,
            "op": self.op,
            "payload": self.payload,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, line: str) -> "Event":
        data = json.loads(line)
        return cls(
            event_id=data["event_id"],
            observed_at=data["observed_at"],
            op=data["op"],
            payload=data["payload"],
        )


class EventLog:
    """Append-only log, stored as one JSON object per line."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def append(self, op: str, payload: dict[str, Any]) -> Event:
        """Append one event and return it.

        Existing lines are never touched. A line that was appended stays
        exactly as it was written, even if a later event contradicts it.
        """
        event = Event(
            event_id=uuid.uuid4().hex,
            observed_at=_now(),
            op=op,
            payload=payload,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json() + "\n")
        return event

    def read(self) -> list[Event]:
        """Read every event back, in the order it was written."""
        if not self.path.exists():
            return []
        events: list[Event] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(Event.from_json(line))
        return events
