
from fastapi import APIRouter

from apps.api.routes.auth_dependencies import AuthContextDependency, DatabaseSession
from apps.api.schemas.auth_schema import UserOut
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.get("/auth/me", response_model=UserOut)
def get_me(
    auth: AuthContextDependency,
    db: DatabaseSession,
) -> UserOut:
    return service.get_user_profile(db, auth.user_id)
