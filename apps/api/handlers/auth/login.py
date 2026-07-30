from fastapi import APIRouter, HTTPException, status

from .dependencies import (
    _create_refresh_token_record,
    _get_user_by_email,
    _issue_tokens,
    _serialize_user,
    _verify_password,
)
from .route_dependencies import DatabaseSession
from .schemas import AuthenticationResponse, LoginRequest

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=AuthenticationResponse)
def login(payload: LoginRequest, db: DatabaseSession) -> AuthenticationResponse:
    user = _get_user_by_email(db, str(payload.email))
    if not user or not _verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )

    tokens = _issue_tokens(user)
    _create_refresh_token_record(db, user.id, tokens.refresh_token)
    return AuthenticationResponse(user=_serialize_user(user), **tokens.model_dump())
