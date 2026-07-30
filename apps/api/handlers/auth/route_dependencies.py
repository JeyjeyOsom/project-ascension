from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from apps.api.db import get_db

from .dependencies import get_current_auth_context
from .schemas import AuthContext

DatabaseSession = Annotated[Session, Depends(get_db)]
AuthContextDependency = Annotated[AuthContext, Depends(get_current_auth_context)]
