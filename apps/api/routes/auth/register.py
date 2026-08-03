from fastapi import APIRouter

from apps.api.routes.auth_dependencies import DatabaseSession
from apps.api.schemas.auth_schema import RegisterRequest, RegisterResponse
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.post("/auth/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: DatabaseSession) -> RegisterResponse:
    return service.register_user(db, payload)
