from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from apps.api.models.organization import Organization
from apps.api.models.organization_membership import OrganizationMembership
from apps.api.models.user import User

from .dependencies import (
    _create_refresh_token_record,
    _get_user_by_email,
    _hash_password,
    _issue_tokens,
    _serialize_user,
)
from .route_dependencies import DatabaseSession
from .schemas import RegisterRequest, RegisterResponse

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: DatabaseSession) -> RegisterResponse:
    if _get_user_by_email(db, str(payload.email)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_taken"
        )

    user = User(
        id=f"user_{datetime.now(timezone.utc).timestamp()}",
        email=str(payload.email),
        username=payload.username,
        password_hash=_hash_password(payload.password),
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

    tokens = _issue_tokens(user)
    _create_refresh_token_record(db, user.id, tokens.refresh_token)
    return RegisterResponse(
        user=_serialize_user(user),
        organization_id=organization.id,
        **tokens.model_dump(),
    )
