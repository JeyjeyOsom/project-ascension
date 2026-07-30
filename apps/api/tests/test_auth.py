from fastapi.testclient import TestClient
from sqlalchemy import inspect

from apps.api.main import app, engine

client = TestClient(app)


def test_register_login_refresh_and_me_flow() -> None:
    register_payload = {
        "email": "user@example.com",
        "username": "demo_user",
        "password": "strong-password-123",
    }

    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["email"] == register_payload["email"]
    assert register_body["user"]["username"] == register_payload["username"]
    assert "access_token" in register_body
    assert "refresh_token" in register_body

    login_response = client.post(
        "/auth/login",
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["user"]["email"] == register_payload["email"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_body['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == register_payload["email"]

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": login_body["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": login_body["refresh_token"]},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "logged_out"


def test_refresh_token_rotation_and_revocation() -> None:
    register_payload = {
        "email": "refresh@example.com",
        "username": "refresh_user",
        "password": "strong-password-123",
    }

    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert login_response.status_code == 200

    first_refresh_token = login_response.json()["refresh_token"]
    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert refresh_response.status_code == 200
    rotated_refresh_token = refresh_response.json()["refresh_token"]
    assert rotated_refresh_token

    reused_refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": first_refresh_token},
    )
    assert reused_refresh_response.status_code == 401

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": rotated_refresh_token},
    )
    assert logout_response.status_code == 200

    after_logout_refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": rotated_refresh_token},
    )
    assert after_logout_refresh_response.status_code == 401


def test_user_can_access_their_organization_and_unauthorized_users_cannot() -> None:
    register_payload = {
        "email": "org@example.com",
        "username": "org_user",
        "password": "strong-password-123",
    }

    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201

    access_token = register_response.json()["access_token"]
    organization_id = register_response.json()["organization_id"]

    authorized_response = client.get(
        f"/auth/organizations/{organization_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert authorized_response.status_code == 200
    assert authorized_response.json()["slug"] == "org"

    other_user_payload = {
        "email": "other@example.com",
        "username": "other_user",
        "password": "strong-password-123",
    }
    other_user_response = client.post("/auth/register", json=other_user_payload)
    assert other_user_response.status_code == 201

    unauthorized_response = client.get(
        f"/auth/organizations/{organization_id}",
        headers={
            "Authorization": f"Bearer {other_user_response.json()['access_token']}"
        },
    )
    assert unauthorized_response.status_code == 403


def test_auth_errors_use_stable_detail_codes() -> None:
    register_payload = {
        "email": "errors@example.com",
        "username": "errors_user",
        "password": "strong-password-123",
    }

    assert client.post("/auth/register", json=register_payload).status_code == 201

    duplicate_response = client.post("/auth/register", json=register_payload)
    assert duplicate_response.status_code == 400
    assert duplicate_response.json() == {"detail": "email_taken"}

    invalid_login_response = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": "incorrect-password"},
    )
    assert invalid_login_response.status_code == 401
    assert invalid_login_response.json() == {"detail": "invalid_credentials"}

    missing_token_response = client.get("/auth/me")
    assert missing_token_response.status_code == 401
    assert missing_token_response.json() == {"detail": "missing_token"}

    malformed_response = client.post("/auth/register", json={})
    assert malformed_response.status_code == 422
    assert "detail" in malformed_response.json()


def test_registration_refresh_token_can_be_refreshed() -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "new-token@example.com",
            "username": "new_token_user",
            "password": "strong-password-123",
        },
    )
    assert register_response.status_code == 201

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": register_response.json()["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["token_type"] == "bearer"


def test_membership_lookup_index_is_migrated() -> None:
    indexes = inspect(engine).get_indexes("organization_memberships")

    assert any(
        index["name"] == "ix_organization_memberships_organization_id_user_id"
        and index["column_names"] == ["organization_id", "user_id"]
        for index in indexes
    )
