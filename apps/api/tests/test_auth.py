from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.main import DATABASE_URL, app, Base, engine, run_migrations

client = TestClient(app)


def setup_function() -> None:
    if DATABASE_URL.startswith("sqlite"):
        db_path = Path(DATABASE_URL.replace("sqlite://", "", 1))
        if db_path.exists():
            try:
                db_path.unlink()
            except PermissionError:
                pass
    try:
        engine.dispose()
    except Exception:
        pass
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
    run_migrations()


def test_register_login_refresh_and_me_flow() -> None:
    register_payload = {
        "email": "user@example.com",
        "username": "demo_user",
        "password": "strong-password-123",
    }

    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 200
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
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={"email": register_payload["email"], "password": register_payload["password"]},
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
    assert register_response.status_code == 200

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
    assert other_user_response.status_code == 200

    unauthorized_response = client.get(
        f"/auth/organizations/{organization_id}",
        headers={"Authorization": f"Bearer {other_user_response.json()['access_token']}"},
    )
    assert unauthorized_response.status_code == 403
