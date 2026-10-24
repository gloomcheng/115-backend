"""Unit 15 — one id that follows a request into the log.

Run:

    pytest -q -k trace

The rule under test: one request, one id, and that id lands on every event
the request produced. After that, one number is enough to pull the whole
request back out of the log.
"""

from harness.trace import (
    TRACE_HEADER,
    is_trace_id,
    new_trace_id,
    normalize_trace_id,
    select_by_trace,
    traces_of,
)


def test_a_generated_trace_id_has_the_right_shape():
    assert is_trace_id(new_trace_id())


def test_a_caller_supplied_trace_id_is_kept():
    candidate = "0123456789abcdef"

    assert normalize_trace_id(candidate) == candidate


def test_a_caller_supplied_id_of_the_wrong_shape_is_replaced():
    # An id the caller fully controls is an id two requests can collide on,
    # so one that does not look like a trace id is dropped, not repaired.
    replaced = normalize_trace_id("../../etc/passwd")

    assert replaced != "../../etc/passwd"
    assert is_trace_id(replaced)


def test_the_response_carries_the_trace_id(client, writer_headers):
    response = client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_1", "tool_name": "todowrite"},
        headers=writer_headers,
    )

    assert TRACE_HEADER in response.headers
    assert is_trace_id(response.headers[TRACE_HEADER])


def test_a_caller_may_correlate_with_its_own_id(client, writer_headers):
    response = client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_1", "tool_name": "todowrite"},
        headers={**writer_headers, TRACE_HEADER: "0123456789abcdef"},
    )

    assert response.headers[TRACE_HEADER] == "0123456789abcdef"


def test_the_event_carries_the_trace_id(client, writer_headers):
    client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_1", "tool_name": "todowrite"},
        headers={**writer_headers, TRACE_HEADER: "0123456789abcdef"},
    )

    event = client.get("/events", headers=writer_headers).json()["events"][0]

    assert event["meta"]["trace_id"] == "0123456789abcdef"


def test_one_trace_id_pulls_out_only_its_own_events(client, host, writer_headers):
    client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_1", "tool_name": "todowrite"},
        headers={**writer_headers, TRACE_HEADER: "aaaaaaaaaaaaaaaa"},
    )
    client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_2", "tool_name": "todowrite"},
        headers={**writer_headers, TRACE_HEADER: "bbbbbbbbbbbbbbbb"},
    )

    events = host.log.read()

    assert len(select_by_trace(events, "aaaaaaaaaaaaaaaa")) == 1
    assert len(select_by_trace(events, "bbbbbbbbbbbbbbbb")) == 1
    assert traces_of(events) == ["aaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbb"]
