"""Unit 14 — the tool call contract.

Run:

    pytest -q -k tools

The rule under test: adding a tool is adding an entry, not adding a
branch. The host speaks the same contract to every one of them, and a tool
that fails is recorded as a failure instead of disappearing.
"""

import pytest

from harness.tools import ToolError, ToolRegistry, build_default_registry
from harness.validation import ToolCallIn

def test_the_catalogue_lists_every_tool_with_its_arguments():
    catalogue = build_default_registry().describe()

    names = [entry["name"] for entry in catalogue]
    assert names == ["read_state", "todowrite"]
    assert catalogue[1]["arguments"]["properties"]["todos"]


def test_a_registered_tool_is_called_by_name():
    registry = build_default_registry()

    spec = registry.get("todowrite")

    assert spec is not None
    assert spec.name == "todowrite"


def test_an_unknown_tool_is_an_execution_failure_not_a_crash():
    registry = build_default_registry()

    with pytest.raises(ToolError) as caught:
        registry.invoke(ToolCallIn(tool_call_id="call_1", tool_name="nope"), context=None)

    assert caught.value.details["error"] == "unknown tool: nope"
    assert "todowrite" in caught.value.details["known_tools"]


def test_bad_arguments_are_reported_as_a_failure():
    registry = build_default_registry()

    with pytest.raises(ToolError) as caught:
        registry.invoke(
            ToolCallIn(tool_call_id="call_1", tool_name="todowrite", arguments={"todos": "nope"}),
            context=None,
        )

    assert caught.value.details["error"] == "bad arguments for todowrite"


def test_a_tool_cannot_be_registered_twice():
    registry = build_default_registry()
    spec = registry.get("todowrite")

    with pytest.raises(ValueError):
        registry.register(spec)


def test_calling_a_tool_through_the_host_records_a_result(client, writer_headers):
    response = client.post(
        "/tools",
        json={
            "tool_call_id": "call_1",
            "tool_name": "todowrite",
            "arguments": {"todos": [{"content": "write the replay tests", "status": "pending"}]},
        },
        headers=writer_headers,
    )

    assert response.status_code == 201
    assert response.json()["payload"]["is_error"] is False
    assert response.json()["payload"]["details"]["todos"][0]["content"] == "write the replay tests"


def test_a_failing_tool_is_recorded_as_a_failure(client, writer_headers):
    response = client.post(
        "/tools",
        json={"tool_call_id": "call_2", "tool_name": "nope", "arguments": {}},
        headers=writer_headers,
    )

    assert response.status_code == 201
    payload = response.json()["payload"]
    assert payload["is_error"] is True
    assert payload["details"]["error"] == "unknown tool: nope"


def test_a_failing_tool_is_recorded_as_evidence_but_not_as_state(client, writer_headers):
    client.post(
        "/tools",
        json={
            "tool_call_id": "call_1",
            "tool_name": "todowrite",
            "arguments": {"todos": [{"content": "write the replay tests", "status": "pending"}]},
        },
        headers=writer_headers,
    )

    client.post(
        "/tools",
        json={"tool_call_id": "call_2", "tool_name": "nope", "arguments": {}},
        headers=writer_headers,
    )

    events = client.get("/events", headers=writer_headers).json()["events"]
    state = client.get("/state", headers=writer_headers).json()

    # The failed call is in the log as evidence: two events, the second one
    # marked as an error.
    assert len(events) == 2
    assert events[1]["payload"]["is_error"] is True

    # But it is not state. The task list still says what the confirmed
    # write said it says.
    assert state["todos"][0]["status"] == "pending"

    # A call to a tool that does not exist was never a write to the task
    # list, so it does not count as a failed task-list write either.
    assert state["last_failed_event_id"] is None


def test_the_catalogue_route_needs_no_writer_role(client, reader_headers):
    response = client.get("/tools", headers=reader_headers)

    assert response.status_code == 200
