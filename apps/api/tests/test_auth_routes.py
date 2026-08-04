from datetime import datetime, timedelta, timezone

import jwt
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


def test_login_rejects_unknown_and_invalid_credentials() -> None:
    client.post(
        "/auth/register",
        json={
            "email": "login-errors@example.com",
            "username": "login_errors_user",
            "password": "strong-password-123",
        },
    )

    unknown_email_response = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "strong-password-123"},
    )
    assert unknown_email_response.status_code == 401
    assert unknown_email_response.json() == {"detail": "invalid_credentials"}

    wrong_password_response = client.post(
        "/auth/login",
        json={
            "email": "login-errors@example.com",
            "password": "wrong-password",
        },
    )
    assert wrong_password_response.status_code == 401
    assert wrong_password_response.json() == {"detail": "invalid_credentials"}


def test_expired_and_invalid_signature_tokens_are_rejected() -> None:
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": "user_123",
        "type": "access",
        "iat": int((now - timedelta(minutes=20)).timestamp()),
        "exp": int((now - timedelta(minutes=1)).timestamp()),
        "jti": "expired-token",
    }
    expired_token = jwt.encode(
        expired_payload,
        "test-secret-key-with-at-least-32-characters",
        algorithm="HS256",
    )

    expired_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired_response.status_code == 401
    assert expired_response.json() == {"detail": "token_expired"}

    invalid_signature_token = jwt.encode(
        {
            "sub": "user_123",
            "type": "access",
            "exp": int((now + timedelta(minutes=15)).timestamp()),
        },
        "different-secret",
        algorithm="HS256",
    )
    invalid_signature_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {invalid_signature_token}"},
    )
    assert invalid_signature_response.status_code == 401
    assert invalid_signature_response.json() == {"detail": "invalid_token"}


def test_refresh_flow_issues_a_new_access_token() -> None:
    client.post(
        "/auth/register",
        json={
            "email": "refresh-flow@example.com",
            "username": "refresh_flow_user",
            "password": "strong-password-123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh-flow@example.com",
            "password": "strong-password-123",
        },
    )
    assert login_response.status_code == 200

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert (
        refresh_response.json()["access_token"] != login_response.json()["access_token"]
    )
