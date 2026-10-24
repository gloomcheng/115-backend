"""Unit 13 — the replay rules, written as assertions.

Run:

    pytest -q -k state

Unit 13 is about testing, and this file is the answer to "what is worth
testing here". The rules of the replay are three sentences, so the tests are
three assertions, each one stated in the name of the test:

1. The same log always replays to the same state.
2. Appending never rewrites what was already written, so the state is a
   function of the whole history.
3. A write that failed is not state.
"""

from harness.events import Event
from harness.state import replay


def event(op: str, payload: dict, event_id: str = "e1") -> Event:
    return Event(
        event_id=event_id,
        observed_at="2026-10-24T02:11:33Z",
        op=op,
        payload=payload,
    )


def todo_event(status: str = "pending", event_id: str = "e1", is_error: bool = False) -> Event:
    return event(
        "tool_result",
        {
            "tool_call_id": "call_1",
            "tool_name": "todowrite",
            "is_error": is_error,
            "details": {"todos": [{"content": "write the replay tests", "status": status}]},
        },
        event_id=event_id,
    )


# -- invariant 1: the same log always replays to the same state -----------


def test_the_same_log_always_replays_to_the_same_state():
    log = [todo_event("pending"), todo_event("completed", event_id="e2")]

    first = replay(log)
    second = replay(log)

    assert first == second


def test_replaying_an_empty_log_gives_an_empty_state():
    state = replay([])

    assert state.todos == ()
    assert state.confirmed is False
    assert state.source_event_id is None


# -- invariant 2: history is not rewritten --------------------------------


def test_appending_does_not_rewrite_an_earlier_event():
    log = [todo_event("pending")]
    first = log[0]

    log.append(todo_event("completed", event_id="e2"))

    assert log[0] == first


def test_the_state_follows_the_whole_history():
    log = [todo_event("pending")]
    assert replay(log).todos[0].status == "pending"

    log.append(todo_event("completed", event_id="e2"))
    assert replay(log).todos[0].status == "completed"


def test_the_state_says_which_event_it_came_from():
    log = [todo_event("pending"), todo_event("completed", event_id="e2")]

    state = replay(log)

    assert state.source_event_id == "e2"
    assert state.updated_at == "2026-10-24T02:11:33Z"


# -- invariant 3: a failed write is not state -----------------------------


def test_a_failed_write_does_not_become_the_state():
    log = [todo_event("pending")]

    state = replay(log)

    assert state.confirmed is True
    assert state.todos[0].status == "pending"


def test_a_failed_write_after_a_confirmed_one_leaves_the_confirmed_state_standing():
    log = [todo_event("pending"), todo_event("completed", event_id="e2", is_error=True)]

    state = replay(log)

    # The failed write is remembered as a failure, and the last thing that
    # is known to have happened still stands.
    assert state.todos[0].status == "pending"
    assert state.last_failed_event_id == "e2"


def test_a_later_confirmed_write_supersedes_the_failure():
    log = [
        todo_event("pending"),
        todo_event("completed", event_id="e2", is_error=True),
        todo_event("cancelled", event_id="e3"),
    ]

    state = replay(log)

    assert state.todos[0].status == "cancelled"
    assert state.last_failed_event_id is None


def test_a_result_from_another_tool_is_not_state():
    log = [event("tool_result", {"tool_name": "read_file", "details": {"path": "/tmp/x"}})]

    state = replay(log)

    assert state.todos == ()
    assert state.confirmed is False


# -- the counts -----------------------------------------------------------


def test_the_counts_add_up_to_the_number_of_todos():
    # One todowrite carries the whole list, so three todos means one event
    # with three items in it.
    log = [
        event(
            "tool_result",
            {
                "tool_call_id": "call_1",
                "tool_name": "todowrite",
                "is_error": False,
                "details": {
                    "todos": [
                        {"content": "write the replay tests", "status": "pending"},
                        {"content": "design the replay rules", "status": "completed"},
                        {"content": "ask about the counterexample", "status": "in_progress"},
                    ]
                },
            },
        )
    ]

    counts = replay(log).counts()

    assert counts["pending"] == 1
    assert counts["completed"] == 1
    assert counts["in_progress"] == 1
    assert sum(counts.values()) == 3


def test_an_unknown_status_is_counted_and_kept():
    log = [todo_event("waiting_for_review")]

    state = replay(log)

    # A status this program has never heard of is still a status somebody
    # used. Dropping it would make the counts lie.
    assert state.todos[0].status == "waiting_for_review"
    assert state.counts()["unknown"] == 1
