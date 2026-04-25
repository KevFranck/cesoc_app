"""Routeur principal API v1."""

from fastapi import APIRouter

from server.app.api.v1.admin import router as admin_router
from server.app.api.v1.auth import router as auth_router
from server.app.api.v1.prints import router as prints_router
from server.app.api.v1.reports import router as reports_router
from server.app.api.v1.sessions import router as sessions_router
from server.app.api.v1.users import router as users_router


api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(auth_router)
api_router.include_router(sessions_router)
api_router.include_router(prints_router)
api_router.include_router(reports_router)
api_router.include_router(users_router)
