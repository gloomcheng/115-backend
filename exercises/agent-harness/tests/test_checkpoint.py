"""The final project — the checkpoint.

Run:

    pytest -q -k checkpoint

The rule under test: the task list exists exactly once. It lives in the
appendix, and the prose next to it points at the appendix instead of
repeating it, because two copies of the same state drift apart.
"""

import pytest

from harness.appendix import APPENDIX_VERSION, build_appendix, parse_appendix
from harness.checkpoint import Checkpoint
from harness.state import TaskState, Todo


def a_state() -> TaskState:
    return TaskState(
        todos=(Todo(content="write the replay tests", status="pending"),),
        confirmed=True,
        source_event_id="abc123",
        updated_at="2026-10-24T02:11:33Z",
    )


def test_the_appendix_carries_the_task_list():
    appendix = build_appendix(a_state())

    assert "write the replay tests" in appendix
    assert 'status="pending"' in appendix


def test_the_appendix_carries_a_version():
    appendix = build_appendix(a_state())

    assert f'version="{APPENDIX_VERSION}"' in appendix


def test_the_appendix_can_be_read_back():
    appendix = build_appendix(a_state())

    parsed = parse_appendix(appendix)

    assert parsed["version"] == APPENDIX_VERSION
    assert parsed["confirmed"] is True
    assert parsed["source_event_id"] == "abc123"
    assert parsed["todos"] == [{"status": "pending", "content": "write the replay tests"}]


def test_an_appendix_of_another_version_is_refused():
    with pytest.raises(ValueError):
        parse_appendix('<harness-context version="99"><task-state confirmed="true" /></harness-context>')


def test_the_prose_never_repeats_the_task_list():
    checkpoint = Checkpoint(goal="ship the replay tests", state=a_state())

    # The task list exists exactly once. If the prose also listed it, the
    # two copies would drift, and nobody would know which one to trust.
    assert "write the replay tests" not in checkpoint.prose()
    assert "write the replay tests" in checkpoint.appendix()


def test_the_prose_points_at_the_appendix():
    checkpoint = Checkpoint(goal="ship the replay tests", state=a_state())

    assert "appendix" in checkpoint.prose()


def test_the_rendered_checkpoint_holds_both_parts():
    checkpoint = Checkpoint(goal="ship the replay tests", state=a_state())

    rendered = checkpoint.render()

    assert rendered.startswith("Goal: ship the replay tests")
    assert "<harness-context" in rendered


def test_a_checkpoint_says_so_when_nothing_was_confirmed():
    checkpoint = Checkpoint(goal="ship the replay tests", state=TaskState())

    assert "No confirmed write" in checkpoint.prose()


def test_a_checkpoint_says_so_when_the_last_write_failed():
    state = TaskState(
        todos=(Todo(content="write the replay tests", status="pending"),),
        confirmed=True,
        source_event_id="abc123",
        last_failed_event_id="def456",
    )
    checkpoint = Checkpoint(goal="ship the replay tests", state=state)

    assert "failed" in checkpoint.prose()


def test_the_checkpoint_route_returns_both_parts(client, writer_headers):
    client.post(
        "/tools",
        json={
            "tool_call_id": "call_1",
            "tool_name": "todowrite",
            "arguments": {"todos": [{"content": "write the replay tests", "status": "pending"}]},
        },
        headers=writer_headers,
    )

    response = client.get("/checkpoint?goal=ship the replay tests", headers=writer_headers)

    assert response.status_code == 200
    body = response.json()
    assert "write the replay tests" not in body["prose"]
    assert "write the replay tests" in body["appendix"]
