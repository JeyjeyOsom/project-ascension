from fastapi import APIRouter

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import RefreshRequest, TokenResponse
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DatabaseSession) -> TokenResponse:
    return service.refresh_token(db, payload)
