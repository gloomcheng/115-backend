"""Unit 11 — who may write, who may read.

Run:

    pytest -q -k authz

The rule under test: a request carries a role, and every write and every
read is checked against that role before it happens.
"""

import pytest

from harness.authz import (
    AuthError,
    Principal,
    issue_token,
    require_role,
    verify_token,
)

SECRET = b"unit-11-secret"


def test_a_token_round_trips_into_a_principal():
    token = issue_token("alice", "writer", SECRET)

    principal = verify_token(token, SECRET)

    assert principal.subject == "alice"
    assert principal.role == "writer"


def test_a_token_signed_with_another_secret_is_refused():
    token = issue_token("alice", "writer", SECRET)

    with pytest.raises(AuthError) as caught:
        verify_token(token, b"a-different-secret")

    assert caught.value.status == 401
    assert caught.value.reason == "bad signature"


def test_a_tampered_payload_is_refused():
    token = issue_token("alice", "reader", SECRET)
    header, _payload, signature = token.split(".")
    forged = f"{header}.eyJzdWIiOiJhbGljZSIsInJvbGUiOiJhZG1pbiJ9.{signature}"

    with pytest.raises(AuthError) as caught:
        verify_token(forged, SECRET)

    assert caught.value.status == 401


def test_a_malformed_token_is_refused():
    with pytest.raises(AuthError) as caught:
        verify_token("not-a-token", SECRET)

    assert caught.value.status == 401
    assert caught.value.reason == "malformed token"


def test_an_expired_token_is_refused():
    token = issue_token("alice", "reader", SECRET, ttl_seconds=60, now=1000.0)

    with pytest.raises(AuthError) as caught:
        verify_token(token, SECRET, now=1061.0)

    assert caught.value.reason == "token expired"


def test_a_reader_cannot_write():
    reader = Principal(subject="bob", role="reader")

    with pytest.raises(AuthError) as caught:
        require_role(reader, "writer")

    assert caught.value.status == 403


def test_a_writer_can_read_and_write():
    writer = Principal(subject="alice", role="writer")

    assert writer.can("reader")
    assert writer.can("writer")
    assert not writer.can("admin")


def test_a_reader_cannot_reach_the_write_route(client, reader_headers):
    response = client.post(
        "/events/tool-result",
        json={"tool_call_id": "call_1", "tool_name": "todowrite"},
        headers=reader_headers,
    )

    assert response.status_code == 403


def test_a_request_without_a_token_is_refused(client):
    response = client.get("/events")

    assert response.status_code == 401


def test_a_request_with_a_bad_token_is_refused(client):
    response = client.get("/events", headers={"Authorization": "Bearer nonsense"})

    assert response.status_code == 401


def test_only_an_admin_may_mint_tokens(client, writer_headers, admin_headers):
    refused = client.post("/tokens?subject=carol&role=reader", headers=writer_headers)
    assert refused.status_code == 403

    allowed = client.post("/tokens?subject=carol&role=reader", headers=admin_headers)
    assert allowed.status_code == 201
    assert allowed.json()["subject"] == "carol"


def test_a_minted_token_works(client, admin_headers, reader_headers):
    minted = client.post("/tokens?subject=carol&role=reader", headers=admin_headers).json()

    response = client.get("/events", headers={"Authorization": f"Bearer {minted['token']}"})

    assert response.status_code == 200
