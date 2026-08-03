
from fastapi import APIRouter

from apps.api.routes.auth_dependencies import AuthContextDependency, DatabaseSession
from apps.api.schemas.auth_schema import OrganizationOut
from apps.api.services.auth_service import AuthService

router = APIRouter(tags=["auth"])
service = AuthService()


@router.get("/auth/organizations/{organization_id}", response_model=OrganizationOut)
def get_organization(
    organization_id: str,
    auth: AuthContextDependency,
    db: DatabaseSession,
) -> OrganizationOut:
    return service.get_organization_access(db, organization_id, auth)
