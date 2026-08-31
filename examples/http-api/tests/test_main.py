from fastapi.testclient import TestClient

from main import app


client = TestClient(app, base_url="https://api.test")


def test_health_returns_200_and_expected_body():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_missing_user_returns_404_and_reason():
    response = client.get("/users/missing-user")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_create_user_returns_201_and_can_be_read():
    create_response = client.post(
        "/users",
        json={"name": "test-reader", "note": "Created by an automated test"},
    )
    read_response = client.get("/users/test-reader")

    assert create_response.status_code == 201
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "test-reader"


def test_request_info_uses_request_url_without_exposing_credentials():
    response = client.get("/request-info")

    assert response.status_code == 200
    assert response.json()["scheme"] == "https"
    assert response.json()["host"] == "api.test"
    assert "password" not in response.json()
    assert "token" not in response.json()
