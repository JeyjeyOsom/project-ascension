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
