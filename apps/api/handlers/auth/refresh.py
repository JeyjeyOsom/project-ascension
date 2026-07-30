from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from .dependencies import (
    _create_refresh_token_record,
    _decode_token,
    _get_refresh_token_record,
    _get_user_by_id,
    _issue_tokens,
    _revoke_refresh_token_record,
)
from .route_dependencies import DatabaseSession
from .schemas import RefreshRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DatabaseSession) -> TokenResponse:
    payload_decoded = _decode_token(payload.refresh_token)
    user_id = payload_decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
        )

    user = _get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
        )

    token_record = _get_refresh_token_record(db, payload.refresh_token)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
        )

    expires_at = token_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if (
        token_record.user_id != user.id
        or token_record.revoked
        or expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
        )

    _revoke_refresh_token_record(db, token_record)
    tokens = _issue_tokens(user)
    _create_refresh_token_record(
        db, user.id, tokens.refresh_token, rotated_from=token_record.id
    )
    return tokens
