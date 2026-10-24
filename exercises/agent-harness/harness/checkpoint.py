"""The checkpoint: what a resumed session is handed.

The final project asks one question: after a session ends, how does the
next one pick up the work without re-reading the whole transcript?

The obvious answer is a summary. That answer is wrong, for a reason worth
being precise about. A summary is prose, and prose is a copy. Two copies of
the same state drift apart the moment one of them is edited, and after that
nobody can say which one is right.

So a checkpoint here has two parts, and the split is the design:

- The prose says where the work is going and points at the appendix. It
  never lists the tasks.
- The appendix holds the task list, in a versioned structured form that a
  program can read.

The rule of the final project: the task list exists exactly once, in the
appendix, and the prose points at it.
"""

from dataclasses import dataclass
from typing import Optional

from harness.appendix import build_appendix
from harness.state import TaskState


@dataclass(frozen=True)
class Checkpoint:
    """One checkpoint of an agent's work."""

    goal: str
    state: TaskState
    trace_id: Optional[str] = None

    def appendix(self) -> str:
        """The structured part: the only copy of the task list."""
        return build_appendix(self.state, self.trace_id)

    def prose(self) -> str:
        """The part a person reads.

        It says what the work is, and where the task list lives. It does
        not repeat the task list, because that is the copy that drifts.
        """
        lines = [
            f"Goal: {self.goal}",
            "",
            "The task list is in the appendix below. That appendix is the only copy of it.",
        ]
        if not self.state.confirmed:
            lines.append("")
            lines.append("No confirmed write has been recorded yet, so the task list is empty.")
        elif self.state.last_failed_event_id:
            lines.append("")
            lines.append(
                "The last write to the task list failed, so the list below is the last confirmed one."
            )
        return "\n".join(lines)

    def render(self) -> str:
        """The whole checkpoint, as it is handed over."""
        return f"{self.prose()}\n\n{self.appendix()}"
