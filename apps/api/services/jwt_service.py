import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status

JWT_SECRET = os.getenv(
    "JWT_SECRET_KEY", "dev-secret-change-me-please-set-a-strong-secret"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900")) // 60
REFRESH_TOKEN_EXPIRE_DAYS = (
    int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", "604800")) // 86400
)


class JWTService:
    def create_access_token(self, subject: str) -> str:
        return self._create_token(subject=subject, token_type="access")

    def create_refresh_token(self, subject: str) -> str:
        return self._create_token(subject=subject, token_type="refresh")

    def verify_token(
        self, token: str, expected_type: str | None = None
    ) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="token_expired"
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
            ) from exc

        token_type = payload.get("type")
        if expected_type and token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token"
            )

        return payload

    def _create_token(self, subject: str, token_type: str) -> str:
        now = self._now()
        payload = {
            "sub": subject,
            "type": token_type,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl_for(token_type)).timestamp()),
            "jti": str(uuid.uuid4()),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def _ttl_for(self, token_type: str) -> timedelta:
        if token_type == "refresh":
            return timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)
