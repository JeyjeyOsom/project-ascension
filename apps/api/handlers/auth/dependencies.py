import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, cast

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from apps.api.db import get_db
from apps.api.models.organization_membership import OrganizationMembership
from apps.api.models.refresh_token import RefreshTokenModel
from apps.api.models.user import User

from .schemas import AuthContext, TokenResponse, UserOut

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "dev-secret-change-me-please-set-a-strong-secret"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900"))
REFRESH_TOKEN_TTL = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _create_token(subject: str, ttl_seconds: int) -> str:
    now = _now()
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        ) from exc


def _hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def _verify_password(password: str, password_hash: str) -> bool:
    return cast(bool, pwd_context.verify(password, password_hash))


def _serialize_user(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        username=user.username,
        is_verified=user.is_verified,
    )


def _issue_tokens(user: User) -> TokenResponse:
    access_token = _create_token(user.id, ACCESS_TOKEN_TTL)
    refresh_token = _create_token(user.id, REFRESH_TOKEN_TTL)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def _create_refresh_token_record(
    db: Session, user_id: str, token: str, rotated_from: str | None = None
) -> RefreshTokenModel:
    expires_at = (_now() + timedelta(seconds=REFRESH_TOKEN_TTL)).replace(
        tzinfo=timezone.utc
    )
    existing = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token_value == token)
        .one_or_none()
    )
    if existing:
        existing.user_id = user_id
        existing.expires_at = expires_at
        existing.revoked = False
        existing.rotated_from = rotated_from
        existing.updated_at = _now()
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing

    record = RefreshTokenModel(
        id=f"rt_{datetime.now(timezone.utc).timestamp()}",
        user_id=user_id,
        token_value=token,
        expires_at=expires_at,
        revoked=False,
        rotated_from=rotated_from,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _get_refresh_token_record(db: Session, token: str) -> RefreshTokenModel | None:
    return (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token_value == token)
        .one_or_none()
    )


def _revoke_refresh_token_record(db: Session, record: RefreshTokenModel) -> None:
    record.revoked = True
    db.add(record)
    db.commit()


def _get_user_membership(
    db: Session, user_id: str, organization_id: str
) -> OrganizationMembership | None:
    return (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
        .one_or_none()
    )


def _require_role(
    db: Session, user_id: str, organization_id: str, minimum_role: str
) -> OrganizationMembership:
    membership = _get_user_membership(db, user_id, organization_id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    role_order = {"member": 1, "admin": 2, "owner": 3}
    if role_order.get(membership.role, 0) < role_order.get(minimum_role, 0):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return membership


def _get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).one_or_none()


def _get_current_auth_context(
    db: Session, credentials: HTTPAuthorizationCredentials | None
) -> AuthContext:
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token"
        )

    payload = _decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
        )

    user = _get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
        )

    return AuthContext(user_id=user.id, email=user.email, username=user.username)


def get_current_auth_context(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    db: Annotated[Session, Depends(get_db)],
) -> AuthContext:
    return _get_current_auth_context(db, credentials)
