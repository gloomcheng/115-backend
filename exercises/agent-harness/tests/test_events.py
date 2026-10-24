"""Unit 10 — the check that stands in front of the log.

Run:

    pytest -q
    pytest -q -k rejected

The rule under test is one sentence: a result that fails the check never
reaches the log. Everything else in this file is there to prove that
sentence holds from both sides.

Note that the requests carry a token. Unit 11 added that, and it did not
change this rule: a request that fails the shape check is still refused
before it reaches the log, whatever else the caller is allowed to do.
"""

import pytest
from pydantic import ValidationError

from harness.events import EventLog
from harness.validation import ToolResultIn

GOOD_RESULT = {
    "tool_call_id": "call_1",
    "tool_name": "todowrite",
    "details": {"todos": [{"content": "write the replay tests", "status": "pending"}]},
}


def test_a_valid_tool_result_is_accepted(client, writer_headers):
    response = client.post("/events/tool-result", json=GOOD_RESULT, headers=writer_headers)

    assert response.status_code == 201


def test_an_accepted_tool_result_becomes_one_event(client, writer_headers):
    client.post("/events/tool-result", json=GOOD_RESULT, headers=writer_headers)

    response = client.get("/events", headers=writer_headers)

    assert response.json()["count"] == 1


def test_the_event_records_what_was_sent(client, writer_headers):
    client.post("/events/tool-result", json=GOOD_RESULT, headers=writer_headers)

    event = client.get("/events", headers=writer_headers).json()["events"][0]

    assert event["op"] == "tool_result"
    assert event["payload"]["tool_call_id"] == "call_1"


def test_a_result_missing_a_required_field_is_rejected(client, writer_headers):
    incomplete = {"tool_name": "todowrite"}

    response = client.post("/events/tool-result", json=incomplete, headers=writer_headers)

    assert response.status_code == 422


def test_the_rejection_points_at_the_field_that_is_missing(client, writer_headers):
    incomplete = {"tool_name": "todowrite"}

    response = client.post("/events/tool-result", json=incomplete, headers=writer_headers)

    # `loc` is the part of the lesson that pays off here: it tells the sender
    # which field to fix, instead of only saying that something is wrong.
    locations = [entry["loc"] for entry in response.json()["detail"]]
    assert ["body", "tool_call_id"] in locations


def test_a_rejected_result_never_reaches_the_log(client, writer_headers):
    client.post("/events/tool-result", json=GOOD_RESULT, headers=writer_headers)

    client.post("/events/tool-result", json={"tool_name": "todowrite"}, headers=writer_headers)

    # The log still holds exactly the one event that was accepted. This is
    # the rule the whole unit is about.
    assert client.get("/events", headers=writer_headers).json()["count"] == 1


def test_an_unknown_field_is_rejected(client, writer_headers):
    extra = dict(GOOD_RESULT)
    extra["admin"] = True

    response = client.post("/events/tool-result", json=extra, headers=writer_headers)

    assert response.status_code == 422


def test_the_log_is_append_only(client, writer_headers):
    client.post("/events/tool-result", json=GOOD_RESULT, headers=writer_headers)
    first = client.get("/events", headers=writer_headers).json()["events"][0]

    client.post(
        "/events/tool-result",
        json=dict(GOOD_RESULT, tool_call_id="call_2"),
        headers=writer_headers,
    )

    events = client.get("/events", headers=writer_headers).json()["events"]
    # The first line is exactly as it was. Nothing rewrites history.
    assert events[0] == first
    assert events[1]["payload"]["tool_call_id"] == "call_2"


def test_reading_a_log_that_does_not_exist_is_not_an_error(tmp_path):
    log = EventLog(tmp_path / "missing.jsonl")

    assert log.read() == []


def test_the_model_rejects_an_unknown_field_outside_the_service():
    with pytest.raises(ValidationError):
        ToolResultIn.model_validate({"tool_call_id": "c", "tool_name": "t", "extra": 1})


def test_an_event_written_before_meta_existed_is_still_readable(tmp_path):
    # `meta` arrived in unit 15. A line written before that has no meta and
    # still has to be readable.
    legacy = (
        '{"event_id":"abc","observed_at":"2026-10-24T02:11:33Z",'
        '"op":"tool_result","payload":{"tool_name":"todowrite"}}'
    )
    path = tmp_path / "events.jsonl"
    path.write_text(legacy + "\n", encoding="utf-8")

    events = EventLog(path).read()

    assert events[0].meta == {}
