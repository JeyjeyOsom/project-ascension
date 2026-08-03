from fastapi import APIRouter

from .auth import (
    login_router,
    logout_router,
    me_router,
    organization_router,
    refresh_router,
    register_router,
)

router = APIRouter(tags=["auth"])
router.include_router(register_router)
router.include_router(login_router)
router.include_router(refresh_router)
router.include_router(logout_router)
router.include_router(me_router)
router.include_router(organization_router)
