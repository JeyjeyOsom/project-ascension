from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from apps.api.db import get_db
from apps.api.schemas.auth_schema import AuthContext
from apps.api.services.auth_service import AuthService

security = HTTPBearer(auto_error=False)
service = AuthService()

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> AuthContext:
    return service.get_current_auth_context(db, credentials)


AuthContextDependency = Annotated[AuthContext, Depends(get_current_auth_context)]
