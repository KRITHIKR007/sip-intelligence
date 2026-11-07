"""
SIP Intelligence — API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.documents import router as documents_router
from app.api.v1.drawings import router as drawings_router
from app.api.v1.chat import router as chat_router
from app.api.v1.validation_api import router as validation_router
from app.api.v1.knowledge import (
    knowledge_router,
    models_router,
    feedback_router,
    admin_router,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(documents_router)
api_router.include_router(drawings_router)
api_router.include_router(chat_router)
api_router.include_router(validation_router)
api_router.include_router(knowledge_router)
api_router.include_router(models_router)
api_router.include_router(feedback_router)
api_router.include_router(admin_router)

