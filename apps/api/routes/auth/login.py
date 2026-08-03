from fastapi import APIRouter

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import AuthenticationResponse, LoginRequest
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/login", response_model=AuthenticationResponse)
def login(payload: LoginRequest, db: DatabaseSession) -> AuthenticationResponse:
    return service.authenticate_user(db, payload)
