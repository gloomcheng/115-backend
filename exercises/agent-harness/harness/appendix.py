"""The machine-readable appendix of a checkpoint.

A checkpoint has two readers. A person picks up the work and wants to know
what it was. The next process picks it up and wants to know what is true.
The second reader cannot read prose reliably, because prose has to be
interpreted and interpretation is where state gets lost.

So the state goes into an appendix: a small, versioned, structured block
that can be parsed without understanding a sentence.

Two rules shape it:

1. It carries a version. A reader that does not know the version cannot
   know what it is looking at.
2. It is the only copy. The prose next to it never repeats the task list,
   because two copies drift, and the copy that drifts is the one nobody
   checks.
"""

from typing import Optional

from harness.state import TaskState

APPENDIX_VERSION = 1
APPENDIX_ROOT = "harness-context"


def _escape_text(value: str) -> str:
    """Escape text content."""
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _escape_attr(value: str) -> str:
    """Escape an attribute value, quotes included."""
    return _escape_text(value).replace('"', "&quot;")


def build_appendix(state: TaskState, trace_id: Optional[str] = None) -> str:
    """Render the state as a versioned, parseable block.

    The shape is XML-like rather than XML: it is meant to be read by a
    person with `cat` and by a program with a regular expression, and it
    does not need to be a valid document to do either.
    """
    attributes = [f'confirmed="{"true" if state.confirmed else "false"}"']
    if state.source_event_id:
        attributes.append(f'source-event-id="{_escape_attr(state.source_event_id)}"')
    if state.updated_at:
        attributes.append(f'updated-at="{_escape_attr(state.updated_at)}"')
    if trace_id:
        attributes.append(f'trace-id="{_escape_attr(trace_id)}"')

    lines = [f'<{APPENDIX_ROOT} version="{APPENDIX_VERSION}">']
    lines.append(f'  <task-state {" ".join(attributes)}>')
    for todo in state.todos:
        lines.append(f'    <todo status="{_escape_attr(todo.status)}">{_escape_text(todo.content)}</todo>')
    lines.append("  </task-state>")
    lines.append(f"</{APPENDIX_ROOT}>")
    return "\n".join(lines)


def parse_appendix(appendix: str) -> dict[str, object]:
    """Read the appendix back.

    This is the other half of the contract: if the appendix is written for
    a program, then a program has to be able to read it. Parsing it here
    means the format cannot quietly become prose-only.
    """
    import re

    version_match = re.search(rf'<{APPENDIX_ROOT} version="(\d+)">', appendix)
    if not version_match:
        raise ValueError("not a harness appendix")
    version = int(version_match.group(1))
    if version != APPENDIX_VERSION:
        raise ValueError(f"unsupported appendix version: {version}")

    confirmed = bool(re.search(r'<task-state [^>]*confirmed="true"', appendix))
    source_match = re.search(r'source-event-id="([^"]*)"', appendix)
    updated_match = re.search(r'updated-at="([^"]*)"', appendix)

    todos = [
        {"status": status, "content": content}
        for status, content in re.findall(r'<todo status="([^"]*)">(.*?)</todo>', appendix, re.S)
    ]

    return {
        "version": version,
        "confirmed": confirmed,
        "source_event_id": source_match.group(1) if source_match else None,
        "updated_at": updated_match.group(1) if updated_match else None,
        "todos": todos,
    }
