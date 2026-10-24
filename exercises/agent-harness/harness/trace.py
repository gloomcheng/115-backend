"""One id that follows an agent turn from the request into the log.

Unit 15 is about logs, and the first question a log has to answer is "which
request is this?". Without an answer, a log is a pile.

A trace id is that answer. It is generated once per request, carried in a
header, and written into the metadata of every event the request produces.
Afterwards, one number is enough to pull out everything that request did.

The id is host-owned. A caller may propose one, and the host will accept it
only if it looks like a trace id, because an id that the caller fully
controls is an id that two different requests can collide on.
"""

import re
import uuid
from typing import Iterable, Optional

from harness.events import Event

TRACE_HEADER = "X-Trace-Id"

# 16 hex characters: short enough to read in a log line, long enough that
# two requests do not collide by accident.
TRACE_ID_PATTERN = re.compile(r"^[0-9a-f]{16}$")


def new_trace_id() -> str:
    """Generate a trace id for a request that did not bring one."""
    return uuid.uuid4().hex[:16]


def is_trace_id(value: str) -> bool:
    """Whether a caller-supplied string is shaped like a trace id."""
    return bool(TRACE_ID_PATTERN.match(value))


def normalize_trace_id(candidate: Optional[str]) -> str:
    """Use the caller's trace id when it is usable, otherwise make one.

    A caller-supplied id that does not fit is dropped rather than repaired.
    Silently rewriting it would break the link to whatever the caller was
    already correlating with.
    """
    if candidate and is_trace_id(candidate):
        return candidate
    return new_trace_id()


def select_by_trace(events: Iterable[Event], trace_id: str) -> list[Event]:
    """Every event that belongs to one trace."""
    return [event for event in events if (event.meta or {}).get("trace_id") == trace_id]


def traces_of(events: Iterable[Event]) -> list[str]:
    """The distinct trace ids in the log, in the order they first appear."""
    seen: list[str] = []
    for event in events:
        trace_id = (event.meta or {}).get("trace_id")
        if trace_id and trace_id not in seen:
            seen.append(trace_id)
    return seen
