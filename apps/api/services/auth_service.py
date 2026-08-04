import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import jwt
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from apps.api.models.organization import Organization
from apps.api.models.organization_membership import OrganizationMembership
from apps.api.models.refresh_token import RefreshTokenModel
from apps.api.models.user import User
from apps.api.repositories.user_repository import UserRepository
from apps.api.schemas.auth_schema import (
    AuthContext,
    AuthenticationResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    OrganizationOut,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserOut,
)

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "dev-secret-change-me-please-set-a-strong-secret"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900"))
REFRESH_TOKEN_TTL = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    def __init__(self, repository: UserRepository | None = None) -> None:
        self.repository = repository or UserRepository()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _create_token(self, subject: str, ttl_seconds: int) -> str:
        now = self._now()
        payload = {
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def _decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
            ) from exc

    def _hash_password(self, password: str) -> str:
        return cast(str, pwd_context.hash(password))

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return cast(bool, pwd_context.verify(password, password_hash))

    def _serialize_user(self, user: User) -> UserOut:
        return UserOut(
            id=user.id,
            email=user.email,
            username=user.username,
            is_verified=user.is_verified,
        )

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = self._create_token(user.id, ACCESS_TOKEN_TTL)
        refresh_token = self._create_token(user.id, REFRESH_TOKEN_TTL)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def _create_refresh_token_record(
        self, db: Session, user_id: str, token: str, rotated_from: str | None = None
    ) -> RefreshTokenModel:
        expires_at = (self._now() + timedelta(seconds=REFRESH_TOKEN_TTL)).replace(
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
            existing.updated_at = self._now()
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

    def _get_refresh_token_record(
        self,
        db: Session,
        token: str,
    ) -> RefreshTokenModel | None:
        return (
            db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token_value == token)
            .one_or_none()
        )

    def _revoke_refresh_token_record(
        self, db: Session, record: RefreshTokenModel
    ) -> None:
        record.revoked = True
        db.add(record)
        db.commit()

    def _get_user_membership(
        self, db: Session, user_id: str, organization_id: str
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
        self, db: Session, user_id: str, organization_id: str, minimum_role: str
    ) -> OrganizationMembership:
        membership = self._get_user_membership(db, user_id, organization_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        role_order = {"member": 1, "admin": 2, "owner": 3}
        if role_order.get(membership.role, 0) < role_order.get(minimum_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        return membership

    def register_user(self, db: Session, payload: RegisterRequest) -> RegisterResponse:
        if self.repository.get_by_email(db, str(payload.email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="email_taken"
            )

        user = User(
            id=f"user_{datetime.now(timezone.utc).timestamp()}",
            email=str(payload.email),
            username=payload.username,
            password_hash=self._hash_password(payload.password),
            is_verified=False,
        )
        organization = Organization(
            id=f"org_{datetime.now(timezone.utc).timestamp()}",
            name=f"{payload.username}'s Organization",
            slug=str(payload.email).split("@", 1)[0].replace(".", "-").lower(),
            owner_id=user.id,
        )
        membership = OrganizationMembership(
            id=f"membership_{datetime.now(timezone.utc).timestamp()}",
            organization_id=organization.id,
            user_id=user.id,
            role="owner",
        )
        db.add_all([user, organization, membership])
        db.commit()
        db.refresh(user)

        tokens = self._issue_tokens(user)
        self._create_refresh_token_record(db, user.id, tokens.refresh_token)
        return RegisterResponse(
            user=self._serialize_user(user),
            organization_id=organization.id,
            **tokens.model_dump(),
        )

    def authenticate_user(
        self, db: Session, payload: LoginRequest
    ) -> AuthenticationResponse:
        user = self.repository.get_by_email(db, str(payload.email))
        if not user or not self._verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
            )

        tokens = self._issue_tokens(user)
        self._create_refresh_token_record(db, user.id, tokens.refresh_token)
        return AuthenticationResponse(
            user=self._serialize_user(user),
            **tokens.model_dump(),
        )

    def refresh_token(self, db: Session, payload: RefreshRequest) -> TokenResponse:
        payload_decoded = self._decode_token(payload.refresh_token)
        user_id = payload_decoded.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
            )

        user = self.repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
            )

        token_record = self._get_refresh_token_record(db, payload.refresh_token)
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
            )

        expires_at = token_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if (
            token_record.user_id != user.id
            or token_record.revoked
            or expires_at < datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
            )

        self._revoke_refresh_token_record(db, token_record)
        tokens = self._issue_tokens(user)
        self._create_refresh_token_record(
            db, user.id, tokens.refresh_token, rotated_from=token_record.id
        )
        return tokens

    def logout(self, db: Session, payload: LogoutRequest) -> LogoutResponse:
        payload_decoded = self._decode_token(payload.refresh_token)
        user_id = payload_decoded.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_refresh_token"
            )

        token_record = self._get_refresh_token_record(db, payload.refresh_token)
        if not token_record or token_record.user_id != user_id or token_record.revoked:
            return LogoutResponse(message="logged_out")

        self._revoke_refresh_token_record(db, token_record)
        return LogoutResponse(message="logged_out")

    def get_current_auth_context(
        self, db: Session, credentials: HTTPAuthorizationCredentials | None
    ) -> AuthContext:
        if credentials is None or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="missing_token"
            )

        payload = self._decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
            )

        user = self.repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found"
            )

        return AuthContext(user_id=user.id, email=user.email, username=user.username)

    def get_user_profile(self, db: Session, user_id: str) -> UserOut:
        user = self.repository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found"
            )
        return self._serialize_user(user)

    def get_organization_access(
        self, db: Session, organization_id: str, auth: AuthContext
    ) -> OrganizationOut:
        organization = db.get(Organization, organization_id)
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="organization_not_found"
            )

        membership = self._require_role(db, auth.user_id, organization_id, "member")
        return OrganizationOut(
            id=organization.id,
            name=organization.name,
            slug=organization.slug,
            owner_id=organization.owner_id,
            role=membership.role,
        )
