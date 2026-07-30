from fastapi import APIRouter, HTTPException, status

from apps.api.models.organization import Organization

from .dependencies import _require_role
from .route_dependencies import AuthContextDependency, DatabaseSession
from .schemas import OrganizationOut

router = APIRouter(tags=["auth"])


@router.get("/auth/organizations/{organization_id}", response_model=OrganizationOut)
def get_organization(
    organization_id: str,
    auth: AuthContextDependency,
    db: DatabaseSession,
) -> OrganizationOut:
    organization = db.get(Organization, organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="organization_not_found"
        )

    membership = _require_role(db, auth.user_id, organization_id, "member")
    return OrganizationOut(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        owner_id=organization.owner_id,
        role=membership.role,
    )
