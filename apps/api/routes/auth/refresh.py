from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Request, Response, status

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import RefreshRequest, TokenResponse
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(
    db: DatabaseSession,
    payload: Annotated[RefreshRequest | None, Body()] = None,
    request: Request | None = None,
    response: Response | None = None,
) -> TokenResponse:
    token_value = (
        payload.refresh_token if payload and payload.refresh_token else None
    ) or (request.cookies.get("refresh_token") if request else None)
    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_refresh_token",
        )

    result = service.refresh_token(db, RefreshRequest(refresh_token=token_value))
    if response is not None:
        response.set_cookie(
            key="refresh_token",
            value=result.refresh_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=604800,
        )
    return result
