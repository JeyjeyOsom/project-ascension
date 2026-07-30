from fastapi import APIRouter, HTTPException, status

from .dependencies import (
    _decode_token,
    _get_refresh_token_record,
    _revoke_refresh_token_record,
)
from .route_dependencies import DatabaseSession
from .schemas import LogoutRequest, LogoutResponse

router = APIRouter(tags=["auth"])


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(payload: LogoutRequest, db: DatabaseSession) -> LogoutResponse:
    payload_decoded = _decode_token(payload.refresh_token)
    user_id = payload_decoded.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
        )

    token_record = _get_refresh_token_record(db, payload.refresh_token)
    if not token_record or token_record.user_id != user_id or token_record.revoked:
        return LogoutResponse(message="logged_out")

    _revoke_refresh_token_record(db, token_record)
    return LogoutResponse(message="logged_out")
