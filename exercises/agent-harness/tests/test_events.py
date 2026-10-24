"""Week 10 — the check that stands in front of the log.

Run:

    pytest -q
    pytest -q -k rejected

The rule under test is one sentence: a result that fails the check never
reaches the log. Everything else in this file is there to prove that
sentence holds from both sides.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import main
from harness.events import EventLog
from harness.validation import ToolResultIn

GOOD_RESULT = {
    "tool_call_id": "call_1",
    "tool_name": "todowrite",
    "details": {"todos": [{"content": "write the replay tests", "status": "pending"}]},
}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Every test gets its own log file, so one test cannot leave state behind
    # for the next and the order of the tests cannot matter.
    monkeypatch.setattr(main, "log", EventLog(tmp_path / "events.jsonl"))
    return TestClient(main.app, base_url="http://api.test")


def test_a_valid_tool_result_is_accepted(client):
    response = client.post("/events/tool-result", json=GOOD_RESULT)

    assert response.status_code == 201


def test_an_accepted_tool_result_becomes_one_event(client):
    client.post("/events/tool-result", json=GOOD_RESULT)

    response = client.get("/events")

    assert response.json()["count"] == 1


def test_the_event_records_what_was_sent(client):
    client.post("/events/tool-result", json=GOOD_RESULT)

    event = client.get("/events").json()["events"][0]

    assert event["op"] == "tool_result"
    assert event["payload"]["tool_call_id"] == "call_1"


def test_a_result_missing_a_required_field_is_rejected(client):
    incomplete = {"tool_name": "todowrite"}

    response = client.post("/events/tool-result", json=incomplete)

    assert response.status_code == 422


def test_the_rejection_points_at_the_field_that_is_missing(client):
    incomplete = {"tool_name": "todowrite"}

    response = client.post("/events/tool-result", json=incomplete)

    # `loc` is the part of the lesson that pays off here: it tells the sender
    # which field to fix, instead of only saying that something is wrong.
    locations = [entry["loc"] for entry in response.json()["detail"]]
    assert ["body", "tool_call_id"] in locations


def test_a_rejected_result_never_reaches_the_log(client):
    client.post("/events/tool-result", json=GOOD_RESULT)

    client.post("/events/tool-result", json={"tool_name": "todowrite"})

    # The log still holds exactly the one event that was accepted. This is
    # the rule the whole unit is about.
    assert client.get("/events").json()["count"] == 1


def test_an_unknown_field_is_rejected(client):
    extra = dict(GOOD_RESULT)
    extra["admin"] = True

    response = client.post("/events/tool-result", json=extra)

    assert response.status_code == 422


def test_the_log_is_append_only(client):
    client.post("/events/tool-result", json=GOOD_RESULT)
    first = client.get("/events").json()["events"][0]

    client.post("/events/tool-result", json=dict(GOOD_RESULT, tool_call_id="call_2"))

    events = client.get("/events").json()["events"]
    # The first line is exactly as it was. Nothing rewrites history.
    assert events[0] == first
    assert events[1]["payload"]["tool_call_id"] == "call_2"


def test_reading_a_log_that_does_not_exist_is_not_an_error(tmp_path):
    log = EventLog(tmp_path / "missing.jsonl")

    assert log.read() == []


def test_the_model_rejects_an_unknown_field_outside_the_service():
    with pytest.raises(ValidationError):
        ToolResultIn.model_validate({"tool_call_id": "c", "tool_name": "t", "extra": 1})
