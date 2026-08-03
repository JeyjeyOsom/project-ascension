from fastapi import APIRouter

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import LogoutRequest, LogoutResponse
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/logout", response_model=LogoutResponse)
def logout(payload: LogoutRequest, db: DatabaseSession) -> LogoutResponse:
    return service.logout(db, payload)
