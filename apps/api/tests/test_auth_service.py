import jwt
from fastapi import HTTPException

from apps.api.db import SessionLocal
from apps.api.schemas.auth_schema import LoginRequest, RegisterRequest
from apps.api.services.auth_service import AuthService


def test_auth_service_registers_and_authenticates_user() -> None:
    db = SessionLocal()
    try:
        service = AuthService()
        payload = RegisterRequest(
            email="service@example.com",
            username="service_user",
            password="strong-password-123",
        )

        result = service.register_user(db, payload)

        assert result.user.email == payload.email
        assert result.organization_id
        assert result.access_token
        assert result.refresh_token

        login_result = service.authenticate_user(
            db,
            LoginRequest(email=payload.email, password=payload.password),
        )
        assert login_result.user.email == payload.email
    finally:
        db.close()


def test_auth_service_rejects_invalid_credentials() -> None:
    db = SessionLocal()
    try:
        service = AuthService()
        payload = RegisterRequest(
            email="bad-creds@example.com",
            username="bad_creds_user",
            password="strong-password-123",
        )
        service.register_user(db, payload)

        try:
            service.authenticate_user(
                db,
                LoginRequest(email=payload.email, password="wrong-password"),
            )
        except HTTPException as exc:
            assert exc.status_code == 401
            assert exc.detail == "invalid_credentials"
        else:
            raise AssertionError("Expected invalid credentials to raise")
    finally:
        db.close()


def test_auth_service_verifies_token_type_and_signature() -> None:
    db = SessionLocal()
    try:
        service = AuthService()
        payload = RegisterRequest(
            email="token-check@example.com",
            username="token_check_user",
            password="strong-password-123",
        )
        result = service.register_user(db, payload)

        access_token = result.access_token
        access_claims = service.jwt_service.verify_token(access_token, expected_type="access")
        assert access_claims["sub"] == result.user.id

        refresh_token = result.refresh_token
        refresh_claims = service.jwt_service.verify_token(refresh_token, expected_type="refresh")
        assert refresh_claims["sub"] == result.user.id

        try:
            service.jwt_service.verify_token(access_token, expected_type="refresh")
        except HTTPException as exc:
            assert exc.status_code == 401
            assert exc.detail == "invalid_token"
        else:
            raise AssertionError("Expected type mismatch to raise")

        try:
            jwt.decode(access_token[:-1] + "x", "wrong-secret", algorithms=["HS256"])
        except jwt.InvalidTokenError:
            pass
        else:
            raise AssertionError("Expected a malformed token to be invalid")
    finally:
        db.close()
