from fastapi import APIRouter

from .get_me import router as get_me_router
from .get_organization import router as get_organization_router
from .login import router as login_router
from .logout import router as logout_router
from .refresh import router as refresh_router
from .register import router as register_router

router = APIRouter()
router.include_router(register_router)
router.include_router(login_router)
router.include_router(refresh_router)
router.include_router(logout_router)
router.include_router(get_me_router)
router.include_router(get_organization_router)
