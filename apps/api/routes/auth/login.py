import os

from fastapi import APIRouter, Response

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import AuthenticationResponse, LoginRequest
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/login", response_model=AuthenticationResponse)
def login(
    payload: LoginRequest,
    db: DatabaseSession,
    response: Response,
) -> AuthenticationResponse:
    result = service.authenticate_user(db, payload)
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        samesite="lax",
        secure=os.getenv("ENVIRONMENT", "development") == "production",
        max_age=int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800")),
    )
    return result
