"""Replay the event log into the state the next turn needs.

The log is a list of things that happened. The state is what is true right
now. The two are not the same, because a log can contain things that did
not succeed.

The rule this unit: state comes only from confirmed writes. A write that
failed is evidence, not state.

That rule has two consequences worth stating out loud:

1. A failed write does not change the state. The last confirmed write
   still stands, because it is still the last thing that is known to have
   happened.
2. A failed write does not stay in the log forever as if it were pending.
   It is recorded, but it is recorded as what it was: a failure.
"""

from dataclasses import dataclass
from typing import Any, Iterable, Optional

from harness.events import Event

# Tools whose results describe the task list. A result from any other tool
# says something happened, but it does not say what the task list is.
STATE_TOOL_NAMES = ("todowrite",)

KNOWN_STATUSES = ("pending", "in_progress", "completed", "cancelled")


@dataclass(frozen=True)
class Todo:
    """One item of the task list."""

    content: str
    status: str

    @property
    def status_is_known(self) -> bool:
        return self.status in KNOWN_STATUSES


@dataclass(frozen=True)
class TaskState:
    """What the log says is true right now.

    `last_failed_event_id` is the last failed write to the *task list* that
    no later confirmed write has superseded. A call to some other tool that
    failed is recorded in the log, but it was never a write to the task
    list, so it does not belong here.
    """

    todos: tuple[Todo, ...] = ()
    confirmed: bool = False
    source_event_id: Optional[str] = None
    updated_at: Optional[str] = None
    last_failed_event_id: Optional[str] = None

    def counts(self) -> dict[str, int]:
        """How many todos sit in each status.

        An unrecognised status is counted under "unknown" instead of being
        dropped. A status this program has never heard of is still a status
        somebody used, and hiding it would make the counts lie.
        """
        counts = {status: 0 for status in KNOWN_STATUSES}
        counts["unknown"] = 0
        for todo in self.todos:
            if todo.status in counts:
                counts[todo.status] += 1
            else:
                counts["unknown"] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "todos": [{"content": todo.content, "status": todo.status} for todo in self.todos],
            "counts": self.counts(),
            "confirmed": self.confirmed,
            "source_event_id": self.source_event_id,
            "updated_at": self.updated_at,
            "last_failed_event_id": self.last_failed_event_id,
        }


def _todos_from(payload: dict[str, Any]) -> tuple[Todo, ...]:
    """Read the todo list out of a tool result payload."""
    details = payload.get("details") or {}
    raw_todos = details.get("todos") or []
    todos: list[Todo] = []
    for raw in raw_todos:
        if not isinstance(raw, dict):
            continue
        todos.append(
            Todo(
                content=str(raw.get("content", "")),
                status=str(raw.get("status", "unknown")),
            )
        )
    return tuple(todos)


def replay(events: Iterable[Event]) -> TaskState:
    """Compute the current state from the whole log.

    This function is pure: the same log always produces the same state,
    and it never touches the log it was given. That is what makes unit 13's
    invariants testable.
    """
    todos: tuple[Todo, ...] = ()
    confirmed = False
    source_event_id: Optional[str] = None
    updated_at: Optional[str] = None
    last_failed_event_id: Optional[str] = None

    for event in events:
        if event.op != "tool_result":
            continue
        payload = event.payload or {}
        if payload.get("tool_name") not in STATE_TOOL_NAMES:
            continue

        if payload.get("is_error"):
            # The write failed. The previous confirmed state still stands,
            # and the failure is remembered as an outstanding one until a
            # later confirmed write supersedes it.
            last_failed_event_id = event.event_id
            continue

        todos = _todos_from(payload)
        confirmed = True
        source_event_id = event.event_id
        updated_at = event.observed_at
        last_failed_event_id = None

    return TaskState(
        todos=todos,
        confirmed=confirmed,
        source_event_id=source_event_id,
        updated_at=updated_at,
        last_failed_event_id=last_failed_event_id,
    )
