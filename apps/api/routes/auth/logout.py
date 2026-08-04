from typing import Annotated

from fastapi import APIRouter, Body, Request, Response

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import LogoutRequest, LogoutResponse
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(
    payload: Annotated[LogoutRequest | None, Body()] = None,
    db: DatabaseSession = None,
    request: Request = None,
    response: Response = None,
) -> LogoutResponse:
    token_value = (
        payload.refresh_token if payload and payload.refresh_token else None
    ) or (request.cookies.get("refresh_token") if request else None)
    if response is not None:
        response.delete_cookie("refresh_token")
    if not token_value:
        return LogoutResponse(message="logged_out")
    return service.logout(db, LogoutRequest(refresh_token=token_value))
