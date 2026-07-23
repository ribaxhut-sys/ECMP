"""API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.health import router as health_router
from app.modules.assignments.router import router as assignments_router
from app.modules.auth.router import router as auth_router
from app.modules.branches.router import router as branches_router
from app.modules.complaints.router import router as complaints_router
from app.modules.customers.router import router as customers_router
from app.modules.escalations.router import (
    escalations_router,
    router as complaint_escalations_router,
)
from app.modules.reports.router import router as reports_router
from app.modules.resolutions.router import router as resolutions_router
from app.modules.timelines.router import router as timelines_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(reports_router)
api_router.include_router(customers_router)
api_router.include_router(branches_router)
api_router.include_router(users_router)
# Specific sub-routes before generic /{id} complaint routes.
api_router.include_router(assignments_router)
api_router.include_router(complaint_escalations_router)
api_router.include_router(escalations_router)
api_router.include_router(resolutions_router)
api_router.include_router(timelines_router)
api_router.include_router(complaints_router)
