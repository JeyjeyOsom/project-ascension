from fastapi import APIRouter, HTTPException, status

from .dependencies import _get_user_by_id, _serialize_user
from .route_dependencies import AuthContextDependency, DatabaseSession
from .schemas import UserOut

router = APIRouter(tags=["auth"])


@router.get("/auth/me", response_model=UserOut)
def get_me(auth: AuthContextDependency, db: DatabaseSession) -> UserOut:
    user = _get_user_by_id(db, auth.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found"
        )
    return _serialize_user(user)
