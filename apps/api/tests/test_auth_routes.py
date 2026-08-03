from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_auth_routes_still_support_login_register_and_me() -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "routes@example.com",
            "username": "routes_user",
            "password": "strong-password-123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "routes@example.com",
            "password": "strong-password-123",
        },
    )
    assert login_response.status_code == 200

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "routes@example.com"
