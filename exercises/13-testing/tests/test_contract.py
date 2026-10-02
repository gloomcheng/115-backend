"""Lesson 13 — the contract, written as assertions.

Run:

    pytest -q
    pytest -q -k health

Section 04 of this lesson deletes the body assertion on purpose and shows
the suite going green on a broken API. That experiment is the point of the
whole unit, so do not skip it.
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    # A fresh app per test, so one test cannot leave state behind for the next.
    return TestClient(app, base_url="https://api.test")


# --- the contract rows -------------------------------------------------


def test_health_returns_200(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_health_body_is_exactly_ok_true(client):
    # This is the assertion that earns its keep. Change True to "yes" in
    # main.py and this one fails while the one above still passes.
    response = client.get("/health")

    assert response.json() == {"ok": True}


def test_health_sets_content_type_json(client):
    response = client.get("/health")

    assert response.headers["content-type"] == "application/json"


def test_missing_note_returns_404_with_reason(client):
    response = client.get("/notes/missing")

    # Status code and body are both part of the contract, so both are asserted.
    assert response.status_code == 404
    assert response.json() == {"detail": "Note not found"}


def test_create_then_read_round_trips(client):
    create_response = client.post(
        "/notes",
        json={"name": "test-note", "title": "From a test", "body": "written by pytest"},
    )
    read_response = client.get("/notes/test-note")

    assert create_response.status_code == 201
    assert read_response.status_code == 200
    assert read_response.json() == {
        "title": "From a test",
        "body": "written by pytest",
    }


def test_list_reports_a_count_that_matches_the_items(client):
    response = client.get("/notes")

    payload = response.json()
    # Asserting the relationship, not a hardcoded number, so the test keeps
    # holding when the fixture data changes.
    assert payload["count"] == len(payload["items"])


def test_create_without_name_is_rejected(client):
    response = client.post("/notes", json={"title": "no name here"})

    assert response.status_code == 422
    assert response.json() == {"detail": "name is required"}
