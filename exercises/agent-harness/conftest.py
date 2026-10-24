"""Fixtures shared by every test in the harness track.

Every test gets its own log file, so one test cannot leave state behind
for the next and the order of the tests cannot matter.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

import main
from harness.authz import issue_token
from harness.events import EventLog
from harness.host import Host

TEST_SECRET = b"harness-test-secret"


@pytest.fixture
def secret() -> bytes:
    # The same secret the service uses, so a token minted by the service
    # verifies against the host the test is talking to.
    return main.SECRET


@pytest.fixture
def writer_token(secret: bytes) -> str:
    return issue_token("alice", "writer", secret)


@pytest.fixture
def reader_token(secret: bytes) -> str:
    return issue_token("bob", "reader", secret)


@pytest.fixture
def admin_token(secret: bytes) -> str:
    return issue_token("root", "admin", secret)


@pytest.fixture
def writer_headers(writer_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {writer_token}"}


@pytest.fixture
def reader_headers(reader_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {reader_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def host(tmp_path, monkeypatch, secret: bytes) -> Host:
    instance = Host(EventLog(tmp_path / "events.jsonl"), secret)
    monkeypatch.setattr(main, "host", instance)
    monkeypatch.setattr(main, "log", instance.log)
    return instance


@pytest.fixture
def client(host: Host) -> TestClient:
    return TestClient(main.app, base_url="http://api.test")
